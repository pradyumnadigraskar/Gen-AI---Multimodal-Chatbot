# backend/services/ollama_client.py
import os
import requests
from ..config import settings

OLLAMA_URL = (settings.OLLAMA_HOST or "http://localhost:11434").rstrip("/")

def ollama_generate(prompt: str, model: str | None = None, images: list[str] | None = None, stream: bool = False) -> str:
    """
    images: list of base64-encoded image strings (NOT file paths)
    """
    payload = {
        "model": model or settings.OLLAMA_TEXT_MODEL,
        "prompt": prompt,
        "stream": stream,
    }
    if images:
        payload["images"] = images  # base64 strings per Ollama spec

    r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=180)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        # bubble up a readable error message from Ollama
        raise RuntimeError(f"Ollama /api/generate {r.status_code}: {r.text}") from e

    data = r.json()
    # non-streaming returns one JSON with "response"
    return (data.get("response") or "").strip()
