# Zoeira — Assistente Multimodal Local (MiniCPM-V + Ollama)

Narradora de IA com **avatar animado** que vê sua tela e reage **como se
fosse vida real acontecendo ao vivo** — surta, debocha, zoa o jogador e
comenta sozinha enquanto você joga. Feita pra **criar conteúdo / clipe de
stream**: ouve o microfone, transcreve com Whisper local, tira screenshot,
manda pro **MiniCPM-V** via **Ollama local**, responde por voz (edge-tts)
e um **avatar abre a boca em lip-sync** com o que ela fala.

100% local — exceto o TTS (edge-tts). Nenhuma API paga.

## Estrutura

```
project/
├── main.py      # orquestra: avatar (thread principal) + assistente (worker)
├── stt.py       # microfone + faster-whisper (voz -> texto)
├── screen.py    # captura de tela (mss) -> base64
├── llm.py       # chamada ao Ollama /api/generate (Qwen2.5-VL)
├── tts.py       # edge-tts -> áudio + lip-sync (sounddevice + scipy)
├── avatar.py    # rosto animado (pygame) que abre a boca ao falar
├── state.py     # estado compartilhado entre avatar e assistente
└── config.py    # configurações
```

## Pré-requisitos (CachyOS / Arch)

```bash
# Dependências de sistema
sudo pacman -S python ffmpeg portaudio wmctrl

# Ollama + modelo
# instale/atualize o Ollama (https://ollama.com), depois:
ollama pull minicpm-v
ollama serve   # deixa rodando em http://localhost:11434
```

`wmctrl` é opcional, só necessário pro avatar ficar **sempre por cima de
outros apps/jogos** (X11/XWayland). No Wayland puro não tem como nenhum
programa se forçar acima de outro — é uma trava do protocolo, não do
Zoeira.

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
- **Persona "vida real"**: ela acredita 100% que o que está na tela está
  acontecendo de verdade — reage com surto, drama e deboche (ótimo pra
  clipe). Tom BR escrachado com palavrão, definido em
  `SYSTEM_PROMPT`/`AUTO_PROMPT` em `config.py` — edite à vontade. Troque o
  nome dela em `PERSONA_NAME`.

## Avatar + criação de conteúdo

Ao rodar, abre uma janela com o avatar. A **boca abre em lip-sync** com a
voz (sincronizada pela amplitude do áudio), o personagem **flutua**
suavemente, e aparece o **status** (ouvindo/pensando/falando) + **legenda**
do que ele está falando.

**Avatar em PNG (seu personagem):** coloque `base.png` (+ opcionalmente
`mouth_closed.png`/`mouth_open.png`) em `assets/avatar/` — veja
`assets/avatar/README.md` pra detalhes de como funciona o anchor da boca.
Sem esses arquivos, cai automaticamente num rosto desenhado em código.

**Capturar no OBS:**
1. O fundo da janela é **verde puro** (`AVATAR_BG`) — adicione a janela como
   *Captura de Janela* no OBS e aplique o filtro **Chroma Key** pra deixar
   o avatar transparente sobre o gameplay.
2. Feche a janela (X) para encerrar tudo.

Desligue o avatar com `AVATAR_ENABLED = False` (roda só no terminal/voz).

## Ajustes rápidos (`config.py`)

| Variável                  | Função                                            |
|---------------------------|----------------------------------------------------|
| `PERSONA_NAME`            | nome da personagem (título da janela/logs)        |
| `SYSTEM_PROMPT`           | personalidade e tom dela                           |
| `WHISPER_MODEL`           | precisão x velocidade do STT (`tiny`..`large-v3`) |
| `WHISPER_DEVICE`          | `cpu` ou `cuda` (GPU NVIDIA)                       |
| `VAD_THRESHOLD`           | sensibilidade do microfone no modo `loop` (RMS)   |
| `AUTO_COMMENT`            | liga/desliga as reações espontâneas                |
| `AUTO_IDLE_SECONDS`       | tempo sem falar até reagir sozinha                 |
| `OLLAMA_NUM_PREDICT`      | tokens máximos da resposta (menor = mais rápido)  |
| `OLLAMA_TEMPERATURE`      | criatividade/caos (maior = mais doido)            |
| `SCREENSHOT_MAX_WIDTH`    | resolução enviada ao modelo (menor = mais rápido) |
| `TTS_VOICE`               | voz do edge-tts (`edge-tts --list-voices`)        |
| `TTS_RATE`                | velocidade da fala (ex: `+12%`)                    |
| `AVATAR_ENABLED`          | liga/desliga a janela do avatar                    |
| `AVATAR_ALWAYS_ON_TOP`    | janela do avatar flutua por cima de qualquer app/jogo (precisa `wmctrl` no Linux) |
| `AVATAR_BG`               | cor de fundo p/ chroma key no OBS                  |
| `AVATAR_MOUTH_SENSITIVITY`| o quanto a boca abre em relação ao volume          |
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
