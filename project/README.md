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
ollama pull qwen2.5vl:3b
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

- **Modo `loop`** (padrão): escuta contínua sem ENTER. Detecta quando você
  começa a falar (VAD por energia), grava e para automaticamente quando você
  fica em silêncio.
- **Modo `push`**: pressione ENTER, fale por `RECORD_SECONDS`, ouça a
  resposta. Edite `MODE = "push"` em `config.py` para usar.

## Ajustes rápidos (`config.py`)

| Variável          | Função                                            |
|-------------------|---------------------------------------------------|
| `WHISPER_MODEL`   | precisão x velocidade do STT (`tiny`..`large-v3`) |
| `WHISPER_DEVICE`  | `cpu` ou `cuda` (GPU NVIDIA)                       |
| `RECORD_SECONDS`  | duração da gravação no modo `push`                |
| `VAD_THRESHOLD`   | sensibilidade do microfone no modo `loop` (RMS)   |
| `VAD_SILENCE_MS`  | silêncio necessário para considerar fala encerrada|
| `VAD_MAX_SECONDS` | corte de segurança por fala no modo `loop`        |
| `TTS_VOICE`       | voz do edge-tts                                   |
| `MODE`            | `loop` (sem ENTER) ou `push`                      |

## Notas

- `ffmpeg` é usado para decodificar o MP3 do edge-tts antes de tocar.
- Erros comuns (Ollama offline, áudio, ffmpeg ausente) são tratados sem
  derrubar o loop.
