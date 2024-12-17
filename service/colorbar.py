"""
RGB Colorbar
"""
import enum

fore_rgb = lambda red, green, blue: f"\x1b[38;2;{red};{green};{blue}m"
back_rgb = lambda red, green, blue: f"\x1b[48;2;{red};{green};{blue}m"
RESET = "\x1b[0m"

BAR_CHARS = ' ▮▬■⌍—…⁙⇶▥▨▭▣▦▩▮▤▧▰⋯※⁕⁘→⇨⇒⇛·∘∞▪◎◯▮●◍◉◯≡≣▶⫸'


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
    return tuple(round(from_rgb[rgb] + (to_rgb[rgb] - from_rgb[rgb]) * fract) for rgb in range(3))


def gradient_color(fract: float,
                   color: rgb_color = None,
                   to_color: rgb_color = None,
                   ) -> rgb_color:
    """
    Generates a gradient color by interpolating between two specified colors based
    on a given fractional value.

    The function calculates a transitional color between a starting color and a target
    color using the specified fraction.
    The fraction determines the weight of each
    color in the resulting gradient.
    This is useful in various graphical applications
    where smooth color transitions are required.

    :param fract: A fractional value is used to weigh the interpolation.
        A value of 0 results in the starting color, and a value of 1 results in the
        target color.
    :param color: The starting color is represented by an `rgb_color` typedef object or integer 24-bit color value.
    :param to_color: The target color.
    :return: The resulting color after gradient interpolation as an `rgb_color` object or integer 24-bit color value.
    """

    return pack_rgb(_gradient_color(color=color, to_color=to_color, fract=fract))


def gradient_bar(fract: float, symbol: str = " ",
                 color: rgb_color = None,
                 to_color: rgb_color = None,
                 k: int = 30,
                 rainbow: bool = True,
                 percent: bool = True) -> str:
    """
    Generates a gradient-styled bar visualization with optional rainbow gradient,
    percentage text, and customizable settings.

    The function creates a string that represents a gradient bar.
    It allows for customization, including using different
    colors, specifying the size of the bar,
    enabling or disabling the rainbow gradient effect, and displaying the fraction
    as a percentage at the end of the bar.
    The function relies on gradient color transitions to produce the visual result.

    :param fract: A float value between 0.0 and 1.0 representing the fraction of the bar to fill.
        Обычно равно i / n, где i - текущее значение итерации,
        а n - всего итераций
    :param symbol: A string used as the repeating unit in the bar, default is a single space.
        Если длина строки больше 1, то результат будет содержать ту же строку цветом от начального до конечного
    :param color: An RGB int representing the starting color of the gradient.
    Represented by an `rgb_color` typedef object
        or integer 24-bit color value.
        Defaults to COLOR_DEFAULT
    :param to_color: An RGB ending color of the gradient.
    Defaults to matching the starting color
        if not provided.
        Defaults to color if it is present or COLOR_DEFAULT
    :param k: An integer specifying length of the bar.
    :param rainbow: A boolean flag indicating whether to apply a rainbow gradient effect.
    If True, the gradient spans
                    through a rainbow spectrum along the bar.
                    Defaults to True.
                    Если False с каждой итерацией
                    будет меняться цвет всего бара.
    :param percent: A boolean flag stating whether to append the fractional percentage is displayed at the end
        of the bar.
        Defaults to True.

    :return: A string representing the gradient-styled bar, optionally with percentage display appended.
        Just print this string, "\r" and end="" to see the progress bar.
    """

    if not color:
        color = COLOR_DEFAULT
        to_color = TO_COLOR_DEFAULT
    if not to_color:
        to_color = color

    back_or_fore = back_rgb if symbol == " " else fore_rgb

    if len(symbol) > 1:
        result = f"{back_or_fore(*_gradient_color(color=color, to_color=to_color, fract=fract))}{symbol}"
    elif rainbow:
        result = symbol.join([f"{back_or_fore(*_gradient_color(color=color, to_color=to_color, fract=w / k))}" for w in
                              range(round(k * fract))]) + symbol
    else:
        result = (f"{back_or_fore(*_gradient_color(color=color, to_color=to_color, fract=fract))}"
                  f"{symbol * round(k * fract)}")

    result += RESET
    if percent:
        result += f" {fract:.0%}"

    return result


if __name__ == '__main__':
    from time import time, sleep
    import shutil
    import random


    def calibrate(interval: int = 1) -> int:
        """
        Прогон типичной операции в тестах в течение 1 секунды или заданного значения.
        Определение количества циклов итераций в тестах
        """
        start = time()
        count = 0
        while True:
            count += 1
            print("Calibrate...", gradient_bar(count / 1_000_000), "\r", end="")
            if time() - start > interval:
                break
        return count

    def generate_delays(num_iterations: int, show_time: int) -> list[float]:
        return sorted([random.random() * show_time for _ in range(num_iterations)])



    terminal_width = shutil.get_terminal_size().columns
    if terminal_width < 80:
        print(f"terminal width must be at least 100, but is {terminal_width}")
        exit(1)

    print(f'\n{" colorbar demo ":·^100}\n')

    print("Bar random examples")
    for i in range(15):
        color1, color2 = random.sample(list(Color), 2)
        print(gradient_bar(1., symbol=random.choice(BAR_CHARS),
                           color=color1,
                           to_color=color2,
                           k=random.randint(10, 100), percent=False))
    print()

    n = calibrate() * 2  # check it for the optimal time of test
    print(" " * 100, "\r", end="")

    print("Default:")
    start = 0
    num_iters = 100
    delays = generate_delays(num_iters, 5)
    for i in range(num_iters):
        print("Progres bar:", gradient_bar((i+1) / num_iters), "\r", end="", flush=True)
        sleep(delays[i] - start)
        start = delays[i]

    print("\nrainbow off, percent off:")
    for i in range(n):
        print(f"Progres bar: {gradient_bar(i / n, rainbow=False, percent=False)}\r", end="")

    print("\nanother colors, symbol, size")
    for i in range(n):
        print("Progres bar:", gradient_bar(i / n, symbol=BAR_CHARS[-1], color=0x1dccc0, to_color=0xd9d259, k=80),
              "\r", end="")

    print("\nColor progres indicator:")
    for i in range(n):
        print(gradient_bar(i / n, symbol="Calculate...", color=Color.RED, to_color=Color.YELLOW), "\r", end="")
