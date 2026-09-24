from datetime import datetime
from pydantic import BaseModel, Field

class ProjectOut(BaseModel):
    id: int
    name: str
    source_filename: str
    source_path: str
    rendered_path: str | None
    status: str
    duration_seconds: float | None
    captions_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RenderRequest(BaseModel):
    remove_silence: bool = True
    remove_filler_words: bool = False
    generate_captions: bool = True
    silence_threshold_db: int = Field(default=-35, ge=-60, le=-10)
    silence_min_duration: float = Field(default=0.45, ge=0.1, le=5)

class JobOut(BaseModel):
    task_id: str
    status: str
    result: object | None = None
