from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..deps import get_db, get_current_user_id
from .. import models

router = APIRouter()

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None

@router.get("/me")
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name or "",
        "phone": user.phone or ""
    }

@router.post("/update")
async def update_profile(
    req: Request,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    # accept JSON or form
    ctype = (req.headers.get("content-type") or "").lower()
    if ctype.startswith("application/json"):
        data = await req.json()
        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
    else:
        form = await req.form()
        name = (form.get("name") or "").strip()
        phone = (form.get("phone") or "").strip()

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = name or None
    user.phone = phone or None
    db.add(user); db.commit(); db.refresh(user)

    return {"ok": True, "name": user.name or "", "phone": user.phone or ""}

@router.get("/recent-chats")
def recent_chats(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    chats = (
        db.query(models.Chat)
        .filter(models.Chat.user_id == user_id)
        .order_by(models.Chat.created_at.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": c.id,
            "title": c.title,
            "modality": c.modality,
            "created_at": c.created_at.isoformat(),
        }
        for c in chats
    ]
