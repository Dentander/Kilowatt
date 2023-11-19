import tkinter
from os import walk
from tkinter.filedialog import askopenfilename

from blur import Blur
from controls_view import ViewBlock
from sound import play_music
from user import WW_Editor_User, WW_Runner_Player, WW_Infinity_Runner_Player
from wire_world import WireWorld, WW_Runner_WireWorld, Infinity_Ruunner_World
from ui import WW_Editor_UI, Button, WW_Game_UI, Menu, MM_Button
from image_loader import load_image

import webbrowser
from game_of_life import GameOfLife
from user import WW_Editor_User
from wire_world import WireWorld
from ui import WW_Editor_UI, Button, Menu, MM_Button
from game_over import *

from config import *
from user import WW_Editor_User
from wire_world import WireWorld
from ui import WW_Editor_UI, Button
from better_editor import Draw_line, Coords_on_screen, end_coord_of_sel_rect, Delete_cells


class WW_Editor:
    """Редактор клеточного автомата WireWorld"""

    def __init__(self, screen):
        """Инициализация"""
        self.def_width, self.def_height = (1000, 600)
        self.screen = screen
        pg.display.set_caption('Kilowatt')
        self.clock = pg.time.Clock()
        self.end_app = False
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0

        self.user = WW_Editor_User()
        self.wire_world = WireWorld()
        self.ui = WW_Editor_UI(self.clock, self.user)
        self.pauseButton = Button('stopButton.png', 0, 0)
        self.pauseButton.onClick(self.pauseSet)
        self.nextStepButton = Button('nextStepButton.png', 20, 0)
        self.nextStepButton.onClick(self.nextStepSet)
        self.uploadButton = Button('upload.png', 40, 0)
        self.uploadButton.onClick(self.upload)
        self.loadButton = Button('load.png', 60, 0)
        self.loadButton.onClick(self.load)

        self.opened_project = None

        context = {
            'ПРАВАЯ КНОПКА МЫШИ': 'ЗАПОЛНИТЬ КЛЕТКУ',
            'SHIFT + КОЛЕСО МЫШИ': 'ВЫБОР ТИПА КЛЕТКИ',
            'КОЛЕСО МЫШИ': 'ПРИБЛИЖАТЬСЯ/ОТДАЛЯТЬСЯ',
            'ЛКМ + ДВИЖЕНИЕ МЫШИ': 'ПЕРЕМЕЩЕНИЕ ПО КЛЕТОЧНОМУ ПОЛЮ',
            'A': 'ДВИЖЕНИЕ ВЛЕВО',
            'W': 'ДВИЖЕНИЕ ВВЕРХ',
            'S': 'ДВИЖЕНИЕ ВПРАВО',
            'D': 'ДВИЖЕНИЕ ВНИЗ',
            'P': 'ПАУЗА',
            'F': 'СЛЕДУЩИЙ КАДР',
            'I': 'ПРОСМОТР МЕНЮ УПРАВЛЕНИЯ',
        }
        self.vb = ViewBlock('УПРАВЛЕНИЕ РЕДАКТОРОМ', context, y=240)

    def get_next_project_num(self):
        filenames = next(walk('levels/user/'), (None, None, []))[2]
        return len(filenames)

    def upload(self):
        tkinter.Tk().withdraw()
        file_name = askopenfilename(initialdir='levels/user/', filetypes=[('', '.txt')])
        self.wire_world.read_from_file(file_name)
        print(file_name.split('/')[len(file_name.split('/')) - 1].split('.txt')[0])
        self.opened_project = file_name.split('/')[len(file_name.split('/')) - 1].split('.txt')[0]

    def load(self):
        if self.opened_project is None:
            self.opened_project = 'project' + str(self.get_next_project_num())
            self.wire_world.save(self.opened_project)
        else:
            self.wire_world.save(self.opened_project)

    def state_update(self):
        """обновление состояния меню"""
        keys = pg.key.get_pressed()
        if keys[pg.K_i]:
            self.state = 'controls menu'
        else:
            self.state = 'main menu'

    def run(self):
        """Запуск редактора"""
        mouseClick = False
        mouseOnOtherObject = False
        lineDrawingMode = False
        SelectionMode = "OFF"
        while not self.end_app:
            self.screen.fill(WW_BACKGROUND_COLOR)

            # scale
            self.width_scale = self.screen.get_width() / self.def_width
            self.height_scale = self.screen.get_height() / self.def_height
            min_scale = min(1.15 * self.width_scale, 1.15 * self.height_scale)

            keys = pg.key.get_pressed()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_app = True
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouseClick = True
                    self.user.mouse_wheel_control(event.button)
                if event.type == pg.KEYDOWN and event.key == pg.K_p:
                    self.pauseSet()
                if event.type == pg.KEYDOWN and event.key == pg.K_f:
                    self.nextStepSet()
                if keys[pg.K_LSHIFT] and event.type == pg.MOUSEBUTTONDOWN and event.button == 1 :
                    lineDrawingMode = True
                    lineFirstFrame = True
                    start_line_x, start_line_y = pg.mouse.get_pos()
                    dist_x, dist_y = start_line_x - self.user.indent_x, start_line_y - self.user.indent_y
                    start_cell_x, start_cell_y = dist_x // self.user.tile, dist_y // self.user.tile
                if lineDrawingMode and event.type == pg.MOUSEBUTTONDOWN and (event.button == 3) and (not lineFirstFrame):
                    lineDrawingMode = False
                if SelectionMode == "STARTING" and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    SelectionMode = "Selected"
                if (SelectionMode == "STARTING" or SelectionMode == "Selected") and event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                    SelectionMode = "OFF"
                if keys[pg.K_LCTRL] and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    SelectionMode = "STARTING"
                    start_selection_x, start_selection_y = pg.mouse.get_pos()
                    dist_x, dist_y = start_selection_x - self.user.indent_x, start_selection_y - self.user.indent_y
                    start_sel_cell_x, start_sel_cell_y = dist_x // self.user.tile, dist_y // self.user.tile

            mouseCoords = pg.mouse.get_pos()
            mouse = pg.mouse.get_pressed()
            if self.pauseButton.chekHover(mouseCoords, mouseClick) or self.nextStepButton.chekHover(mouseCoords, mouseClick)\
                    or self.loadButton.chekHover(mouseCoords, mouseClick) or self.uploadButton.chekHover(mouseCoords, mouseClick):
                mouseOnOtherObject = True
            if lineDrawingMode:
                mouse_x, mouse_y = pg.mouse.get_pos()
                dist_x, dist_y = mouse_x - self.user.indent_x, mouse_y - self.user.indent_y
                end_cell_x, end_cell_y = dist_x // self.user.tile, dist_y // self.user.tile
                if mouseClick and mouse[0] and (not lineFirstFrame):
                    lineDrawingMode = False
                    self.wire_world = Draw_line(start_cell_x, start_cell_y,
                                                end_cell_x, end_cell_y,
                                                self.user, self.wire_world)
                lineFirstFrame = False

            if SelectionMode == "Selected" or SelectionMode == "STARTING":
                end_selection_x, end_selection_y = pg.mouse.get_pos()
                mouseOnOtherObject = True
                if SelectionMode == "STARTING":
                    dist_x, dist_y = end_selection_x - self.user.indent_x, end_selection_y - self.user.indent_y
                    end_sel_cell_x, end_sel_cell_y = dist_x // self.user.tile, dist_y // self.user.tile

                if SelectionMode == "Selected" and (keys[pg.K_BACKSPACE] or keys[pg.K_DELETE]):
                    SelectionMode = "OFF"
                    self.wire_world = Delete_cells(start_sel_cell_x, start_sel_cell_y,
                                                   end_sel_cell_x, end_sel_cell_y,
                                                   self.user, self.wire_world)
            mouseClick = False

            if not self.pause:
                self.timeBetweenSteps += self.clock.get_time()
                if self.nextStep and self.timeBetweenSteps >= RENDERING_TIME:
                    self.timeBetweenSteps = 0
                    self.pause = True
                    self.nextStep = False
                self.wire_world.update(self.user.rendering_time, self.clock.get_time())
            self.wire_world.update(self.user.rendering_time, self.clock.get_time())
            self.user.update(self.wire_world, self.clock.get_time(), mouseOnOtherObject)
            keys = pg.key.get_pressed()
            if keys[pg.K_r]:
                self.wire_world.draw(self.user, self.screen)
            if SelectionMode == "STARTING" or SelectionMode == "Selected":
                pg.draw.rect(self.screen, LIGHT_GREEN,
                             [Coords_on_screen(start_sel_cell_x, start_sel_cell_y, self.user),
                             end_coord_of_sel_rect(start_sel_cell_x, start_sel_cell_y, end_sel_cell_x, end_sel_cell_y,
                             self.user)], 2)
            if lineDrawingMode:
                pg.draw.line(self.screen, LIGHT_GREEN,
                             Coords_on_screen(start_cell_x, start_cell_y, self.user),
                             Coords_on_screen(end_cell_x, end_cell_y, self.user), 3)
            self.ui.draw(self.screen, self.opened_project)
            self.pauseButton.draw(self.screen)
            self.nextStepButton.draw(self.screen)
            self.loadButton.draw(self.screen)
            self.uploadButton.draw(self.screen)
            mouseOnOtherObject = False

            self.state_update()
            self.vb.update_and_draw(self.screen, min_scale * 0.65, self.state)

            pg.display.flip()
            self.clock.tick(FPS)

    def pauseSet(self):
        self.pause = not self.pause

    def nextStepSet(self):
        self.nextStep = True
        self.pause = False


