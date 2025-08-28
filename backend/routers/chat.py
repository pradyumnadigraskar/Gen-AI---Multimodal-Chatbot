# backend/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..deps import get_db, get_current_user_id
from .. import models
from ..services.embeddings import embed_texts
from ..services.vectorstore import ensure_collection, upsert, search
from ..services.ollama_client import ollama_generate
from ..services.utils import make_id
from ..config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    chat_id: Optional[int] = None
    message: str

class ChatCreate(BaseModel):
    title: Optional[str] = None

def _process_message(req: ChatRequest, user_id: int, db: Session):
    # ensure (or create) chat
    if req.chat_id:
        chat = (
            db.query(models.Chat)
            .filter(models.Chat.id == req.chat_id, models.Chat.user_id == user_id)
            .first()
        )
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
    else:
        title = (req.message or "New Chat")[:40]
        chat = models.Chat(user_id=user_id, title=title, modality="text")
        db.add(chat); db.commit(); db.refresh(chat)

    # save user message
    if req.message:
        um = models.Message(chat_id=chat.id, role="user", content=req.message)
        db.add(um); db.commit(); db.refresh(um)

        # embeddings + vector store
        vec = embed_texts([req.message])[0]
        ensure_collection(dim=len(vec))
        upsert([(make_id(), vec, {"user_id": user_id, "chat_id": chat.id, "role": "user"})])
        hits = search(vec, top_k=3)
        context = [h.payload for h in hits]
    else:
        context = []

    # LLM via Ollama
    prompt = (
        f"You are a helpful assistant. Useful context (optional): {context}\n"
        f"User: {req.message}"
    )
    answer = ollama_generate(prompt, model=settings.OLLAMA_TEXT_MODEL)

    # save assistant message
    am = models.Message(chat_id=chat.id, role="assistant", content=answer)
    db.add(am); db.commit(); db.refresh(am)

    return {"chat_id": chat.id, "reply": answer}

# NEW: create empty chat so the frontend can start one before sending messages
@router.post("/new")
def create_chat(
    req: ChatCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    title = (req.title or "New Chat")[:40]
    chat = models.Chat(user_id=user_id, title=title, modality="text")
    db.add(chat); db.commit(); db.refresh(chat)
    return {"id": chat.id, "title": chat.title, "modality": chat.modality}

# Send (used by your current chat page)
@router.post("/send")
def send_message(
    req: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return _process_message(req, user_id, db)

# Root POST (keeps previous frontend that posts to /api/chat working)
@router.post("/")
def chat_text(
    req: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return _process_message(req, user_id, db)

# List chats
@router.get("/list")
def list_chats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    chats = (
        db.query(models.Chat)
        .filter(models.Chat.user_id == user_id)
        .order_by(models.Chat.created_at.desc())
        .all()
    )
    return [
        {"id": c.id, "title": c.title, "modality": c.modality, "created_at": c.created_at.isoformat()}
        for c in chats
    ]

# Get chat by id
@router.get("/{chat_id}")
def get_chat(chat_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    chat = (
        db.query(models.Chat)
        .filter(models.Chat.id == chat_id, models.Chat.user_id == user_id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {
        "id": chat.id,
        "title": chat.title,
        "modality": chat.modality,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "media_type": m.media_type,
                "media_path": m.media_path,
                "created_at": m.created_at.isoformat(),
            }
            for m in chat.messages
        ],
    }
