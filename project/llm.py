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


def _ask_gemini(prompt: str, image_b64: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": config.SYSTEM_PROMPT}]},
        "contents": [
            {
                "parts": [
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}},
                    {"text": prompt},
                ],
            }
        ],
        "generationConfig": {
            "maxOutputTokens": config.GEMINI_MAX_TOKENS,
            "temperature": config.GEMINI_TEMPERATURE,
        },
        "safetySettings": [
            {"category": c, "threshold": "BLOCK_NONE"}
            for c in [
                "HARM_CATEGORY_HARASSMENT",
                "HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "HARM_CATEGORY_DANGEROUS_CONTENT",
            ]
        ],
    }
    try:
        r = requests.post(url, json=payload, timeout=config.GEMINI_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return _clean(text)
    except requests.exceptions.Timeout:
        return "Porra, travou tudo, nao consigo pensar direito agora."
    except requests.exceptions.ConnectionError:
        return "Mano, perdi a conexao, to isolado aqui."
    except (KeyError, IndexError):
        return "Caralho, bugou minha cabeca, tenta de novo."
    except Exception as e:
        return f"Erro Gemini: {e}"


def _ask_nim(prompt: str, image_b64: str) -> str:
    headers = {
        "Authorization": f"Bearer {config.NIM_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                },
                {"type": "text", "text": prompt},
            ],
        },
    ]
    payload = {
        "model": config.NIM_MODEL,
        "messages": messages,
        "max_tokens": config.NIM_MAX_TOKENS,
        "temperature": config.NIM_TEMPERATURE,
        "top_p": config.NIM_TOP_P,
        "stream": False,
    }
    try:
        r = requests.post(
            config.NIM_URL, json=payload, headers=headers, timeout=config.NIM_TIMEOUT
        )
        if r.status_code == 429:
            payload["model"] = config.NIM_MODEL_FALLBACK
            r = requests.post(
                config.NIM_URL, json=payload, headers=headers, timeout=config.NIM_TIMEOUT
            )
        r.raise_for_status()
        return _clean(r.json()["choices"][0]["message"]["content"])
    except requests.exceptions.Timeout:
        return "Porra, travou tudo, nao consigo pensar direito agora."
    except requests.exceptions.ConnectionError:
        return "Mano, perdi a conexao, to isolado aqui."
    except Exception as e:
        return f"Erro NIM: {e}"


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
    except Exception as e:
        return f"Erro Ollama: {e}"


def ask(prompt: str, image_b64: str) -> str:
    if config.LLM_BACKEND == "gemini":
        return _ask_gemini(prompt, image_b64)
    if config.LLM_BACKEND == "nim":
        return _ask_nim(prompt, image_b64)
    return _ask_ollama(prompt, image_b64)
