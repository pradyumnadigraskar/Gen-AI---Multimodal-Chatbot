# from fastapi import APIRouter, UploadFile, File, Depends, Form
# from sqlalchemy.orm import Session
# from ..deps import get_db, get_current_user_id
# from .. import models
# from ..services.video_tools import analyze_video, text_to_video

# router = APIRouter()

# @router.post("/query")
# async def video_query(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
#     data = await file.read()
#     # Save temp file
#     import tempfile
#     with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
#         tmp.write(data)
#         vpath = tmp.name
#     analysis = analyze_video(vpath)
#     chat = models.Chat(user_id=user_id, title="Video query", modality="video")
#     db.add(chat); db.commit(); db.refresh(chat)
#     db.add(models.Message(chat_id=chat.id, role="user", content="[video uploaded]", media_type="video"))
#     db.add(models.Message(chat_id=chat.id, role="assistant", content=analysis))
#     db.commit()
#     return {"chat_id": chat.id, "analysis": analysis}

# # backend/routers/video.py
# @router.post("/generate")
# async def video_generate(prompt: str = Form(...), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
#     out_path = text_to_video(prompt)
#     public_path = out_path.replace("\\", "/")

#     chat = models.Chat(user_id=user_id, title="Text2Video", modality="video")
#     db.add(chat); db.commit(); db.refresh(chat)
#     db.add(models.Message(chat_id=chat.id, role="user", content=prompt))
#     db.add(models.Message(chat_id=chat.id, role="assistant", content="[video generated]", media_type="video", media_path=public_path))
#     db.commit()
#     return {"chat_id": chat.id, "video_path": public_path}


# from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException 
# from sqlalchemy.orm import Session
# from pathlib import Path
# import tempfile, os

# from ..deps import get_db, get_current_user_id
# from .. import models
# from ..services.video_tools import analyze_video, text_to_video
# from ..services.video_tools import caption_video
# router = APIRouter()

# @router.post("/query")
# async def video_query(
#     file: UploadFile = File(...),
#     user_id: int = Depends(get_current_user_id),
#     db: Session = Depends(get_db)
# ):
#     if file.content_type and not file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Please upload a video file.")

#     data = await file.read()

#     # Save temp file for OpenCV to read
#     with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
#         tmp.write(data)
#         vpath = tmp.name

#     try:
#         analysis = analyze_video(vpath)
#     finally:
#         # Clean up temp file
#         try:
#             os.unlink(vpath)
#         except Exception:
#             pass

#     chat = models.Chat(user_id=user_id, title="Video query", modality="video")
#     db.add(chat); db.commit(); db.refresh(chat)
#     db.add(models.Message(chat_id=chat.id, role="user", content="[video uploaded]", media_type="video"))
#     db.add(models.Message(chat_id=chat.id, role="assistant", content=analysis))
#     db.commit()

#     return {"chat_id": chat.id, "analysis": analysis}


# @router.post("/generate")
# async def video_generate(
#     prompt: str = Form(...),
#     user_id: int = Depends(get_current_user_id),
#     db: Session = Depends(get_db)
# ):
#     # Create the video file and return a browser-safe URL under /media
#     out_abs_path = Path(text_to_video(prompt))  # absolute path
#     fname = out_abs_path.name
#     public_url = f"/media/video/{fname}"

#     chat = models.Chat(user_id=user_id, title="Text2Video", modality="video")
#     db.add(chat); db.commit(); db.refresh(chat)
#     db.add(models.Message(chat_id=chat.id, role="user", content=prompt))
#     db.add(models.Message(
#         chat_id=chat.id,
#         role="assistant",
#         content="[video generated]",
#         media_type="video",
#         media_path=public_url
#     ))
#     db.commit()

#     return {"chat_id": chat.id, "video_url": public_url}

# @router.post("/caption")
# async def video_caption(
#     file: UploadFile = File(...),
#     user_id: int = Depends(get_current_user_id),
#     db: Session = Depends(get_db)
# ):
#     if file.content_type and not file.content_type.startswith("video/"):
#         raise HTTPException(status_code=400, detail="Please upload a video file.")

#     data = await file.read()
#     # Save temp mp4
#     import tempfile, os
#     with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
#         tmp.write(data)
#         vpath = tmp.name

#     try:
#         result = caption_video(vpath)
#     finally:
#         try:
#             os.unlink(vpath)
#         except Exception:
#             pass

#     # store a quick chat record (optional but consistent)
#     chat = models.Chat(user_id=user_id, title="Video caption", modality="video")
#     db.add(chat); db.commit(); db.refresh(chat)
#     db.add(models.Message(chat_id=chat.id, role="user", content="[video uploaded]", media_type="video"))
#     db.add(models.Message(chat_id=chat.id, role="assistant",
#                           content=f"Summary:\n{result['summary']}\n\nTranscript:\n{result['transcript']}"))
#     db.commit()

#     # backend/routers/video.py (end of video_generate)
#     return {
#         "chat_id": chat.id }


# backend/routers/video.py
from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import tempfile, os

from ..deps import get_db, get_current_user_id
from .. import models
from ..services.video_tools import analyze_video, text_to_video, caption_video

router = APIRouter()

@router.post("/query")
async def video_query(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Please upload a video file.")

    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(data)
        vpath = tmp.name

    try:
        analysis = analyze_video(vpath)
    finally:
        try:
            os.unlink(vpath)
        except Exception:
            pass

    chat = models.Chat(user_id=user_id, title="Video query", modality="video")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content="[video uploaded]", media_type="video"))
    db.add(models.Message(chat_id=chat.id, role="assistant", content=analysis))
    db.commit()

    return {"chat_id": chat.id, "analysis": analysis}

@router.post("/generate")
async def video_generate(
    prompt: str = Form(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    out_abs_path = Path(text_to_video(prompt))  # absolute path
    fname = out_abs_path.name
    public_url = f"/media/video/{fname}"

    chat = models.Chat(user_id=user_id, title="Text2Video", modality="video")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content=prompt))
    db.add(models.Message(
        chat_id=chat.id,
        role="assistant",
        content="[video generated]",
        media_type="video",
        media_path=public_url
    ))
    db.commit()

    return {
        "chat_id": chat.id,
        "video_url": public_url,   # new key
        "video_path": public_url   # legacy key for old frontend
    }

@router.post("/caption")
async def video_caption(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Please upload a video file.")

    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(data)
        vpath = tmp.name

    try:
        result = caption_video(vpath)   # {"summary":..., "transcript":...}
    finally:
        try:
            os.unlink(vpath)
        except Exception:
            pass

    chat = models.Chat(user_id=user_id, title="Video caption", modality="video")
    db.add(chat); db.commit(); db.refresh(chat)
    db.add(models.Message(chat_id=chat.id, role="user", content="[video uploaded]", media_type="video"))
    db.add(models.Message(
        chat_id=chat.id,
        role="assistant",
        content=f"Summary:\n{result['summary']}\n\nTranscript:\n{result['transcript']}"
    ))
    db.commit()

    return {
        "chat_id": chat.id,
        "summary": result["summary"],
        "transcript": result["transcript"]
    }
