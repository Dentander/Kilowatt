from blur import Blur
from config import *


class ViewBlock:
    def __init__(self, header, info, y=140):
        """
        инициализация
        :param header: заголовок таблици
        :param info: инфоррмация таблици(словарь)
        :param y: сдвиг пооси y
        """

        # заголовок
        self.h_f_size = 60
        self.header_font = pg.font.SysFont('cmmi10', self.h_f_size)
        self.header = self.header_font.render(header, True, BLACK)
        self.header_text = header
        self.header_indent = 10

        # линия
        self.line_w_scale = 0.85

        # информация
        self.i_f_size = 30
        self.info = info
        self.info_font = pg.font.SysFont('cmmi10', self.i_f_size)
        self.dist_between_info = 7
        self.info_c_scale = 0.27

        # transform
        self.y = y
        self.height = self.header.get_height() + \
                      self.header_indent + len(self.info) * (self.info_font.get_height() + self.dist_between_info)
        self.bg_indent = 20

        # effects
        self.blur = Blur()

        self.scale = 1

    def update_and_draw_header(self, sc, min_scale):
        """
        Рисование и обновление заголовка
        :param sc: экран на котором рисуется таблица
        :param min_scale: мин из scale_x и scale_y
        :return:
        """
        w, h = sc.get_size()
        # update
        if min_scale != self.scale:
            self.header_font = pg.font.SysFont('cmmi10', int(self.h_f_size * min_scale))
            self.header = self.header_font.render(self.header_text, True, BLACK)

        # draw
        r = self.header.get_rect()
        sc.blit(self.header, ((w - r.width) // 2, self.y * min_scale))
        line_x = self.y * min_scale + r.height
        pg.draw.line(sc, SKY_BLUE, ((1 - self.line_w_scale) * w, line_x + self.header_indent * min_scale ),
                     (self.line_w_scale * w, line_x + self.header_indent * min_scale),
                     int(4 * min_scale))

    def update_and_draw_background(self, sc, min_scale):
        """
        Рисование и обновление информации таблици
        :param sc: экран на котором рисуется таблица
        :param min_scale: мин из scale_x и scale_y
        :return:
        """
        pg.draw.rect(sc, LIGHT_BLUE, (0, (self.y -  self.bg_indent) * min_scale, sc.get_width(),
                                         (self.height + 2 *  self.bg_indent) * min_scale))

    def update_and_draw_info(self, sc, min_scale):
        """
        Рисование и обновление информации таблици
        :param sc: экран на котором рисуется таблица
        :param min_scale: мин из scale_x и scale_y
        :return:
        """
        # update
        w, h = sc.get_size()

        if min_scale != self.scale:
            self.info_font = pg.font.SysFont('cmmi10', int(self.i_f_size * min_scale))

        # draw
        pos_y = self.y * min_scale + self.header.get_rect().height + \
                (self.dist_between_info + self.header_indent + 5) * min_scale
        for item in self.info.items():
            text1 = self.info_font.render(item[0], True, BLACK)
            text2 = self.info_font.render(item[1], True, BLACK)

            sc.blit(text1, (w * self.info_c_scale - text1.get_rect().width // 2, pos_y))
            sc.blit(text2, ((w - w * self.info_c_scale) - text2.get_rect().width // 2, pos_y))

            pos_y += text1.get_rect().height + self.dist_between_info * min_scale

    def update_and_draw(self, sc, min_scale, state='controls menu'):
        """
        Рисование и обновление таблици
        :param state: состояние меню (главное или к примеру меню управления и тд)
        :param sc: экран на котором рисуется таблица
        :param min_scale: мин из scale_x и scale_y
        :return:
        """
        if state == 'controls menu':
            self.blur.blur(sc)
            self.update_and_draw_background(sc, min_scale)
            self.update_and_draw_header(sc, min_scale)
            self.update_and_draw_info(sc, min_scale)
            self.scale = min_scale
