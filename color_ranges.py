"""
Определение закрашенных областей
"""
import configparser
from pathlib import Path
from time import sleep

import colorama as co
from PIL import Image

from print_ascii import make_ascii_picture, total_colors, get_background_color, get_color_from_pixel, \
    pack_rgb, back_rgb, fore_rgb

pos = lambda y, x: co.Cursor.POS(x, y)

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
r, g, b = list(map(int, bg_color))
print(f"Цвет фона    : {back_rgb(r, g, b)}  {co.Back.RESET} #{r:02x}{g:02x}{b:02x}")


def print_char_xy(x: int, y: int, char: str):
    b_c = get_color_from_pixel(img, (y-1, x-1))     # same background color
    f_c = tuple(255 - v for v in b_c)   # inverse colors

    print(pos(x + 1, y * 2 - 1) + back_rgb(*b_c) + fore_rgb(*f_c) + char + "\x1b[0m" + pos(24, 1), end="", flush=True)
    if __debug__:
        sleep(0.01)


def check_around(x: int, y: int):
    def check(x: int, y: int) -> bool:

        if any([x < 0, x > img.width - 1, y < 0, y > img.height - 1]):
            return False
        if (x, y) in checked:
            return False

        if get_color_from_pixel(img, (x, y)) == bg_color:
            checked_append((x, y))
            print_char_xy(y + 1, x + 1, "· ")
            return False
        return True

    if check(x, y):
        stack.append((x, y))
        checked_append((x, y))


def checked_append(xy: tuple):
    if __debug__:
        sleep(0.1)
    if xy not in checked:
        checked.append(xy)
    else:
        print_char_xy(xy[1] + 1, xy[0] + 1, "? ")
        if __debug__:
            sleep(1)


pixels_count = img.width * img.height
pixel_processed = 1
regions = {}
region_index = -1
colors = []
checked = []
correct_append = True
x = y = 0
stack = []
while len(checked) < pixels_count:
    if (x, y) not in checked:
        cur_color = get_color_from_pixel(img, (x, y))  # ищем первую и следующую область
        checked_append((x, y))
        if cur_color != bg_color:
            colors.append(cur_color)
            region_index += 1     # start with 1?
            regions[region_index] = []  # сюда мы будем сохранять координаты точек в каждой области
            stack.append((x, y))
        else:
            print_char_xy(y + 1, x + 1, "· ")
    while stack:    # Область найдена, заливаем пока не зальем полностью
        c, r = stack.pop()
        regions[region_index].append((c, r))
        print_char_xy(r + 1, c + 1, "+ ")

        check_around(c - 1, r)
        check_around(c + 1, r)
        check_around(c, r - 1)
        check_around(c, r + 1)

    x += 1
    if x == img.width:
        x = 0
        y += 1

print(pos(24, 1))
assert len(checked) == len(set(checked))
print("Done.")


