# sfx.py — efeitos sonoros de zueira para os comentários.
# Funciona sem nenhum arquivo: gera os efeitos na hora (numpy). Se existir
# assets/sfx/<nome>.wav, usa o seu arquivo no lugar do gerado.

import os
import re
import threading
import time

import numpy as np
import sounddevice as sd

import config

_RATE = 44100
_last_play = 0.0
_lock = threading.Lock()


def _env(n, attack=0.01, release=0.3):
    """Envelope simples ataque/decaimento para o som não 'estalar'."""
    a = int(_RATE * attack)
    r = int(_RATE * release)
    env = np.ones(n, dtype=np.float32)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if r > 0 and r < n:
        env[-r:] = np.linspace(1, 0, r)
    return env


def _tone(freq, dur, kind="sine", vol=1.0):
    t = np.linspace(0, dur, int(_RATE * dur), endpoint=False)
    if kind == "saw":
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    else:
        wave = np.sin(2 * np.pi * freq * t)
    return (wave * _env(len(wave), release=dur * 0.5) * vol).astype(np.float32)


def _silence(dur):
    return np.zeros(int(_RATE * dur), dtype=np.float32)


# --- Geradores de efeitos -------------------------------------------------

def _gen_boom():
    """'Vine boom' — grave que desce, pra momentos de tensão/morte."""
    dur = 0.7
    t = np.linspace(0, dur, int(_RATE * dur), endpoint=False)
    freq = np.linspace(120, 45, len(t))
    wave = np.sin(2 * np.pi * np.cumsum(freq) / _RATE)
    return (wave * _env(len(wave), 0.005, dur * 0.8)).astype(np.float32)


def _gen_airhorn():
    """Buzina de baile — pra zoeira/comemoração."""
    base = _tone(330, 0.5, "saw", 0.5) + _tone(415, 0.5, "saw", 0.4)
    blast = base / np.max(np.abs(base) or 1.0)
    gap = _silence(0.06)
    return np.concatenate([blast[: int(_RATE * 0.18)], gap, blast])


def _gen_rimshot():
    """'Ba dum tss' — pra piada/deboche."""
    drum1 = _tone(180, 0.12, "sine", 0.8)
    drum2 = _tone(150, 0.12, "sine", 0.8)
    noise = np.random.randn(int(_RATE * 0.4)).astype(np.float32)
    cymbal = noise * _env(len(noise), 0.001, 0.4) * 0.3
    return np.concatenate([drum1, _silence(0.05), drum2, _silence(0.03), cymbal])


def _gen_ding():
    """Plim de acerto/positivo."""
    return _tone(880, 0.15, "sine", 0.6) + np.concatenate(
        [_silence(0.0), _tone(1320, 0.25, "sine", 0.4)]
    )[: int(_RATE * 0.15)]


_GENERATORS = {
    "boom": _gen_boom,
    "airhorn": _gen_airhorn,
    "rimshot": _gen_rimshot,
    "ding": _gen_ding,
}

# Palavras no comentário/fala que disparam cada efeito (ordem = prioridade).
_TRIGGERS = [
    ("boom", r"\b(morr|morreu|morri|perdeu|perdi|game over|acabou|fim|caiu|tomou)\b"),
    ("airhorn", r"(haha|kkk|rsrs|que isso|caralho|porra|mds|eita|nossa|aff)"),
    ("ding", r"\b(boa|isso|consegui|ganhou|venceu|matou|acertou|pegou|win)\b"),
    ("rimshot", r"\b(piada|trocadilho|nada|hein|sei|claro|aham|tá certo)\b"),
]

_cache: dict[str, np.ndarray] = {}


def _load(name: str) -> "np.ndarray | None":
    if name in _cache:
        return _cache[name]
    # 1) arquivo do usuário tem prioridade
    path = os.path.join(os.path.dirname(__file__), config.SFX_DIR, f"{name}.wav")
    data = None
    if os.path.exists(path):
        try:
            from scipy.io import wavfile

            _, raw = wavfile.read(path)
            raw = raw.astype(np.float32)
            if raw.ndim > 1:
                raw = raw.mean(axis=1)
            peak = np.max(np.abs(raw)) or 1.0
            data = raw / peak
        except Exception:
            data = None
    # 2) cai no gerado proceduralmente
    if data is None and name in _GENERATORS:
        data = _GENERATORS[name]()
        peak = np.max(np.abs(data)) or 1.0
        data = data / peak
    if data is not None:
        _cache[name] = data
    return data


def pick(text: str) -> "str | None":
    """Escolhe o efeito que combina com o texto, ou None."""
    low = (text or "").lower()
    for name, pattern in _TRIGGERS:
        if re.search(pattern, low):
            return name
    return None


def play(name: str) -> None:
    """Toca um efeito (bloqueante). Respeita cooldown e volume."""
    global _last_play
    if not config.SFX_ENABLED or not name:
        return
    with _lock:
        now = time.time()
        if now - _last_play < config.SFX_COOLDOWN:
            return
        _last_play = now
    data = _load(name)
    if data is None:
        return
    try:
        sd.play(data * config.SFX_VOLUME, _RATE)
        sd.wait()
    except Exception as e:
        print(f"[SFX] erro: {e}")


def play_for(text: str) -> None:
    """Atalho: escolhe e toca o efeito que combina com o texto."""
    play(pick(text))
