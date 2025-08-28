# from fastapi import FastAPI, Request
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from .config import settings
# from .database import init_db
# from fastapi.responses import RedirectResponse
# from .routers import users, chat, image, audio, video, history
# from starlette.middleware.sessions import SessionMiddleware
# from fastapi import FastAPI, Request, Depends, HTTPException

# app = FastAPI(title="Agentic Multimodal (Ollama)", debug=True)
# # 1️⃣ Add SessionMiddleware
# app.add_middleware(SessionMiddleware, secret_key="super-secret-key")
# app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")
# templates = Jinja2Templates(directory="frontend/templates")
# templates.env.auto_reload = True

# app.include_router(users.router, prefix="/api/auth", tags=["auth"])
# app.include_router(chat.router, prefix="/api/chat", tags=["chat"])  # text chat
# app.include_router(image.router, prefix="/api/image", tags=["image"])  # image proc/gen
# app.include_router(audio.router, prefix="/api/audio", tags=["audio"])  # asr/tts
# app.include_router(video.router, prefix="/api/video", tags=["video"])  # video proc/gen
# app.include_router(history.router, prefix="/api/history", tags=["history"])  # history

# @app.on_event("startup")
# async def startup():
#     init_db()

# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     return templates.TemplateResponse("dashboard.html", {"request": request})

# def login_required(request: Request):
#     user = request.session.get("user")
#     if not user:
#         # Return a redirect response instead of raising a non-exception
#         response = RedirectResponse(url="/login?msg=Please+login+first", status_code=303)
#         raise HTTPException(status_code=303, detail="Redirecting", headers={"Location": "/login?msg=Please+login+first"})
#     return user

# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.get("/logout")
# async def logout(request: Request):
#     # If you are using session cookies
#     request.session.clear()  # clear all session data
    
#     # Redirect to login page
#     return RedirectResponse(url="/login", status_code=303)

# @app.get("/signup", response_class=HTMLResponse)
# async def signup_page(request: Request):
#     return templates.TemplateResponse("signup.html", {"request": request})


# @app.get("/chat", response_class=HTMLResponse)
# async def chat_text_page(request: Request, user: str = Depends(login_required)):
#     if isinstance(user, RedirectResponse):  # if not logged in
#         return user
#     return templates.TemplateResponse("chat_text.html", {"request": request, "user": user})


# @app.get("/image", response_class=HTMLResponse)
# async def image_page(request: Request, user: str = Depends(login_required)):
#     if isinstance(user, RedirectResponse):
#         return user
#     return templates.TemplateResponse("image_tools.html", {"request": request, "user": user})


# @app.get("/audio", response_class=HTMLResponse)
# async def audio_page(request: Request, user: str = Depends(login_required)):
#     if isinstance(user, RedirectResponse):
#         return user
#     return templates.TemplateResponse("audio_tools.html", {"request": request, "user": user})


# @app.get("/video", response_class=HTMLResponse)
# async def video_page(request: Request, user: str = Depends(login_required)):
#     if isinstance(user, RedirectResponse):
#         return user
#     return templates.TemplateResponse("video_tools.html", {"request": request, "user": user})


# @app.get("/history", response_class=HTMLResponse)
# async def history_page(request: Request):
#     return templates.TemplateResponse("history.html", {"request": request})


# from fastapi import FastAPI, Request, Depends,HTTPException
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from jose import jwt, JWTError
# from .config import settings
# from .database import init_db
# from .routers import users, chat, image, audio, video, history
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from routers.users import router as users_router
# from starlette.middleware.base import BaseHTTPMiddleware
# from fastapi.responses import RedirectResponse

# app = FastAPI(title="Agentic Multimodal (Ollama)", debug=True)

# # Static & Templates
# app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
# app.mount("/media", StaticFiles(directory="media"), name="media")
# templates = Jinja2Templates(directory="frontend/templates")
# templates.env.auto_reload = True


# # JWT check middleware
# class AuthRedirectMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         if request.url.path not in ["/login", "/signup"]:  # allow auth routes
#             token = request.cookies.get("token")
#             if not token:
#                 return RedirectResponse("/login?msg=Please+login+first")
#         return await call_next(request)

# # CORS if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Add middleware
# app.add_middleware(AuthRedirectMiddleware)

# # Routers
# app.include_router(users.router, prefix="/api/auth", tags=["auth"])
# app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
# app.include_router(image.router, prefix="/api/image", tags=["image"])
# app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
# app.include_router(video.router, prefix="/api/video", tags=["video"])
# app.include_router(history.router, prefix="/api/history", tags=["history"])

