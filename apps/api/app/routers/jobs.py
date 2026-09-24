from celery.result import AsyncResult
from fastapi import APIRouter
from ..celery_app import celery_app
from ..schemas import JobOut

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/{task_id}", response_model=JobOut)
def job_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    payload = None
    if result.successful():
        payload = result.result
    elif result.failed():
        payload = {"error": str(result.result)}
    return JobOut(task_id=task_id, status=result.status.lower(), result=payload)
