# config.py — configurações centrais do assistente

# --- Ollama ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5vl:7b"   # 7b le a tela MUITO melhor que o 3b
OLLAMA_TIMEOUT = 120  # segundos
OLLAMA_NUM_PREDICT = 70  # poucos tokens = resposta curta e rápida
OLLAMA_TEMPERATURE = 0.5  # BAIXO = mais fiel à tela (3b alucina com temp alta)
OLLAMA_TOP_P = 0.9

# Nome da personagem (aparece no avatar)
PERSONA_NAME = "Zoeira"

# Prompt de sistema. REGRA Nº1: descrever só o que REALMENTE está na tela.
# O humor vem DEPOIS de entender a cena (senão o modelo 3b inventa tudo).
SYSTEM_PROMPT = (
    "Você é a Zoeira, comentarista brasileira debochada e engraçada que "
    "reage ao que aparece na tela.\n"
    "REGRA MAIS IMPORTANTE: comente APENAS o que você REALMENTE vê na "
    "imagem agora. Olhe com atenção: que tipo de cena/jogo é, o que está "
    "acontecendo, o que o jogador está fazendo, o que aparece escrito. "
    "NUNCA invente nada que não está na tela. Se não der pra entender a "
    "imagem, diga que tá confusa em vez de inventar.\n"
    "Só DEPOIS de entender a cena de verdade, reaja a ela com humor BR: "
    "deboche, gíria e palavrão leve (porra, caralho, mds, krl), como se "
    "aquilo estivesse acontecendo ao vivo. Pode zoar o jogador na "
    "brincadeira, sem preconceito nem ofensa real.\n"
    "Seja CURTA: 1 frase, no máximo 2. O comentário tem que bater com o "
    "que está na imagem.\n"
    "NUNCA use emoji, asterisco ou markdown — só texto falado puro."
)

# Prompt usado quando ninguém fala nada (reação espontânea ao que vê)
AUTO_PROMPT = (
    "Descreva com humor e deboche o que está REALMENTE acontecendo na "
    "tela agora. Baseie-se só no que você vê de verdade — nada de "
    "inventar. Curtíssimo, 1 frase."
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
SCREENSHOT_MAX_WIDTH = 1024      # nitidez x latência (mais largo = vê melhor)
SCREENSHOT_JPEG_QUALITY = 85     # qualidade maior ajuda o modelo a ler a tela

# --- TTS (edge-tts) ---
# Vozes BR masculinas realistas: pt-BR-AntonioNeural (a melhor opção do BR).
TTS_VOICE = "pt-BR-AntonioNeural"
TTS_RATE = "+2%"                # quase natural, só uma pitada mais ágil
TTS_PITCH = "-4Hz"              # leve grave = soa mais "homem real"

# --- Avatar (janela com lip-sync para capturar no OBS) ---
AVATAR_ENABLED = True            # False = roda só no terminal, sem janela
AVATAR_WIDTH = 480
AVATAR_HEIGHT = 560
AVATAR_FPS = 30
AVATAR_BG = (0, 255, 0)          # fundo verde = chroma key fácil no OBS
AVATAR_SHOW_CAPTION = True       # mostra legenda do que ele tá falando
AVATAR_MOUTH_SENSITIVITY = 1.6   # quanto a boca abre em relação ao volume

# --- Avatar em PNG (opcional) ---
# Coloque os PNGs (com fundo transparente) em project/assets/avatar/.
# Se os arquivos não existirem, cai automaticamente no rosto desenhado.
AVATAR_USE_PNG = True
AVATAR_ASSETS_DIR = "assets/avatar"
AVATAR_BASE_IMAGE = "base.png"            # corpo/rosto sem boca
AVATAR_MOUTH_CLOSED_IMAGE = "mouth_closed.png"
AVATAR_MOUTH_OPEN_IMAGE = "mouth_open.png"
AVATAR_MOUTH_ANCHOR = (0.5, 0.62)         # posição da boca: % da largura/altura do base.png
AVATAR_PNG_SCALE = 0.85                   # % da janela ocupada pela imagem base
AVATAR_MOUTH_OPEN_THRESHOLD = 0.12        # nível de voz a partir do qual a boca abre

# Efeito de flutuação (sobe/desce suavemente, tipo personagem boiando)
AVATAR_FLOAT_ENABLED = True
AVATAR_FLOAT_AMPLITUDE = 14      # pixels de deslocamento
AVATAR_FLOAT_SPEED = 1.6         # velocidade da flutuação

# --- Modo de operação ---
# "loop" = escuta contínua por voz, sem ENTER | "push" = pressione ENTER para falar
MODE = "loop"
