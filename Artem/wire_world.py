from config import *
from sound import play_sound
from user import WW_Runner_Player
import random
from image_loader import load_image


class WireWorld:
    """
    Клеточный автомат в котором реализуются правила:
        Empty → Empty
        Electron head → Electron tail
        Electron tail → Connector
        Connector →
            → Electron head if exactly one or two of the neighboring cells are electron heads
            → remains connector otherwise

    Сокращения в коде:
        n - neighboring
        f - future
        a - actual
    """

    def __init__(self):
        """Инициализация

        :param self.delta_time: время между прошлым и нынешним кадром
        :type self.delta_time: int
        :param self.connectors: set который содержит координаты x и y всех коннекторов на поле
        :type self.connectors: set
        :param self.electron_heads: set который содержит координаты x и y всех голов эллектронов на поле
        :type self.electron_heads: set
        :param self.electron_tails: set который содержит координаты x и y всех хвостов эллектронов на поле
        :type self.electron_heads: set
        :param self.f_electron_heads: set который содержит координаты x и y всех голов эллектронов на следуюший ход
        :type self.f_electron_heads: set
        :param self.addConnectorsPos: set который содержит координаты x и y всех блоков добавления коннекторов, а также количество коннекторов, которое он прибавляет
        :type self.addConnectorsPos: set
        :param self.clickGenerators: set который содержит координаты x и y всех блоков создание электронов
        :type self.clickGenerators: set
        :param self.endBlocks: set который содержит координаты x и y всех блоков до которых электрон должен дойти
        :type self.endBlocks: set
        """
        self.delta_time = 0
        self.connectors = set()
        self.electron_heads = set()
        self.electron_tails = set()
        self.f_electron_heads = set()
        self.addConnectorsPos = set()
        self.clickGenerators = set()
        self.endBlocks = set()
        ##self.read_from_file('primes.txt')

    def read_from_file(self, file_name):
        """
        Чтение клеточного поля из файла

        :param file_name: путь к файлу с клеточным полем
        :type file_name: str
        """
        try:
            input_file = open(file_name)
            self.connectors = set()
            self.electron_heads = set()
            self.electron_tails = set()
            self.f_electron_heads = set()
            self.addConnectorsPos = set()
            self.clickGenerators = set()
            self.endBlocks = set()
            for line in input_file:
                cell_information = line.split(' ')
                cell = int(float(cell_information[1])), int(float(cell_information[2]))
                if cell_information[0] == 'c':
                    self.connectors.add(cell)
                elif cell_information[0] == 'h':
                    self.electron_heads.add(cell)
                    self.connectors.add(cell)
                elif cell_information[0] == 't':
                    self.electron_tails.add(cell)
                    self.connectors.add(cell)
                elif cell_information[0] == 'a':
                    cell = (int(float(cell_information[1])), int(float(cell_information[2])), int(float(cell_information[3])))
                    self.addConnectorsPos.add(cell)
                elif cell_information[0] == 'g':
                    cell = (int(float(cell_information[1])), int(float(cell_information[2])), cell_information[3])
                    self.clickGenerators.add(cell)
                elif cell_information[0] == 'e':
                    cell = (int(float(cell_information[1])), int(float(cell_information[2])))
                    self.endBlocks.add(cell)
            input_file.close()
        except Exception as error:
            print(error)

    @staticmethod
    def get_n_cells(cell):
        """
        Возвращает позиции 8 соседних клеток к данной

        :param cell: клетка, вокруг которой надо найти соседние
        :type cell: tuple
        """
        px, py = cell
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

    def update(self, rendering_time, delta_time):
        """
        Полное обновление клеточного автомата с учотом времени между рендерингом

        :param rendering_time: время между рендерингом
        :type rendering_time: int
        :param delta_time: время между прошлым и нынешним кадром
        :type delta_time: int
        """
        if SYNCHRONIZATION:
            self.delta_time += delta_time
            if self.delta_time >= rendering_time:
                self.delta_time %= rendering_time
                self.render()
        else:
            self.render()

    def count_n_heads(self, cell):
        """
        Возвращает колличество соседних электронов вокруг данной клетки

        :param cell: клетка, вокруг которой надо посчитать соседние
        :type cell: tuple
        :return: колличество соседних электронов
        :rtype: int
        """
        res = 0
        for cell in WireWorld.get_n_cells(cell):
            if cell in self.electron_heads:
                res += 1
        return res

    def render_n_cells(self, cell):
        """
        Обновляет состояния соседних клеток к данной
        :param cell: клетка, вокруг которой будут обновлятся соседние
        :type cell: tuple
        """
        for n_cell in WireWorld.get_n_cells(cell):
            if n_cell in self.connectors and \
                    n_cell not in self.electron_tails and \
                    n_cell not in self.electron_heads:
                n_heads_count = self.count_n_heads(n_cell)
                if n_heads_count == 1 or n_heads_count == 2:
                    self.f_electron_heads.add(n_cell)

    def render(self):
        """Полное обновление клеточного автомата"""
        for head in self.electron_heads:
            self.render_n_cells(head)
        self.electron_tails = self.electron_heads
        self.electron_heads = self.f_electron_heads
        self.f_electron_heads = set()

    def draw_one_type_cells(self, sc, cells, color, indent_x, indent_y, tile):
        """
        Отрисока клеток одного типа

        :param sc: экран отрисовки
        :param cells: отрисовывающиеся клетки
        :type cells: set
        :param color: цвет клеток
        :type color: tuple
        :param indent_x: отступ по оси x
        :type indent_x: int
        :param indent_y: отступ по оси y
        :type indent_y: int
        :param tile: размер клетки
        :type tile: int
        """
        for cell in cells:
            cell_x, cell_y = cell[0], cell[1]
            if len(cell) > 2:
                pg.draw.rect(sc, color, (cell_x * tile + indent_x, cell_y * tile + indent_y, tile + 1, tile + 1))
                f1 = pg.font.Font(None, int(tile))
                if cell[2] != 'E':
                    text1 = f1.render(str(cell[2]), True,
                                      (0, 255, 0))
                else:
                    text1 = f1.render(str(cell[2]), True,
                                      (255, 0, 0))
                sc.blit(text1, (cell_x * tile + indent_x, cell_y * tile + indent_y))
            else:
                pg.draw.rect(sc, color, (cell_x * tile + indent_x, cell_y * tile + indent_y, tile + 1, tile + 1))

    @staticmethod
    def draw_grid(sc, indent_x, indent_y, tile):
        """
        Отрисока задней сетки

        :param sc: экран отрисовки
        :param indent_x: отступ по оси x
        :type indent_x: int
        :param indent_y: отступ по оси y
        :type indent_y: int
        :param tile: размер клетки
        :type tile: int
        """
        first_h = indent_x % tile
        for horizontal in range(int(sc.get_width() / tile) + 1):
            px = first_h + horizontal * tile
            pg.draw.line(sc, GRID_COLOR, (px, 0), (px, sc.get_height()))
        first_v = indent_y % tile
        for vertical in range(int(sc.get_width() / tile) + 1):
            py = first_v + vertical * tile
            pg.draw.line(sc, GRID_COLOR, (0, py), (sc.get_width(), py))

    def draw_chosen_cell(self, sc, cell, cell_type, indent_x, indent_y, tile):
        """
        Отрисовка выбранной клетки

        :param sc: экран отрисовки
        :param cell: позиция выбранной клетки
        :type cell: tuple
        :param cell_type: вид выбранной кдетки
        :type cell_type: int
        :type indent_x: int
        :param indent_y: отступ по оси y
        :type indent_y: int
        :param tile: размер клетки
        :type tile: int
        """
        if pg.mouse.get_focused():
            cell_x, cell_y = cell
            side = tile * CHOSEN_CELL_SIDE + 1
            color = WW_COLORS[cell_type]
            cell_x = cell_x * tile + indent_x + tile * (1 - CHOSEN_CELL_SIDE) / 2
            cell_y = cell_y * tile + indent_y + tile * (1 - CHOSEN_CELL_SIDE) / 2
            pg.draw.rect(sc, color, (cell_x, cell_y, side, side))

    def draw(self, user, sc):
        """
        Отрисовка кдеточного поля

        :param user: пользователь клеточным автоматом
        :param sc: экран отрисовки
        """
        tile = user.tile
        indent_x, indent_y = user.get_indent()
        self.draw_one_type_cells(sc, self.connectors, WW_CONNECTORS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.electron_heads, WW_ELECTRON_HEADS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.electron_tails, WW_ELECTRON_TAILS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.addConnectorsPos, WW_ADD_CONNECTORS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.clickGenerators, WW_GENERATOR_COLOR, indent_x, indent_y,
                                             tile)
        self.draw_one_type_cells(sc, self.endBlocks, WW_END_BLOCK_COLOR, indent_x, indent_y,
                                             tile)
        self.draw_chosen_cell(sc, user.chosen_cell, user.chosen_type, indent_x, indent_y, tile)
        if tile > 6:
            self.draw_grid(sc, indent_x, indent_y, tile)

    def save(self, name):
        """
        Сохранеие уровня
        """
        file = open(f'levels/user/{name}.txt', 'w')
        for cell in self.connectors:
            file.write('c ' + ' '.join(list(map(str, cell))) + '\n')
        for cell in self.electron_heads:
            file.write('h ' + ' '.join(list(map(str, cell))) + '\n')
        for cell in self.electron_tails:
            file.write('t ' + ' '.join(list(map(str, cell))) + '\n')
        for cell in self.addConnectorsPos:
            file.write('a ' + ' '.join(list(map(str, cell))) + '\n')
        for cell in self.clickGenerators:
            file.write('g ' + ' '.join(list(map(str, cell))) + '\n')
        for cell in self.endBlocks:
            file.write('e ' + ' '.join(list(map(str, cell))) + '\n')
        file.close()


