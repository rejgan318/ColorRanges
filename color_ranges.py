"""
Определение закрашенных областей
"""
import configparser
from pathlib import Path

from PIL import Image
import numpy as np

CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

IMG_DIR = config["DEFAULT"]["img_dir"]
MAX_SAMPLE_SIZE = int(config["DEFAULT"]["max_sample_size"])
img_name = config["DEFAULT"]["img_name"]


def unpack_rgb(packed:  int) -> tuple[int, int, int]:
    rgb = ((packed >> 16) & 0xff,
           (packed >> 8) & 0xff,
           packed & 0xff)
    return rgb


def pack_rgb(rgb:  tuple[int, int, int]) -> int:
    return rgb[0] << 16 | rgb[1] << 8 | rgb[2]


def background_color(image) -> tuple[int, int, int]:
    """
    Возвращает цвет фона изображения. Определяется как наиболее часто встречающийся
    :param image: изображение
    :return: цвет фона изображения
    """
    unique, counts = np.unique(image, return_counts=True)
    return unpack_rgb(unique[counts.argmax()])


def total_colors(img: Image) -> set[tuple[int, int, int]]:
    """
    Возвращает количество цветов в изображении
    """
    total_color = set()
    for x in range(img.width):
        for y in range(img.height):
            total_color.add(img.getpixel((x, y)))

    return total_color


img = Image.open(Path(IMG_DIR) / img_name)
# print(f"{img.format=}\n{img.size=}\n{img.mode=}\n{img.info=}\n{img.filename=}\n{img.format_description=}\n{img.palette=}")
# print(f"{len(total_colors(img))=}")

rgb = np.array(img).astype(np.uint32).reshape((-1, 3))
rgb = (rgb[:, 0] << 16 |
       rgb[:, 1] << 8 |
       rgb[:, 2])

bg_color = background_color(rgb)
print(f"Цвет фона: {bg_color}, В запакованном виде {pack_rgb(bg_color)}")
print("Done.")
