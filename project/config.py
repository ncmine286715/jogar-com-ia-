# config.py — configurações centrais do assistente

# --- Ollama ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5vl"
OLLAMA_TIMEOUT = 120  # segundos

# Prompt de sistema: força respostas curtas e em português
SYSTEM_PROMPT = (
    "Você é um assistente útil que vê a tela do usuário. "
    "Responda em português, de forma curta e direta (1-3 frases)."
)

# --- STT (faster-whisper) ---
WHISPER_MODEL = "small"        # tiny | base | small | medium | large-v3
WHISPER_DEVICE = "cpu"          # "cuda" se tiver GPU NVIDIA
WHISPER_COMPUTE = "int8"        # int8 (cpu) | float16 (gpu)
WHISPER_LANGUAGE = "pt"

# --- Áudio (gravação) ---
SAMPLE_RATE = 16000             # Whisper espera 16 kHz
CHANNELS = 1
RECORD_SECONDS = 5              # duração no modo loop contínuo

# --- TTS (edge-tts) ---
TTS_VOICE = "pt-BR-AntonioNeural"
TTS_RATE = "+0%"

# --- Modo de operação ---
# "push" = pressione ENTER para falar | "loop" = grava automaticamente em ciclo
MODE = "push"
