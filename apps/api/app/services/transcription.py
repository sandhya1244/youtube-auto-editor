from __future__ import annotations

from dataclasses import dataclass

FILLER_WORDS = {
    "um", "uh", "like", "you know", "basically", "actually", "literally"
}

@dataclass
class Word:
    text: str
    start: float
    end: float

def transcribe(audio_path: str, model_name: str) -> tuple[str, list[Word]]:
    """Optional local transcription. Install faster-whisper to enable it."""
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("faster-whisper is not installed. Add it to the AI requirements and rebuild.") from exc

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, word_timestamps=True, vad_filter=True)
    words: list[Word] = []
    text_parts: list[str] = []
    for segment in segments:
        text_parts.append(segment.text.strip())
        for w in segment.words or []:
            if w.start is not None and w.end is not None:
                words.append(Word(w.word.strip(), float(w.start), float(w.end)))
    return " ".join(text_parts).strip(), words

def filler_cuts(words: list[Word], pad: float = 0.04) -> list[tuple[float, float]]:
    cuts = []
    for word in words:
        normalized = word.text.lower().strip(".,!?;:\"'()[]{}")
        if normalized in FILLER_WORDS:
            cuts.append((max(0, word.start - pad), word.end + pad))
    return cuts
