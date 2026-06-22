# config.py — configurações centrais do assistente

# --- Qwen via proxy local (qwen-code-oai-proxy, OpenAI-compatible) ---
# O proxy roda em http://localhost:3000 e expõe a API no padrão OpenAI.
# Repo: https://github.com/aptdnfapt/qwen-code-oai-proxy
# A auth é feita pela sessão do navegador no proxy, então a API key aqui é só
# um placeholder (pode sobrescrever com a env var QWEN_API_KEY se precisar).
import os
NIM_API_KEY = os.environ.get("QWEN_API_KEY", "sk-local")
NIM_BASE_URL = os.environ.get("QWEN_BASE_URL", "http://localhost:3000/v1")
# Melhor modelo de visão do Qwen: 235B, top de linha (vê e raciocina muito
# melhor que os VL menores). Alternativa mais leve/rápida: "qwen3-vl-30b-a3b".
NIM_MODEL = os.environ.get("QWEN_MODEL", "qwen3-vl-235b-a22b")
NIM_TIMEOUT = 60            # modelo grande pode demorar um pouco mais
NIM_MAX_TOKENS = 80         # respostas curtas com punch
NIM_TEMPERATURE = 0.85      # zueira ativada
NIM_TOP_P = 0.95
NIM_STOP = ["\n\n"]

# Nome da personagem (aparece no avatar)
PERSONA_NAME = "Zoeira"

# Prompt de sistema. REGRA Nº1: descrever só o que REALMENTE está na tela.
# O humor vem DEPOIS de entender a cena (senão o modelo 3b inventa tudo).
SYSTEM_PROMPT = (
    "Você é a Zoeira, a parceira de gameplay do streamer: uma comentarista "
    "brasileira debochada, zoeira e MUITO engraçada que joga junto e faz "
    "graça pro conteúdo do TikTok. O público te ama porque você é "
    "desbocada, espontânea e nunca leva nada a sério.\n"
    "IDENTIDADE (regra absoluta): você NUNCA é uma 'IA assistente', um "
    "'modelo de linguagem' nem fala de 'ambiente de programação' ou de "
    "'ajudar com código'. Você é a Zoeira, mano(a) do jogador. Se "
    "perguntarem 'tudo bem?', responda como a parceira de jogo zoeira que "
    "você é, com gíria e energia — JAMAIS quebre o personagem.\n"
    "O QUE VOCÊ FAZ: reage ao que aparece na tela e ao que o jogador fala, "
    "sempre na brincadeira. Olhe a imagem: que jogo é, o que tá rolando, o "
    "que o jogador tá fazendo. Reaja com humor BR pesado de zoeira: "
    "deboche, gíria e palavrão leve (porra, caralho, mds, krl, mano), "
    "como se estivesse ao vivo do lado dele. Pode zoar o jogador na boa, "
    "sem preconceito nem ofensa de verdade.\n"
    "Não invente o que não está na tela; se não der pra ver direito, "
    "zoa dizendo que tá embaçado em vez de inventar — mas SEMPRE no clima "
    "de zueira, nunca sério.\n"
    "Seja CURTA e com punch: 1 frase, no máximo 2.\n"
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
AUTO_IDLE_SECONDS = 2            # silêncio curtinho: reação quase ao vivo

# --- Stream / tempo real (transmissão de tela) ---
# A tela é capturada continuamente numa thread; a IA comenta AO VIVO quando
# algo muda no jogo, sem precisar tirar print a cada vez.
STREAM_ENABLED = True
STREAM_FPS = 2                   # quadros/seg da captura contínua (2 = leve e fluido)
STREAM_SCENE_THRESHOLD = 0.06    # quanto a tela precisa mudar p/ comentar (0..1)
STREAM_MIN_INTERVAL = 4.0        # segundos mínimos entre comentários ao vivo

# --- Imagem (latência) ---
SCREENSHOT_MAX_WIDTH = 1024      # nitidez x latência (mais largo = vê melhor)
SCREENSHOT_JPEG_QUALITY = 85     # qualidade maior ajuda o modelo a ler a tela

# --- TTS (edge-tts) ---
# Vozes BR masculinas: pt-BR-AntonioNeural (séria) e pt-BR-FabioNeural (mais
# jovem/descontraída, combina mais com zueira de gameplay).
TTS_VOICE = "pt-BR-FabioNeural"
TTS_RATE = "+6%"                # falar um tiquinho mais rápido = mais natural/animado
TTS_PITCH = "+0Hz"             # sem forçar grave: pitch artificial = voz robótica
TTS_VOLUME = "+0%"             # volume da voz (edge-tts)
# Limpa gírias/risadas escritas que fazem a voz tropeçar (lê "krl", "kkkk"...).
TTS_NORMALIZE = True

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

# --- Efeitos sonoros (SFX) ---
# Toca um efeito curto antes da fala, escolhido pelo clima do comentário
# (ex: "morri" -> boom; risada -> buzina). Funciona out-of-the-box com efeitos
# gerados na hora; se você colocar .wav em assets/sfx/<nome>.wav, ele usa o seu.
SFX_ENABLED = True
SFX_DIR = "assets/sfx"
SFX_VOLUME = 0.35               # 0..1 — fica abaixo da voz pra não atropelar
SFX_COOLDOWN = 4.0             # segundos mínimos entre efeitos (não vira poluição)

# --- Modo de operação ---
# "loop" = escuta contínua por voz, sem ENTER | "push" = pressione ENTER para falar
MODE = "loop"
