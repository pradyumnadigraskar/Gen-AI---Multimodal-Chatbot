# # backend/services/video_tools.py


# from pathlib import Path
# import uuid
# import shutil
# import subprocess
# import tempfile

# import cv2
# import numpy as np
# from PIL import Image

# from ..services.ollama_client import ollama_generate
# from ..config import settings
# import subprocess, os, tempfile
# from faster_whisper import WhisperModel

# # --- Paths ---
# ROOT_DIR = Path(__file__).resolve().parents[2]
# MEDIA_DIR = ROOT_DIR / "media" / "video"
# MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# def _norm(p: str) -> str:
#     return p.replace("\\", "/")

# # -------- Frame sampling & analysis --------
# def sample_frames(video_path: str, stride: int = 30, max_frames: int = 8) -> list[str]:
#     cap = cv2.VideoCapture(video_path)
#     frames = []
#     i = 0
#     while True:
#         ok, frame = cap.read()
#         if not ok:
#             break
#         if i % stride == 0:
#             out = MEDIA_DIR / f"frame_{i:05d}.jpg"
#             cv2.imwrite(str(out), frame)
#             frames.append(_norm(str(out)))
#             if len(frames) >= max_frames:
#                 break
#         i += 1
#     cap.release()
#     return frames

# def analyze_video(video_path: str, question: str = "What is happening?") -> str:
#     frames = sample_frames(video_path)
#     if not frames:
#         return "I couldn't read any frames from the video."

#     answers = []
#     for p in frames:
#         img_uri = f"file://{Path(p).resolve()}"
#         ans = ollama_generate(question, model=settings.OLLAMA_VISION_MODEL, images=[img_uri])
#         answers.append(ans)
#     summary = ollama_generate("Summarize: \n" + "\n".join(answers), model=settings.OLLAMA_TEXT_MODEL)
#     return summary

# # -------- Video writing (browser-compatible) --------
# def _write_video_cv2(frame_paths: list[str], out_path: str, fps: int = 24, size: tuple[int, int] | None = None) -> str:
#     if not frame_paths:
#         frame_paths = []
#         for _ in range(3):
#             img = Image.new("RGB", (1280, 720), (255, 255, 255))
#             fp = MEDIA_DIR / f"placeholder_{uuid.uuid4().hex}.png"
#             img.save(fp)
#             frame_paths.append(_norm(str(fp)))

#     if size is None:
#         first = cv2.imread(frame_paths[0])
#         h, w = first.shape[:2]
#         size = (w, h)

#     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#     writer = cv2.VideoWriter(out_path, fourcc, fps, size)

#     for p in frame_paths:
#         frame = cv2.imread(p)
#         if frame is None:
#             continue
#         if (frame.shape[1], frame.shape[0]) != size:
#             frame = cv2.resize(frame, size, interpolation=cv2.INTER_LANCZOS4)
#         writer.write(frame)

#     writer.release()
#     return _norm(out_path)

# def _write_video_ffmpeg(frame_paths: list[str], out_path: str, fps: int = 24) -> str:
#     if not frame_paths:
#         frame_paths = []
#         for _ in range(3):
#             img = Image.new("RGB", (1280, 720), (255, 255, 255))
#             fp = MEDIA_DIR / f"placeholder_{uuid.uuid4().hex}.png"
#             img.save(fp)
#             frame_paths.append(str(fp))

#     with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lst:
#         for p in frame_paths:
#             lst.write(f"file '{Path(p).as_posix()}'\n")
#         list_path = lst.name

#     cmd = [
#         "ffmpeg", "-y",
#         "-r", str(fps),
#         "-f", "concat", "-safe", "0",
#         "-i", list_path,
#         "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
#         "-c:v", "libx264",
#         "-pix_fmt", "yuv420p",
#         "-movflags", "+faststart",
#         out_path,
#     ]
#     try:
#         subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     finally:
#         try:
#             Path(list_path).unlink(missing_ok=True)
#         except Exception:
#             pass

#     return _norm(out_path)

