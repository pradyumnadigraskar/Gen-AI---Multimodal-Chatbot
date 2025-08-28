# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from ..deps import get_db, get_current_user_id
# from .. import models

# router = APIRouter()

# @router.get("/")
# def list_chats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
#     chats = db.query(models.Chat).filter(models.Chat.user_id == user_id).order_by(models.Chat.created_at.desc()).all()
#     return [{"id": c.id, "title": c.title, "modality": c.modality, "created_at": c.created_at.isoformat()} for c in chats]

# @router.get("/{chat_id}")
# def get_chat(chat_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
#     chat = db.query(models.Chat).filter(models.Chat.id == chat_id, models.Chat.user_id == user_id).first()
#     if not chat:
#         return {"messages": []}
#     return {
#         "id": chat.id,
#         "title": chat.title,
#         "modality": chat.modality,
#         "messages": [{
#             "id": m.id, "role": m.role, "content": m.content, "media_type": m.media_type, "media_path": m.media_path,
#             "created_at": m.created_at.isoformat()
#         } for m in chat.messages]
#     }



from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user_id
from .. import models

router = APIRouter()

@router.get("/")
def list_chats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    chats = db.query(models.Chat).filter(models.Chat.user_id == user_id).order_by(models.Chat.created_at.desc()).all()
    return [{"id": c.id, "title": c.title, "modality": c.modality, "created_at": c.created_at.isoformat()} for c in chats]

@router.get("/{chat_id}")
def get_chat(chat_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id, models.Chat.user_id == user_id).first()
    if not chat:
        return {"messages": []}
    return {
        "id": chat.id,
        "title": chat.title,
        "modality": chat.modality,
        "messages": [{
            "id": m.id, "role": m.role, "content": m.content, "media_type": m.media_type, "media_path": m.media_path,
            "created_at": m.created_at.isoformat()
        } for m in chat.messages]
    }
