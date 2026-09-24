from app.celery_app import celery_app
from app.services.video import process_project

@celery_app.task(bind=True, name="render_project")
def render_project(self, project_id: int, options: dict):
    return process_project(project_id, options)