# def _write_video(frame_paths: list[str], out_path: str, fps: int = 24) -> str:
#     if shutil.which("ffmpeg"):
#         return _write_video_ffmpeg(frame_paths, out_path, fps=fps)
#     else:
#         return _write_video_cv2(frame_paths, out_path, fps=fps)

# def storyboard_to_video(frame_paths: list[str], out_name: str | None = None, fps: int = 24) -> str:
#     if out_name is None:
#         out_name = f"storyboard_{uuid.uuid4().hex}.mp4"
#     out_path = str(MEDIA_DIR / out_name)
#     return _write_video(frame_paths, out_path, fps=fps)

# # -------- Text-to-Video (ModelScope) --------
# from diffusers import DiffusionPipeline
# import torch

# # Load the model once at startup (GPU required!)
# text2video_pipe = DiffusionPipeline.from_pretrained(
#     "ali-vilab/text-to-video-ms-1.7b",
#     torch_dtype=torch.float16,
#     variant="fp16"
# ).to("cuda")



# def text_to_video(prompt: str, num_frames: int = 16, fps: int = 8) -> str:
#     """
#     Generate a short video from text using ali-vilab/text-to-video-ms-1.7b
#     Returns the absolute path to the MP4 file.
#     """
#     out_name = f"text2video_{uuid.uuid4().hex}.mp4"
#     out_path = str(MEDIA_DIR / out_name)

#     # Run inference
#     result = text2video_pipe(prompt, num_frames=num_frames)
#     video_frames = result.frames[0]  # list of numpy RGB frames

#     # Save frames temporarily
#     frame_paths = []
#     for frame in video_frames:
#     # Convert float32 [0,1] or [-1,1] to uint8 [0,255]
#         if frame.dtype != np.uint8:
#             frame = np.clip(frame * 255, 0, 255).astype(np.uint8)
#         fp = MEDIA_DIR / f"t2v_{uuid.uuid4().hex}.png"
#         Image.fromarray(frame).save(fp)
#         frame_paths.append(str(fp))


#     # Encode to MP4
#     final_path = _write_video(frame_paths, out_path, fps=fps)
#     return str(Path(final_path).resolve())

# def _ffmpeg_bin() -> str:
#     # Use FFMPEG_EXE from .env if set; else rely on PATH
#     exe = getattr(settings, "FFMPEG_EXE", None)
#     return exe if exe else "ffmpeg"

# _asr_model_caption = None
# def _get_asr_caption():
#     global _asr_model_caption
#     if _asr_model_caption is None:
#         _asr_model_caption = WhisperModel("small")
#     return _asr_model_caption

# def extract_audio_wav16k(video_path: str) -> str:
#     out_wav = Path(tempfile.gettempdir()) / f"cap_{Path(video_path).stem}_{uuid.uuid4().hex}.wav"
#     cmd = [
#         _ffmpeg_bin(), "-y",
#         "-i", video_path,
#         "-ac", "1",           # mono
#         "-ar", "16000",       # 16 kHz
#         "-vn",                # no video
#         str(out_wav)
#     ]
#     subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     return str(out_wav)

# def transcribe_audio_file(wav_path: str) -> str:
#     model = _get_asr_caption()
#     segments, _ = model.transcribe(wav_path)
#     return " ".join([s.text.strip() for s in segments])

# def caption_video(video_path: str, question: str = "Describe this frame briefly.") -> dict:
#     """
#     Returns:
#     {
#       "frame_captions": [ "..." ],
#       "transcript": "...",
#       "summary": "one or two sentences + bullets"
#     }
#     """
#     # 1) Sample visual frames
#     frames = sample_frames(video_path, stride=30, max_frames=6)

#     # 2) Caption frames with your vision model in Ollama
#     frame_caps = []
#     if frames:
#         from .vision_tools import _file_to_base64  # reuse your helper
#         for p in frames:
#             cap = ollama_generate(
#                 question,
#                 model=settings.OLLAMA_VISION_MODEL,
#                 images=[_file_to_base64(p)]
#             )
#             frame_caps.append(cap.strip())

