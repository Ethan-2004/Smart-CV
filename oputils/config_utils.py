import os
import json

CONFIG_PATH = os.path.join("config", "config.json")  # 或直接用 "config.json"

DEFAULT_CONFIG = {
    "model_config": {
        "model_name": "default-model",
        "api_url": "https://api.example.com/v1",
        "api_key": ""
    }
}

def ensure_config_exists():
    """确保配置文件存在"""
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

def load_config():
    ensure_config_exists()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_model_config():
    config = load_config()
    return config.get("model_config", {})

def update_model_config(model_name, api_url, api_key):
    config = load_config()
    config["model_config"] = {
        "model_name": model_name,
        "api_url": api_url,
        "api_key": api_key
    }
    save_config(config)
