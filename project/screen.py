# screen.py — captura de tela e codificação em base64

import base64
import io

import mss
from PIL import Image

import config


def capture_base64(monitor: int = 1) -> str:
    """Captura a tela e retorna JPEG em base64 (leve = menos latência)."""
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[monitor])
        img = Image.frombytes("RGB", shot.size, shot.rgb)

    max_width = config.SCREENSHOT_MAX_WIDTH
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=config.SCREENSHOT_JPEG_QUALITY)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
