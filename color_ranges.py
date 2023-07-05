"""
Определение закрашенных областей
"""
import configparser
from pathlib import Path

import colorama as co
from PIL import Image

from print_ascii import make_ascii_picture, total_colors, get_background_color, get_color_from_pixel, pack_rgb, back_rgb

pos = lambda y, x: co.Cursor.POS(x, y)

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
print(co.ansi.clear_screen() + pos(1, 1))

img = Image.open(Path(IMG_DIR) / img_name)
print(make_ascii_picture(img))
colors = total_colors(img)
print(f"Всего цветов : {len(colors)} " + ''.join([back_rgb(*bg) + "  " for bg in colors]) + co.Back.RESET)
bg_color = get_background_color(img)
print(f"Цвет фона    : {back_rgb(*bg_color)}  {co.Back.RESET} "
      f"{bg_color}, #{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}, {pack_rgb(bg_color)}")


def print_char_xy(x: int, y: int, char: str, ascii: str):
    print(pos(x + 1, y * 2 - 1) + ascii + char, end="")


def check(x: int, y: int) -> bool:
    if x < 0 or x > img.width - 1 or y < 0 or y > img.height - 1:
        return False
    if (x, y) in completed:
        return False

    completed.append((x, y))
    if get_color_from_pixel(img, (x, y)) == bg_color:
        return False
    return True

def check_around(x: int, y: int) -> bool:
    if check(x , y):
        stack.append((x, y))
    else:
        completed.append((x, y))

pixels_count = img.width * img.height
pixel_processed = 1
regions = {}
region_index = 0
completed = []
x = y = 0
stack = []
while len(completed) < pixels_count:
    cur_color = get_color_from_pixel(img, (x, y))   # ищем первую и следующую область
    if cur_color != bg_color and (x, y) not in completed:
        region_index += 1     # start with 1?
        regions[region_index] = []  # сюда мы будем сохранять координаты точек в каждой области
        stack.append((x, y))
    else:
        completed.append((x, y))
    while stack:    # Область найдена, заливаем
        c, r = stack.pop()
        regions[region_index].append((c, r))
        completed.append((c, r))
        print_char_xy(r + 1, c + 1, "++", "")

        check_around(c - 1, r)
        check_around(c + 1, r)
        check_around(c, r - 1)
        check_around(c, r + 1)

    # print_char_xy(y + 1, x + 1, "00", "")
    x += 1
    if x == img.width:
        x = 0
        y += 1


print(pos(20, 1))
print("Done.")