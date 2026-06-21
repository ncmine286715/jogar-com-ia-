# tts.py — síntese de voz (edge-tts) + reprodução (sounddevice + scipy)

import asyncio
import os
import subprocess
import tempfile

import edge_tts
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


def speak(text: str) -> None:
    """Sintetiza e reproduz o texto. Silencioso em caso de falha."""
    if not text:
        return
    wav_path = None
    try:
        mp3 = asyncio.run(_synthesize(text))
        wav_path = _mp3_to_wav_file(mp3)
        rate, data = wavfile.read(wav_path)
        sd.play(data, rate)
        sd.wait()
    except FileNotFoundError:
        print("[TTS] ffmpeg não encontrado. Instale com: sudo pacman -S ffmpeg")
    except Exception as e:
        print(f"[TTS] erro: {e}")
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
