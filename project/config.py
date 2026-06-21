# config.py — configurações centrais do assistente

# --- Ollama ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5vl:3b"
OLLAMA_TIMEOUT = 120  # segundos
OLLAMA_NUM_PREDICT = 60  # poucos tokens = resposta curta e rápida
OLLAMA_TEMPERATURE = 0.9  # mais solto/espontâneo (persona zoeira)

# Prompt de sistema: persona zueira BR, respostas curtas (latência)
SYSTEM_PROMPT = (
    "Você é o parceiro zoeiro brasileiro que tá vendo a tela/jogo do "
    "usuário e comenta junto. Fale igual um amigo no Discord: gíria, "
    "deboche, pode soltar um palavrão leve (porra, caralho, mds, mano) "
    "pra dar ênfase, sem ser robótico nem formal. É tudo brincadeira "
    "entre parceiros — sem ofender de verdade, sem preconceito, sem "
    "atacar ninguém pessoalmente. Respostas BEM curtas (1 frase, no "
    "máximo 2), direto na lata e engraçado."
)

# Prompt usado quando ninguém fala nada (comentário espontâneo sobre a tela)
AUTO_PROMPT = (
    "Ninguém te perguntou nada. Olha a tela/jogo agora e solta um "
    "comentário espontâneo, zoeiro e curto sobre o que tá rolando."
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

# --- Modo autônomo: comenta a tela sozinho quando ninguém fala ---
AUTO_COMMENT = True              # True = comenta sem precisar de voz
AUTO_IDLE_SECONDS = 8            # silêncio antes de comentar por conta própria

# --- Imagem (latência) ---
SCREENSHOT_MAX_WIDTH = 960       # menor = mais rápido pro modelo
SCREENSHOT_JPEG_QUALITY = 70     # JPEG é bem mais leve que PNG p/ screenshots

# --- TTS (edge-tts) ---
TTS_VOICE = "pt-BR-AntonioNeural"
TTS_RATE = "+0%"

# --- Modo de operação ---
# "loop" = escuta contínua por voz, sem ENTER | "push" = pressione ENTER para falar
MODE = "loop"
