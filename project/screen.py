# screen.py — captura de tela e codificação em base64

import base64
import io

import mss
from PIL import Image


def capture_base64(monitor: int = 1, max_width: int = 1280) -> str:
    """Captura a tela e retorna PNG em base64.

    max_width reduz a imagem para baixar latência/banda do LLM.
    """
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[monitor])
        img = Image.frombytes("RGB", shot.size, shot.rgb)

    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
