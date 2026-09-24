from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..config import get_settings
from ..db import get_db
from ..models import Project
from ..schemas import JobOut, ProjectOut, RenderRequest
from ..services.video import ffprobe_duration
from ..celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()

@router.post("", response_model=ProjectOut)
async def create_project(
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    allowed = {"video/mp4", "video/quicktime", "video/x-matroska", "video/webm"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Unsupported video type. Use MP4, MOV, MKV or WebM.")
    upload_dir = Path(settings.data_dir) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "video.mp4").suffix.lower() or ".mp4"
    destination = upload_dir / f"{uuid4().hex}{suffix}"
    size = 0
    with destination.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                destination.unlink(missing_ok=True)
                raise HTTPException(413, "File is too large")
            out.write(chunk)
    project = Project(name=name or Path(file.filename or "Untitled").stem, source_filename=file.filename or destination.name, source_path=str(destination), status="uploaded")
    db.add(project)
    db.commit()
    db.refresh(project)
    try:
        project.duration_seconds = ffprobe_duration(str(destination))
        db.commit()
        db.refresh(project)
    except Exception:
        pass
    return project

@router.post("/{project_id}/render", response_model=JobOut)
def render_project(project_id: int, payload: RenderRequest, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    task = celery_app.send_task("render_project", args=[project_id, payload.model_dump()])
    project.status = "queued"
    db.commit()
    return JobOut(task_id=task.id, status="queued")

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project
