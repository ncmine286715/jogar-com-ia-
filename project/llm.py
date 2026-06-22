# llm.py — chamada ao modelo de visão, via Ollama (local) ou NVIDIA NIM (cloud)

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
    """Envia texto + imagem (base64) ao backend configurado e retorna a resposta."""
    if config.LLM_BACKEND == "nim":
        return _ask_nim(prompt, image_b64)
    return _ask_ollama(prompt, image_b64)


def _ask_ollama(prompt: str, image_b64: str) -> str:
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
            "top_k": getattr(config, "OLLAMA_TOP_K", 60),
            "repeat_penalty": getattr(config, "OLLAMA_REPEAT_PENALTY", 1.15),
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


def _nim_payload(model: str, prompt: str, image_b64: str) -> dict:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                ],
            },
        ],
        "max_tokens": config.NIM_MAX_TOKENS,
        "temperature": config.NIM_TEMPERATURE,
        "top_p": config.NIM_TOP_P,
        "stream": False,
    }


def _post_nim(model: str, prompt: str, image_b64: str) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {config.NIM_API_KEY}",
        "Accept": "application/json",
    }
    return requests.post(
        config.NIM_URL,
        headers=headers,
        json=_nim_payload(model, prompt, image_b64),
        timeout=config.NIM_TIMEOUT,
    )


def _ask_nim(prompt: str, image_b64: str) -> str:
    if not config.NIM_API_KEY:
        return (
            "Erro: NVIDIA_API_KEY não configurada. Rode "
            "'export NVIDIA_API_KEY=nvapi-xxxx' antes de iniciar."
        )
    try:
        r = _post_nim(config.NIM_MODEL, prompt, image_b64)
        if r.status_code == 429 and config.NIM_MODEL_FALLBACK:
            # estourou o limite do free tier no modelo principal -> tenta o menor
            r = _post_nim(config.NIM_MODEL_FALLBACK, prompt, image_b64)
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"]
        return _clean(text)
    except requests.exceptions.ConnectionError:
        return "Erro: sem conexão com a API da NVIDIA NIM."
    except requests.exceptions.Timeout:
        return "Erro: o modelo da NIM demorou demais para responder."
    except requests.exceptions.HTTPError as e:
        try:
            detail = r.json().get("detail", r.json().get("error", str(e)))
        except Exception:
            detail = str(e)
        return f"Erro da NIM: {detail}"
    except Exception as e:
        return f"Erro ao consultar a NIM: {e}"
