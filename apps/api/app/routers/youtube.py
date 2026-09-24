from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..config import get_settings
from ..db import get_db
from ..models import Project
from ..services.youtube import authorization_url, exchange_code, upload_video

router = APIRouter(prefix="/api/youtube", tags=["youtube"])

class UploadRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = ""
    tags: list[str] = []
    privacy_status: str = "private"

@router.get("/auth")
def youtube_auth():
    try:
        return {"url": authorization_url()}
    except Exception as exc:
        raise HTTPException(500, f"YouTube OAuth is not configured: {exc}")

@router.get("/callback")
def youtube_callback(code: str):
    settings = get_settings()
    try:
        exchange_code(code)
    except Exception as exc:
        raise HTTPException(400, f"OAuth callback failed: {exc}")
    return RedirectResponse(f"{settings.web_base_url}/?youtube=connected")

@router.post("/projects/{project_id}/upload")
def youtube_upload(project_id: int, payload: UploadRequest, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project or not project.rendered_path:
        raise HTTPException(400, "Render the project before uploading it.")
    if payload.privacy_status not in {"private", "unlisted", "public"}:
        raise HTTPException(400, "privacy_status must be private, unlisted or public")
    try:
        video_id = upload_video(project.rendered_path, payload.title, payload.description, payload.tags, payload.privacy_status)
    except FileNotFoundError as exc:
        raise HTTPException(400, "YouTube OAuth is not connected. Visit /api/youtube/auth first.") from exc
    except Exception as exc:
        raise HTTPException(500, f"YouTube upload failed: {exc}") from exc
    return {"video_id": video_id, "url": f"https://youtu.be/{video_id}"}
