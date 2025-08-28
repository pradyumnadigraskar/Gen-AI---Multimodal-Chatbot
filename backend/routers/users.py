# backend/routers/users.py
from fastapi import APIRouter, Depends, Form, Response, HTTPException, Request
from sqlalchemy.orm import Session
from .. import models
from ..deps import get_db
from jose import jwt
from passlib.hash import bcrypt
from ..config import settings
from datetime import datetime, timedelta

router = APIRouter()

def create_jwt(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def _read_email_password(request: Request):
    ctype = (request.headers.get("content-type") or "").lower()
    if ctype.startswith("application/json"):
        data = await request.json()
        return (data.get("email"), data.get("password"))
    # default: treat as form post
    form = await request.form()
    return (form.get("email"), form.get("password"))

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email, password = await _read_email_password(request)
    if not email or not password:
        raise HTTPException(status_code=422, detail="email and password are required")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_jwt(user.id)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # set True behind HTTPS
        max_age=7 * 24 * 3600,
    )
    return {"ok": True}

@router.post("/signup")
async def signup(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email, password = await _read_email_password(request)
    if not email or not password:
        raise HTTPException(status_code=422, detail="email and password are required")

    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(email=email, password_hash=bcrypt.hash(password))
    db.add(user); db.commit(); db.refresh(user)

    token = create_jwt(user.id)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7 * 24 * 3600,
    )
    return {"ok": True}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"ok": True}
