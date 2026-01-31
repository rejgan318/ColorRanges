"""
Клеточная сетка типа лабиринта, поля игры "жизнь", судоку и пр. Реализация TUI
- загрузка
- вывод TUI
"""
from pathlib import Path
import csv

from PIL import Image


class Walls:
    def __init__(self, file_name: Path = None, txt: str = None):

        self.wall: list[list[str]] = []
        self.file_name = file_name
        self.palette = []

        if file_name and txt:
            raise ValueError("Должен быть указан только один параметр: file_name или txt")

        if file_name:
            self.load()
        elif txt:
            self.wall = self.load_from_str(txt)
        else:
            raise ValueError("Один из параметров (file_name или txt) должен быть указан")

    def load(self) -> None:
        load_method = {
            '.txt': self.load_from_txt,
            '.csv': self.load_from_csv,
            '.png': self.load_from_png,
        }
        ext = self.file_name.suffix.lower()
        if ext not in load_method:
            raise ImportError(f"Неподдерживаемый формат файла: {ext}")

        self.wall = load_method[ext]()
        if not self.validate_cells():
            raise ImportError(f"Некорректные длины входных данных в файле {self.file_name}")

    def validate_cells(self):
        return all(len(self.wall[0]) == len(self.wall[i]) for i in range(1, len(self.wall)))

    def load_from_txt(self):
        """
        Формат входного текстового файла
            строка-символов-без-пробелов-и-разделителей1
            строка-символов-без-пробелов-и-разделителей2
            ...
        :return:
        """
        return self.load_from_str(self.file_name.read_text())

    def load_from_str(self, string: str):
        """
        Формат строки такой же, как у текстового файла
        :param string:
        :return:
        """
        result = []
        for i, row in enumerate(string.splitlines()):
            result.append(list(row))
        return result

    def load_from_csv(self):
        """
        разделитель - ,
        :return:
        """
        with open(self.file_name, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            return [list(row) for row in reader]

    def load_from_png(self):

        max_png_width = 179
        max_png_height = 28
        img = Image.open(self.file_name)

        assert img.mode == 'RGB'
        assert img.size[0] < max_png_width, f"Ширина {self.file_name} {img.width} > {max_png_width}"
        assert img.size[1] < max_png_height, f"Высота {self.file_name} {img.height} > {max_png_height}"

        self.palette = {}
        color_to_chars = "0123456789abcdef"
        char_idx = 0
        cells = [['0'] * img.width for _ in range(img.height)]
        for row in range(img.height):
            for col in range(img.width):
                color = img.getpixel((col, row))
                if color not in self.palette.values():
                    assert char_idx < len(color_to_chars), f"Too many colors in {self.file_name}"
                    # сохраним цвет в палитре
                    self.palette[color_to_chars[char_idx]] = color
                    char_idx += 1

                color_char = next(k for k, v in self.palette.items() if v == color)
                cells[row][col] = color_char    # кодируем цвет одним из символов color_to_chars

        return cells

    def convert(self, convert_table: dict = None):
        """
        Можно разукрасить перед печатью, заменив символы на более наглядные
        :param convert_table:
        :return:
        """
        convert_table = convert_table or {'0': "▮", '1': "▭"}

        for row in self.wall:
            for i in range(len(row)):
                row[i] = convert_table[row[i]]
        return self

    def print(self):
        for row in self.wall:
            print(' '.join(map(str, row)))

    def print_color(self, palette: dict = None):
        """
        из сохраненной палитры получаем цвета по закодированному символу
        и используем их при печати двух пробелов (только для эстетических пропорций) с этим цветом фона
        Цвет формируется esc-последовательностью. Палитра должна быть известна после загрузки png
        либо передается пареметром (для остальных типов данных)
        :param palette:
        :return:
        """
        back_rgb = lambda red, green, blue: f"\x1b[48;2;{red};{green};{blue}m"
        RESET = "\x1b[0m"

        palette = palette or self.palette

        for row in self.wall:
            colored_string = ""
            old_color = None
            for i in range(len(row)):
                coded_color = row[i]
                color = palette[coded_color]
                r, g, b = color
                # немного избавимся от избыточности, esc-последовательности только для неповторяющихся цветов
                colored_string += (back_rgb(r, g, b) if color != old_color else "") + '  '
                old_color = color
            print(colored_string + RESET)


def main():

    print("\nCSV")
    lab = Walls(Path("data/labirint.csv"))
    lab.print()
    print("\nРаскраска")
    lab.print_color(palette={'0': (100, 100, 100), '1': (200, 200, 200)})

    print("\nTXT в других символах")
    Walls(txt="101\n000\n101").convert(convert_table={'0': '▮', '1': '▭'}).print()

    print("\nPNG в оригинальных цветах")
    Walls(Path("imgs/small_probe.png")).print_color()


if __name__ == '__main__':
    main()
