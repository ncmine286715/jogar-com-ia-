# Assistente Multimodal Local (Qwen2.5-VL + Ollama)

Assistente de voz que vê sua tela: escuta o microfone, transcreve com Whisper
local, captura um screenshot, envia tudo para o **Qwen2.5-VL** via **Ollama
local** e responde por voz (edge-tts).

100% local — exceto o TTS (edge-tts). Nenhuma API paga.

## Estrutura

```
project/
├── main.py      # loop principal (push-to-talk ou contínuo)
├── stt.py       # microfone + faster-whisper (voz -> texto)
├── screen.py    # captura de tela (mss) -> base64
├── llm.py       # chamada ao Ollama /api/generate (Qwen2.5-VL)
├── tts.py       # edge-tts -> áudio (sounddevice + scipy)
└── config.py    # configurações
```

## Pré-requisitos (CachyOS / Arch)

```bash
# Dependências de sistema
sudo pacman -S python ffmpeg portaudio

# Ollama + modelo
# instale o Ollama (https://ollama.com), depois:
ollama pull qwen2.5vl
ollama serve   # deixa rodando em http://localhost:11434
```

## Instalação

```bash
cd project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

- **Modo push-to-talk** (padrão): pressione ENTER, fale ~5s, ouça a resposta.
- **Modo contínuo**: edite `MODE = "loop"` em `config.py`.

## Ajustes rápidos (`config.py`)

| Variável          | Função                                            |
|-------------------|---------------------------------------------------|
| `WHISPER_MODEL`   | precisão x velocidade do STT (`tiny`..`large-v3`) |
| `WHISPER_DEVICE`  | `cpu` ou `cuda` (GPU NVIDIA)                       |
| `RECORD_SECONDS`  | duração da gravação                               |
| `TTS_VOICE`       | voz do edge-tts                                   |
| `MODE`            | `push` ou `loop`                                  |

## Notas

- `ffmpeg` é usado para decodificar o MP3 do edge-tts antes de tocar.
- Erros comuns (Ollama offline, áudio, ffmpeg ausente) são tratados sem
  derrubar o loop.
