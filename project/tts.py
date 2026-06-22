# tts.py — síntese de voz (edge-tts) + reprodução (sounddevice + scipy)
# Durante a fala, dirige state.mouth_level pela amplitude (lip-sync do avatar).

import asyncio
import os
import re
import subprocess
import tempfile
import time

import edge_tts
import numpy as np
import sounddevice as sd
from scipy.io import wavfile

import config
import state

# Gírias/abreviações/internetês escritas que a voz lê errado ou engole ->
# expandidas pra palavra completa, como se fosse falar em voz alta.
_SPEECH_FIXES = {
    "krl": "caralho", "kct": "caralho", "pqp": "puta que pariu",
    "mds": "meu deus", "pq": "porque", "vc": "você", "vcs": "vocês",
    "tb": "também", "tbm": "também", "blz": "beleza", "vlw": "valeu",
    "flw": "falou", "pf": "por favor", "msm": "mesmo", "qnd": "quando",
    "obg": "obrigado", "dpois": "depois", "agr": "agora", "td": "tudo",
    "n": "não", "naum": "não", "eh": "é", "ctz": "com certeza",
    "slc": "se lasca", "fdp": "filho da puta", "vsf": "vai se foder",
}
# Risada escrita repetida (kkkk, rsrs, hahaha, ahahah) -> uma risada limpa.
_LAUGH_RE = re.compile(r"\b(?:k{2,}|(?:rs){2,}|(?:a?ha){2,}h?|hu{2,})\b", re.I)
# Letras repetidas em excesso (ééééé, simmm) -> no máximo duas.
_REPEAT_RE = re.compile(r"(.)\1{2,}")


def _normalize_for_speech(text: str) -> str:
    """Deixa o texto mais falável: troca gírias e some com risada digitada."""
    if not config.TTS_NORMALIZE:
        return text
    text = _LAUGH_RE.sub("haha", text)
    text = _REPEAT_RE.sub(r"\1\1", text)

    def _swap(m):
        return _SPEECH_FIXES.get(m.group(0).lower(), m.group(0))

    text = re.sub(r"\b\w+\b", _swap, text)
    return re.sub(r"\s+", " ", text).strip()


async def _stream_voice(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=config.TTS_RATE,
        pitch=config.TTS_PITCH,
        volume=config.TTS_VOLUME,
    )
    audio = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
    return bytes(audio)


async def _synthesize(text: str) -> bytes:
    """Gera MP3 com edge-tts. Tenta de novo e cai numa voz alternativa se o
    servidor devolver áudio vazio ('No audio was received')."""
    voices = [config.TTS_VOICE] + [
        v for v in config.TTS_FALLBACK_VOICES if v != config.TTS_VOICE
    ]
    last_err = None
    for voice in voices:
        for attempt in range(config.TTS_RETRIES):
            try:
                audio = await _stream_voice(text, voice)
                if audio:
                    return audio
                last_err = "áudio vazio"
            except Exception as e:
                last_err = e
            await asyncio.sleep(0.4)  # respiro antes de tentar de novo
    raise RuntimeError(f"edge-tts falhou ({last_err}). Atualize: pip install -U edge-tts")


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
        mp3 = asyncio.run(_synthesize(_normalize_for_speech(text)))
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
