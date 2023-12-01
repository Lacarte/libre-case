import sys
import os
import configparser
from datetime import datetime
import logging


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Use the directory of the script file as the base path
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def setup_logging():
    logs_path = create_directory("logs")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(logs_path, f"log-{datetime.now().strftime('%Y-%m-%d')}.log"), mode="w", encoding='utf-8'),
            logging.StreamHandler(),
        ],
    )



def create_directory(dir_name):
    try:
        path = resource_path(dir_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
    except Exception as e:
        logging.error(f"Error creating '{dir_name}' directory: {e}")
        sys.exit(1)



def get_folder_path_from_config():
    config = configparser.ConfigParser()
    config_path = resource_path("config.ini")
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.ini file not found.")

    config.read(config_path)
    return config.get('Settings', 'folder_path')


