from pathlib import Path
import logging

shelf_path = "data"
shelf_name = "shelf"
shelf = shelf_path + "/" + shelf_name

def create_directory(filepath):
    if not Path(filepath).is_dir():
        logging.info(f"Creating shelf directory {filepath}")
        Path(filepath).mkdir(parents=True, exist_ok=True)
