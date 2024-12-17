from time import time
import enum
import random

import colorama
from PIL import Image
import numpy as np

type rgb_color = tuple[int, int, int]

fore_rgb = lambda red, green, blue: f"\x1b[38;2;{red};{green};{blue}m"
back_rgb = lambda red, green, blue: f"\x1b[48;2;{red};{green};{blue}m"
RESET = "\x1b[0m"


class Color(enum.Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 0)
    MAGENTA = (255, 0, 255)
    BLACK = (0, 0, 0)
    GREY = (128, 128, 128)


class Gradient(enum.Enum):
    RED_TO_GREEN = (Color.RED.value, Color.GREEN.value)
    BLACK_TO_WHITE = (Color.BLACK.value, Color.WHITE.value)
    WHITE_TO_BLACK = (Color.WHITE.value, Color.BLACK.value)
    YELLOW_TO_MAGENTA = (Color.YELLOW.value, Color.MAGENTA.value)
    BLUE_TO_YELLOW = (Color.BLUE.value, Color.YELLOW.value)
    GREY_TO_WHITE = (Color.GREY.value, Color.WHITE.value)
    GREY_TO_BLACK = (Color.GREY.value, Color.BLACK.value)

    DEFAULT = (Color.RED.value, Color.GREEN.value)

chars_for_bar = ' ▮▬■⌍—…⁙⇶▥▨▭▣▦▩▮▤▧▰⋯※⁕⁘→⇨⇒⇛·∘∞▪◎◯▮●◍◉◯≡≣▶⫸'


def unpack_rgb(packed:  int) -> tuple[int, int, int]:
    rgb = ((packed >> 16) & 0xff,
           (packed >> 8) & 0xff,
           packed & 0xff)
    return rgb


def pack_rgb(rgb:  tuple[int, int, int]) -> int:
    return rgb[0] << 16 | rgb[1] << 8 | rgb[2]


def get_background_color(image: Image) -> tuple[int, int, int]:
    """
    Возвращает цвет фона изображения. Определяется как наиболее часто встречающийся
    :param image: изображение Pillow
    :return: цвет фона изображения
    """
    rgb = np.array(image).astype(np.uint32).reshape((-1, 3))
    rgb = (rgb[:, 0] << 16 |
           rgb[:, 1] << 8 |
           rgb[:, 2])
    fraction = 0.05
    # size = int(rgb.size * fraction)
    # rgb = np.random.choice(rgb, size=size, replace=False)
    unique, counts = np.unique(rgb, return_counts=True)
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


def get_color_from_pixel(img, pixel):
    return img.getpixel(pixel)


def make_ascii_picture(img, multiplexer: int = None):
    multiplexer = multiplexer or 2
    assert isinstance(img, Image.Image)
    assert img.mode == 'RGB'
    assert img.size[0] * multiplexer < 179
    assert img.size[1] < 28

    result = ""
    for row in range(img.height):
        out_row = ""
        old_color = None
        for char in range(img.width):
            color = get_color_from_pixel(img, (char, row))
            if old_color != color:
                out_row += back_rgb(*color)
                old_color = color
            out_row += " " * multiplexer
        result += f"{out_row}{colorama.Style.RESET_ALL}\n"
    result += RESET
    return result

def gradient_color(from_color: rgb_color = None, to_color: rgb_color = None, fraction: float = 1.0) -> rgb_color:
    from_color = from_color or Gradient.DEFAULT.value[0]
    to_color = to_color or Gradient.DEFAULT.value[1]

    return [round(from_color[rgb] + (to_color[rgb] - from_color[rgb]) * fraction) for rgb in range(3)]


def make_gradient_bar(symbol: str = " ",
                      colors: rgb_color = Gradient.DEFAULT.value,
                      k: int = 30, fract: float = 1.0, rainbow: bool = True):

    back_or_fore = back_rgb if symbol == " " else fore_rgb
    if rainbow:
        result = symbol.join([f"{back_or_fore(*gradient_color(*colors, w / k))}" for w in range(round(k * fract))]) + symbol
    else:
        result = f"{back_or_fore(*gradient_color(*colors, fraction=fract))}{symbol * round(k * fract)}"
    return result  + RESET


def make_color_string(s: str, color: rgb_color) -> str:
    return f"{fore_rgb(*color)}{s}{RESET}"


if __name__ == '__main__':

    TEST_get_background_color = False

    if TEST_get_background_color:
        IMAGE_FILE_NAME = r'd:\dev\data\get_background_color.png'
        img = Image.open(IMAGE_FILE_NAME)
        start = time()
        print(get_background_color(img))
        print(f"time: {time() - start:.2f}")
        # (255, 255, 255)

    if TEST_make_ascii_picture:
        IMAGE_FILE_NAME = r'D:\dev\python\ColorRanges\imgs\small_probe.png'
        img = Image.open(IMAGE_FILE_NAME)
        print(make_ascii_picture(img))
