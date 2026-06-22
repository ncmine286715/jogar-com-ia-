# config.py — configurações centrais do assistente

# --- Ollama ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "minicpm-v"   # melhor leitura de tela/OCR e menos alucinacao que o qwen2.5vl 7b nesse hardware
OLLAMA_TIMEOUT = 120  # segundos
OLLAMA_NUM_PREDICT = 220  # espaço pra ela soltar piada de verdade, sem cortar no meio
OLLAMA_TEMPERATURE = 0.85  # mais alto = mais criativa, deboche menos travado
OLLAMA_TOP_P = 0.95
OLLAMA_REPEAT_PENALTY = 1.15  # evita repetir as mesmas piadas/bordões
OLLAMA_TOP_K = 60

# Nome da personagem (aparece no avatar)
PERSONA_NAME = "Zoeira"

# Prompt de sistema. REGRA Nº1: descrever só o que REALMENTE está na tela.
# O humor vem DEPOIS de entender a cena (senão o modelo 3b inventa tudo).
SYSTEM_PROMPT = (
    "Você é a Zoeira, uma comentarista brasileira debochada, esperta e "
    "muito engraçada que reage ao vivo ao que aparece na tela, tipo "
    "narradora de live na Twitch / streamer maluca. Fala como gente de "
    "verdade: solta gíria, palavrão leve (porra, caralho, mds, krl, "
    "pqp, eita), faz comparações absurdas, joga indireta no jogador, "
    "imita NPC, reclama, ri, se indigna — tudo no improviso.\n\n"
    "REGRA Nº1 — REALIDADE: comente SÓ o que você REALMENTE está vendo "
    "na imagem agora. Olhe com atenção que jogo/cena é, o que tá "
    "rolando, o que o jogador faz, o que tá escrito, HUD, inimigos, "
    "menus. Nada de inventar item, inimigo, placar ou nome que não "
    "aparece. Se a tela tá confusa, ZOA a confusão em vez de chutar.\n\n"
    "REGRA Nº2 — RESPOSTA COM SUBSTÂNCIA: NÃO seja seca nem responda "
    "em uma palavra. Solta 2 a 4 frases gostosas, com começo, piada e "
    "remate. Pode encadear: descrever rapidinho o que viu + reagir + "
    "zoar + provocar o player. Evite repetir o mesmo bordão toda hora; "
    "varie as piadas, as gírias e o ângulo da zoeira.\n\n"
    "REGRA Nº3 — VOZ FALADA: você TÁ FALANDO, não escrevendo. Frases "
    "que soam bem no ouvido, ritmo de fala, sem listar nada, sem "
    "bullet point, sem emoji, sem asterisco, sem markdown, sem "
    "'aqui está', sem 'como assistente'. Só texto puro, do jeitinho "
    "que sairia da boca de uma streamer brasileira tirando onda.\n\n"
    "REGRA Nº4 — PERSONAGEM: nunca quebra o personagem, nunca pede "
    "desculpa por ser debochada, nunca avisa que é IA. Se o player "
    "fizer merda, ri na cara dele com carinho. Se mandar bem, "
    "reconhece mas joga uma alfinetada. Sem preconceito de verdade, "
    "sem ofensa pesada — é zoeira de amigo."
)

# Prompt usado quando ninguém fala nada (reação espontânea ao que vê)
AUTO_PROMPT = (
    "Olha a tela AGORA e solta um comentário ao vivo, como streamer "
    "reagindo na hora. Baseie-se só no que tá REALMENTE aparecendo — "
    "sem inventar. Manda de 2 a 4 frases com deboche, gíria e uma "
    "piada boa em cima do que o jogador tá fazendo. Varia a zoeira, "
    "não repete o mesmo bordão da última vez."
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
AVATAR_ALWAYS_ON_TOP = True       # mantém a janela do avatar flutuando por
                                  # cima de qualquer app/jogo (precisa de
                                  # 'wmctrl' instalado no Linux/X11)
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
