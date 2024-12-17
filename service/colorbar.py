"""
RGB Colorbar
"""

from time import time
import enum
import random

import colorama

# from print_ascii import total_colors

fore_rgb = lambda red, green, blue: f"\x1b[38;2;{red};{green};{blue}m"
back_rgb = lambda red, green, blue: f"\x1b[48;2;{red};{green};{blue}m"
RESET = "\x1b[0m"


class Color(enum.IntEnum):
    RED = 0xff0000
    GREEN = 0x00ff00
    BLUE = 0x0000ff
    WHITE = 0xffffff
    YELLOW = 0xffff00
    MAGENTA = 0xff00ff
    BLACK = 0x000000
    GREY = 0x808080

COLOR_DEFAULT = Color.RED
TO_COLOR_DEFAULT = Color.GREEN


class Gradient(enum.Enum):
    RED_TO_GREEN = (Color.RED, Color.GREEN)
    BLACK_TO_WHITE = (Color.BLACK, Color.WHITE)
    WHITE_TO_BLACK = (Color.WHITE, Color.BLACK)
    YELLOW_TO_MAGENTA = (Color.YELLOW, Color.MAGENTA)
    BLUE_TO_YELLOW = (Color.BLUE, Color.YELLOW)
    GREY_TO_WHITE = (Color.GREY, Color.WHITE)
    GREY_TO_BLACK = (Color.GREY, Color.BLACK)

    DEFAULT = (COLOR_DEFAULT, TO_COLOR_DEFAULT)

type rgb_color = Color | int


bar_chars = ' ▮▬■⌍—…⁙⇶▥▨▭▣▦▩▮▤▧▰⋯※⁕⁘→⇨⇒⇛·∘∞▪◎◯▮●◍◉◯≡≣▶⫸'


def unpack_rgb(packed:  int) -> tuple[int, int, int]:
    rgb = ((packed >> 16) & 0xff,
           (packed >> 8) & 0xff,
           packed & 0xff)
    return rgb


def pack_rgb(rgb:  tuple[int, int, int]) -> int:
    return rgb[0] << 16 | rgb[1] << 8 | rgb[2]


def _gradient_color(color: rgb_color = None,
                    to_color: rgb_color = None,
                    fract: float = 1.0) -> tuple[int, int, int]:
    color = color or COLOR_DEFAULT
    to_color = to_color or TO_COLOR_DEFAULT

    from_rgb = unpack_rgb(color)
    to_rgb = unpack_rgb(to_color)
    return [round(from_rgb[rgb] + (to_rgb[rgb] - from_rgb[rgb]) * fract) for rgb in range(3)]


def gradient_color(fract: float = 1.0,
                   color: rgb_color = None,
                   to_color: rgb_color = None,
                   ) -> rgb_color:

    return pack_rgb(_gradient_color(color=color, to_color=to_color, fract=fract))


def gradient_bar(fract: float = 1.0, symbol: str = " ",
                 color: rgb_color = None,
                 to_color: rgb_color = None,
                 k: int = 30,
                 rainbow: bool = True,
                 percent: bool = True):

    if not color:
        color = COLOR_DEFAULT
        to_color = TO_COLOR_DEFAULT
    if not to_color:
        to_color = color

    back_or_fore = back_rgb if symbol == " " else fore_rgb

    if len(symbol) > 1:
        result = f"{back_or_fore(*_gradient_color(color=color, to_color=to_color, fract=fract))}{symbol}"
    elif rainbow:
        result = symbol.join([f"{back_or_fore(*_gradient_color(color=color, to_color=to_color, fract=w / k))}" for w in range(round(k * fract))]) + symbol
    else:
        result = f"{back_or_fore(*_gradient_color(color=color, to_color=to_color, fract=fract))}{symbol * round(k * fract)}"

    result += RESET
    if percent:
        result += f" {fract:.0%}"

    return result


if __name__ == '__main__':

    print(f'\n{" colorbar demo ":·^100}\n')
    print("Bar random examples")
    for i in range(15):
        color, to_color = random.sample(list(Color), 2)
        print(gradient_bar(symbol=random.choice(bar_chars),
                           color=color,
                           to_color=to_color,
                           k=random.randint(10, 120), percent=False))
    print()

    n = 50_000  # check it for the optimal time of test

    print("Default:")
    for i in range(n):
        print("Progres bar:", gradient_bar(i / n), "\r", end="")
    print()

    print("rainbow off, percent off:")
    for i in range(n):
        print(f"Progres bar: {gradient_bar(i / n, rainbow=False, percent=False)}\r", end="")
    print()

    print("another colors, symbol, size")
    for i in range(n):
        print("Progres bar:", gradient_bar(i / n, symbol=bar_chars[-1], color=0x1dccc0, to_color=0xd9d259, k=100), "\r", end="")
    print()

    print("Color progres indicator:")
    for i in range(n):
        print(gradient_bar(i / n, symbol="Calculate...", color=Color.RED, to_color=Color.YELLOW), "\r", end="")
    print()
