import json
from pathlib import Path

CONFIG_PATH = Path("config.json")


def load_config():
    if not CONFIG_PATH.exists():
        return {"chatgpt_input": None}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
