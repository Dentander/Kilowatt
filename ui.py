from collisons import dot_cube_collision
from config import *
from image_loader import load_image
from sound import play_sound
from user import WW_Editor_User


class Menu:
    """Меню"""

    def __init__(self, x, y, buttons, text, scale=1.6):
        """
        Инициализация

        :param x: позиция по оси x
        :param y: позиция по оси y
        :param buttons: кнопки
        """
        self.scale = scale
        self.x, self.y = x * scale, y * scale
        self.dist_between_buttons = 5 * scale
        self.buttons = buttons
        self.text = text
        self.height = self.dist_between_buttons * (len(self.buttons) - 1) + \
                      self.buttons[0].text_rect.height * len(self.buttons)
        self.font = pg.font.SysFont('cmmi10', int(30 * scale))
        self.text_surf = self.font.render(text, True, (255, 255, 255))
        self.text_surf = pg.transform.rotate(self.text_surf, 90)
        self.text_rect = self.text_surf.get_rect()
        self.text_rect.x, self.text_rect.y = self.x, self.y
        self.dist_between_buttons_and_text = int(6 * scale)

        for index, value in enumerate(self.buttons):
            value.text_rect.x = self.dist_between_buttons_and_text + self.text_rect.width + self.x
            value.text_rect.y = self.y + index * (self.buttons[0].text_rect.height + self.dist_between_buttons)

    def change_scale(self, scale_buttons, scale_menu):
        """менять масштаб меню"""
        if self.scale != scale_buttons:
            for button in self.buttons:
                button.change_scale(scale_buttons)
            self.__init__(self.x / self.scale, self.y / self.scale, self.buttons, self.text, scale_menu)

    def can_be_pressed(self, a=False):
        for i in self.buttons:
            i.can_be_pressed = a

    def draw(self, sc, delta_time, scale_buttons, scale_menu, state='main menu'):
        """отрисовка меню"""
        if state == 'main menu':
            self.change_scale(scale_buttons, scale_menu)
            for button in self.buttons:
                button.draw(sc)
            d_b_b_a_t = self.dist_between_buttons_and_text
            pg.draw.rect(sc, (40, 40, 40), (self.text_rect.x - d_b_b_a_t // 2, self.text_rect.y - d_b_b_a_t // 2,
                                            self.text_rect.width + d_b_b_a_t,
                                            max(self.text_rect.height + d_b_b_a_t, self.height + 10)))
            pg.draw.rect(sc, (40, 40, 40), (self.text_rect.x - d_b_b_a_t * 2, self.text_rect.y - d_b_b_a_t // 2,
                                            d_b_b_a_t, max(self.text_rect.height + d_b_b_a_t, self.height + 10)))
            sc.blit(self.text_surf, self.text_rect)

    def update(self, sc, delta_time, scale_buttons, scale_menu, state='main menu'):
        for button in self.buttons:
            button.update(delta_time, state)


