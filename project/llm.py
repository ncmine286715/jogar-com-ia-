# llm.py — chamada ao Qwen2.5-VL via Ollama (/api/generate)

import re

import requests

import config

# Remove emojis e símbolos (o TTS lê ou engasga neles) + markdown
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002190-\U000021FF\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F]+"
)


def _clean(text: str) -> str:
    text = _EMOJI.sub("", text)
    text = text.replace("*", "").replace("#", "")
    return re.sub(r"\s+", " ", text).strip()


def ask(prompt: str, image_b64: str) -> str:
    """Envia texto + imagem (base64) ao Ollama e retorna a resposta textual."""
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "system": config.SYSTEM_PROMPT,
        "images": [image_b64],
        "stream": False,
        "options": {
            "num_predict": config.OLLAMA_NUM_PREDICT,
            "temperature": config.OLLAMA_TEMPERATURE,
            "top_p": config.OLLAMA_TOP_P,
        },
    }
    try:
        r = requests.post(
            config.OLLAMA_URL, json=payload, timeout=config.OLLAMA_TIMEOUT
        )
        r.raise_for_status()
        return _clean(r.json().get("response", ""))
    except requests.exceptions.ConnectionError:
        return "Erro: Ollama offline. Inicie com 'ollama serve'."
    except requests.exceptions.Timeout:
        return "Erro: o modelo demorou demais para responder."
    except requests.exceptions.HTTPError as e:
        try:
            detail = r.json().get("error", str(e))
        except Exception:
            detail = str(e)
        return f"Erro do Ollama: {detail} (verifique 'ollama pull {config.OLLAMA_MODEL}')"
    except Exception as e:
        return f"Erro ao consultar o modelo: {e}"
