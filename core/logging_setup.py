import yaml
import logging.config

def setup_logging():
    with open("config/logging.yaml", "r") as file:
        logging.config.dictConfig(yaml.safe_load(file)) # đọc file yaml và chuyển sang python dictionary