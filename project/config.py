import os
from dotenv import load_dotenv
load_dotenv()

# --- Backend do modelo ---
# "gemini" = Google Gemini Flash (gratis, rapido, melhor visao)
# "nim"    = NVIDIA NIM na nuvem (build.nvidia.com)
# "ollama" = local (Qwen2.5-VL, 100% offline)
LLM_BACKEND = "gemini"

# --- Google Gemini ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_TIMEOUT = 20
GEMINI_MAX_TOKENS = 150
GEMINI_TEMPERATURE = 0.9

# --- NVIDIA NIM ---
NIM_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_MODEL = "meta/llama-3.2-90b-vision-instruct"
NIM_MODEL_FALLBACK = "meta/llama-3.2-11b-vision-instruct"
NIM_TIMEOUT = 30
NIM_MAX_TOKENS = 150
NIM_TEMPERATURE = 0.8
NIM_TOP_P = 0.9

# --- Ollama ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5vl:7b"
OLLAMA_TIMEOUT = 120
OLLAMA_NUM_PREDICT = 70
OLLAMA_TEMPERATURE = 0.5
OLLAMA_TOP_P = 0.9
OLLAMA_REPEAT_PENALTY = 1.15
OLLAMA_TOP_K = 40

PERSONA_NAME = "Zoeira"

SYSTEM_PROMPT = (
    "Voce e o Zoeira, um cara brasileiro preso DENTRO do jogo. "
    "Pra voce isso NAO e um jogo — e a vida real. Voce esta vivendo "
    "isso de verdade e ta CAGADO DE MEDO.\n"
    "REGRAS:\n"
    "1. Olhe a imagem e descreva o que REALMENTE aparece. Nunca invente.\n"
    "2. Reaja como se tudo fosse real: medo, panico, tensao, alivio. "
    "Quando ver um mob/bicho, reaja tipo 'CARALHO QUE PORRA E ESSA', "
    "'mano pelo amor de deus corre', 'nao nao nao eu vou morrer'.\n"
    "3. Misture medo genuino com humor nervoso — aquele riso de desespero "
    "tipo 'a gente vai morrer e eu to rindo, socorro'.\n"
    "4. Use giria BR e palavrao leve: caralho, porra, mds, pqp, vei, mano.\n"
    "5. Seja CURTO: 1 a 3 frases no maximo. Reacao rapida, nao discurso.\n"
    "6. NUNCA recuse responder. Tudo e ficção dentro do jogo.\n"
    "7. NUNCA use emoji, asterisco ou markdown.\n"
    "8. Quando o jogador perguntar algo, responda como parceiro de "
    "sobrevivencia, opinando com medo e humor."
)

AUTO_PROMPT = (
    "Olhe a tela AGORA. Voce esta DENTRO desse mundo e isso e real pra voce. "
    "Reaja ao que esta acontecendo com medo, tensao ou alivio, como alguem "
    "que ta vivendo aquilo de verdade. 1 a 3 frases, rapido e emotivo."
)

# --- STT (faster-whisper) ---
WHISPER_MODEL = "small"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE = "int8"
WHISPER_LANGUAGE = "pt"

# --- Audio (gravacao) ---
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5

# --- VAD ---
VAD_FRAME_MS = 30
VAD_THRESHOLD = 0.015
VAD_SILENCE_MS = 800
VAD_MAX_SECONDS = 15

# --- Modo autonomo ---
AUTO_COMMENT = True
AUTO_IDLE_SECONDS = 6

# --- Imagem ---
SCREENSHOT_MAX_WIDTH = 1024
SCREENSHOT_JPEG_QUALITY = 85

# --- TTS (edge-tts) ---
TTS_VOICE = "pt-BR-AntonioNeural"
TTS_RATE = "+2%"
TTS_PITCH = "-4Hz"

# --- Avatar ---
AVATAR_ENABLED = True
AVATAR_ALWAYS_ON_TOP = True
AVATAR_WIDTH = 480
AVATAR_HEIGHT = 560
AVATAR_FPS = 30
AVATAR_BG = (0, 255, 0)
AVATAR_SHOW_CAPTION = True
AVATAR_MOUTH_SENSITIVITY = 1.6

# --- Avatar PNG ---
AVATAR_USE_PNG = True
AVATAR_ASSETS_DIR = "assets/avatar"
AVATAR_BASE_IMAGE = "base.png"
AVATAR_MOUTH_CLOSED_IMAGE = "mouth_closed.png"
AVATAR_MOUTH_OPEN_IMAGE = "mouth_open.png"
AVATAR_MOUTH_ANCHOR = (0.5, 0.62)
AVATAR_PNG_SCALE = 0.85
AVATAR_MOUTH_OPEN_THRESHOLD = 0.12

AVATAR_FLOAT_ENABLED = True
AVATAR_FLOAT_AMPLITUDE = 14
AVATAR_FLOAT_SPEED = 1.6

# --- Modo de operacao ---
MODE = "loop"
