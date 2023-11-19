from config import *
from sound import play_sound


class QuestionWindow:
    def __init__(self, go_content='GAME OVER', btn1_content='menu', btn2_content='restart', background_color=RED):
        """
        Инициализация
        """

        # заголовок
        self.go_font = pg.font.SysFont('cmmi10', int(60 * 1))
        self.go_content = go_content
        self.go_text = self.go_font.render('GAME OVER', True, BLACK)
        self.go_text_h_scale = 0.45 + 0.05

        # кнопки меню и повтора
        self.bn_font = pg.font.SysFont('cmmi10', int(45 * 1))
        self.mb_text = self.bn_font.render(btn1_content, True, BLACK)
        self.btn1_content = btn1_content
        self.rb_text = self.bn_font.render(btn2_content, True, BLACK)
        self.btn2_content = btn2_content
        self.buttons_text_h_scale = 0.76 + 0.05

        # линии по середине
        self.mid_lines_h_scale = 0.6 + 0.05
        self.mid_lines_dit_x = 10
        self.mid_lines_dit_y = 10

        # динамичне линни
        self.d_lines_indent = 0
        self.d_lines_indent_speed = 3

        # задник
        # bra - background red alpha
        self.bra = 0
        self.bra_speed = 0.1
        self.bra_max = 20
        self.bra_color = background_color

        # sound
        self.is_first_update = True
        self.is_menu_button_chosen = True

        self.state = 0
        self.scale = 1
        self.can_be_clicked = False

    def update_and_draw_surf(self, sc, scale_x, scale_y):
        """
        Обновление и отрисовка прозрачных элементов
        :param sc: экран отрисовки
        :param scale_x: отношение изначальной высоты на нынешнюю экрана
        :param scale_y: отношение изначальной ширины на нынешнюю экрана
        :return:
        """
        # update
        if self.bra < self.bra_max:
            self.bra += self.bra_speed
        if self.bra > self.bra_max:
            self.bra = self.bra_max

        # draw
        w, h = sc.get_size()
        mp = pg.mouse.get_pos()

        blue = pg.Surface((w // 2, w - h * self.mid_lines_h_scale))
        blue.fill((0, 206, 235))
        blue.set_alpha(140)
        if mp[0] < w//2:
            sc.blit(blue, (
            -self.mid_lines_dit_x * scale_x * 2, h * self.mid_lines_h_scale + self.mid_lines_dit_y * scale_y * 2))
        else:
            sc.blit(blue, (w // 2 + self.mid_lines_dit_x * scale_x * 2,
                           h * self.mid_lines_h_scale + self.mid_lines_dit_y * scale_y * 2))

        bra = pg.Surface(sc.get_size())
        bra.fill(self.bra_color)
        bra.set_alpha(int(self.bra))
        sc.blit(bra, (0, 0))

    def update_and_draw_go(self, sc, min_scale):
        """
        Обновление и отрисовка прозрачных заголовка
        :param sc: экран отрисовки
        :param min_scale: min(отношение изначальной высоты на нынешнюю экрана, тношение изначальной ширины на нынешнюю экрана)
        :return:
        """
        w, h = sc.get_size()
        # update
        self.go_font = pg.font.SysFont('cmmi10', int(60 * min_scale))
        self.go_text = self.go_font.render(self.go_content, True, BLACK)

        # draw
        r = self.go_text.get_rect()
        sc.blit(self.go_text, ((w - r.width) // 2, h * self.go_text_h_scale))

    def draw_mid_lines(self, sc, scale_x, scale_y, min_scale):
        """
        Отрисовка прозрачных заголовка
        :param sc: экран отрисовки
        :param scale_x: отношение изначальной высоты на нынешнюю экрана
        :param scale_y: отношение изначальной ширины на нынешнюю экрана
        :param min_scale: min(отношение изначальной высоты на нынешнюю экрана, тношение изначальной ширины на нынешнюю экрана)
        :return:
        """
        w, h = sc.get_size()

        lines_h = int(h * self.mid_lines_h_scale)
        mldx, mldy = self.mid_lines_dit_x * scale_x, self.mid_lines_dit_y * scale_y

        pg.draw.line(sc, SKY_BLUE, (w // 2, h), (w // 2, lines_h), int(3 * min_scale))
        pg.draw.line(sc, BLACK, (w // 2 - mldx, h + mldy),
                     (w // 2 - mldx, lines_h + mldy), int(3 * min_scale))
        pg.draw.line(sc, BLACK, (w // 2 + mldx, h + mldy),
                     (w // 2 + mldx, lines_h + mldy), int(3 * min_scale))

    def update_and_draw_dynamic_lines(self, sc, scale_x, scale_y, min_scale, delta_time):
        """
        Отрисовка центральных линий
        :param sc: экран отрисовки
        :param scale_x: отношение изначальной высоты на нынешнюю экрана
        :param scale_y: отношение изначальной ширины на нынешнюю экрана
        :param min_scale: min(отношение изначальной высоты на нынешнюю экрана, тношение изначальной ширины на нынешнюю экрана)
        :param delta_time: время между кадрами
        :return:
        """
        w, h = sc.get_size()
        lines_h = int(h * self.mid_lines_h_scale)

        # update
        mp = pg.mouse.get_pos()
        self.d_lines_indent = self.d_lines_indent
        if mp[0] <= w // 2:
            self.d_lines_indent -= self.d_lines_indent_speed * scale_x * delta_time
            if self.d_lines_indent < 0:
                self.d_lines_indent = 0
        else:
            self.d_lines_indent += self.d_lines_indent_speed * scale_x * delta_time
            if self.d_lines_indent > w // 2:
                self.d_lines_indent = w // 2

        # draw
        # 1
        d = min(w // 2 - self.mid_lines_dit_x * scale_x, self.d_lines_indent + self.mid_lines_dit_x * 7 * scale_x)
        pg.draw.line(sc, SKY_BLUE, (self.d_lines_indent, lines_h), (w // 2, lines_h), int(3 * min_scale))
        pg.draw.line(sc, BLACK, (d, lines_h + self.mid_lines_dit_y * scale_y),
                     (w // 2 - self.mid_lines_dit_x * scale_x, lines_h + self.mid_lines_dit_y * scale_y),
                     int(3 * min_scale))

        # 2
        d = max(w // 2 + self.mid_lines_dit_x * scale_x,
                w // 2 + self.d_lines_indent - self.mid_lines_dit_x * 7 * scale_x)
        pg.draw.line(sc, SKY_BLUE, (w // 2 + self.d_lines_indent, lines_h), (w // 2, lines_h), int(3 * min_scale))
        pg.draw.line(sc, BLACK, (d, lines_h + self.mid_lines_dit_y * scale_y),
                     (w // 2 + self.mid_lines_dit_x * scale_x, lines_h + self.mid_lines_dit_y * scale_y),
                     int(3 * min_scale))

    def update_and_draw_buttons(self, sc, min_scale):
        """
        Отрисовка кнопок
        :param sc: экран отрисовки
        :param min_scale: min(отношение изначальной высоты на нынешнюю экрана, тношение изначальной ширины на нынешнюю экрана)
        :return:
        """
        w, h = sc.get_size()
        mp = pg.mouse.get_pos()
        # update
        self.bn_font = pg.font.SysFont('cmmi10', int(45 * min_scale))
        self.mb_text = self.bn_font.render(self.btn1_content, True, BLACK)
        self.rb_text = self.bn_font.render(self.btn2_content, True, BLACK)

        pressed = pg.mouse.get_pressed()
        if pressed[0] and self.can_be_clicked and mp[1] > h * 0.65:
            play_sound('sound/220166__gameaudio__button-confirm-spacey.wav', 100)
            if mp[0] >= w // 2:
                self.state = 2
            else:
                self.state = 1
        if not pressed[0]:
            self.can_be_clicked = True

        # draw
        r1 = self.mb_text.get_rect()
        r2 = self.rb_text.get_rect()
        sc.blit(self.mb_text, ((w // 2 - r1.width) // 2, h * self.buttons_text_h_scale))
        sc.blit(self.rb_text, (w // 2 + (w // 2 - r2.width) // 2, h * self.buttons_text_h_scale))

    def sound_update(self, sc):
        """
        Обновление звука
        :param sc: экран отрисовки
        :return:
        """
        w, h = sc.get_size()
        mp = pg.mouse.get_pos()
        if self.is_first_update:
            # play_sound('sound/game_over.mp3')
            self.is_first_update = False
        if self.is_menu_button_chosen == (mp[0] <= w//2):
            play_sound('sound/button_click_v2.wav')
        self.is_menu_button_chosen = not (mp[0] <= w // 2)

    def update_and_draw(self, sc, scale_x, scale_y, delta_time):
        """
        Отрисовка
        :param sc: экран отрисовки
        :param scale_x: отношение изначальной высоты на нынешнюю экрана
        :param scale_y: отношение изначальной ширины на нынешнюю экрана
        :param delta_time: время между кадрами
        :return:
        """

        self.state = 0
        min_scale = min(scale_x, scale_y)

        self.update_and_draw_surf(sc, scale_x, scale_y)
        self.update_and_draw_go(sc, min_scale)
        self.draw_mid_lines(sc, scale_x, scale_y, min_scale)
        self.update_and_draw_dynamic_lines(sc, scale_x, scale_y, min_scale, delta_time)
        self.update_and_draw_buttons(sc, min_scale)
        self.sound_update(sc)

        self.scale = min_scale
        # self.state:
        # 0 - nothing
        # 1 - left clicked
        # 2 - right-clicked
        return self.state
