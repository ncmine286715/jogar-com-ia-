#!/usr/bin/env python3
# main.py — loop principal do assistente multimodal local

import sys

import config
import llm
import screen
import stt
import tts


def respond(prompt_text: str, label: str) -> None:
    """Captura tela, manda pro LLM com o prompt dado e fala a resposta."""
    image_b64 = screen.capture_base64()
    answer = llm.ask(prompt_text, image_b64)
    print(f"🤖 IA ({label}): {answer}")
    tts.speak(answer)


def interact(use_vad: bool) -> None:
    """Um ciclo completo: ouve -> vê -> pergunta -> fala.

    No modo VAD com AUTO_COMMENT ligado, se ninguém falar dentro de
    AUTO_IDLE_SECONDS, comenta a tela por conta própria.
    """
    if use_vad:
        idle = config.AUTO_IDLE_SECONDS if config.AUTO_COMMENT else None
        print("🎤 Ouvindo... (fale quando quiser)")
        user_text = stt.listen_vad(idle_timeout=idle)
    else:
        print("🎤 Gravando...")
        user_text = stt.listen()

    if user_text is None:
        respond(config.AUTO_PROMPT, "espontâneo")
        return

    if not user_text:
        print("   (nada entendido)")
        return
    print(f"👤 Você: {user_text}")
    respond(user_text, "resposta")


def main() -> None:
    print("=== Assistente Multimodal Local (Qwen2.5-VL) ===")
    print(f"Modo: {config.MODE}  |  Ctrl+C para sair\n")
    use_vad = config.MODE != "push"
    try:
        while True:
            if config.MODE == "push":
                cmd = input("ENTER para falar (q + ENTER para sair): ")
                if cmd.strip().lower() == "q":
                    break
            interact(use_vad)
            print("-" * 40)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nEncerrando. Até logo!")
        sys.exit(0)


if __name__ == "__main__":
    main()
