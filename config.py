import copy
import json
import os
from loguru import logger
from utils import resource_path

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "snippets": {
        "max_snippets": 10,
        "max_content_length": 1400,
    },
}

_config = None


def save_config(config):
    try:
        with open(resource_path(CONFIG_FILE), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except OSError as e:
        logger.warning(f"Could not write {CONFIG_FILE}: {e}")


def load_config():
    """Read config.json, falling back to defaults for missing or invalid values."""
    config = copy.deepcopy(DEFAULT_CONFIG)
    config_path = resource_path(CONFIG_FILE)

    if not os.path.exists(config_path):
        save_config(config)
        return config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Could not read {CONFIG_FILE}, using defaults: {e}")
        return config

    if not isinstance(user_config, dict):
        logger.warning(f"{CONFIG_FILE} must contain a JSON object, using defaults")
        return config

    for section, defaults in DEFAULT_CONFIG.items():
        user_section = user_config.get(section, {})
        if not isinstance(user_section, dict):
            logger.warning(f"Section '{section}' in {CONFIG_FILE} must be an object, using defaults")
            continue

        for key, default in defaults.items():
            if key not in user_section:
                continue
            value = user_section[key]
            # type() check rejects bools for int settings (bool is a subclass of int)
            if type(value) is not type(default) or (isinstance(value, int) and value <= 0):
                logger.warning(f"Invalid value for '{section}.{key}' in {CONFIG_FILE}: {value!r}, using {default}")
                continue
            config[section][key] = value

    return config


def get_setting(section, key):
    global _config
    if _config is None:
        _config = load_config()
    return _config[section][key]
