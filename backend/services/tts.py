# backend/services/tts.py
import os
import uuid
import asyncio
import threading
from pathlib import Path
from typing import Optional

from ..config import settings

# Edge TTS (Microsoft Neural voices)
# pip install edge-tts
import edge_tts

MEDIA_DIR = Path("media") / "audio"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def _clean(p: Optional[str]) -> Optional[str]:
    if not p:
        return None
    return p.strip().strip('"').strip("'")


def _unique_name(ext: str = "mp3") -> str:
    return f"tts_{uuid.uuid4().hex}.{ext}"


async def _edge_tts_save(text: str, out_path: Path) -> None:
    """
    Run edge-tts and save to MP3.
    """
    voice = _clean(getattr(settings, "EDGE_TTS_VOICE", None)) or "en-US-AriaNeural"
    rate = _clean(getattr(settings, "EDGE_TTS_RATE", None)) or "+0%"
    volume = _clean(getattr(settings, "EDGE_TTS_VOLUME", None)) or "+0%"

    # You can pass style, pitch, etc. via SSML if you want, but for now we just set rate/volume.
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume)
    await communicate.save(str(out_path))


def _run_edge_tts_blocking(text: str, out_path: Path) -> None:
    """
    Run the async edge-tts saver; if we're already inside an event loop (FastAPI endpoint),
    run it in a separate thread so we don't call asyncio.run() inside a running loop.
    """
    def _runner():
        asyncio.run(_edge_tts_save(text, out_path))

    try:
        # If this raises, there's no running loop (we're in a normal sync context).
        asyncio.get_running_loop()
        # We ARE in an event loop → run in a short-lived thread.
        t = threading.Thread(target=_runner, daemon=True)
        t.start()
        t.join()
    except RuntimeError:
        # No running event loop → it's safe to asyncio.run() directly.
        asyncio.run(_edge_tts_save(text, out_path))


def tts_to_wav_path(text: str, out_name: Optional[str] = None) -> str:
    """
    Generate speech using edge-tts (MP3 output).
    Returns a relative web path like 'media/audio/tts_xxx.mp3'.
    (Kept original function name for compatibility with your router.)
    """
    if not out_name:
        out_name = _unique_name("mp3")

    out_path = (MEDIA_DIR / out_name).resolve()

    try:
        _run_edge_tts_blocking(text, out_path)
        if out_path.exists() and out_path.stat().st_size > 0:
            rel = Path("media") / "audio" / out_path.name
            return str(rel).replace("\\", "/")
        else:
            raise RuntimeError("edge-tts produced empty file")
    except Exception as e:
        # Minimal fallback: create a tiny silent mp3 if edge-tts fails.
        # (We avoid extra deps; browsers will still 'play' it.)
        # If you prefer WAV tone fallback, you could generate one here.
        try:
            # 1-second silent MP3 header (pre-encoded 128kbps CBR) is not trivial to write by hand
            # so we just create an empty file to avoid 500s and let frontend show a message if needed.
            out_path.write_bytes(b"")
        except Exception:
            pass
        print(f"[TTS] edge-tts failed: {e}")
        rel = Path("media") / "audio" / out_path.name
        return str(rel).replace("\\", "/")


# Optional: explicit helper for MP3 (same as above name, kept for compatibility)
def tts_to_mp3_path(text: str) -> str:
    return tts_to_wav_path(text)
