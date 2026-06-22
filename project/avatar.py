# avatar.py — avatar com lip-sync (pygame). Roda na thread principal.
# Suporta avatar em PNG (assets/avatar/*.png) com efeito de flutuação;
# se os PNGs não existirem, cai automaticamente no rosto desenhado.

import math
import os
import platform
import random
import shutil
import subprocess
import time

import config
import state


def _set_always_on_top(window_title: str) -> None:
    """Tenta fixar a janela do avatar por cima de qualquer outro app.
    Best-effort: cada SO/servidor grafico tem sua propria API e o pygame
    nao expoe isso direto, entao usamos a ferramenta nativa disponivel."""
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes

            hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
            if hwnd:
                HWND_TOPMOST = -1
                SWP_NOMOVE, SWP_NOSIZE = 0x0002, 0x0001
                ctypes.windll.user32.SetWindowPos(
                    hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
                )
            return

        if system == "Linux":
            # Wayland nao deixa apps fixarem "always on top" por fora
            # (limitacao do protocolo, nao do programa). X11 (incluindo
            # XWayland) aceita via wmctrl/xdotool.
            if shutil.which("wmctrl"):
                subprocess.run(
                    ["wmctrl", "-r", window_title, "-b", "add,above"],
                    check=False, capture_output=True,
                )
            elif shutil.which("xdotool"):
                subprocess.run(
                    ["xdotool", "search", "--name", window_title,
                     "windowstate", "--above", "add"],
                    check=False, capture_output=True,
                )
            else:
                print(
                    "[AVATAR] instale 'wmctrl' (sudo apt install wmctrl) "
                    "pra fixar a janela por cima de outros apps."
                )
            return

        if system == "Darwin":
            print("[AVATAR] always-on-top automatico nao suportado no macOS; "
                  "fixe manualmente ou use o app Yoink/AlwaysOnTop.")
    except Exception as e:
        print(f"[AVATAR] nao consegui fixar janela por cima ({e}).")

# Cores (modo desenhado / fallback)
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


def _float_offset(now: float) -> int:
    if not config.AVATAR_FLOAT_ENABLED:
        return 0
    return int(math.sin(now * config.AVATAR_FLOAT_SPEED) * config.AVATAR_FLOAT_AMPLITUDE)


def _load_png_assets(pygame, win_w: int, win_h: int):
    """Carrega base.png/mouth_closed.png/mouth_open.png já escalados.
    Retorna None se AVATAR_USE_PNG=False ou o base.png não existir."""
    if not config.AVATAR_USE_PNG:
        return None

    base_path = os.path.join(config.AVATAR_ASSETS_DIR, config.AVATAR_BASE_IMAGE)
    if not os.path.exists(base_path):
        return None

    try:
        base = pygame.image.load(base_path).convert_alpha()
        target_h = int(win_h * config.AVATAR_PNG_SCALE)
        scale = target_h / base.get_height()
        target_w = int(base.get_width() * scale)
        base = pygame.transform.smoothscale(base, (target_w, target_h))

        def _load_optional(name):
            path = os.path.join(config.AVATAR_ASSETS_DIR, name)
            if not os.path.exists(path):
                return None
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(
                img, (int(img.get_width() * scale), int(img.get_height() * scale))
            )

        return {
            "base": base,
            "mouth_closed": _load_optional(config.AVATAR_MOUTH_CLOSED_IMAGE),
            "mouth_open": _load_optional(config.AVATAR_MOUTH_OPEN_IMAGE),
        }
    except Exception as e:
        print(f"[AVATAR] falha ao carregar PNGs ({e}); usando rosto desenhado.")
        return None


def _draw_png(pygame, screen, assets, cx, cy, y_off, level):
    base = assets["base"]
    bx = cx - base.get_width() // 2
    by = cy - base.get_height() // 2 + y_off
    screen.blit(base, (bx, by))

    mouth_img = (
        assets["mouth_open"]
        if level > config.AVATAR_MOUTH_OPEN_THRESHOLD
        else assets["mouth_closed"]
    )
    if mouth_img:
        ax, ay = config.AVATAR_MOUTH_ANCHOR
        mx = bx + int(base.get_width() * ax) - mouth_img.get_width() // 2
        my = by + int(base.get_height() * ay) - mouth_img.get_height() // 2
        screen.blit(mouth_img, (mx, my))


