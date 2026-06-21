# state.py — estado compartilhado entre a thread do assistente e o avatar

# Abertura da boca: 0.0 (fechada) a 1.0 (escancarada). Atualizado pelo TTS
# durante a fala e lido pelo avatar a cada frame.
mouth_level = 0.0

# Status atual, mostrado no avatar: ouvindo | pensando | falando
status = "iniciando"

# Última fala da IA (legenda no avatar / overlay de stream)
caption = ""

# Flag global: vira False quando a janela é fechada, encerra o programa.
running = True
