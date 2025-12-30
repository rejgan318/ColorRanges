"""
Переписываю алгоритм заливки
"""
from pathlib import Path
import csv

from PIL import Image


def _get_from_str(string: str):
    result = []
    for i, row in enumerate(string.splitlines()):
        result.append(list(row))
    return result


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
            self.wall = _get_from_str(txt)
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
        if not self.validate_wall():
            raise ImportError(f"Некорректные длины входных данных в файле {self.file_name}")

    def validate_wall(self):
        return all(len(self.wall[0]) == len(self.wall[i]) for i in range(1, len(self.wall)))

    def load_from_txt(self):
        return _get_from_str(self.file_name.read_text())

    def load_from_csv(self):
        with open(self.file_name, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            return [list(row) for row in reader]
        # return [list(map(int, row.split(","))) for row in self.file_name.read_text().split("\n")]

    def load_from_png(self):

        max_png_width = 179
        max_png_height = 28
        img = Image.open(self.file_name)
        assert img.mode == 'RGB'
        assert img.size[0] < max_png_width, f"Ширина {self.file_name} {img.width} > {max_png_width}"
        assert img.size[1] < max_png_height, f"Высота {self.file_name} {img.height} > {max_png_height}"

        self.palette = []
        cells = [[0] * img.width for _ in range(img.height)]
        for row in range(img.height):
            for col in range(img.width):
                color = img.getpixel((col, row))
                if color not in self.palette:
                    self.palette.append(color)
                color_index = self.palette.index(color)
                cells[row][col] = str(color_index)

        return cells

    def convert(self, convert_table: dict = None):

        # convert_table = convert_table or {'0': "0", '1': "1", "2": "2", "3": "3", "4": "4"}
        convert_table = convert_table or {'0': "▮", '1': "▭"}

        for row in self.wall:
            for i in range(len(row)):
                row[i] = convert_table[row[i]]
        return self

    def print(self):
        for row in self.wall:
            print(' '.join(map(str, row)))


def main():

    print("\nCSV")
    walls = Walls(Path("data/labirint.csv"))
    walls.convert().print()

    print("\nTXT")
    walls = Walls(txt="101\n000\n101")
    walls.convert().print()

    print("\nPNG")
    walls = Walls(Path("imgs/small_probe.png"))
    walls.convert(convert_table={'0': "0", '1': "1", "2": "2", "3": "3", "4": "4"}).print()

if __name__ == '__main__':
    main()
