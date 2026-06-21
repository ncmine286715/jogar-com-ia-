# screen.py — captura de tela (X11 via mss; Wayland via grim/spectacle/etc)

import base64
import io
import os
import shutil
import subprocess
import tempfile

import mss
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


def capture_base64(monitor: int = 1) -> str:
    """Captura a tela e retorna JPEG em base64 (leve = menos latência)."""
    img = _grab(monitor)

    max_width = config.SCREENSHOT_MAX_WIDTH
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=config.SCREENSHOT_JPEG_QUALITY)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
