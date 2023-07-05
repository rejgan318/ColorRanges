import colorama
from PIL import Image
import numpy as np

fore_rgb = lambda red, green, blue: f"\x1b[38;2;{red};{green};{blue}m"
back_rgb = lambda red, green, blue: f"\x1b[48;2;{red};{green};{blue}m"


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
    :param image: изображение
    :return: цвет фона изображения
    """
    rgb = np.array(image).astype(np.uint32).reshape((-1, 3))
    # rgb = np.array(img).astype(np.uint32).reshape((-1, 3)).np.random.random_sample(MIN_SAMPLE_SIZE)
    rgb = (rgb[:, 0] << 16 |
           rgb[:, 1] << 8 |
           rgb[:, 2])
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
        # print(out_row + colorama.Style.RESET_ALL)
    result += "\033[0m"
    # print("\033[0m")
    return result


if __name__ == '__main__':
    colorama.just_fix_windows_console()

    IMAGE_FILE_NAME = 'imgs/small_probe.png'
    img = Image.open(IMAGE_FILE_NAME)

    print(make_ascii_picture(img))
