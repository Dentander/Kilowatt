from numpy import sign

def Coords_on_screen(x_cell,y_cell,user):
    """
    Возвращает координаты центра клетки на экране

    :param x_cell: положение клетки по Х
    :type x_cell: int
    :param y_cell: положение клетки по Y
    :type y_cell: int
    :param user: user
    :type user: user
    :return: Координаты центра клетки на экране
    :rtype: list of two int

    """
    dist_x,dist_y = x_cell * user.tile + user.tile/2,y_cell * user.tile + user.tile/2
    x, y = user.indent_x + dist_x, user.indent_y + dist_y
    return [x, y]

def end_coord_of_sel_rect(start_sel_cell_x,start_sel_cell_y,end_sel_cell_x,end_sel_cell_y,user):
    """
        Возвращает числа, необходимые для рисования границы выделения

        :param start_sel_cell_x: положение стартовой клетки по Х
        :type start_sel_cell_x: int
        :param start_sel_cell_y: положение стартовой клетки по Y
        :type start_sel_cell_y: int
        :param end_sel_cell_x: положение конечной клетки по Х
        :type end_sel_cell_x: int
        :param end_sel_cell_y: положение конечной клетки по Y
        :type end_sel_cell_y: int
        :param user: user
        :type user: user
        :return: размеры по высоте/ширине
        :rtype: list of two int

        """
    st_x, st_y = Coords_on_screen(start_sel_cell_x, start_sel_cell_y, user)
    en_x, en_y = Coords_on_screen(end_sel_cell_x, end_sel_cell_y, user)
    return en_x - st_x, en_y - st_y

def Delete_cells(start_cell_x, start_cell_y, end_cell_x, end_cell_y,user,wire_world):
    """
            Удаляет клетки в заданном диапазоне

            :param start_sel_cell_x: положение стартовой клетки по Х
            :type start_sel_cell_x: int
            :param start_sel_cell_y: положение стартовой клетки по Y
            :type start_sel_cell_y: int
            :param end_sel_cell_x: положение конечной клетки по Х
            :type end_sel_cell_x: int
            :param end_sel_cell_y: положение конечной клетки по Y
            :type end_sel_cell_y: int
            :param user: user
            :type user: user
            :return: WW с удалёнными клетками
            :rtype: WireWorld

            """
    if start_cell_x < end_cell_x:
        upper_end, lower_end = int(start_cell_x),int(end_cell_x)
    else:
        upper_end, lower_end = int(end_cell_x), int(start_cell_x)

    if start_cell_y < end_cell_y:
        left_end, right_end = int(start_cell_y),int(end_cell_y)
    else:
        left_end, right_end = int(end_cell_y), int(start_cell_y)

    for cell_x in range(upper_end, lower_end+1):
        for cell_y in range(left_end, right_end+1):
            cell = cell_x, cell_y

            user.remove_from_ca(wire_world.connectors, cell)
            user.remove_from_ca(wire_world.electron_heads, cell)
            user.remove_from_ca(wire_world.electron_tails, cell)

    return(wire_world)


def Draw_line(x_start, y_start, x_end, y_end, user, wire_world):
    """
    Сам алгоритм рисования линии.

    :param x_start: стартовое положение клетки по Х
    :type x_start: int
    :param y_start: стартовое положение клетки по Y
    :type y_start: int
    :param x_end: конченое положение клетки по Х
    :type x_end: int
    :param y_end: конченое положение клетки по Y
    :type y_end: int
    :param user: user
    :type user: user
    :param wire_world: wire_world
    :type wire_world: wire_world
    :return: Возвращает поле с проведённой линией
    :rtype: WireWorld

    """
    dx = x_end - x_start
    dy = y_end - y_start

    sign_x = sign(dx)
    sign_y = sign(dy)

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        pdx, pdy = sign_x, 0
        es, el = dy, dx
    else:
        pdx, pdy = 0, sign_y
        es, el = dx, dy

    x, y = x_start, y_start

    error, t = el / 2, 0

    cell = x,y

    if user.chosen_type == 0:
        wire_world.connectors.add(cell)
    if user.chosen_type == 1:
        wire_world.electron_heads.add(cell)
    if user.chosen_type == 2:
        wire_world.electron_tails.add(cell)
    if user.chosen_type == 3:
        user.remove_from_ca(wire_world.connectors, cell)
        user.remove_from_ca(wire_world.electron_heads, cell)
        user.remove_from_ca(wire_world.electron_tails, cell)

    while t < el:
        error -= es
        if error < 0:
            error += el
            x += sign_x
            y += sign_y
        else:
            x += pdx
            y += pdy
        t += 1
        cell = x, y
        if user.chosen_type == 0:
            wire_world.connectors.add(cell)
        if user.chosen_type == 1:
            wire_world.electron_heads.add(cell)
        if user.chosen_type == 2:
            wire_world.electron_tails.add(cell)
        if user.chosen_type == 3:
            user.remove_from_ca(wire_world.connectors, cell)
            user.remove_from_ca(wire_world.electron_heads, cell)
            user.remove_from_ca(wire_world.electron_tails, cell)

    return wire_world
