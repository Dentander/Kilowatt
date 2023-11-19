from config import *


class WW_Editor_User:
    """Пользователь редактора WireWorld"""

    def __init__(self):
        """
        Инициализация

        :param self.indent_x: сдвиг камеры по оси x
        :type self.indent_x: float
        :param self.indent_y: сдвиг камеры по оси y
        :type self.indent_y: float
        :param self.speed: скорость камеры
        :type self.speed: float
        :param self.tile: размер клеток
        :type self.tile: float
        :param self.chosen_cell: координаты текущей клетки на поле
        :type self.chosen_cell: tuple
        :param self.chosen_type: тип выбранной клетки
        :type self.chosen_type: int
        :param self.rendering_time: время рендера
        :type self.rendering_time: int
        """
        self.indent_x, self.indent_y = 0, 0
        self.pmx, self.pmy = False, False
        self.speed = MOVE_SPEED
        self.tile = DEF_TILE
        self.chosen_cell = 0, 0
        self.chosen_type = 0
        self.rendering_time = RENDERING_TIME

    def get_indent(self):
        """
        Возврашает отступ на экране, для отображения клеточного автомата

        :return: отступ на экране, для отображения клеточного автомата
        :rtype: tuple
        """
        return self.indent_x, self.indent_y

    def mouse_wheel_control(self, button):
        """
        Удаление и приближение к полю колёсиком мыши, переключение выбранного типа клетки

        :param button: нажатые кнопки мыши
        :type button: list
        """
        keys = pg.key.get_pressed()
        mouse_x, mouse_y = pg.mouse.get_pos()
        dist_x, dist_y = mouse_x - self.indent_x, mouse_y - self.indent_y
        new_tile = self.tile
        if keys[pg.K_LSHIFT]:
            if button == 4:
                self.chosen_type += 1
            if button == 5:
                self.chosen_type -= 1
            self.chosen_type %= 4
        else:
            if button == 4 and self.tile + self.tile / DEF_TILE * TILE_SPEED <= MAX_TILE:
                new_tile += self.tile / DEF_TILE * TILE_SPEED
            if button == 5 and self.tile - self.tile / DEF_TILE * TILE_SPEED >= MIN_TILE:
                new_tile -= self.tile / DEF_TILE * TILE_SPEED
        self.indent_x += dist_x - dist_x * new_tile / self.tile
        self.indent_y += dist_y - dist_y * new_tile / self.tile
        self.tile = new_tile

    @staticmethod
    def remove_from_ca(cells, cell):
        """
        Безопасное удаление клетки из списка клеток 1ого типа

        :param cells: список клеток
        :type cells: set
        :param cell: клетка, которую надо удалить
        :type cell: tuple
        """
        if cell in cells:
            cells.remove(cell)

    def mouse_update(self, wire_world, mouseOnOtherObject=False):
        """
        Управление передвижением и стонавлением выбранной клетки

        :param wire_world: WireWorld
        """
        mouse = pg.mouse.get_pressed()
        if mouse[2] and self.pmx and self.pmy:
            amx, amy = pg.mouse.get_pos()
            self.indent_x += (amx - self.pmx)
            self.indent_y += (amy - self.pmy)
            self.pmx, self.pmy = amx, amy
        elif mouse[2]:
            self.pmx, self.pmy = pg.mouse.get_pos()
        else:
            self.pmx, self.pmy = False, False

        if mouse[0] and not mouseOnOtherObject:
            if self.chosen_type == 0:
                wire_world.connectors.add(self.chosen_cell)
            if self.chosen_type == 1:
                wire_world.electron_heads.add(self.chosen_cell)
            if self.chosen_type == 2:
                wire_world.electron_tails.add(self.chosen_cell)
            if self.chosen_type == 3:
                WW_Editor_User.remove_from_ca(wire_world.connectors, self.chosen_cell)
                WW_Editor_User.remove_from_ca(wire_world.electron_heads, self.chosen_cell)
                WW_Editor_User.remove_from_ca(wire_world.electron_tails, self.chosen_cell)
            if self.chosen_type == 3:
                WW_Editor_User.remove_from_ca(wire_world.addConnectorsPos,
                                              (self.chosen_cell[0], self.chosen_cell[1], 10))
                WW_Editor_User.remove_from_ca(wire_world.clickGenerators,
                                              (self.chosen_cell[0], self.chosen_cell[1], 'E'))
                WW_Editor_User.remove_from_ca(wire_world.connectors, self.chosen_cell)
                WW_Editor_User.remove_from_ca(wire_world.electron_heads, self.chosen_cell)
                WW_Editor_User.remove_from_ca(wire_world.electron_tails, self.chosen_cell)
                WW_Editor_User.remove_from_ca(wire_world.endBlocks, self.chosen_cell)
            if self.chosen_type == 4:
                wire_world.addConnectorsPos.add((self.chosen_cell[0], self.chosen_cell[1], 10))
            if self.chosen_type == 5:
                wire_world.clickGenerators.add((self.chosen_cell[0], self.chosen_cell[1], 'E'))
            if self.chosen_type == 6:
                wire_world.endBlocks.add(self.chosen_cell)

    def keys_update(self, delta_time):
        """
        Управление перемещением пользователя по полю с помощью клавиатуры

        :param delta_time: время между прошлым и нынешним кадром
        :type delta_time: int
        """
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.indent_y += self.speed * delta_time * self.tile
        if keys[pg.K_s]:
            self.indent_y -= self.speed * delta_time * self.tile
        if keys[pg.K_a]:
            self.indent_x += self.speed * delta_time * self.tile
        if keys[pg.K_d]:
            self.indent_x -= self.speed * delta_time * self.tile

    def chosen_cell_update(self):
        """Обновление положения выбранной клетки"""
        mouse_x, mouse_y = pg.mouse.get_pos()
        dist_x, dist_y = mouse_x - self.indent_x, mouse_y - self.indent_y
        self.chosen_cell = dist_x // self.tile, dist_y // self.tile

    def update(self, wire_world, delta_time, mouseOnOtherObject=False):
        """
        Полное обновление пользователя

        :param wire_world: WireWorld
        :param delta_time: время между прошлым и нынешним кадром
        :type delta_time: int
        """
        self.mouse_update(wire_world, mouseOnOtherObject)
        self.keys_update(delta_time)
        self.chosen_cell_update()


