# screen.py — captura de tela (X11 via mss; Wayland via grim/spectacle/etc)
# Suporta um modo "stream": uma thread mantém o último frame sempre pronto
# (latência baixa) e mede o quanto a tela mudou (reação ao vivo a eventos).

import base64
import io
import os
import shutil
import subprocess
import tempfile
import threading
import time

import mss
import numpy as np
from PIL import Image, ImageStat

import config

# Ferramentas externas de screenshot p/ Wayland (mss captura tela preta nele).
# {f} é substituído pelo arquivo de saída. Ordem = preferência.
_WAYLAND_TOOLS = [
    ["grim", "{f}"],                                  # wlroots (Sway/Hyprland)
    ["spectacle", "-b", "-n", "-f", "-o", "{f}"],     # KDE Plasma
    ["gnome-screenshot", "-f", "{f}"],                # GNOME
    ["scrot", "{f}"],                                 # X11 fallback
]


def _is_wayland() -> bool:
    return "wayland" in os.environ.get("XDG_SESSION_TYPE", "").lower() or bool(
        os.environ.get("WAYLAND_DISPLAY")
    )


def _brightness(img: Image.Image) -> float:
    """Brilho médio 0..255. Perto de 0 = imagem preta (captura falhou)."""
    return ImageStat.Stat(img.convert("L")).mean[0]


def _capture_mss(monitor: int) -> Image.Image:
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[monitor])
    return Image.frombytes("RGB", shot.size, shot.rgb)


def _capture_external() -> Image.Image | None:
    """Tenta capturar via ferramenta de sistema (necessário no Wayland)."""
    for tool in _WAYLAND_TOOLS:
        if not shutil.which(tool[0]):
            continue
        f = tempfile.mktemp(suffix=".png")
        try:
            subprocess.run(
                [a.format(f=f) for a in tool],
                timeout=10,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            if os.path.exists(f) and os.path.getsize(f) > 0:
                img = Image.open(f).convert("RGB")
                return img
        except Exception:
            continue
        finally:
            if os.path.exists(f):
                os.remove(f)
    return None


_warned = False


def _grab(monitor: int) -> Image.Image:
    """Captura robusta: no Wayland usa ferramenta externa; valida se não é preta."""
    global _warned
    img = None

    if _is_wayland():
        img = _capture_external()

    if img is None:
        img = _capture_mss(monitor)

    # Se veio preta (típico do mss no Wayland), tenta a externa como resgate.
    if _brightness(img) < 8:
        alt = _capture_external()
        if alt is not None and _brightness(alt) >= 8:
            img = alt
        elif not _warned:
            _warned = True
            print(
                "[SCREEN] Tela capturada está PRETA. No Wayland, instale uma "
                "ferramenta de screenshot: 'grim' (Sway/Hyprland), 'spectacle' "
                "(KDE) ou 'gnome-screenshot' (GNOME). A IA não consegue ver a "
                "tela sem isso e vai 'inventar'."
            )
    return img


def _encode(img: Image.Image) -> str:
    """Redimensiona e devolve JPEG base64 (leve = menos latência)."""
    max_width = config.SCREENSHOT_MAX_WIDTH
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=config.SCREENSHOT_JPEG_QUALITY)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def capture_base64(monitor: int = 1) -> str:
    """Captura a tela na hora e retorna JPEG em base64."""
    return _encode(_grab(monitor))


# --- Modo stream (tempo real) --------------------------------------------
# Uma thread captura a tela continuamente. O resto do programa pega sempre o
# último frame (instantâneo) e consulta o quanto a tela mudou desde a última
# fala, pra reagir AO VIVO quando algo acontece no jogo.

_stream_b64 = None
_stream_thumb = None          # miniatura cinza p/ medir mudança de cena
_stream_lock = threading.Lock()
_stream_thread = None


def _thumb(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("L").resize((32, 18)), dtype=np.float32)


def _stream_loop(monitor: int) -> None:
    global _stream_b64, _stream_thumb
    period = 1.0 / max(1, config.STREAM_FPS)
    while state_running():
        t0 = time.time()
        try:
            img = _grab(monitor)
            b64 = _encode(img)
            th = _thumb(img)
            with _stream_lock:
                _stream_b64, _stream_thumb = b64, th
        except Exception as e:
            print(f"[STREAM] erro: {e}")
        sleep = period - (time.time() - t0)
        if sleep > 0:
            time.sleep(sleep)


def state_running() -> bool:
    # import tardio p/ evitar ciclo de import com state
    import state
    return state.running


def start_stream(monitor: int = 1) -> None:
    """Inicia a captura contínua em background (idempotente)."""
    global _stream_thread
    if not config.STREAM_ENABLED or _stream_thread is not None:
        return
    _stream_thread = threading.Thread(
        target=_stream_loop, args=(monitor,), daemon=True
    )
    _stream_thread.start()


def latest_base64(monitor: int = 1) -> str:
    """Último frame do stream (instantâneo). Cai pra captura na hora se vazio."""
    with _stream_lock:
        b64 = _stream_b64
    return b64 if b64 is not None else capture_base64(monitor)


def scene_change() -> float:
    """Diferença média (0..1) entre o frame atual e o último frame 'marcado'."""
    with _stream_lock:
        cur, ref = _stream_thumb, _scene_ref[0]
    if cur is None or ref is None:
        return 1.0
    return float(np.mean(np.abs(cur - ref)) / 255.0)


_scene_ref = [None]


def mark_scene() -> None:
    """Marca o frame atual como referência (chamar após comentar)."""
    with _stream_lock:
        _scene_ref[0] = _stream_thumb
