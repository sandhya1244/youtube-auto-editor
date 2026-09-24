# YouTube Auto Editor

A starter monorepo for a web-based automated YouTube editor.

## Included

- Next.js 16 frontend
- FastAPI REST API
- PostgreSQL project metadata
- Redis + Celery background rendering
- FFmpeg silence detection and automated cutting
- Optional `faster-whisper` transcription/filler-word removal
- YouTube OAuth + upload endpoint
- Docker Compose for local development

## Project structure

```text
youtube-auto-editor/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── routers/
│   │   │   │   ├── projects.py
│   │   │   │   ├── jobs.py
│   │   │   │   └── youtube.py
│   │   │   ├── services/
│   │   │   │   ├── video.py
│   │   │   │   ├── transcription.py
│   │   │   │   └── youtube.py
│   │   │   ├── celery_app.py
│   │   │   ├── config.py
│   │   │   ├── db.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── worker/
│   │   ├── worker.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       ├── Dockerfile
│       └── package.json
├── data/
│   ├── uploads/
│   ├── renders/
│   └── tokens/
├── docker-compose.yml
└── .env.example
```

## Run locally

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open `http://localhost:3000`.
4. API docs are at `http://localhost:8000/docs`.

The first render performs silence detection and cuts detected silent regions. Transcript generation and filler-word removal are opt-in because local speech-to-text is expensive. The current starter stores the transcript but does not yet burn captions into the video.

### Enable local transcription

Set `ENABLE_TRANSCRIPTION=true` and install `faster-whisper` into the worker image (or create a separate AI image). The code already exposes word timestamps and filler-word cut generation.

A practical production setup is to move transcription into its own GPU worker rather than loading the model inside the render worker.

## YouTube setup

Create OAuth 2.0 web application credentials in Google Cloud, enable the YouTube Data API v3, and save the downloaded client secret JSON as:

`data/tokens/client_secret.json`

Make sure the authorized redirect URI exactly matches:

`http://localhost:8000/api/youtube/callback`

From the web UI, click **Connect YouTube**, approve the scope, and then use **Upload as private**. The starter intentionally uses private uploads. YouTube documents the `videos.insert` upload flow and OAuth requirement in its Data API documentation. See the links in the implementation notes below.

## Production hardening

Before deploying publicly, add authentication, per-user project ownership, signed download URLs, object storage, rate limits, malware/file validation, encrypted OAuth token storage, resumable uploads, persistent job records, and isolated render workers. Do not expose the local `/media` mount publicly in a production deployment.

## Next features

- Timeline editor with crop/trim/zoom markers
- Captions rendered with ASS/WebVTT
- AI-generated title/description/chapters
- Highlight/Shorts extraction
- Brand presets (fonts, colors, intro/outro)
- S3/R2 storage and direct-to-browser uploads
- Multi-user auth + billing
