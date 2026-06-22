#!/usr/bin/env python3
# main.py — loop principal do assistente multimodal local.
# Avatar (pygame) roda na thread principal; o assistente roda numa worker.

import threading
import time
import traceback

import avatar
import config
import llm
import screen
import sfx
import state
import stt
import tts


_last_live = 0.0  # quando saiu o último comentário "ao vivo" (controle de ritmo)


def respond(prompt_text: str, label: str) -> None:
    """Vê o frame mais recente do stream, manda pro LLM e fala."""
    state.status = "pensando"
    image_b64 = screen.latest_base64()        # frame ao vivo, latência baixa
    answer = llm.ask(prompt_text, image_b64)
    print(f"[{config.PERSONA_NAME} | {label}] {answer}")
    state.caption = answer
    sfx.play_for(answer)            # efeito sonoro que combina com o clima
    tts.speak(answer)
    screen.mark_scene()             # zera o detector de mudança após comentar
    state.status = "ouvindo"


def cycle(use_vad: bool) -> None:
    """Um ciclo: ouve -> vê -> reage. Se ninguém fala, comenta AO VIVO quando
    a tela muda (reação a eventos do jogo em tempo real)."""
    global _last_live
    if use_vad:
        state.status = "ouvindo"
        idle = config.AUTO_IDLE_SECONDS if config.AUTO_COMMENT else None
        user_text = stt.listen_vad(idle_timeout=idle)
    else:
        state.status = "ouvindo"
        user_text = stt.listen()

    if user_text is None:               # ninguém falou
        if not config.AUTO_COMMENT:
            return
        # Só comenta ao vivo se a tela mudou o bastante E respeitou o ritmo.
        changed = screen.scene_change() >= config.STREAM_SCENE_THRESHOLD
        ready = (time.time() - _last_live) >= config.STREAM_MIN_INTERVAL
        if changed and ready:
            _last_live = time.time()
            respond(config.AUTO_PROMPT, "ao vivo")
        return
    if not user_text:                   # falhou transcrição / vazio
        return
    print(f"[Você] {user_text}")
    respond(user_text, "resposta")


def worker(use_vad: bool) -> None:
    """Loop do assistente (roda em thread separada quando há avatar)."""
    while state.running:
        try:
            if config.MODE == "push" and not config.AVATAR_ENABLED:
                cmd = input("ENTER para falar (q + ENTER para sair): ")
                if cmd.strip().lower() == "q":
                    state.running = False
                    break
            cycle(use_vad)
        except Exception as e:
            print(f"[LOOP] erro: {e}")
            traceback.print_exc()
    state.running = False


def main() -> None:
    print(f"=== {config.PERSONA_NAME} — Assistente Multimodal Local ===")
    print(f"Modo: {config.MODE} | Avatar: {config.AVATAR_ENABLED} | Ctrl+C p/ sair\n")
    use_vad = config.MODE != "push"

    screen.start_stream()           # captura de tela contínua (tempo real)

    try:
        if config.AVATAR_ENABLED:
            t = threading.Thread(target=worker, args=(use_vad,), daemon=True)
            t.start()
            if avatar.run():            # bloqueia até fechar a janela
                state.running = False   # janela fechada -> encerra a worker
            else:
                t.join()                # sem janela: mantém só a worker viva
        else:
            worker(use_vad)
    except KeyboardInterrupt:
        pass
    finally:
        state.running = False
        print("\nEncerrando. Falou!")


if __name__ == "__main__":
    main()
