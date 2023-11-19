from config import *


class ColorBlock:
    """Класс для отрисовки блока цветов в меню цветов"""
    def __int__(self, color1, color2, color3, w, h, x, y):
        """
        Инициализация
        :param color1: цвет конектора
        :param color2: цвет электрона
        :param color3: цвет хвоста электрона
        :param w: ширина
        :param h: высота
        :param x: x
        :param y: y
        :return:
        """
        # transform
        self.w, self.h, self.x, self.y = w, h, x, y
        # colors
        self.colors = [color1, color2, color3]
        self.dist_between_colors = 10
        self.color_width = (self.w - 2 * self.dist_between_colors) / 3
        # effects
        self.is_chosen = False

    def update_and_draw(self, sc, min_scale, scale_x, scale_y):
        """
        Рисование и обновление блока
        :param sc: экран на котором рисуется таблица
        :param min_scale: мин из scale_x и scale_y
        :param scale_x:
        :param scale_y:
        :return:
        """
        if self.is_chosen:
            pg.draw.rect(sc, LIGHT_BLUE,
                         (self.w * min_scale, self.h * min_scale, self.x * scale_x, self.y * scale_y))

        for i in range(len(self.colors)):
            x = self.x + (self.dist_between_colors + self.color_width) * i
            pg.draw.rect(sc, self.colors[0],
                         (self.color_width * min_scale, self.h * min_scale, x * scale_x, self.y * scale_y))


class ColorMenu:
    def __int__(self):
        pass

    def update_and_draw(self, sc):
        pass
