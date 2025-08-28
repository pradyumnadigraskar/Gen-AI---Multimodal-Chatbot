# backend/services/vision_tools.py
import base64
from pathlib import Path
from ..services.ollama_client import ollama_generate
from ..config import settings

MEDIA_DIR = Path("media/images")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def save_image(file_bytes: bytes, filename: str) -> str:
    path = MEDIA_DIR / filename
    with open(path, "wb") as f:
        f.write(file_bytes)
    return str(path)

def _file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def caption_image(path: str, prompt: str = "Describe this image.") -> str:
    b64 = _file_to_base64(path)
    return ollama_generate(prompt, model=settings.OLLAMA_VISION_MODEL, images=[b64], stream=False)

def vqa(path: str, question: str) -> str:
    b64 = _file_to_base64(path)
    prompt = f"Answer the question about the image.\nQuestion: {question}"
    return ollama_generate(prompt, model=settings.OLLAMA_VISION_MODEL, images=[b64], stream=False)
