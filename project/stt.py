# stt.py — gravação de microfone + transcrição local (faster-whisper)

import queue
import time

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

_FRAME_SAMPLES = int(config.SAMPLE_RATE * config.VAD_FRAME_MS / 1000)
_SILENCE_FRAMES_TO_STOP = max(1, int(config.VAD_SILENCE_MS / config.VAD_FRAME_MS))


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


def _rms(frame: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(frame, dtype=np.float64))))


def record_until_silence(idle_timeout: float = None) -> "np.ndarray | None":
    """Escuta continuamente e grava só quando detecta fala (VAD por energia).

    Se idle_timeout for passado e ninguém falar dentro desse tempo, retorna
    None (permite ao caller decidir comentar sozinho, ex: modo autônomo).
    """
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        q.put(indata.copy())

    buffer = []
    speaking = False
    silence_frames = 0
    speech_start = None
    wait_start = time.time()

    with sd.InputStream(
        samplerate=config.SAMPLE_RATE,
        channels=config.CHANNELS,
        dtype="float32",
        blocksize=_FRAME_SAMPLES,
        callback=callback,
    ):
        while True:
            frame = q.get().flatten()
            level = _rms(frame)

            if level > config.VAD_THRESHOLD:
                if not speaking:
                    speaking = True
                    speech_start = time.time()
                silence_frames = 0
                buffer.append(frame)
            elif speaking:
                buffer.append(frame)
                silence_frames += 1
                if silence_frames >= _SILENCE_FRAMES_TO_STOP:
                    break

            if speaking and (time.time() - speech_start) > config.VAD_MAX_SECONDS:
                break
            if (
                not speaking
                and idle_timeout is not None
                and (time.time() - wait_start) > idle_timeout
            ):
                return None

    return np.concatenate(buffer) if buffer else np.array([], dtype="float32")


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
    """Grava por tempo fixo + transcreve (modo push). Vazio se falhar."""
    try:
        audio = record_audio(seconds)
        return transcribe(audio)
    except Exception as e:
        print(f"[STT] erro: {e}")
        return ""


def listen_vad(idle_timeout: float = None) -> "str | None":
    """Escuta contínua por voz (sem ENTER) + transcreve.

    Retorna None se idle_timeout expirar sem ninguém falar, "" se falhar
    a transcrição, ou o texto reconhecido.
    """
    try:
        audio = record_until_silence(idle_timeout)
        if audio is None:
            return None
        if audio.size == 0:
            return ""
        return transcribe(audio)
    except Exception as e:
        print(f"[STT] erro: {e}")
        return ""
