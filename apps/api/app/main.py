from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .db import Base, engine
from .routers import projects, jobs, youtube

settings = get_settings()
Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
Path(settings.data_dir, "uploads").mkdir(parents=True, exist_ok=True)
Path(settings.data_dir, "renders").mkdir(parents=True, exist_ok=True)
Path(settings.data_dir, "tokens").mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="YouTube Auto Editor API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=settings.data_dir), name="media")
app.include_router(projects.router)
app.include_router(jobs.router)
app.include_router(youtube.router)

@app.get("/health")
def health():
    return {"ok": True}
