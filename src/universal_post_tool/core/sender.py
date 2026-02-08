import pyautogui
import time
from universal_post_tool.core.config import load_config


def send_to_chatgpt(text: str):
    config = load_config()
    pos = config.get("chatgpt_input")
    if not pos:
        raise RuntimeError("Keine Eingabeposition gespeichert")

    input_x, input_y = pos

    # Maus zum Eingabefeld bewegen
    pyautogui.moveTo(input_x, input_y, duration=0.2)
    pyautogui.click()
    time.sleep(0.4)  # Fokus sicherstellen

    # Sicherheit: Feld nochmal aktivieren
    pyautogui.click()
    time.sleep(0.3)

    # Einfügen
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)  # warten bis Text wirklich drin ist

    # Absenden
    pyautogui.press("enter")
