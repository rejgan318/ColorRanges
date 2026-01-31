"""
Визуализация в динамике
"""
from enum import Enum, auto
from dataclasses import dataclass
from time import time
from pathlib import Path
from typing import ClassVar

import arcade


type rgb_color = tuple[int, int, int] | tuple[int, int, int, int]


@dataclass
class XY:
    x: int
    y: int


@dataclass
class CellXY:
    xy: XY
    color: rgb_color
    id: int | None = None
    sleep: float = 0.0
    
    _id_counter: ClassVar[int] = 0
    
    def __post_init__(self):
        if self.id is None:
            self.id = CellXY._id_counter
            CellXY._id_counter += 1


@dataclass
class Sprites:
    cells: list[CellXY]
    cur_id: int = 0

    def append(self, cell: CellXY):
        # """ Добавление элемента с автоматическим созданием id """
        # if not cell.id:
        #     cell.id = self.cur_id
        #     self.cur_id += 1
        # else:
        #     self.cur_id = cell.id + 1

        self.cells.append(cell)

    def update(self, id: int, xy: XY = None, color: rgb_color = None, sleep: float = 0.0):
        pass
        # self.cells[cell.id] = cell


class STATE(Enum):
    IDLE = auto()
    NEXT = auto()
    EXIT = auto()


class PlayerA(arcade.Window):

    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    TITLE = "Arcade Player"
    BACKGROUND_COLOR: rgb_color = arcade.color.CORNFLOWER_BLUE[:3]

    def __init__(self, nw: int, nh: int,
                 window_width: int = WINDOW_WIDTH,
                 window_height: int = WINDOW_HEIGHT,
                 title: str = TITLE,
                 background_color: rgb_color = BACKGROUND_COLOR,
                 sleep: float = 0.0,
                 ):

        super().__init__(window_width, window_height, title)

        self.nw = nw    # количество ячеек сетки
        self.nh = nh

        self.window_width = window_width
        self.window_height = window_height

        self.texture_w = self.texture_h = 64    # реальные размеры ячеек без масштабирования

        self.cells_background_color = background_color

        self.sleep = sleep

        self.sprites = arcade.SpriteList()
        self.actions: list[CellXY] = []

        self.act_idx = 0
        self.accumulated_time = 0.0
        self.scale_cells = 1

        # self.cell_w = None  # Размеры ячейки сетки
        # self.cell_h = None

        self.cur_cell = None
        self._state = STATE.NEXT

        self.setup()
        print("Init finished")

    def setup(self):
        PADDING = 0.9
        scale_w = self.window_width / (self.texture_w * self.nw)
        scale_h = self.window_height / (self.texture_h * self.nh)
        if scale_w < 1 or scale_h < 1:
            self.scale_cells = min(scale_w, scale_h) * PADDING
        else:
            self.scale_cells = 1

        arcade.set_background_color(self.cells_background_color)

        print("Setup finished")
        pass

    def _get_cell_coords(self):
        """ координаты сетки - в экранные центрированные """
        # sprite = self.cell_list[0]
        center_x = (self.nw - 1) * self.texture_w / 2
        center_y = (self.nh - 1) * self.texture_h / 2
        x0, y0 = self.width / 2 - center_x, self.height / 2 - center_y

        return (x0 + self.cur_cell.xy.x * self.texture_w * self.scale_cells,
                y0 + self.cur_cell.xy.y * self.texture_h * self.scale_cells)

    def append_action(self, cell: CellXY):
        x, y = self._get_cell_coords()
        self.sprites.append(arcade.SpriteSolidColor(self.texture_w, self.texture_h, x, y, cell.color))

    def on_update(self, delta_time: float):
        """
        :param delta_time: Время с момента прошлого вызова. То есть время вывода одного (последнего) кадра,
        величина, обратная текущему fps
        """
        while True:
            match self._state:
                case STATE.IDLE:
                    self.accumulated_time += delta_time
                    sleep_time = self.cur_cell.sleep if self.cur_cell.sleep > 0.0 else self.sleep
                    if self.accumulated_time >= sleep_time:
                        # print("Next")
                        self._state = STATE.NEXT
                    else:   # отрисовываем текущий кадр и ждём
                        break
                case STATE.NEXT:
                    self.accumulated_time = 0.0
                    # print(f"{self.act_idx=}, {len(self.actions)=}")
                    if self.act_idx == len(self.actions):
                        self._state = STATE.EXIT
                        print("Exit")
                        continue
                    self.cur_cell = self.actions[self.act_idx]
                    self.append_action(self.cur_cell)
                    self.act_idx += 1
                    if self.cur_cell.sleep > 0.0 or self.sleep > 0.0:
                        self._state = STATE.IDLE
                        continue
                    else:
                        pass
                case STATE.EXIT:
                    arcade.close_window()
                    return

            # while self.actions[self.act_idx].sleep == 0.0:
            #     self.cur_cell = self.actions[self.act_idx]
            #     sleep(.1)
            #     # break
            #     # xy = self.cur_cell.xy
            #     x, y = self._get_cell_coords()
            #
            #     self.sprites.append(arcade.SpriteSolidColor(self.texture_w, self.texture_h, x, y, self.cur_cell.color))
            #     self.act_idx += 1

    def on_draw(self):
        self.clear()
        self.sprites.draw()

    def run(self, actions: list[CellXY]):
        self.actions = actions
        arcade.run()


if __name__ == "__main__":

    TEST1 = False
    TEST2 = False
    TEST3 = False

    # TEST1 = True
    TEST2 = True
    # TEST3 = True

    if TEST1:
        actions: list[CellXY] = [
            CellXY(xy=XY(0, 0), color=arcade.color.WHITE, sleep=1.0),
            CellXY(xy=XY(1, 0), color=arcade.color.BLACK,),
            CellXY(xy=XY(2, 0), color=arcade.color.RED,),
            CellXY(xy=XY(7, 7), color=arcade.color.BLUEBERRY, sleep=.2),
            CellXY(xy=XY(8, 8), color=arcade.color.BLOND, sleep=.2),
            CellXY(xy=XY(9, 9), color=arcade.color.BLUE, sleep=3.0),
        ]
        player = PlayerA(10, 10, sleep=1.)
        player.run(actions)

    if TEST2:
        from flood_fill import Walls

        small = Walls(Path("imgs/small_probe.png"))
        w = len(small.wall[0])
        h = len(small.wall)

        actions: list[CellXY] = []
        for r, row in enumerate(small.wall):
            for c, cell in enumerate(row):
                actions.append(CellXY(XY(c, h-r), color=small.palette[cell]))

        actions.append(CellXY(XY(0, h), color=small.palette['0'], sleep=3.0))
        player = PlayerA(w, h, sleep=0.07)
        player.run(actions)

    if TEST3:
        from flood_fill import Walls

        small = Walls(Path("data/ex1.txt"))
        small.print_color(palette={'0': (50, 50, 50), '1': (200, 200, 200)})

        w = len(small.wall[0])
        h = len(small.wall)

        palette = {'0': arcade.color.BLACK, '1': arcade.color.WHITE}
        actions: list[CellXY] = []
        for r, row in enumerate(small.wall):
            for c, cell in enumerate(row):
                actions.append(CellXY(XY(c, h-r-1), color=palette[cell]))

        actions.append(CellXY(XY(0, 0), color=palette[small.wall[h-1][0]], sleep=5.0))

        player = PlayerA(w, h, sleep=0.06)
        player.run(actions)

    print("Done.")