def _draw_procedural(pygame, screen, cx, cy, blinking, level):
    head_w, head_h = int(config.AVATAR_WIDTH * 0.62), int(config.AVATAR_HEIGHT * 0.52)

    pygame.draw.ellipse(
        screen, HAIR,
        (cx - head_w // 2 - 12, cy - head_h // 2 - 22, head_w + 24, head_h + 30),
    )
    pygame.draw.ellipse(screen, SKIN, (cx - head_w // 2, cy - head_h // 2, head_w, head_h))
    pygame.draw.ellipse(
        screen, SKIN_DK, (cx - head_w // 2, cy - head_h // 2, head_w, head_h), 3
    )

    eye_dx = int(head_w * 0.22)
    eye_y = cy - int(head_h * 0.08)
    eye_w, eye_h = int(head_w * 0.20), int(head_h * 0.16)
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

    for sx in (-1, 1):
        pygame.draw.circle(
            screen, BLUSH, (cx + sx * int(head_w * 0.28), cy + int(head_h * 0.14)), 14
        )

    mouth_y = cy + int(head_h * 0.27)
    mouth_w = int(head_w * 0.42)
    open_h = int(6 + level * config.AVATAR_MOUTH_SENSITIVITY * 64)
    if open_h <= 8:
        pygame.draw.arc(
            screen, MOUTH, (cx - mouth_w // 2, mouth_y - 14, mouth_w, 30),
            math.pi, 2 * math.pi, 6,
        )
    else:
        rect = (cx - mouth_w // 2, mouth_y - open_h // 2, mouth_w, open_h)
        pygame.draw.ellipse(screen, MOUTH, rect)
        if open_h > 26:
            t_h = open_h // 3
            pygame.draw.ellipse(
                screen, TONGUE,
                (cx - mouth_w // 4, mouth_y + open_h // 6, mouth_w // 2, t_h),
            )


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

    if config.AVATAR_ALWAYS_ON_TOP:
        time.sleep(0.3)  # da tempo do window manager registrar a janela
        _set_always_on_top(config.PERSONA_NAME)

    png_assets = _load_png_assets(pygame, W, H)
    if png_assets:
        print(f"[AVATAR] usando PNG de {config.AVATAR_ASSETS_DIR}/")
        cx, cy = W // 2, H // 2
    else:
        print("[AVATAR] PNGs não encontrados; usando rosto desenhado.")
        cx, cy = W // 2, int(H * 0.42)

    next_blink = time.time() + random.uniform(2, 5)
    blink_until = 0.0
    next_top_refresh = time.time() + 3.0

    while state.running:
        now = time.time()

        # alguns window managers "esquecem" o always-on-top quando outro
        # app rouba o foco (jogo em fullscreen, por ex.); reforça de tempos
        # em tempos pra garantir que o avatar continue sobreposto.
        if config.AVATAR_ALWAYS_ON_TOP and now > next_top_refresh:
            _set_always_on_top(config.PERSONA_NAME)
            next_top_refresh = now + 3.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                state.running = False

        if now > next_blink:
            blink_until = now + 0.12
            next_blink = now + random.uniform(2, 5)
        blinking = now < blink_until

        level = max(0.0, min(1.0, state.mouth_level))
        accent = STATUS_COLORS.get(state.status, (200, 200, 200))
        y_off = _float_offset(now)

        screen.fill(config.AVATAR_BG)

        if png_assets:
            _draw_png(pygame, screen, png_assets, cx, cy + y_off, 0, level)
        else:
            _draw_procedural(pygame, screen, cx, cy + y_off, blinking, level)

        # Status (topo)
        pygame.draw.circle(screen, accent, (24, 26), 12)
        screen.blit(f_status.render(state.status.upper(), True, (30, 30, 30)), (42, 14))

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