# # Startup DB init
# @app.on_event("startup")
# async def startup():
#     init_db()

# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     return templates.TemplateResponse("dashboard.html", {"request": request})

# # 🔑 Decode JWT from cookie
# def get_current_user_id(request: Request):
#     token = request.cookies.get("token")
#     if not token:
#         # for API: raise error
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     try:
#         payload = jwt.decode(
#             token,
#             settings.JWT_SECRET,
#             algorithms=["HS256"],
#         )
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return user_id

#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")

#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# # 🔒 Protected Pages
# @app.get("/chat", response_class=HTMLResponse)
# async def chat_text_page(request: Request, user_id: int = Depends(get_current_user_id)):
#     return templates.TemplateResponse("chat_text.html", {"request": request, "user_id": user_id})

# @app.get("/image", response_class=HTMLResponse)
# async def image_page(request: Request, user_id: int = Depends(get_current_user_id)):
#     return templates.TemplateResponse("image_tools.html", {"request": request, "user_id": user_id})

# @app.get("/audio", response_class=HTMLResponse)
# async def audio_page(request: Request, user_id: int = Depends(get_current_user_id)):
#     return templates.TemplateResponse("audio_tools.html", {"request": request, "user_id": user_id})

# @app.get("/video", response_class=HTMLResponse)
# async def video_page(request: Request, user_id: int = Depends(get_current_user_id)):
#     return templates.TemplateResponse("video_tools.html", {"request": request, "user_id": user_id})

# # ℹ️ Public pages
# @app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# @app.get("/signup", response_class=HTMLResponse)
# async def signup_page(request: Request):
#     return templates.TemplateResponse("signup.html", {"request": request})

# @app.get("/history", response_class=HTMLResponse)
# async def history_page(request: Request):
#     return templates.TemplateResponse("history.html", {"request": request})

# backend/app.py
# 


#--
# app.py
from fastapi import FastAPI, Request, Depends, HTTPException , APIRouter 
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .config import settings
from .database import init_db
from .routers import users, chat, image, audio, video, history , profile

app = FastAPI(title="Agentic Multimodal (Ollama)", debug=True)

# Static & Templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])

templates = Jinja2Templates(directory="frontend/templates")
templates.env.auto_reload = True

# CORS (adjust origins if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT check middleware (for browser navigation → redirect to /login)
class AuthRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        public_paths = {
            "/login",
            "/signup",
            "/static",
            "/media",
            "/api/auth/login",
            "/api/auth/signup",
        }
        if any(path == p or path.startswith(p + "/") for p in public_paths):
            return await call_next(request)

        token = request.cookies.get("token")
        if not token:
            return RedirectResponse("/login?msg=Please+login+first",status_code=303)

        try:
            jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except Exception:
            return RedirectResponse("/login?msg=Invalid+or+expired+token")

        return await call_next(request)

app.add_middleware(AuthRedirectMiddleware)

# Routers
app.include_router(users.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(image.router, prefix="/api/image", tags=["image"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(video.router, prefix="/api/video", tags=["video"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

# Init DB on startup
@app.on_event("startup")
async def startup():
    init_db()

# ----------- Helpers -----------
def get_current_user_id(request: Request) -> int:
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return int(sub)  # <- important

# ----------- Pages -----------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# 🔒 Protected pages
#@app.get("/chat", response_class=HTMLResponse)
# async def chat_text_page(request: Request, user_id: int = Depends(get_current_user_id)):
#     return templates.TemplateResponse("chat_text.html", {"request": request, "user_id": user_id})pp
@app.get("/chat", response_class=HTMLResponse)
async def chat_text_page(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("chat_text.html", {"request": request, "user_id": user_id, "user": True})

@app.get("/image", response_class=HTMLResponse)
async def image_page(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("image_tools.html", {"request": request, "user_id": user_id})

@app.get("/audio", response_class=HTMLResponse)
async def audio_page(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("audio_tools.html", {"request": request, "user_id": user_id})

@app.get("/video", response_class=HTMLResponse)
async def video_page(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("video_tools.html", {"request": request, "user_id": user_id})

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("history.html", {"request": request, "user_id": user_id})

# ℹ️ Public pages
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_dashboard(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("profile_dashboard.html", {"request": request, "user_id": user_id})

@app.get("/profile/edit", response_class=HTMLResponse)
async def profile_update(request: Request, user_id: int = Depends(get_current_user_id)):
    return templates.TemplateResponse("profile_edit.html", {"request": request, "user_id": user_id})
