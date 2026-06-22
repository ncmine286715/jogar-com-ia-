# Zoeira — Assistente Multimodal Local (Qwen2.5-VL + Ollama)

Narradora de IA com **avatar animado** que vê sua tela e reage **como se
fosse vida real acontecendo ao vivo** — surta, debocha, zoa o jogador e
comenta sozinha enquanto você joga. Feita pra **criar conteúdo / clipe de
stream**: ouve o microfone, transcreve com Whisper local, tira screenshot,
manda pro **Qwen2.5-VL** via **Ollama local**, responde por voz (edge-tts)
e um **avatar abre a boca em lip-sync** com o que ela fala.

> Testamos o MiniCPM-V como alternativa (benchmark sugeria menos
> alucinação), mas na prática ele misturou idiomas e inventou histórias
> inteiras que não estavam na tela. O Qwen2.5-VL 7B se manteve mais fiel
> ao que realmente aparece — por isso é o padrão local do projeto.

Por padrão roda 100% local (exceto o TTS, que usa edge-tts). Também dá
pra usar a **NVIDIA NIM** (nuvem, tier gratuito) no lugar do Ollama —
modelo muito mais forte, sem precisar de GPU local — trocando
`LLM_BACKEND` em `config.py` (veja a seção **NVIDIA NIM** abaixo).

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
ollama pull qwen2.5vl:7b
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

## NVIDIA NIM (cloud, opcional)

Em vez do Ollama local, dá pra usar a [NVIDIA NIM](https://build.nvidia.com)
— tem tier **gratuito** com limite de requisições por minuto, e os modelos
são bem mais fortes que qualquer coisa que caiba numa RTX 8GB.

1. Crie a conta em build.nvidia.com e gere uma API key (`nvapi-...`).
2. **NUNCA** cole a key em nenhum arquivo do repositório. Exporte como
   variável de ambiente antes de rodar:
   ```bash
   export NVIDIA_API_KEY="nvapi-xxxxxxxxxxxxxxxx"
   ```
   (pra não digitar de novo a cada terminal, adicione essa linha no seu
   `~/.bashrc`/`~/.zshrc`, ou crie um arquivo `project/.env` — já está no
   `.gitignore` — e exporte a partir dele com `source .env` antes de
   rodar o `main.py`.)
3. Em `config.py`, defina `LLM_BACKEND = "nim"` (já é o padrão).
4. Rode `python main.py` normalmente — sem precisar do `ollama serve`.

O modelo padrão é o `meta/llama-3.2-90b-vision-instruct`, hoje uma das
melhores opções de visão+chat disponíveis na NIM: entende cena e
texto/HUD na imagem muito melhor que os modelos locais de 7-11B, e segue
a persona em PT-BR com menos alucinação. Se bater o limite do free tier
(HTTP 429), o código cai automaticamente pro `NIM_MODEL_FALLBACK`
(`meta/llama-3.2-11b-vision-instruct`, mais leve).

Pra voltar ao modo 100% local, basta `LLM_BACKEND = "ollama"`.

## Ajustes rápidos (`config.py`)

| Variável                  | Função                                            |
|---------------------------|----------------------------------------------------|
| `PERSONA_NAME`            | nome da personagem (título da janela/logs)        |
| `SYSTEM_PROMPT`           | personalidade e tom dela                           |
| `LLM_BACKEND`             | `"ollama"` (local) ou `"nim"` (NVIDIA NIM, cloud)  |
| `NIM_MODEL`               | modelo de visão usado na NIM                       |
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
