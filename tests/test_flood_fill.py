import pytest
from pathlib import Path
from flood_fill import Walls
import tempfile
from PIL import Image


def test_walls_init_with_txt():
    txt_content = "###\n#.#\n###"
    walls = Walls(txt=txt_content)
    assert walls.wall == [['#', '#', '#'], ['#', '.', '#'], ['#', '#', '#']]


def test_walls_init_no_params():
    with pytest.raises(ValueError, match=r"Один из параметров \(file_name или txt\) должен быть указан"):
        Walls()


def test_walls_init_both_params():
    with pytest.raises(ValueError, match="Должен быть указан только один параметр: file_name или txt"):
        Walls(file_name=Path("test.txt"), txt="some text")


def test_walls_get_from_str():
    txt = (
        "line1\n"
        "line2\n"
        "line3")
    walls = Walls(txt=txt)
    assert len(walls.wall) == 3
    assert walls.wall[0] == ['l', 'i', 'n', 'e', '1']
    assert walls.wall[1] == ['l', 'i', 'n', 'e', '2']
    assert walls.wall[2] == ['l', 'i', 'n', 'e', '3']


def test_walls_load_from_txt_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("###\n#.#\n###")
        temp_path = Path(f.name)

    try:
        walls = Walls(file_name=temp_path)
        assert walls.wall == [
            ['#', '#', '#'],
            ['#', '.', '#'],
            ['#', '#', '#']
        ]

    finally:
        temp_path.unlink()


def test_walls_load_from_csv_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("1,0,1\n0,0,0\n1,0,1")
        temp_path = Path(f.name)

    try:
        walls = Walls(file_name=temp_path)
        assert walls.wall == [['1', '0', '1'], ['0', '0', '0'], ['1', '0', '1']]
    finally:
        temp_path.unlink()


def test_walls_validate_cells_correct():
    txt_content = "###\n#.#\n###"
    walls = Walls(txt=txt_content)
    assert walls.validate_cells() is True


def test_walls_validate_cells_incorrect():
    walls = Walls.__new__(Walls)
    walls.wall = ["###", "#.#", "##"]
    assert walls.validate_cells() is False


def test_walls_load_unsupported_format():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{}")
        temp_path = Path(f.name)

    try:
        with pytest.raises(ImportError, match="Неподдерживаемый формат файла: .json"):
            Walls(file_name=temp_path)
    finally:
        temp_path.unlink()


def test_walls_load_invalid_dimensions():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("###\n#.#\n##")
        temp_path = Path(f.name)

    try:
        with pytest.raises(ImportError, match=r"Некорректные длины входных данных в файле"):
            Walls(file_name=temp_path)
    finally:
        temp_path.unlink()


def test_walls_load_from_png_basic():
    """Базовый тест загрузки PNG с двумя цветами"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = Path(f.name)

    try:
        # Создаём простое изображение 3x3 с двумя цветами
        img = Image.new('RGB', (3, 3), color=(255, 0, 0))  # Красный фон
        pixels = img.load()
        pixels[1, 1] = (0, 0, 255)  # Синий центр
        img.save(temp_path)

        walls = Walls(file_name=temp_path)

        # Проверяем, что wall заполнен
        assert len(walls.wall) == 3
        assert len(walls.wall[0]) == 3

        # Проверяем палитру
        assert len(walls.palette) == 2
        assert (255, 0, 0) in walls.palette
        assert (0, 0, 255) in walls.palette

        # Проверяем индексы
        red_idx = walls.palette.index((255, 0, 0))
        blue_idx = walls.palette.index((0, 0, 255))
        assert walls.wall[1][1] == str(blue_idx)
        assert walls.wall[0][0] == str(red_idx)
    finally:
        temp_path.unlink()


def test_walls_load_from_png_multiple_colors():
    """Тест с несколькими разными цветами"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = Path(f.name)

    try:
        img = Image.new('RGB', (2, 2))
        pixels = img.load()
        pixels[0, 0] = (255, 0, 0)    # Красный
        pixels[1, 0] = (0, 255, 0)    # Зелёный
        pixels[0, 1] = (0, 0, 255)    # Синий
        pixels[1, 1] = (255, 255, 0)  # Жёлтый
        img.save(temp_path)

        walls = Walls(file_name=temp_path)

        # Все 4 цвета должны быть в палитре
        assert len(walls.palette) == 4
        assert walls.wall[0][0] == str(walls.palette.index((255, 0, 0)))
        assert walls.wall[0][1] == str(walls.palette.index((0, 255, 0)))
        assert walls.wall[1][0] == str(walls.palette.index((0, 0, 255)))
        assert walls.wall[1][1] == str(walls.palette.index((255, 255, 0)))
    finally:
        temp_path.unlink()


def test_walls_load_from_png_same_color():
    """Тест с одним цветом"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = Path(f.name)

    try:
        img = Image.new('RGB', (3, 3), color=(128, 128, 128))
        img.save(temp_path)

        walls = Walls(file_name=temp_path)

        # Только один цвет
        assert len(walls.palette) == 1
        assert walls.palette[0] == (128, 128, 128)

        # Все ячейки имеют индекс 0
        for row in walls.wall:
            for cell in row:
                assert cell == '0'
    finally:
        temp_path.unlink()


def test_walls_load_from_png_width_limit():
    """Тест превышения максимальной ширины"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = Path(f.name)

    try:
        img = Image.new('RGB', (180, 10))  # Ширина > 179
        img.save(temp_path)

        with pytest.raises(AssertionError, match="Ширина"):
            Walls(file_name=temp_path)
    finally:
        temp_path.unlink()


def test_walls_load_from_png_height_limit():
    """Тест превышения максимальной высоты"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = Path(f.name)

    try:
        img = Image.new('RGB', (10, 29))  # Высота > 28
        img.save(temp_path)

        with pytest.raises(AssertionError, match="Высота"):
            Walls(file_name=temp_path)
    finally:
        temp_path.unlink()


def test_walls_load_from_png_wrong_mode():
    """Тест с неподдерживаемым режимом изображения"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        temp_path = Path(f.name)

    try:
        img = Image.new('L', (10, 10))  # Grayscale вместо RGB
        img.save(temp_path)

        with pytest.raises(AssertionError):
            Walls(file_name=temp_path)
    finally:
        temp_path.unlink()
