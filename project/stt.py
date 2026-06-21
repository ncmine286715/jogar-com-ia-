# stt.py — gravação de microfone + transcrição local (faster-whisper)

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

import config

# Carrega o modelo uma única vez (custo alto de init)
_model = WhisperModel(
    config.WHISPER_MODEL,
    device=config.WHISPER_DEVICE,
    compute_type=config.WHISPER_COMPUTE,
)


def record_audio(seconds: float = None) -> np.ndarray:
    """Grava do microfone e retorna float32 mono em 16 kHz."""
    seconds = seconds or config.RECORD_SECONDS
    audio = sd.rec(
        int(seconds * config.SAMPLE_RATE),
        samplerate=config.SAMPLE_RATE,
        channels=config.CHANNELS,
        dtype="float32",
    )
    sd.wait()
    return audio.flatten()


def transcribe(audio: np.ndarray) -> str:
    """Transcreve áudio float32 para texto."""
    segments, _ = _model.transcribe(
        audio,
        language=config.WHISPER_LANGUAGE,
        beam_size=1,            # rápido (latência baixa)
        vad_filter=True,        # ignora silêncio
    )
    return " ".join(seg.text.strip() for seg in segments).strip()


def listen(seconds: float = None) -> str:
    """Grava + transcreve. Retorna texto vazio se falhar."""
    try:
        audio = record_audio(seconds)
        return transcribe(audio)
    except Exception as e:
        print(f"[STT] erro: {e}")
        return ""
