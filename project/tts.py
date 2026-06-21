# tts.py — síntese de voz (edge-tts) + reprodução (sounddevice + scipy)
# Durante a fala, dirige state.mouth_level pela amplitude (lip-sync do avatar).

import asyncio
import os
import subprocess
import tempfile
import time

import edge_tts
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

import config
import state


async def _synthesize(text: str) -> bytes:
    """Gera MP3 com edge-tts e retorna os bytes."""
    communicate = edge_tts.Communicate(
        text, voice=config.TTS_VOICE, rate=config.TTS_RATE
    )
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


def _mp3_to_wav_file(mp3: bytes) -> str:
    """Converte MP3 -> WAV PCM via ffmpeg, escrevendo num arquivo (seekable)
    para o header sair correto. Retorna o caminho do WAV temporário."""
    wav_path = tempfile.mktemp(suffix=".wav")
    subprocess.run(
        ["ffmpeg", "-y", "-i", "pipe:0", "-f", "wav", wav_path],
        input=mp3,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    return wav_path


def _envelope(data, rate):
    """Envelope de volume (RMS por frame) normalizado 0..1 para o lip-sync."""
    mono = data.astype(np.float32)
    if mono.ndim > 1:
        mono = mono.mean(axis=1)
    peak = np.max(np.abs(mono)) or 1.0
    mono /= peak
    step = max(1, int(rate / config.AVATAR_FPS))
    env = [
        float(np.sqrt(np.mean(np.square(mono[i:i + step]))))
        for i in range(0, len(mono), step)
    ]
    m = max(env) if env else 1.0
    return [min(1.0, v / m * 1.4) for v in env]  # realça aberturas


def speak(text: str) -> None:
    """Sintetiza, reproduz e anima a boca do avatar. Silencioso se falhar."""
    if not text:
        return
    wav_path = None
    try:
        mp3 = asyncio.run(_synthesize(text))
        wav_path = _mp3_to_wav_file(mp3)
        rate, data = wavfile.read(wav_path)
        env = _envelope(data, rate)

        state.status = "falando"
        frame_dt = 1.0 / config.AVATAR_FPS
        sd.play(data, rate)
        t0 = time.time()
        for i, lvl in enumerate(env):
            if not state.running:
                break
            state.mouth_level = lvl
            target = t0 + (i + 1) * frame_dt
            sleep = target - time.time()
            if sleep > 0:
                time.sleep(sleep)
        sd.wait()
    except FileNotFoundError:
        print("[TTS] ffmpeg não encontrado. Instale com: sudo pacman -S ffmpeg")
    except Exception as e:
        print(f"[TTS] erro: {e}")
    finally:
        state.mouth_level = 0.0
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
