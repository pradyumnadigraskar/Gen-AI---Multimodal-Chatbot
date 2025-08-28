# ASR via faster-whisper
from faster_whisper import WhisperModel
import tempfile, os

_model = None

def get_model():
    global _model
    if _model is None:
        _model = WhisperModel("small")  # choose size per your GPU/CPU
    return _model

def transcribe_wav_bytes(b: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(b)
        tmp_path = tmp.name
    model = get_model()
    segments, _ = model.transcribe(tmp_path)
    text = " ".join([s.text for s in segments])
    os.remove(tmp_path)
    return text
