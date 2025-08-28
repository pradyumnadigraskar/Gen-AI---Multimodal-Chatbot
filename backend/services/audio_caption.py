# backend/services/audio_caption.py
from pathlib import Path
import tempfile
from faster_whisper import WhisperModel
from .ollama_client import ollama_generate
from ..config import settings

_asr_model = None

def _get_asr():
    global _asr_model
    if _asr_model is None:
        # pick your size: tiny, base, small, medium, large-v3
        _asr_model = WhisperModel("small")
    return _asr_model

def transcribe_bytes_to_text(wav_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(wav_bytes)
        wav_path = tmp.name
    model = _get_asr()
    segments, _ = model.transcribe(wav_path)
    return " ".join(s.text.strip() for s in segments)

def summarize_transcript(transcript: str) -> str:
    if not transcript.strip():
        return "No speech detected."
    prompt = f"""You are an expert at writing concise captions.
Transcript:
{transcript}

Write one short caption (max 18 words) that sounds natural and informative."""
    return ollama_generate(prompt, model=settings.OLLAMA_TEXT_MODEL)

def audio_caption_from_bytes(wav_bytes: bytes) -> dict:
    """
    Returns: { "transcript": str, "caption": str }
    """
    transcript = transcribe_bytes_to_text(wav_bytes)
    caption = summarize_transcript(transcript)
    return {"transcript": transcript, "caption": caption}
