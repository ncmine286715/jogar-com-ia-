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
- **Comentário autônomo** (`AUTO_COMMENT = True`, padrão): se você ficar
  `AUTO_IDLE_SECONDS` sem falar nada, a IA olha a tela por conta própria e
  solta um comentário sozinha — útil pra ela narrar/zoar enquanto você joga
  sem precisar perguntar nada. Desligue com `AUTO_COMMENT = False`.
- **Modo `push`**: pressione ENTER, fale por `RECORD_SECONDS`, ouça a
  resposta. Edite `MODE = "push"` em `config.py` para usar.
- **Persona**: respostas vêm no tom zoeiro/BR (gíria, deboche, palavrão
  leve), definido em `SYSTEM_PROMPT`/`AUTO_PROMPT` em `config.py` — edite
  livremente pra ajustar o tom.

## Ajustes rápidos (`config.py`)

| Variável                  | Função                                            |
|---------------------------|----------------------------------------------------|
| `WHISPER_MODEL`           | precisão x velocidade do STT (`tiny`..`large-v3`) |
| `WHISPER_DEVICE`          | `cpu` ou `cuda` (GPU NVIDIA)                       |
| `RECORD_SECONDS`          | duração da gravação no modo `push`                |
| `VAD_THRESHOLD`           | sensibilidade do microfone no modo `loop` (RMS)   |
| `VAD_SILENCE_MS`          | silêncio necessário para considerar fala encerrada|
| `VAD_MAX_SECONDS`         | corte de segurança por fala no modo `loop`        |
| `AUTO_COMMENT`            | liga/desliga o comentário espontâneo               |
| `AUTO_IDLE_SECONDS`       | tempo sem falar até comentar sozinha               |
| `OLLAMA_NUM_PREDICT`      | tokens máximos da resposta (menor = mais rápido)  |
| `SCREENSHOT_MAX_WIDTH`    | resolução enviada ao modelo (menor = mais rápido) |
| `SCREENSHOT_JPEG_QUALITY` | qualidade do JPEG enviado (menor = mais rápido)   |
| `TTS_VOICE`               | voz do edge-tts                                   |
| `MODE`                    | `loop` (sem ENTER) ou `push`                      |

## Sobre a latência

A maior parte do delay costuma vir do tempo de inferência do modelo no
Ollama (depende do hardware) e do edge-tts, que depende de internet (é a
única peça não-100%-local do projeto). Reduzimos o impacto via
`OLLAMA_NUM_PREDICT` baixo, screenshot em JPEG menor, e pulando o STT
inteiramente no comentário autônomo. Se ainda estiver lento:
- troque `WHISPER_MODEL` para `tiny` (perde um pouco de precisão);
- baixe `SCREENSHOT_MAX_WIDTH` ainda mais (ex: 768);
- confirme que o Ollama está usando GPU, se disponível (`ollama ps`).

## Notas

- `ffmpeg` é usado para decodificar o MP3 do edge-tts antes de tocar.
- Erros comuns (Ollama offline, áudio, ffmpeg ausente) são tratados sem
  derrubar o loop.
