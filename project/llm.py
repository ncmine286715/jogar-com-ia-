# llm.py — chamada ao modelo de visão via NVIDIA NIM (API OpenAI-compatible)

import re

import requests

import config

_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002190-\U000021FF\U00002B00-\U00002BFF\U0000FE00-\U0000FE0F]+"
)


def _clean(text: str) -> str:
    text = _EMOJI.sub("", text)
    text = text.replace("*", "").replace("#", "")
    return re.sub(r"\s+", " ", text).strip()


_PERSONA_TAG = (
    "[Você é a ZOEIRA, parceira de gameplay zoeira e debochada — responda "
    "no personagem, com gíria BR e humor, NUNCA como IA/assistente.] "
)


def ask(prompt: str, image_b64: str) -> str:
    """Envia texto + imagem ao NVIDIA NIM e retorna a resposta textual."""
    if not config.NIM_API_KEY:
        return "Erro: defina QWEN_API_KEY ou rode o proxy em localhost:3000"

    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                },
                {"type": "text", "text": _PERSONA_TAG + prompt},
            ],
        },
    ]

    payload = {
        "model": config.NIM_MODEL,
        "messages": messages,
        "max_tokens": config.NIM_MAX_TOKENS,
        "temperature": config.NIM_TEMPERATURE,
        "top_p": config.NIM_TOP_P,
        "stop": config.NIM_STOP,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {config.NIM_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(
            f"{config.NIM_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=config.NIM_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"]
        return _clean(text)
    except requests.exceptions.ConnectionError:
        return "Erro: proxy offline. Rode o qwen-code-oai-proxy em localhost:3000."
    except requests.exceptions.Timeout:
        return "Erro: o modelo demorou demais pra responder."
    except requests.exceptions.HTTPError as e:
        try:
            detail = r.json().get("detail", r.json().get("error", {}).get("message", str(e)))
        except Exception:
            detail = str(e)
        if r.status_code == 401:
            return "Erro: nao autorizado. Verifique a sessao/login do proxy."
        if r.status_code == 429:
            return "Erro: limite de requisicoes atingido. Espere um pouco."
        return f"Erro do proxy ({r.status_code}): {detail}"
    except (KeyError, IndexError):
        return "Erro: resposta inesperada do proxy."
    except Exception as e:
        return f"Erro ao consultar o modelo: {e}"
