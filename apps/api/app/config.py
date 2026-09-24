from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://video_editor:video_editor@localhost:5432/video_editor"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"
    data_dir: str = "./data"
    max_upload_mb: int = 2048
    enable_transcription: bool = False
    whisper_model: str = "small"
    google_client_secrets: str = "./data/tokens/client_secret.json"
    google_token_file: str = "./data/tokens/youtube_token.json"
    youtube_redirect_uri: str = "http://localhost:8000/api/youtube/callback"
    web_base_url: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