class WW_Infinity_Runner:
    def __init__(self, screen):
        self.screen = screen
        self.def_width, self.def_height = (1000, 600)
        self.width_scale = self.screen.get_width() / self.def_width
        self.height_scale = self.screen.get_height() / self.def_height
        pg.display.set_caption('Kilowatt')
        self.clock = pg.time.Clock()
        self.end_app = False
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0
        self.current_level = 0

        self.user = WW_Infinity_Runner_Player()
        self.wire_world = Infinity_Ruunner_World(self.user)
        self.ui = WW_Game_UI(self.clock, self.user)
        self.winBackground = load_image("wonBackground.png")
        self.looseScreen = QuestionWindow()
        self.winScreen = QuestionWindow('VICTORY', 'menu', 'next level', 'blue')

    def run(self):
        """Запуск редактора"""
        mouseOnOtherObject = False
        is_first_death_frame = True
        self.user.indent_y -= (self.def_height - self.screen.get_height()) / 2
        while not self.end_app:
            sH = self.screen.get_height()
            self.height_scale = self.screen.get_height() / self.def_height
            self.width_scale = self.screen.get_width() / self.def_width
            self.screen.fill(WW_BACKGROUND_COLOR)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.user.mouse_wheel_control(event.button)
                if event.type == pg.VIDEORESIZE:
                    self.user.indent_y -= (sH - event.size[1]) / 2
            if not self.user.win and (len(self.wire_world.electron_heads) > 0 or not self.user.started):
                if not self.pause:
                    self.timeBetweenSteps += self.clock.get_time()
                    if self.nextStep and self.timeBetweenSteps >= RENDERING_TIME:
                        self.timeBetweenSteps = 0
                        self.pause = True
                        self.nextStep = False
                    self.wire_world.update(self.user.rendering_time, self.clock.get_time())
                self.user.update(self.wire_world, self.clock.get_time(), mouseOnOtherObject)
                self.wire_world.draw(self.user, self.screen)
                self.ui.draw(self.screen)
                mouseOnOtherObject = False
            elif self.user.win:
                result = self.winScreen.update_and_draw(self.screen, self.width_scale, self.height_scale, self.clock.get_time())
                if result == 2:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    self.nextLevel()
                elif result == 1:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    return
            else:
                if is_first_death_frame:
                    play_sound('sound/game_over.mp3')
                    is_first_death_frame = False
                result = self.looseScreen.update_and_draw(self.screen, self.width_scale, self.height_scale, self.clock.get_time())
                if result == 2:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    self.restart()
                elif result == 1:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    return
            pg.display.flip()
            self.clock.tick(FPS)

    def pauseSet(self):
        self.pause = not self.pause

    def nextStepSet(self):
        self.nextStep = True
        self.pause = False

    def nextLevel(self):
        self.current_level += 1
        self.current_level %= 3
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0
        self.user = WW_Infinity_Runner_Player()
        self.wire_world = Infinity_Ruunner_World(self.user)
        self.ui = WW_Game_UI(self.clock, self.user)
        self.user.indent_y -= (self.def_height - self.screen.get_height()) / 2

    def restart(self):
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0
        self.user = WW_Infinity_Runner_Player()
        self.wire_world = Infinity_Ruunner_World(self.user)
        self.ui = WW_Game_UI(self.clock, self.user)
        self.user.indent_y -= (self.def_height - self.screen.get_height()) / 2


