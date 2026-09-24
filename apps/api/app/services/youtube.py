from __future__ import annotations

import json
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from ..config import get_settings

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def build_flow() -> Flow:
    settings = get_settings()
    flow = Flow.from_client_secrets_file(settings.google_client_secrets, scopes=SCOPES)
    flow.redirect_uri = settings.youtube_redirect_uri
    return flow

def authorization_url() -> str:
    flow = build_flow()
    url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
    return url

def save_credentials(credentials: Credentials) -> None:
    settings = get_settings()
    path = Path(settings.google_token_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(credentials.to_json())

def load_credentials() -> Credentials:
    settings = get_settings()
    return Credentials.from_authorized_user_file(settings.google_token_file, SCOPES)

def exchange_code(code: str) -> Credentials:
    flow = build_flow()
    flow.fetch_token(code=code)
    save_credentials(flow.credentials)
    return flow.credentials

def upload_video(video_path: str, title: str, description: str, tags: list[str], privacy_status: str) -> str:
    credentials = load_credentials()
    youtube = build("youtube", "v3", credentials=credentials)
    body = {
        "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
        "status": {"privacyStatus": privacy_status},
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
    )
    response = request.execute()
    return response["id"]