#     # 3) Extract + transcribe audio (if ffmpeg available)
#     transcript = ""
#     try:
#         wav = extract_audio_wav16k(video_path)
#         try:
#             transcript = transcribe_audio_file(wav)
#         finally:
#             try:
#                 Path(wav).unlink(missing_ok=True)
#             except Exception:
#                 pass
#     except Exception:
#         # ffmpeg missing or audio-less video; it’s okay
#         transcript = ""

#     # 4) Fuse into a final summary
#     summary_prompt = f"""
# You will write a concise caption of the video and 3–5 helpful bullet points.

# Frame captions:
# {chr(10).join(f"- {c}" for c in frame_caps) if frame_caps else "(no frames were captioned)"}

# Transcript:
# {transcript if transcript.strip() else "(no speech detected)"}

# Write:
# 1) One-sentence overall caption
# 2) 3–5 concise bullets highlighting important actions/objects/scenes
# """
#     summary = ollama_generate(summary_prompt, model=settings.OLLAMA_TEXT_MODEL)

#     return {
#         "frame_captions": frame_caps,
#         "transcript": transcript,
#         "summary": summary.strip()
#     }


# backend/services/video_tools.py
from pathlib import Path
import uuid
import shutil
import subprocess
import tempfile
import base64

import cv2
import numpy as np
from PIL import Image

from ..services.ollama_client import ollama_generate
from ..config import settings
from .asr import transcribe_wav_bytes  # reuse your ASR

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parents[2]
MEDIA_DIR = ROOT_DIR / "media" / "video"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

def _norm(p: str) -> str:
    return p.replace("\\", "/")

def _file_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# -------- Frame sampling & analysis --------
def sample_frames(video_path: str, stride: int = 30, max_frames: int = 8) -> list[str]:
    cap = cv2.VideoCapture(video_path)
    frames = []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % stride == 0:
            out = MEDIA_DIR / f"frame_{i:05d}.jpg"
            cv2.imwrite(str(out), frame)
            frames.append(_norm(str(out)))
            if len(frames) >= max_frames:
                break
        i += 1
    cap.release()
    return frames

def analyze_video(video_path: str, question: str = "Describe what happens in this video.") -> str:
    """
    Captions a handful of frames and summarizes them using your Ollama vision+text models.
    IMPORTANT: send base64 images (not file paths) to Ollama.
    """
    frames = sample_frames(video_path)
    if not frames:
        return "I couldn't read any frames from the video."

    per_frame = []
    for p in frames:
        b64 = _file_to_base64(p)
        ans = ollama_generate(question, model=settings.OLLAMA_VISION_MODEL, images=[b64])
        per_frame.append(ans)

    summary_prompt = "Summarize the following frame-by-frame descriptions into a concise paragraph:\n\n" + "\n".join(per_frame)
    summary = ollama_generate(summary_prompt, model=settings.OLLAMA_TEXT_MODEL)
    return summary

# -------- Video writing (browser-compatible) --------
def _write_video_cv2(frame_paths: list[str], out_path: str, fps: int = 24, size: tuple[int, int] | None = None) -> str:
    if not frame_paths:
        frame_paths = []
        for _ in range(3):
            img = Image.new("RGB", (1280, 720), (255, 255, 255))
            fp = MEDIA_DIR / f"placeholder_{uuid.uuid4().hex}.png"
            img.save(fp)
            frame_paths.append(_norm(str(fp)))

    if size is None:
        first = cv2.imread(frame_paths[0])
        h, w = first.shape[:2]
        size = (w, h)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, size)

    for p in frame_paths:
        frame = cv2.imread(p)
        if frame is None:
            continue
        if (frame.shape[1], frame.shape[0]) != size:
            frame = cv2.resize(frame, size, interpolation=cv2.INTER_LANCZOS4)
        writer.write(frame)

    writer.release()
    return _norm(out_path)

