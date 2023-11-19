from config import *
import pygame as pg
import random


def get_n_cells(pos):
    """
    Получить 8 соседних клеток
    :param pos: выбранная клетка
    :return:
    """
    try:
        px, py = pos
        return [
            (px + 1, py + 1),
            (px - 1, py + 1),
            (px + 1, py - 1),
            (px - 1, py - 1),
            (px, py + 1),
            (px, py - 1),
            (px + 1, py),
            (px - 1, py)
        ]
    except:
        pass


class GameOfLife:
    def __init__(self):
        """
        Инициализация
        """
        self.delta_time = 0
        self.cells = set()
        self.random_restart(0.4)

        # constants
        self.TIME_BETWEEN_RENDERERS = 150

    def random_restart(self, filling_ratio, tile=20, width=WIDTH, height=HEIGHT):
        """
        Случайное заполнение поля
        :param filling_ratio: сколько процентов экрана закрасить
        :param tile: размер клетки
        :param width: ширина экрана
        :param height: высота экрана
        :return:
        """
        for _ in range(int(width * height / tile / tile * filling_ratio)):
            pos = (random.randint(0, width // tile), random.randint(0, height // tile))
            self.cells.add(pos)

    def update(self, delta_time):
        """
        Обновление с учотом времени между кадрами
        :param delta_time: время между кадрами
        :return:
        """
        self.delta_time += delta_time
        if self.delta_time > self.TIME_BETWEEN_RENDERERS:
            self.delta_time %= self.TIME_BETWEEN_RENDERERS
            self.render()

    def count_n_cells(self, cell):
        """
        Подсчет соседних клеток вокруг выбранной
        :param cell: выбранная клетка
        :return:
        """
        res = 0
        for i in get_n_cells(cell):
            if i in self.cells:
                res += 1
        return res

    def render(self):
        """
        Обновление состояния клеточного поля
        :return:
        """
        future_cells = set()
        for cell in self.cells:
            # self render
            if cell not in future_cells and 2 <= self.count_n_cells(cell) <= 3:
                future_cells.add(cell)

            # n cells render
            for n_cell in get_n_cells(cell):
                if n_cell not in future_cells and self.count_n_cells(n_cell) == 3:
                    future_cells.add(n_cell)
        self.cells = future_cells

    def draw(self, sc, tile, min_boarder=False):
        """

        :param sc: экран отрисовки
        :param tile: размер клетки
        :param min_boarder: расстояние от незакрашеной клетки до правого верчнего угла
        :return:
        """
        count = 0
        to_delete = []
        if not min_boarder:
            min_boarder = min(sc.get_width(), sc.get_height())
        for cell in self.cells:
            cell_x, cell_y = cell
            n = min(((cell_x * cell_x + cell_y * cell_y)*tile*tile)**0.5 / max(min_boarder, 1), 1)
            if n != 1 and cell_x >= 0 and cell_y >= 0:
                count += 1
                color = (n * 255, n * 255, n * 255)
                pg.draw.rect(sc, color, (-cell_x * tile + sc.get_width(), cell_y * tile, tile + 1, tile + 1))
            else:
                to_delete.append(cell)

        for i in to_delete:
            self.cells.remove(i)

        for _ in range(120 - count):
            cell = tuple(random.sample(self.cells, 1))
            cell = cell[0]
            for pos in get_n_cells(cell):
                self.cells.add(pos)
