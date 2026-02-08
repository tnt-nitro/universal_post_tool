from pynput import mouse
from universal_post_tool.core.config import load_config, save_config


def record_once(callback):
    """Startet einen Mauslistener, der beim ersten Klick den Callback aufruft."""
    def on_click(x, y, button, pressed):
        if pressed:
            callback(x, y)
            return False

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()


def record_send_position():
    position = {}

    def on_click(x, y, button, pressed):
        if pressed:
            position["chatgpt_send"] = [x, y]
            return False  # Listener stoppen

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    config = load_config()
    config["chatgpt_send"] = position.get("chatgpt_send")
    save_config(config)

    return config["chatgpt_send"]