def fill_surf(surf, color=(0, 0, 0), speed=4):
    clock = pg.time.Clock()
    surf1 = pg.Surface(surf.get_size())
    surf1.set_alpha(speed)
    surf1.fill(color)
    for i in range(int(600 // speed)):
        surf.blit(surf1, (0 ,0))
        pg.display.flip()
        clock.tick(FPS)



class WW_Runner:
    def __init__(self, screen):
        self.screen = screen
        self.def_width, self.def_height = (1000, 600)
        self.width_scale = self.screen.get_width() / self.def_width
        self.height_scale = self.screen.get_height() / self.def_height
        pg.display.set_caption('Kilowatt')
        self.clock = pg.time.Clock()
        self.end_app = False
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0
        self.current_level = 0

        self.user = WW_Runner_Player()
        self.wire_world = WW_Runner_WireWorld(self.user)
        self.ui = WW_Game_UI(self.clock, self.user)
        self.looseScreen = QuestionWindow()
        self.winScreen = QuestionWindow('VICTORY', 'menu', 'next level', 'blue')

    def run(self):
        """Запуск редактора"""
        mouseClick = False
        mouseOnOtherObject = False
        is_first_death_frame = True
        self.user.indent_y -= (self.def_height - self.screen.get_height()) / 2
        while not self.end_app:
            sH = self.screen.get_height()
            self.height_scale = self.screen.get_height() / self.def_height
            self.width_scale = self.screen.get_width() / self.def_width
            mouseClick = False
            self.screen.fill(WW_BACKGROUND_COLOR)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.user.mouse_wheel_control(event.button)
                    mouseClick = True
                if event.type == pg.VIDEORESIZE:
                    self.user.indent_y -= (sH - event.size[1]) / 2
            if not self.user.win and (len(self.wire_world.electron_heads) > 0 or not self.user.started):
                mouseCoords = pg.mouse.get_pos()
                if not self.pause:
                    self.timeBetweenSteps += self.clock.get_time()
                    if self.nextStep and self.timeBetweenSteps >= RENDERING_TIME:
                        self.timeBetweenSteps = 0
                        self.pause = True
                        self.nextStep = False
                    self.wire_world.update(self.user.rendering_time, self.clock.get_time())
                self.user.update(self.wire_world, self.clock.get_time(), mouseOnOtherObject)
                self.wire_world.draw(self.user, self.screen)
                self.ui.draw(self.screen)
                mouseOnOtherObject = False
            elif self.user.win:
                min_scale = min(self.width_scale, self.height_scale)
                result = self.winScreen.update_and_draw(self.screen, self.width_scale, self.height_scale,
                                                        self.clock.get_time())
                if result == 2:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    self.nextLevel()
                elif result == 1:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    return
            else:
                if is_first_death_frame:
                    is_first_death_frame = False
                    play_sound('sound/game_over.mp3')
                min_scale = min(self.width_scale, self.height_scale)
                result = self.looseScreen.update_and_draw(self.screen, self.width_scale, self.height_scale,
                                                          self.clock.get_time())
                if result == 2:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    self.restart()
                elif result == 1:
                    fill_surf(self.screen)
                    pg.time.wait(100)
                    return
            pg.display.flip()
            self.clock.tick(FPS)

    def pauseSet(self):
        self.pause = not self.pause

    def nextStepSet(self):
        self.nextStep = True
        self.pause = False

    def nextLevel(self):
        self.current_level += 1
        self.current_level %= 3
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0
        self.user = WW_Runner_Player()
        self.wire_world = WW_Runner_WireWorld(self.user, self.current_level)
        self.ui = WW_Game_UI(self.clock, self.user)
        self.user.indent_y -= (self.def_height - self.screen.get_height()) / 2

    def restart(self):
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0
        self.user = WW_Runner_Player()
        self.wire_world = WW_Runner_WireWorld(self.user, self.current_level)
        self.ui = WW_Game_UI(self.clock, self.user)
        self.user.indent_y -= (self.def_height - self.screen.get_height()) / 2


class MainMenu:
    def __init__(self):
        """инициализация"""
        pg.init()
        play_music('sound/Paweł Błaszczak - Horizon.mp3', 0.6)

        # screen
        self.def_width, self.def_height = (1000, 600)
        self.screen = pg.display.set_mode(RESOLUTION, pg.RESIZABLE)
        pg.display.set_caption('Kilowatt')
        self.clock = pg.time.Clock()
        self.end_app = False

        # state
        self.state = 'main menu'

        # scale
        self.width_scale = self.screen.get_width() / self.def_width
        self.height_scale = self.screen.get_height() / self.def_height
        scale_menu = min(self.width_scale, self.height_scale)

        # кнопки
        self.buttons = [
            MM_Button('РАННЕР', self.open_game1, scale=scale_menu),
            MM_Button('УРОВНИ', self.open_game2, scale=scale_menu),
            MM_Button('РЕДАКТОР', self.open_editor, scale=scale_menu),
            MM_Button('ССЫЛКА GITLAB', self.open_gitlab, scale=scale_menu),
            MM_Button('ВЫЙТИ', self.exit, scale=scale_menu),
        ]
        self.menu = Menu(45, 190, self.buttons, 'ГЛАВНОЕ МЕНЮ', scale=scale_menu)

        # background
        self.game_of_life = GameOfLife()
        self.blur = Blur()

        # меню управления
        self.qw = QuestionWindow()
        context = {
            'ПРАВАЯ КНОПКА МЫШИ': 'ЗАПОЛНИТЬ КЛЕТКУ',
            'SHIFT + КОЛЕСО МЫШИ': 'ВЫБОР ТИПА КЛЕТКИ',
            'КОЛЕСО МЫШИ': 'ПРИБЛИЖАТЬСЯ/ОТДАЛЯТЬСЯ',
            'ЛКМ + ДВИЖЕНИЕ МЫШИ': 'ПЕРЕМЕЩЕНИЕ ПО КЛЕТОЧНОМУ ПОЛЮ',
            'A': 'ДВИЖЕНИЕ ВЛЕВО',
            'W': 'ДВИЖЕНИЕ ВВЕРХ',
            'S': 'ДВИЖЕНИЕ ВПРАВО',
            'D': 'ДВИЖЕНИЕ ВНИЗ',
            'P': 'ПАУЗА',
            'F': 'СЛЕДУЩИЙ КАДР',
            'I': 'ПРОСМОТР МЕНЮ УПРАВЛЕНИЯ',
        }
        self.vb = ViewBlock('УПРАВЛЕНИЕ РЕДАКТОРОМ', context, y=240)

    def open_gitlab(self):
        """открыть ссылку на gitlab"""
        self.menu.can_be_pressed()
        webbrowser.open('https://gitlab.informatics.ru/2021-2022/vk/s102/kilowatt')
        self.menu.can_be_pressed(True)

    def exit(self):
        """закрыть приложение"""
        self.end_app = True

    def open_editor(self):
        """открыть редактор"""
        self.menu.can_be_pressed()
        fill_surf(self.screen)
        pg.time.wait(100)
        editor = WW_Editor(self.screen)
        editor.run()
        self.menu.can_be_pressed(True)

    def open_game1(self):
        """открыть игру 1"""
        self.menu.can_be_pressed()
        fill_surf(self.screen)
        pg.time.wait(100)
        ww_game = WW_Infinity_Runner(self.screen)
        ww_game.run()
        self.menu.can_be_pressed(True)

    def open_game2(self):
        """открыть игру 2"""
        self.menu.can_be_pressed()
        fill_surf(self.screen)
        pg.time.wait(100)
        ww_game = WW_Runner(self.screen)
        ww_game.run()


    def state_update(self):
        """обновление состояния меню"""
        keys = pg.key.get_pressed()
        if keys[pg.K_i]:
            self.state = 'controls menu'
        else:
            self.state = 'main menu'


    def run(self):
        """запуск меню"""
        while not self.end_app:
            # events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.end_app = True

            # scale
            self.width_scale = self.screen.get_width() / self.def_width
            self.height_scale = self.screen.get_height() / self.def_height
            min_scale = min(1.15 * self.width_scale, 1.15 * self.height_scale)

            # обновление состояния меню
            self.state_update()

            # draw and update
            self.game_of_life.update(self.clock.get_time())
            self.menu.update(self.screen, min(self.clock.get_time(), 100), 1.3 * min_scale, 1.3 * min_scale, self.state)
            self.screen.fill(MM_BACKGROUND)
            self.game_of_life.draw(self.screen, 15 * min_scale)
            self.blur.blur(self.screen)
            self.menu.draw(self.screen, min(self.clock.get_time(), 100), 1.5 * self.height_scale,
                           1.5 * self.height_scale, self.state)
            self.vb.update_and_draw(self.screen, min_scale * 0.65, self.state)
            # self.qw.update_and_draw(self.screen, self.width_scale, self.height_scale, self.clock.get_time())

            pg.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    ww_editor = MainMenu()
    ww_editor.run()