class WW_Runner_WireWorld(WireWorld):
    def __init__(self, player, level=0):
        """
        Инициализация

        :param self.player: обьект текушего игрока
        :type self.player: WW_Runner_Player
        :param self.connectors: set который содержит координаты x и y всех коннекторов на поле
        :type self.connectors: set
        """
        super().__init__()
        self.toClickImage = load_image("clickHere.png")
        self.player = player
        self.read_from_file(f'levels/developer/{level}.txt')
        self.x, self.y = 0, 0
        for start in self.clickGenerators:
            self.x, self.y = start[:2]
            self.x *= self.player.tile
            self.y *= self.player.tile
            self.player.indent_x = -self.x + 3 * self.player.tile
            self.player.indent_y = -self.y + (HEIGHT // self.player.tile // 2) * self.player.tile
            break

    def draw_one_type_cells(self, sc, cells, color, indent_x, indent_y, tile):
        """
        Отрисока клеток одного типа

        :param sc: экран отрисовки
        :param cells: отрисовывающиеся клетки
        :type cells: set
        :param color: цвет клеток
        :type color: tuple
        :param indent_x: отступ по оси x
        :type indent_x: int
        :param indent_y: отступ по оси y
        :type indent_y: int
        :param tile: размер клетки
        :type tile: int
        """
        cell_to_remove = []
        for cell in cells:
            cell_x, cell_y = cell[0], cell[1]
            if cell_x >= -self.player.indent_x // tile:
                if len(cell) > 2:
                    pg.draw.rect(sc, color, (cell_x * tile + indent_x, cell_y * tile + indent_y, tile + 1, tile + 1))
                    f1 = pg.font.Font(None, int(tile))
                    if cell[2] != 'E':
                        text1 = f1.render(str(cell[2]), True,
                                          (0, 255, 0))
                    else:
                        text1 = f1.render(str(cell[2]), True,
                                          (255, 0, 0))
                    sc.blit(text1, (cell_x * tile + indent_x, cell_y * tile + indent_y))
                else:
                    pg.draw.rect(sc, color, (cell_x * tile + indent_x, cell_y * tile + indent_y, tile + 1, tile + 1))
            else:
                cell_to_remove.append(cell)
        for cell in cell_to_remove:
            cells.remove(cell)

    def draw(self, user, sc):
        """
        Отрисовка кдеточного поля

        :param user: пользователь клеточным автоматом
        :param sc: экран отрисовки
        """
        tile = user.tile
        indent_x, indent_y = user.get_indent()
        self.draw_one_type_cells(sc, self.connectors, WW_CONNECTORS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.electron_heads, WW_ELECTRON_HEADS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.electron_tails, WW_ELECTRON_TAILS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.addConnectorsPos, WW_ADD_CONNECTORS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.clickGenerators, WW_GENERATOR_COLOR, indent_x, indent_y,
                                             tile)
        self.draw_one_type_cells(sc, self.endBlocks, WW_END_BLOCK_COLOR, indent_x, indent_y,
                                             tile)
        self.draw_chosen_cell(sc, user.chosen_cell, user.chosen_type, indent_x, indent_y, tile)
        if tile > 6:
            self.draw_grid(sc, indent_x, indent_y, tile)
        if self.player.started == False:
            sc.blit(self.toClickImage, (self.x + indent_x - 130, self.y + indent_y + self.player.tile))

    def render_n_cells(self, cell):
        """
        Обновляет состояния соседних клеток к данной
        :param cell: клетка, вокруг которой будут обновлятся соседние
        :type cell: tuple
        """
        cell_to_remove = []
        for n_cell in WireWorld.get_n_cells(cell):
            if n_cell in self.connectors and \
                    n_cell not in self.electron_tails and \
                    n_cell not in self.electron_heads:
                n_heads_count = self.count_n_heads(n_cell)
                if n_heads_count == 1 or n_heads_count == 2:
                    self.f_electron_heads.add(n_cell)
            for cell in self.addConnectorsPos:
                if n_cell == cell[:2]:
                    self.player.how_much_connectors_are_left_to_place += cell[2]
                    cell_to_remove.append(cell)
            for cell in self.endBlocks:
                if n_cell == cell[:2]:
                    self.player.win = True
        for cell in cell_to_remove:
            self.addConnectorsPos.remove(cell)

    def render(self):
        """Полное обновление клеточного автомата"""
        for head in self.electron_heads:
            self.render_n_cells(head)
        self.electron_tails = self.electron_heads
        self.electron_heads = self.f_electron_heads
        self.f_electron_heads = set()


class WW_Level_Creator(WireWorld):
    def __init__(self):
        """Инициализация"""
        super().__init__()


class Infinity_Ruunner_World(WireWorld):
    def __init__(self, player):
        """Инициализация"""
        super().__init__()
        self.toClickImage = load_image("clickHere.png")
        self.player = player
        self.mainRoot = []
        self.roots = []
        self.connectorsLeftToPlace = self.player.how_much_connectors_are_left_to_place
        self.read_from_file(f'levels/developer/RunnerStart.txt')
        for start in self.clickGenerators:
            self.x, self.y = start[:2]
            self.x *= self.player.tile
            self.y *= self.player.tile
            self.player.indent_x = -self.x + 3 * self.player.tile
            self.player.indent_y = -self.y + (HEIGHT // self.player.tile // 2) * self.player.tile
            break
        self.mainRoot = self.connectors.pop()
        print(self.mainRoot)
        self.mainRoot = [self.mainRoot[0] - 1, self.mainRoot[1], 0]
        self.y //= self.player.tile
        self.didntPlaceRoot = 0
        self.timeCellNotPassed = 0
        self.timeToSpeedUpdate = 0

    def render_n_cells(self, cell):
        """
        Обновляет состояния соседних клеток к данной
        :param cell: клетка, вокруг которой будут обновлятся соседние
        :type cell: tuple
        """
        cell_to_remove = []
        for n_cell in WireWorld.get_n_cells(cell):
            if n_cell in self.connectors and \
                    n_cell not in self.electron_tails and \
                    n_cell not in self.electron_heads:
                n_heads_count = self.count_n_heads(n_cell)
                if n_heads_count == 1 or n_heads_count == 2:
                    self.f_electron_heads.add(n_cell)
            for cell in self.addConnectorsPos:
                if n_cell == cell[:2]:
                    play_sound('sound/mixkit-futuristic-robotic-fast-sweep-171.wav')
                    self.player.how_much_connectors_are_left_to_place += cell[2]
                    self.connectorsLeftToPlace += 10 - 2
                    self.timeCellNotPassed += 1
                    cell_to_remove.append(cell)
            for cell in self.endBlocks:
                if n_cell == cell[:2]:
                    self.player.win = True
        for cell in cell_to_remove:
            self.addConnectorsPos.remove(cell)

    def draw_one_type_cells(self, sc, cells, color, indent_x, indent_y, tile):
        """
        Отрисока клеток одного типа

        :param sc: экран отрисовки
        :param cells: отрисовывающиеся клетки
        :type cells: set
        :param color: цвет клеток
        :type color: tuple
        :param indent_x: отступ по оси x
        :type indent_x: int
        :param indent_y: отступ по оси y
        :type indent_y: int
        :param tile: размер клетки
        :type tile: int
        """
        cell_to_remove = []
        for cell in cells:
            cell_x, cell_y = cell[0], cell[1]
            if cell_x >= -self.player.indent_x // tile:
                if len(cell) > 2:
                    pg.draw.rect(sc, color, (cell_x * tile + indent_x, cell_y * tile + indent_y, tile + 1, tile + 1))
                    f1 = pg.font.Font(None, int(tile))
                    if cell[2] != 'E':
                        text1 = f1.render(str(cell[2]), True,
                                          (0, 255, 0))
                    else:
                        text1 = f1.render(str(cell[2]), True,
                                          (255, 0, 0))
                    sc.blit(text1, (cell_x * tile + indent_x, cell_y * tile + indent_y))
                else:
                    pg.draw.rect(sc, color, (cell_x * tile + indent_x, cell_y * tile + indent_y, tile + 1, tile + 1))
            else:
                cell_to_remove.append(cell)
                if len(cell) > 2:
                    if cell[2] != 'E':
                        self.timeCellNotPassed = 0
        for cell in cell_to_remove:
            cells.remove(cell)

    def draw(self, user, sc):
        """
        Отрисовка кдеточного поля

        :param user: пользователь клеточным автоматом
        :param sc: экран отрисовки
        """
        tile = user.tile
        indent_x, indent_y = user.get_indent()
        self.draw_one_type_cells(sc, self.connectors, WW_CONNECTORS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.electron_heads, WW_ELECTRON_HEADS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.electron_tails, WW_ELECTRON_TAILS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.addConnectorsPos, WW_ADD_CONNECTORS_COLOR, indent_x, indent_y, tile)
        self.draw_one_type_cells(sc, self.clickGenerators, WW_GENERATOR_COLOR, indent_x, indent_y,
                                             tile)
        self.draw_one_type_cells(sc, self.endBlocks, WW_END_BLOCK_COLOR, indent_x, indent_y,
                                             tile)
        self.draw_chosen_cell(sc, user.chosen_cell, user.chosen_type, indent_x, indent_y, tile)
        if tile > 6:
            self.draw_grid(sc, indent_x, indent_y, tile)
        if self.player.started == False:
            sc.blit(self.toClickImage, (self.x + indent_x - 130, self.y * self.player.tile + indent_y + self.player.tile))

    def generate_new_paths(self):
        blank = 0
        if self.timeCellNotPassed > 5:
            self.timeCellNotPassed = 0
            self.connectorsLeftToPlace = max(0, self.player.how_much_connectors_are_left_to_place - 2)
        if self.connectorsLeftToPlace > 0:
            blank = 1 if random.randint(0, 10 + max(self.connectorsLeftToPlace // 3, 10) - 10) >= max(3, 8 - self.mainRoot[
                2]) else 0
            if blank == 1:
                self.connectorsLeftToPlace -= 1
        if blank == 0:
            self.connectors.add((self.mainRoot[0], self.mainRoot[1]))
        if random.randint(0, 8) == 7:
            turn = random.choice([-1, 1])
            self.mainRoot = (self.mainRoot[0] + 1, self.mainRoot[1] + turn if self.y + (HEIGHT // self.player.tile // 2) - 3 > (self.mainRoot[1] + turn) > self.y - (HEIGHT // self.player.tile // 2) + 3 else self.mainRoot[1], 0 if blank == 0 else self.mainRoot[2] + 1)
        else:
            self.mainRoot = (self.mainRoot[0] + 1, self.mainRoot[1], 0 if blank == 0 else self.mainRoot[2] + 1)
        addnewRoot = random.randint(0, 10)
        if addnewRoot >= 9 and self.didntPlaceRoot > 5:
            self.didntPlaceRoot = 0
            turn = random.choice([-1, 1])
            self.roots.append((self.mainRoot[0], self.mainRoot[1] + turn, 1, turn, 0))
        newRoots = []
        for root in self.roots:
            if root[2] > 3:
                end = random.randint(1, 8)
            else:
                end = 0
            if end >= 7:
                self.connectorsLeftToPlace += 2
                self.addConnectorsPos.add((root[0], root[1], 10))
            else:
                if root[4] <= 0:
                    self.connectors.add((root[0], root[1]))
                turn = random.choice([-1, 0, 1])
                blank = 0
                if (self.connectorsLeftToPlace - 1) >= 0:
                    blank = 1 if random.randint(0, 10 + max(self.connectorsLeftToPlace // 3, 10) - 10) >= max(3, 8 - root[4]) else 0
                    if blank == 1:
                        self.connectorsLeftToPlace -= 1
                if root[1] + turn < self.y + (HEIGHT // self.player.tile // 2) > root[1] + turn > self.y - (HEIGHT // self.player.tile // 2):
                    if (root[3] == -1 and root[1] == self.mainRoot[1]):
                        newRoots.append((root[0], root[1] - 1, root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
                    elif (root[3] == -1 and root[1] == self.mainRoot[1] - 1):
                        newRoots.append((root[0] + 1, root[1] - 1, root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
                    elif (root[3] == 1 and root[1] == self.mainRoot[1]):
                        newRoots.append((root[0], root[1] + 1, root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
                    elif (root[3] == 1 and root[1] == self.mainRoot[1] + 1):
                        newRoots.append((root[0] + 1, root[1] + 1, root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
                    elif (root[3] == -1 and root[1] + turn == self.mainRoot[1] - 1):
                        newRoots.append((root[0] + 1, root[1], root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
                    elif (root[3] == 1 and root[1] + turn == self.mainRoot[1] + 1):
                        newRoots.append((root[0] + 1, root[1], root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
                    else:
                        newRoots.append((root[0] + 1, root[1] + turn, root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
                else:
                    newRoots.append((root[0] + 1, root[1] + 0, root[2] + 1, root[3], 0 if blank == 0 else root[4] + 1))
        self.didntPlaceRoot += 1
        self.roots = newRoots

    def update(self, rendering_time, delta_time):
        """
        Полное обновление клеточного автомата с учотом времени между рендерингом

        :param rendering_time: время между рендерингом
        :type rendering_time: int
        :param delta_time: время между прошлым и нынешним кадром
        :type delta_time: int
        """
        if SYNCHRONIZATION:
            self.delta_time += delta_time
            if self.delta_time >= rendering_time:
                self.connectors.add((4.0, 10.0))
                self.timeToSpeedUpdate += 1
                if self.timeToSpeedUpdate == 30:
                    self.player.rendering_time -= 2
                    self.timeToSpeedUpdate = 0
                self.delta_time %= rendering_time
                self.render()
        else:
            self.render()
