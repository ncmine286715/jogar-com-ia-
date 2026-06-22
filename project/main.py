#!/usr/bin/env python3
# main.py — loop principal do assistente multimodal local.
# Avatar (pygame) roda na thread principal; o assistente roda numa worker.

import threading

import avatar
import config
import llm
import screen
import sfx
import state
import stt
import tts


def respond(prompt_text: str, label: str) -> None:
    """Captura tela, manda pro LLM e fala (com lip-sync no avatar)."""
    state.status = "pensando"
    image_b64 = screen.capture_base64()
    answer = llm.ask(prompt_text, image_b64)
    print(f"[{config.PERSONA_NAME} | {label}] {answer}")
    state.caption = answer
    sfx.play_for(answer)            # efeito sonoro que combina com o clima
    tts.speak(answer)
    state.status = "ouvindo"


def cycle(use_vad: bool) -> None:
    """Um ciclo: ouve -> vê -> reage -> fala (ou reage sozinha se ninguém fala)."""
    if use_vad:
        state.status = "ouvindo"
        idle = config.AUTO_IDLE_SECONDS if config.AUTO_COMMENT else None
        user_text = stt.listen_vad(idle_timeout=idle)
    else:
        state.status = "ouvindo"
        user_text = stt.listen()

    if user_text is None:               # ninguém falou -> reage por conta própria
        respond(config.AUTO_PROMPT, "espontâneo")
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
    state.running = False


def main() -> None:
    print(f"=== {config.PERSONA_NAME} — Assistente Multimodal Local ===")
    print(f"Modo: {config.MODE} | Avatar: {config.AVATAR_ENABLED} | Ctrl+C p/ sair\n")
    use_vad = config.MODE != "push"

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
