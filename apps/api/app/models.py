from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    source_filename: Mapped[str] = mapped_column(String(512))
    source_path: Mapped[str] = mapped_column(String(1024))
    rendered_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="uploaded")
    duration_seconds: Mapped[float | None] = mapped_column(nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    captions_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