class WW_Runner_Player(WW_Editor_User):
    def __init__(self):
        super().__init__()
        self.started = False
        self.win = False
        self.how_much_connectors_are_left_to_place = 10
        self.rendering_time = RENDERING_TIME_RUNNER

    def mouse_update(self, wire_world, mouseOnOtherObject=False):
        """
        Управление передвижением и стонавлением выбранной клетки

        :param wire_world: WireWorld
        """
        mouse = pg.mouse.get_pressed()
        if mouse[0] and not mouseOnOtherObject:
            for cell in wire_world.clickGenerators:
                if cell[:2] == self.chosen_cell:
                    wire_world.connectors.add(self.chosen_cell)
                    wire_world.electron_heads.add(self.chosen_cell)
                    wire_world.clickGenerators.remove(cell)
                    self.started = True
                    return
            if not self.started:
                return
            if self.chosen_type == 0:
                if self.chosen_cell not in wire_world.connectors and self.how_much_connectors_are_left_to_place > 0:
                    wire_world.connectors.add(self.chosen_cell)
                    self.how_much_connectors_are_left_to_place -= 1

    def update(self, wire_world, delta_time, mouseOnOtherObject=False, stop=False):
        """
        Полное обновление пользователя

        :param wire_world: WireWorld
        :param delta_time: время между прошлым и нынешним кадром
        :type delta_time: int
        """
        if self.started:
            self.indent_x -= self.tile / self.rendering_time * delta_time
        self.chosen_cell_update()
        self.mouse_update(wire_world, mouseOnOtherObject)

    def mouse_wheel_control(self, button):
        """
        Удаление и приближение к полю колёсиком мыши, переключение выбранного типа клетки

        :param button: нажатые кнопки мыши
        :type button: list
        """
        pass


class WW_Level_Creator_Player(WW_Editor_User):
    def __init__(self):
        super().__init__()

    def mouse_wheel_control(self, button):
        """
        Удаление и приближение к полю колёсиком мыши, переключение выбранного типа клетки

        :param button: нажатые кнопки мыши
        :type button: list
        """
        keys = pg.key.get_pressed()
        mouse_x, mouse_y = pg.mouse.get_pos()
        dist_x, dist_y = mouse_x - self.indent_x, mouse_y - self.indent_y
        new_tile = self.tile
        if keys[pg.K_LSHIFT]:
            if button == 4:
                self.chosen_type += 1
            if button == 5:
                self.chosen_type -= 1
            self.chosen_type %= 7
        else:
            if button == 4 and self.tile + self.tile / DEF_TILE * TILE_SPEED <= MAX_TILE:
                new_tile += self.tile / DEF_TILE * TILE_SPEED
            if button == 5 and self.tile - self.tile / DEF_TILE * TILE_SPEED >= MIN_TILE:
                new_tile -= self.tile / DEF_TILE * TILE_SPEED
        self.indent_x += dist_x - dist_x * new_tile / self.tile
        self.indent_y += dist_y - dist_y * new_tile / self.tile
        self.tile = new_tile


class WW_Infinity_Runner_Player(WW_Runner_Player):
    def __init__(self):
        super().__init__()
        self.lastTile = -1
        self.rendering_time = RENDERING_TIME_INFINITY_RUNNER

    def update(self, wire_world, delta_time, mouseOnOtherObject=False, stop=False):
        """
        Полное обновление пользователя

        :param wire_world: WireWorld
        :param delta_time: время между прошлым и нынешним кадром
        :type delta_time: int
        """
        if -self.indent_x >= (wire_world.mainRoot[0] - 100) * self.tile and wire_world.mainRoot[0] != self.lastTile:
            self.lastTile = wire_world.mainRoot[0]
            wire_world.generate_new_paths()
        if self.started:
            self.indent_x -= self.tile / self.rendering_time * delta_time
        self.chosen_cell_update()
        self.mouse_update(wire_world, mouseOnOtherObject)