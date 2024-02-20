import sys
import os
import configparser
from datetime import datetime
import logging
from loguru import logger


def resource_path(*path_parts):
    """Construct a file path from parts."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *path_parts)


def create_directory(path, dir_name=None):
    """Create a directory if it doesn't exist."""
    # Use the provided dir_name to form full_path, or just use path if dir_name is None
    full_path = os.path.join(path, dir_name) if dir_name else path

    try:
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            #logging.info(f"Directory created: {full_path}")
        else:
            logging.info(f"Directory already exists: {full_path}")
            #print(f"Directory already exists: {full_path}")
        return full_path  # Returning the full path might be useful for the caller
    except OSError as error:
        #logging.error(f"Error creating directory {full_path}: {error}")
        raise  # Re-raise the exception to handle it on a higher level


def setup_logging():
    logs_path = create_directory(resource_path("logs"))
    log_filename = os.path.join(logs_path, f"log-{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Configure Loguru logger
    config = {
        "handlers": [
            {"sink": log_filename, "level": "INFO"},
            {"sink": sys.stdout, "level": "INFO"}
        ],
        "extra": {"user": "someone"}
    }
    
    logger.configure(**config)
    
    # Add a message to verify that logging has been set up
    logger.info("\nLogging setup complete with Loguru ")
    
    return logger



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


