from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session
from .transcription import filler_cuts, transcribe
from ..config import get_settings
from ..db import SessionLocal
from ..models import Project


def run_cmd(args: list[str]) -> str:
    completed = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return completed.stdout

def ffprobe_duration(path: str) -> float:
    out = run_cmd([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ])
    return float(out.strip())

def detect_silence(path: str, threshold_db: int, min_duration: float) -> list[tuple[float, float]]:
    out = run_cmd([
        "ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=noise={threshold_db}dB:d={min_duration}",
        "-f", "null", "-"
    ])
    starts: list[float] = []
    cuts: list[tuple[float, float]] = []
    for line in out.splitlines():
        m_start = re.search(r"silence_start:\s*([0-9.]+)", line)
        if m_start:
            starts.append(float(m_start.group(1)))
        m_end = re.search(r"silence_end:\s*([0-9.]+)", line)
        if m_end and starts:
            start = starts.pop(0)
            end = float(m_end.group(1))
            if end > start:
                cuts.append((start, end))
    return cuts

def merge_intervals(intervals: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    ordered = sorted((float(a), float(b)) for a, b in intervals if b > a)
    if not ordered:
        return []
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + 0.02:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged

def invert_cuts(duration: float, cuts: list[tuple[float, float]], min_clip: float = 0.05) -> list[tuple[float, float]]:
    keep = []
    cursor = 0.0
    for start, end in cuts:
        start = max(0.0, min(duration, start))
        end = max(0.0, min(duration, end))
        if start > cursor and start - cursor >= min_clip:
            keep.append((cursor, start))
        cursor = max(cursor, end)
    if duration - cursor >= min_clip:
        keep.append((cursor, duration))
    return keep

def render_segments(source: str, keeps: list[tuple[float, float]], output: str) -> None:
    out_dir = Path(tempfile.mkdtemp(prefix="segments-", dir=str(Path(output).parent)))
    try:
        segments = []
        for i, (start, end) in enumerate(keeps):
            seg = out_dir / f"seg_{i:05d}.mp4"
            run_cmd([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", source,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(seg)
            ])
            segments.append(seg)
        concat_file = out_dir / "concat.txt"
        concat_file.write_text("".join(f"file '{seg.as_posix().replace("'", "'\\''")}'\n" for seg in segments))
        run_cmd([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
            "-i", str(concat_file), "-c", "copy", "-movflags", "+faststart", output
        ])
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)

def process_project(project_id: int, options: dict) -> dict:
    settings = get_settings()
    db: Session = SessionLocal()
    project = db.get(Project, project_id)
    if not project:
        db.close()
        raise ValueError("Project not found")
    try:
        project.status = "processing"
        db.commit()

        duration = ffprobe_duration(project.source_path)
        project.duration_seconds = duration

        cuts: list[tuple[float, float]] = []
        if options.get("remove_silence", True):
            cuts.extend(detect_silence(project.source_path, options.get("silence_threshold_db", -35), options.get("silence_min_duration", 0.45)))

        transcript_text = None
        project.captions_enabled = bool(options.get("generate_captions", False))
        if options.get("remove_filler_words", False) or options.get("generate_captions", False):
            if settings.enable_transcription:
                transcript_text, words = transcribe(project.source_path, settings.whisper_model)
                if options.get("remove_filler_words", False):
                    cuts.extend(filler_cuts(words))
            else:
                project.status = "transcription-disabled"
                db.commit()

        cuts = merge_intervals(cuts)
        keeps = invert_cuts(duration, cuts)

        render_dir = Path(settings.data_dir) / "renders"
        render_dir.mkdir(parents=True, exist_ok=True)
        output = render_dir / f"project_{project.id}.mp4"
        if cuts:
            render_segments(project.source_path, keeps, str(output))
        else:
            shutil.copy2(project.source_path, output)

        project.rendered_path = str(output)
        project.transcript = transcript_text
        project.status = "completed"
        db.commit()
        return {
            "project_id": project.id,
            "status": project.status,
            "rendered_path": project.rendered_path,
            "removed_seconds": round(sum(e - s for s, e in cuts), 3),
            "cuts": [{"start": s, "end": e} for s, e in cuts],
        }
    except Exception:
        project.status = "failed"
        db.commit()
        raise
    finally:
        db.close()
