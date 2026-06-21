#!/usr/bin/env python3
# main.py — loop principal do assistente multimodal local

import sys

import config
import llm
import screen
import stt
import tts


def interact() -> None:
    """Um ciclo completo: ouve -> vê -> pergunta -> fala."""
    print("🎤 Gravando...")
    user_text = stt.listen()
    if not user_text:
        print("   (nada entendido)")
        return
    print(f"👤 Você: {user_text}")

    print("🖥️  Capturando tela...")
    image_b64 = screen.capture_base64()

    print("🤖 Pensando...")
    answer = llm.ask(user_text, image_b64)
    print(f"🤖 IA: {answer}")

    tts.speak(answer)


def main() -> None:
    print("=== Assistente Multimodal Local (Qwen2.5-VL) ===")
    print(f"Modo: {config.MODE}  |  Ctrl+C para sair\n")
    try:
        while True:
            if config.MODE == "push":
                cmd = input("ENTER para falar (q + ENTER para sair): ")
                if cmd.strip().lower() == "q":
                    break
            interact()
            print("-" * 40)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nEncerrando. Até logo!")
        sys.exit(0)


if __name__ == "__main__":
    main()