class MM_Button:
    """Кнопки главного меню"""

    def __init__(self, text, func, x=0, y=0, scale=1.6):
        """
        Инициализация
        :param text: текст кнопки
        :param func: вызымаемаю при нажатии функция
        :param x: позиция по оси x
        :param y: позиция по оси y
        """
        self.can_be_pressed = False
        self.scale = scale
        self.line_indent = 2 * scale
        self.arrow_alpha_speed = 2 * scale
        self.text_color = [0, 0, 0]
        self.font = pg.font.SysFont('cmmi10', int(45 * scale))
        self.text_content = text
        self.text = self.font.render(text, True, self.text_color)
        self.func = func
        self.text_rect = self.text.get_rect()
        self.text_rect.x, self.text_rect.y = x, y
        self.background_width = 0
        self.background_speed = 0.15 * scale
        self.mouse_on = self.mouse_on_button()
        self.arrow = pg.image.load('images/arrow_v6.png').convert_alpha()
        self.dist_between_text_and_arrow = 6 * scale
        self.indent = 0
        self.indent_speed = 0.1 * scale
        self.max_indent = 5 * scale
        self.arrow = pg.transform.scale(self.arrow,
                                        (int(0.7 * self.text_rect.height * self.arrow.get_width() /
                                             self.arrow.get_height()),
                                         int(0.7 * self.text_rect.height)))
        self.arrow.set_alpha(0)
        self.ffo = True

    def change_scale(self, scale):
        """менять масштаб кнопки"""
        self.__init__(self.text_content, self.func, self.text_rect.x, self.text_rect.y, scale)

    def mouse_on_button(self):
        """Находится ли курсор на кнопке"""
        mpx, mpy = pg.mouse.get_pos()
        return self.text_rect.x <= mpx <= self.text_rect.x + self.text_rect.width \
            and self.text_rect.y <= mpy <= self.text_rect.y + self.text_rect.height

    def func_update(self):
        """обновления состояния метода при нажатии кнпки"""
        if self.mouse_on and self.ffo:
            play_sound("sound/button_click_v2.wav", 10)
            self.ffo = False
        try:
            if self.mouse_on and self.can_be_pressed:
                key = pg.mouse.get_pressed()
                if key[0]:
                    play_sound("sound/start.mp3", 10)
                    self.can_be_pressed = False
                    self.func()
        except:
            pass
        if not self.mouse_on:
            self.ffo = True
            self.can_be_pressed = True

    def background_width_update(self, delta_time):
        """
        Обновление заднего фона

        :param delta_time: время между кадрами
        """
        if self.mouse_on:
            if self.background_width < self.text_rect.width:
                self.background_width = self.text_rect.width
            else:
                self.background_width += self.background_speed * delta_time
        else:
            self.background_width -= self.background_speed * delta_time * 10

        if self.background_width > \
                self.text_rect.width + self.arrow.get_width() + self.dist_between_text_and_arrow + self.indent * 2:
            self.background_width = \
                self.text_rect.width + self.arrow.get_width() + self.dist_between_text_and_arrow + self.indent * 2
        elif self.background_width < 0:
            self.background_width = 0

    def color_update(self, delta_time):
        """
        Обновление цаета стрелки

        :param delta_time: время между кадрами
        """
        if self.mouse_on:
            if self.arrow.get_alpha() < 255:
                self.arrow.set_alpha(self.arrow.get_alpha() + delta_time * self.arrow_alpha_speed)
            if self.arrow.get_alpha() > 255:
                self.arrow.set_alpha(255)
        else:
            self.arrow.set_alpha(self.arrow.get_alpha() - delta_time * self.arrow_alpha_speed)
        if self.arrow.get_alpha() < 0:
            self.arrow.set_alpha(0)

    def indent_update(self, delta_time):
        """
        Обновление отступа

        :param delta_time: время между кадрами
        """
        if self.mouse_on:
            if self.indent < self.max_indent:
                self.indent += self.indent_speed * delta_time
            else:
                self.indent = self.max_indent
        elif self.indent > 0:
            self.indent -= self.indent_speed * delta_time
        else:
            self.indent = 0

    def draw(self, sc):
        if self.background_width:
            pg.draw.line(sc, MM_BUTTON_BACKGROUND_COLOR, (self.text_rect.x, self.text_rect.y - self.line_indent - 2),
                         (self.text_rect.x + self.background_width, self.text_rect.y - self.line_indent - 2), 2)
            pg.draw.line(sc, MM_BUTTON_BACKGROUND_COLOR,
                         (self.text_rect.x, self.text_rect.y + self.line_indent + self.text_rect.height),
                         (self.text_rect.x + self.background_width,
                          self.text_rect.y + self.line_indent + self.text_rect.height), 2)
        pg.draw.rect(sc, MM_BUTTON_BACKGROUND_COLOR,
                     (self.text_rect.x, self.text_rect.y,
                      self.background_width, self.text_rect.height))
        sc.blit(self.arrow, (self.text_rect.x + self.text_rect.width + self.dist_between_text_and_arrow + self.indent,
                             self.text_rect.y + (self.text_rect.height - self.arrow.get_height()) // 2))
        sc.blit(self.text, (self.text_rect.x + self.indent, self.text_rect.y + self.text_rect.height * 0.05))

    def update(self, delta_time, state='main menu'):
        if state == 'main menu':
            self.func_update()
            self.mouse_on = self.mouse_on_button()
            self.background_width_update(delta_time)
            self.indent_update(delta_time)
            self.color_update(delta_time)

    def update_and_draw(self, sc, delta_time, state='main menu'):
        """
        Обновление и отображение кнопки

        :param state: состояние меню (главное или к примеру меню управления и тд)
        :param sc: экран отрисовки
        :param delta_time: время между кадрами
        """
        # update
        if state == 'main menu':
            self.update(delta_time)
        # draw
        self.draw(sc)


def nullFunc():
    pass


class Button:
    def __init__(self, image, x, y):
        """
        Инициализация

        :param image: название ихображения
        :param x: позиция на экране по оси x
        :param y: позиция на экране по оси y
        :param normalImage: здесь храниться изначальное изображение
        :param hoverImage: здесь храниться изображение, которое будет показываться при наведении мышки на кнопку
        :param clickImage: здесь храниться изображение, которое будет показываться при нажатии мышкой на кнопку
        :param func: здесь храниться функции котороя будет вызвана при  нажатии на кнопку
        """
        self.normalImage = load_image(image)
        self.image = self.normalImage
        self.hoverImage = load_image(image, 225)
        self.clickImage = load_image(image, 150)
        self.rect = self.image.get_rect()
        self.rect.x += x
        self.rect.y += y
        self.func = nullFunc

    def chekHover(self, mouseCoords, isClick=False):
        """

        Обработка нажатий и позиции мыши

        :param mouseCoords: координаты мышки
        :param isClick: сюда передается нажата ли кнопка на мышке
        """
        if dot_cube_collision(mouseCoords, self):
            if not isClick:
                self.image = self.hoverImage
                return True
            else:
                self.image = self.clickImage
                self.click()
                return True
        else:
            self.image = self.normalImage
            return False

    def onClick(self, func):
        """

        Назначение функции котороя будет вызываться при нажатии на кнопку

        :param func: функция котороя будет вызвана при нажатии на кнопку
        """
        self.func = func

    def click(self):
        """

        Вызов функции нажатия

        """
        self.func()

    def draw(self, screen):
        """

        Вызов функции нажатия

        :param screen: pygame.screen где надо будет отрисовать кнопку
        """
        screen.blit(self.image, (self.rect.x, self.rect.y))


class WW_Editor_UI:
    """Интерфейс редактора WireWorld"""

    def __init__(self, clock, user):
        """
        Инициализация

        :param clock: Путь до файла с музыкой
        :type clock: pygame.time.Clock
        :param user: Путь до файла с музыкой
        :type user: WW_Editor_User
        """
        self.clock = clock
        self.user = user

    def draw_info(self, sc, project_name):
        """
        Отрисовыват на экран

        :param sc: экран отрисовки
        """
        sc_width = sc.get_width()
        indent_x, indent_y = INFO_INDENT
        content = [
            f'FPS: {int(self.clock.get_fps())}',
            f'TILE: {int(self.user.tile)}',
            f'CHOSEN TYPE: {self.user.chosen_type}',
            f'CELL POS: {int(self.user.chosen_cell[0])}; {int(self.user.chosen_cell[1])}',
            f'RENDERING TIME: {self.user.rendering_time}',
            f'PRESS "I" FOR INFO',
            f'OPENED PROJECT: {str(project_name).upper()}'
        ]
        text = []
        text_height = 0
        text_width = 0
        for i, line in enumerate(content):
            text.append(INFO_TEXT_FONT.render(line, True, INFO_TEXT_COLOR))
            text_height += text[i].get_height()
            if text_width < text[i].get_width():
                text_width = text[i].get_width()
        sf = pg.Surface((text_width + indent_x, text_height + indent_y))
        sf.fill(INFO_BACKGROUND_COLOR)
        sf.set_alpha(128)
        sc.blit(sf, (sc_width - indent_x // 2 - sf.get_width(), indent_y // 2))
        for i, line in enumerate(text):
            sc.blit(line, (sc_width - indent_x - text_width, indent_y + line.get_height() * i))

    def draw(self, sc, project_name=None):
        """
        Отрисовывает на экран интерфейс редактора

        :param sc: экран отрисовки
        """
        self.draw_info(sc, project_name)


class WW_Game_UI:
    """Интерфейс редактора WireWorld"""

    def __init__(self, clock, user):
        """
        Инициализация

        :param clock: Путь до файла с музыкой
        :type clock: pygame.time.Clock
        :param user: Путь до файла с музыкой
        :type user: WW_Editor_User
        """
        self.clock = clock
        self.user = user

    def draw_info(self, sc):
        """
        Отрисовыват на экран

        :param sc: экран отрисовки
        """
        sc_width = sc.get_width()
        indent_x, indent_y = INFO_INDENT
        content = [
            f'FPS: {int(self.clock.get_fps())}',
            f'TILE: {int(self.user.tile)}',
            f'CHOSEN TYPE: {self.user.chosen_type}',
            f'CELL POS: {int(self.user.chosen_cell[0])}; {int(self.user.chosen_cell[1])}',
            f'RENDERING TIME: {self.user.rendering_time}',
            f'CONNECTORS LEFT: {self.user.how_much_connectors_are_left_to_place}',
        ]
        text = []
        text_height = 0
        text_width = 0
        for i, line in enumerate(content):
            text.append(INFO_TEXT_FONT.render(line, True, INFO_TEXT_COLOR))
            text_height += text[i].get_height()
            if text_width < text[i].get_width():
                text_width = text[i].get_width()
        sf = pg.Surface((text_width + indent_x, text_height + indent_y))
        sf.fill(INFO_BACKGROUND_COLOR)
        sf.set_alpha(128)
        sc.blit(sf, (sc_width - indent_x // 2 - sf.get_width(), indent_y // 2))
        for i, line in enumerate(text):
            sc.blit(line, (sc_width - indent_x - text_width, indent_y + line.get_height() * i))

    def draw(self, sc):
        """
        Отрисовывает на экран интерфейс редактора

        :param sc: экран отрисовки
        """
        self.draw_info(sc)
