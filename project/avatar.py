# avatar.py — rosto animado com lip-sync (pygame). Roda na thread principal.

import math
import os
import random
import time

import config
import state

# Cores
SKIN = (255, 219, 172)
SKIN_DK = (214, 170, 120)
HAIR = (60, 40, 30)
MOUTH = (90, 20, 30)
TONGUE = (220, 90, 110)
WHITE = (255, 255, 255)
PUPIL = (40, 30, 30)
BLUSH = (255, 150, 150)
STATUS_COLORS = {
    "ouvindo": (90, 200, 255),
    "pensando": (255, 200, 60),
    "falando": (120, 255, 120),
    "iniciando": (200, 200, 200),
}


def _wrap(font, text, max_w):
    """Quebra texto em linhas que cabem em max_w pixels."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines[-3:]  # no máximo 3 últimas linhas


def run():
    """Loop de render do avatar. Retorna False se não conseguir abrir janela."""
    try:
        os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        import pygame
    except Exception as e:
        print(f"[AVATAR] pygame indisponível ({e}); rodando sem janela.")
        return False

    try:
        pygame.init()
        W, H = config.AVATAR_WIDTH, config.AVATAR_HEIGHT
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption(config.PERSONA_NAME)
        clock = pygame.time.Clock()
        f_status = pygame.font.SysFont("Arial", 22, bold=True)
        f_cap = pygame.font.SysFont("Arial", 24, bold=True)
    except Exception as e:
        print(f"[AVATAR] não foi possível abrir janela ({e}); sem avatar.")
        return False

    cx, cy = W // 2, int(H * 0.42)
    head_w, head_h = int(W * 0.62), int(H * 0.52)
    next_blink = time.time() + random.uniform(2, 5)
    blink_until = 0.0

    while state.running:
        now = time.time()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                state.running = False

        # Pisca os olhos de vez em quando (dá vida)
        if now > next_blink:
            blink_until = now + 0.12
            next_blink = now + random.uniform(2, 5)
        blinking = now < blink_until

        level = max(0.0, min(1.0, state.mouth_level))
        accent = STATUS_COLORS.get(state.status, (200, 200, 200))

        screen.fill(config.AVATAR_BG)

        # Cabelo (atrás da cabeça)
        pygame.draw.ellipse(
            screen, HAIR,
            (cx - head_w // 2 - 12, cy - head_h // 2 - 22, head_w + 24, head_h + 30),
        )
        # Rosto
        pygame.draw.ellipse(
            screen, SKIN, (cx - head_w // 2, cy - head_h // 2, head_w, head_h)
        )
        pygame.draw.ellipse(
            screen, SKIN_DK,
            (cx - head_w // 2, cy - head_h // 2, head_w, head_h), 3,
        )

        eye_dx = int(head_w * 0.22)
        eye_y = cy - int(head_h * 0.08)
        eye_w, eye_h = int(head_w * 0.20), int(head_h * 0.16)
        # Sobrancelhas sobem quando fala mais alto (expressivo)
        brow = int(level * 10)
        for sx in (-1, 1):
            ex = cx + sx * eye_dx
            if blinking:
                pygame.draw.line(
                    screen, SKIN_DK, (ex - eye_w // 2, eye_y), (ex + eye_w // 2, eye_y), 4
                )
            else:
                pygame.draw.ellipse(
                    screen, WHITE, (ex - eye_w // 2, eye_y - eye_h // 2, eye_w, eye_h)
                )
                pygame.draw.circle(screen, PUPIL, (ex, eye_y + 2), max(4, eye_h // 4))
            pygame.draw.line(
                screen, HAIR,
                (ex - eye_w // 2, eye_y - eye_h // 2 - 8 - brow),
                (ex + eye_w // 2, eye_y - eye_h // 2 - 12 - brow), 5,
            )

        # Bochechas
        for sx in (-1, 1):
            pygame.draw.circle(
                screen, BLUSH,
                (cx + sx * int(head_w * 0.28), cy + int(head_h * 0.14)), 14
            )

        # Boca com lip-sync: altura cresce com o volume da fala
        mouth_y = cy + int(head_h * 0.27)
        mouth_w = int(head_w * 0.42)
        open_h = int(6 + level * config.AVATAR_MOUTH_SENSITIVITY * 64)
        if open_h <= 8:  # boca fechada = sorriso fino
            pygame.draw.arc(
                screen, MOUTH,
                (cx - mouth_w // 2, mouth_y - 14, mouth_w, 30),
                math.pi, 2 * math.pi, 6,
            )
        else:
            rect = (cx - mouth_w // 2, mouth_y - open_h // 2, mouth_w, open_h)
            pygame.draw.ellipse(screen, MOUTH, rect)
            if open_h > 26:  # língua quando escancara
                t_h = open_h // 3
                pygame.draw.ellipse(
                    screen, TONGUE,
                    (cx - mouth_w // 4, mouth_y + open_h // 6, mouth_w // 2, t_h),
                )

        # Status (topo)
        dot = 12
        pygame.draw.circle(screen, accent, (24, 26), dot)
        screen.blit(
            f_status.render(state.status.upper(), True, (30, 30, 30)), (42, 14)
        )

        # Legenda (rodapé) — ótimo pra clipe
        if config.AVATAR_SHOW_CAPTION and state.caption:
            lines = _wrap(f_cap, state.caption, W - 30)
            ty = H - 18 - len(lines) * 28
            for ln in lines:
                surf = f_cap.render(ln, True, (20, 20, 20))
                bg = surf.get_rect(centerx=W // 2, y=ty).inflate(16, 6)
                pygame.draw.rect(screen, (255, 255, 255), bg, border_radius=8)
                screen.blit(surf, surf.get_rect(centerx=W // 2, y=ty))
                ty += 28

        pygame.display.flip()
        clock.tick(config.AVATAR_FPS)

    pygame.quit()
    return True
