# tts.py — síntese de voz (edge-tts) + reprodução (sounddevice + scipy)

import asyncio
import io
import subprocess

import edge_tts
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

import config


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


def _mp3_to_wav(mp3: bytes) -> bytes:
    """Converte MP3 -> WAV PCM via ffmpeg (decodifica o formato do edge-tts)."""
    proc = subprocess.run(
        ["ffmpeg", "-i", "pipe:0", "-f", "wav", "pipe:1"],
        input=mp3,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    return proc.stdout


def speak(text: str) -> None:
    """Sintetiza e reproduz o texto. Silencioso em caso de falha."""
    if not text:
        return
    try:
        mp3 = asyncio.run(_synthesize(text))
        wav = _mp3_to_wav(mp3)
        rate, data = wavfile.read(io.BytesIO(wav))
        sd.play(data, rate)
        sd.wait()
    except FileNotFoundError:
        print("[TTS] ffmpeg não encontrado. Instale com: sudo pacman -S ffmpeg")
    except Exception as e:
        print(f"[TTS] erro: {e}")
