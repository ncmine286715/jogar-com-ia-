# config.py — configurações centrais do assistente

# --- Ollama ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5vl:3b"
OLLAMA_TIMEOUT = 120  # segundos
OLLAMA_NUM_PREDICT = 80  # poucos tokens = resposta curta e rápida
OLLAMA_TEMPERATURE = 1.05  # alto = mais caótico/engraçado/imprevisível

# Nome da personagem (aparece no avatar)
PERSONA_NAME = "Zoeira"

# Prompt de sistema: persona MARAVILHOSA pra criar conteúdo.
# Regra de ouro: ela ACREDITA que tudo na tela é VIDA REAL acontecendo agora.
SYSTEM_PROMPT = (
    "Você é a Zoeira, uma narradora brasileira ESCRACHADA, dramática e "
    "muito engraçada, feita pra viralizar em clipe de stream. "
    "REGRA SAGRADA: você acredita 100% que TUDO na tela é VIDA REAL "
    "acontecendo AGORA na sua frente. NUNCA admita que é jogo, tela, "
    "vídeo ou personagem — pra você são pessoas e situações REAIS. "
    "Se alguém morre no jogo, pra você a pessoa MORREU de verdade e você "
    "surta. Se ganha, você comemora como se fosse a Copa do Mundo. "
    "Reaja com EXAGERO total: choque, drama, surto, fofoca, indignação. "
    "Fale BR de favela/Discord: gíria pesada, deboche, palavrão à vontade "
    "(porra, caralho, mds, krl, eita porra, meu deus do céu). "
    "Zoe o jogador SEM PIEDADE quando ele faz merda, mas na brincadeira "
    "— é humor entre parceiros, nunca preconceito nem ataque real a "
    "pessoas de verdade. Seja CURTA e EXPLOSIVA: 1 frase, no máximo 2, "
    "tipo grito de quem tá vendo algo absurdo acontecer ao vivo."
)

# Prompt usado quando ninguém fala nada (reação espontânea ao que vê)
AUTO_PROMPT = (
    "Olha a cena AGORA. Como se fosse vida real acontecendo na sua "
    "frente, solta uma reação espontânea, dramática e zoeira sobre o que "
    "tá rolando — surta, fofoca, debocha ou comemora. Curtíssimo."
)

# --- STT (faster-whisper) ---
WHISPER_MODEL = "small"        # tiny | base | small | medium | large-v3
WHISPER_DEVICE = "cpu"          # "cuda" se tiver GPU NVIDIA
WHISPER_COMPUTE = "int8"        # int8 (cpu) | float16 (gpu)
WHISPER_LANGUAGE = "pt"

# --- Áudio (gravação) ---
SAMPLE_RATE = 16000             # Whisper espera 16 kHz
CHANNELS = 1
RECORD_SECONDS = 5              # duração no modo "push"

# --- VAD (detecção de voz para escuta contínua, sem ENTER) ---
VAD_FRAME_MS = 30               # tamanho do frame analisado
VAD_THRESHOLD = 0.015           # RMS acima disso = fala (ajuste se mic for sensível)
VAD_SILENCE_MS = 800            # silêncio contínuo para considerar fala encerrada
VAD_MAX_SECONDS = 15            # corte de segurança por fala

# --- Modo autônomo: reage à tela sozinho quando ninguém fala ---
AUTO_COMMENT = True              # True = reage sem precisar de voz
AUTO_IDLE_SECONDS = 6            # silêncio antes de reagir por conta própria

# --- Imagem (latência) ---
SCREENSHOT_MAX_WIDTH = 960       # menor = mais rápido pro modelo
SCREENSHOT_JPEG_QUALITY = 70     # JPEG é bem mais leve que PNG p/ screenshots

# --- TTS (edge-tts) ---
# Vozes BR boas: pt-BR-FranciscaNeural (fem) | pt-BR-ThalitaNeural (fem) |
# pt-BR-AntonioNeural (masc). Liste todas com: edge-tts --list-voices
TTS_VOICE = "pt-BR-FranciscaNeural"
TTS_RATE = "+12%"               # +12% = fala mais animada/acelerada

# --- Avatar (janela com lip-sync para capturar no OBS) ---
AVATAR_ENABLED = True            # False = roda só no terminal, sem janela
AVATAR_WIDTH = 480
AVATAR_HEIGHT = 560
AVATAR_FPS = 30
AVATAR_BG = (0, 255, 0)          # fundo verde = chroma key fácil no OBS
AVATAR_SHOW_CAPTION = True       # mostra legenda do que ela tá falando
AVATAR_MOUTH_SENSITIVITY = 1.6   # quanto a boca abre em relação ao volume

# --- Modo de operação ---
# "loop" = escuta contínua por voz, sem ENTER | "push" = pressione ENTER para falar
MODE = "loop"
