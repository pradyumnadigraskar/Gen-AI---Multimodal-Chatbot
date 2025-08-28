# backend/services/image_gen.py
import base64, io, os
from pathlib import Path
import requests
from PIL import Image
import uuid
import os

from ..config import settings

# Optional diffusers imports (only used when fallback is needed or preferred)
try:
    import torch
    from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline
except Exception:  # keep app alive even if diffusers isn't installed
    torch = None
    StableDiffusionPipeline = None
    StableDiffusionXLPipeline = None

MEDIA_DIR = Path("media/images")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def save_image_bytes(data: bytes, filename: str) -> str:
    path = MEDIA_DIR / filename
    with open(path, "wb") as f:
        f.write(data)
    return str(path)

# ---------------------------
# Automatic1111 txt2img (if running)
# ---------------------------
def a1111_txt2img(prompt: str, steps: int = 25, width: int = 768, height: int = 768) -> bytes:
    if not getattr(settings, "A1111_URL", None):
        raise RuntimeError("A1111_URL not set")
    url = f"{settings.A1111_URL}/sdapi/v1/txt2img"
    payload = {"prompt": prompt, "steps": steps, "width": width, "height": height}
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()
    b64 = data["images"][0]
    return base64.b64decode(b64)

# ---------------------------
# Diffusers txt2img (local, no web UI required)
# ---------------------------
_DIFFUSERS_PIPE = None

def _get_diffusers_pipe():
    global _DIFFUSERS_PIPE
    if _DIFFUSERS_PIPE is not None:
        return _DIFFUSERS_PIPE

    if torch is None or (StableDiffusionPipeline is None and StableDiffusionXLPipeline is None):
        raise RuntimeError("diffusers/torch not available")

    model_id = os.getenv("DIFFUSERS_MODEL_ID", "stabilityai/stable-diffusion-2-1").strip()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    if "stable-diffusion-xl" in model_id or "sdxl" in model_id:
        pipe = StableDiffusionXLPipeline.from_pretrained(model_id, torch_dtype=dtype)
    else:
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)

    # Optional: disable safety checker if you set DIFFUSERS_DISABLE_SAFETY=1
    if os.getenv("DIFFUSERS_DISABLE_SAFETY", "0") in ("1","true","yes","on"):
        try:
            pipe.safety_checker = None
        except Exception:
            pass

    pipe = pipe.to(device)
    try:
        pipe.enable_attention_slicing()
    except Exception:
        pass
    _DIFFUSERS_PIPE = pipe
    return _DIFFUSERS_PIPE

def diffusers_txt2img(
    prompt: str,
    steps: int = 30,
    width: int = 768,
    height: int = 768,
    guidance_scale: float = 7.5,
    seed: int | None = None,
) -> bytes:
    pipe = _get_diffusers_pipe()
    generator = None
    if seed is not None and torch is not None:
        generator = torch.Generator(device=pipe.device).manual_seed(seed)

    # Some pipelines ignore width/height (SDXL needs valid multiples of 8)
    result = pipe(
        prompt,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
        generator=generator,
    )
    img = result.images[0]
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ---------------------------
# Fallback image if everything fails
# ---------------------------
def fallback_blank_png() -> bytes:
    img = Image.new("RGB", (1024, 768), (240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ---------------------------
# Unified entry point your router can call
# ---------------------------
def generate_image_from_text(prompt: str, filename: str | None = None) -> str:
    """Create a unique file and return its path."""
    data = None

    # Try A1111 first if configured
    try:
        if getattr(settings, "A1111_URL", None):
            data = a1111_txt2img(prompt)
    except Exception:
        data = None

    # Diffusers fallback / primary
    if data is None:
        try:
            data = diffusers_txt2img(prompt)
        except Exception:
            data = None

    if data is None:
        data = fallback_blank_png()

    if not filename:
        filename = f"{uuid.uuid4().hex}.png"
    return save_image_bytes(data, filename)