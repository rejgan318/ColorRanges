"""
Определение закрашенных областей
"""
import configparser
from pathlib import Path

import colorama as co
from PIL import Image
import numpy as np

from print_ascii import make_ascii_picture, total_colors, get_background_color, pack_rgb, back_rgb

print(f"{__file__}")

CONFIG_FILE = "config.ini"
CONFIG_FILE = CONFIG_FILE if Path(CONFIG_FILE).exists() else Path(__file__).parent / CONFIG_FILE

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

IMG_DIR = config["DEFAULT"]["img_dir"]
IMG_DIR = IMG_DIR if Path(IMG_DIR).exists() and Path(IMG_DIR).is_dir() else Path(__file__).parent / IMG_DIR

MIN_SAMPLE_SIZE = int(config["DEFAULT"].get("min_sample_size", "1000"))
img_name = config["DEFAULT"]["img_name"]
assert (Path(IMG_DIR) / img_name).exists(), f"Файл {img_name} не найден"

co.just_fix_windows_console()

img = Image.open(Path(IMG_DIR) / img_name)
colors = total_colors(img)
print(make_ascii_picture(img))
bg_color = get_background_color(img)
print(f"Всего цветов : {len(colors)} " + ''.join([back_rgb(*bg) + "  " for bg in colors]) + co.Back.RESET)
print(f"Цвет фона    : {back_rgb(*bg_color)}  {co.Back.RESET} "
      f"{bg_color}, #{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}, {pack_rgb(bg_color)}")

