from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user_id
from .. import models
from ..services.asr import transcribe_wav_bytes
from ..services.tts import tts_to_wav_path
from ..services.audio_caption import audio_caption_from_bytes
from fastapi import HTTPException

router = APIRouter()

@router.post("/query")
async def audio_query(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    data = await file.read()
    text = transcribe_wav_bytes(data)
    chat = models.Chat(user_id=user_id, title="Audio query", modality="audio")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content="[audio uploaded]", media_type="audio"))
    db.add(models.Message(chat_id=chat.id, role="assistant", content=text))
    db.commit()
    return {"chat_id": chat.id, "transcript": text}


@router.post("/generate")
async def audio_generate(text: str = Form(...), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    path = tts_to_wav_path(text)                  # e.g. 'media/audio/tts_...wav'
    public_path = path.replace("\\", "/")         # normalize just in case

    chat = models.Chat(user_id=user_id, title="TTS", modality="audio")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content=text))
    db.add(models.Message(chat_id=chat.id, role="assistant", content="[tts generated]", media_type="audio", media_path=public_path))
    db.commit()
    return {"chat_id": chat.id, "audio_path": public_path}


@router.post("/caption")
async def audio_caption(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Basic content-type guard (optional)
    if file.content_type and not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Please upload an audio file (.wav recommended).")

    data = await file.read()
    result = audio_caption_from_bytes(data)

    # store a small chat record (optional but consistent with your flow)
    chat = models.Chat(user_id=user_id, title="Audio caption", modality="audio")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content="[audio uploaded]", media_type="audio"))
    db.add(models.Message(chat_id=chat.id, role="assistant",
                          content=f"Caption: {result['caption']}\n\nTranscript: {result['transcript']}"))
    db.commit()

    return {"chat_id": chat.id, **result}