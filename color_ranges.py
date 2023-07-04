"""
Определение закрашенных областей
"""
import configparser

from PIL import Image

CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

IMG_DIR = config["DEFAULT"]["img_dir"]
MAX_SAMPLE_SIZE = int(config["DEFAULT"]["max_sample_size"])


print("Done.")
