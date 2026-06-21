# llm.py — chamada ao Qwen2.5-VL via Ollama (/api/generate)

import requests

import config


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
        },
    }
    try:
        r = requests.post(
            config.OLLAMA_URL, json=payload, timeout=config.OLLAMA_TIMEOUT
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
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