def _write_video_ffmpeg(frame_paths: list[str], out_path: str, fps: int = 24) -> str:
    if not frame_paths:
        frame_paths = []
        for _ in range(3):
            img = Image.new("RGB", (1280, 720), (255, 255, 255))
            fp = MEDIA_DIR / f"placeholder_{uuid.uuid4().hex}.png"
            img.save(fp)
            frame_paths.append(str(fp))

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as lst:
        for p in frame_paths:
            lst.write(f"file '{Path(p).as_posix()}'\n")
        list_path = lst.name

    cmd = [
        "ffmpeg", "-y",
        "-r", str(fps),
        "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        out_path,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    finally:
        try:
            Path(list_path).unlink(missing_ok=True)
        except Exception:
            pass

    return _norm(out_path)

def _write_video(frame_paths: list[str], out_path: str, fps: int = 24) -> str:
    if shutil.which("ffmpeg"):
        return _write_video_ffmpeg(frame_paths, out_path, fps=fps)
    else:
        return _write_video_cv2(frame_paths, out_path, fps=fps)

def storyboard_to_video(frame_paths: list[str], out_name: str | None = None, fps: int = 24) -> str:
    if out_name is None:
        out_name = f"storyboard_{uuid.uuid4().hex}.mp4"
    out_path = str(MEDIA_DIR / out_name)
    return _write_video(frame_paths, out_path, fps=fps)

# -------- Text-to-Video (ModelScope) --------
from diffusers import DiffusionPipeline
import torch

# Load once (GPU required)
text2video_pipe = DiffusionPipeline.from_pretrained(
    "ali-vilab/text-to-video-ms-1.7b",
    torch_dtype=torch.float16,
    variant="fp16"
).to("cuda")

def text_to_video(prompt: str, num_frames: int = 16, fps: int = 8) -> str:
    out_name = f"text2video_{uuid.uuid4().hex}.mp4"
    out_path = str(MEDIA_DIR / out_name)
    result = text2video_pipe(prompt, num_frames=num_frames)
    video_frames = result.frames[0]  # list of numpy RGB frames

    frame_paths = []
    for frame in video_frames:
        if frame.dtype != np.uint8:
            frame = np.clip(frame * 255, 0, 255).astype(np.uint8)
        fp = MEDIA_DIR / f"t2v_{uuid.uuid4().hex}.png"
        Image.fromarray(frame).save(fp)
        frame_paths.append(str(fp))

    final_path = _write_video(frame_paths, out_path, fps=fps)
    return str(Path(final_path).resolve())

# -------- New: Video captioning (audio + visual) --------
def _extract_audio_to_wav(video_path: str) -> bytes | None:
    """
    Uses ffmpeg (if present) to extract mono 16k WAV from the video, returns bytes.
    If ffmpeg isn't installed, returns None so we can skip transcript.
    """
    if not shutil.which("ffmpeg"):
        return None
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-ac", "1",
            "-ar", "16000",
            wav_path,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(wav_path, "rb") as f:
            data = f.read()
        return data
    finally:
        try:
            Path(wav_path).unlink(missing_ok=True)
        except Exception:
            pass

def caption_video(video_path: str) -> dict:
    """
    Returns:
      {
        "summary": "<one-paragraph summary>",
        "transcript": "<best-effort transcript or message>"
      }
    """
    # 1) Visual: frame captions -> summary
    frames = sample_frames(video_path)
    visual_notes = []
    for p in frames:
        b64 = _file_to_base64(p)
        cap = ollama_generate("Describe this frame briefly.", model=settings.OLLAMA_VISION_MODEL, images=[b64])
        visual_notes.append(cap)
    visual_summary = ollama_generate(
        "Summarize these frame captions into a concise description of the video:\n\n" + "\n".join(visual_notes),
        model=settings.OLLAMA_TEXT_MODEL
    ) if visual_notes else "No visual frames could be processed."

    # 2) Audio: transcript (if ffmpeg available)
    wav_bytes = _extract_audio_to_wav(video_path)
    if wav_bytes:
        try:
            transcript = transcribe_wav_bytes(wav_bytes)
        except Exception:
            transcript = "(audio transcription failed)"
    else:
        transcript = "(audio transcription unavailable: ffmpeg not installed)"

    # 3) Final single-paragraph summary mixing both
    final_summary = ollama_generate(
        f"Produce a clear one-paragraph summary given this visual description and (optional) transcript.\n\n"
        f"Visual: {visual_summary}\n\nTranscript: {transcript}\n",
        model=settings.OLLAMA_TEXT_MODEL
    )

    return {"summary": final_summary, "transcript": transcript}
