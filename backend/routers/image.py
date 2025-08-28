# backend/routers/image.py
from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user_id
from .. import models

# ✅ use image_gen for generation
from ..services.image_gen import generate_image_from_text, save_image_bytes

# keep vision captioning if you use LLaVA for /query
from ..services.vision_tools import save_image as save_uploaded_image, caption_image

router = APIRouter()

@router.post("/query")
async def image_query(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    data = await file.read()
    path = save_uploaded_image(data, file.filename)  # saves uploaded image
    caption = caption_image(path)                    # LLaVA/Qwen-VL caption
    chat = models.Chat(user_id=user_id, title=f"Image: {file.filename}", modality="image")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content="[uploaded image]", media_type="image", media_path=path))
    db.add(models.Message(chat_id=chat.id, role="assistant", content=caption))
    db.commit()
    return {"chat_id": chat.id, "caption": caption}

@router.post("/generate")
async def image_generate(
    prompt: str = Form(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # ✅ this returns a unique file path inside media/images (uuid.png)
    path = generate_image_from_text(prompt)

    chat = models.Chat(user_id=user_id, title=f"Image gen: {prompt[:40]}", modality="image")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content=prompt))
    db.add(models.Message(chat_id=chat.id, role="assistant", content="[image generated]", media_type="image", media_path=path))
    db.commit()

    return {"chat_id": chat.id, "image_path": path}
