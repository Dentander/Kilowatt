from config import *
from user import WW_Level_Creator_Player
from wire_world import WW_Level_Creator
from ui import WW_Editor_UI, Button


class WW_Editor:
    """Редактор клеточного автомата WireWorld"""

    def __init__(self):
        """Инициализация"""
        self.screen = pg.display.set_mode(RESOLUTION, pg.RESIZABLE)
        pg.display.set_caption('WireWorld')
        self.clock = pg.time.Clock()
        self.end_app = False
        self.pause = False
        self.nextStep = False
        self.timeBetweenSteps = 0

        self.user = WW_Level_Creator_Player()
        self.wire_world = WW_Level_Creator()
        self.ui = WW_Editor_UI(self.clock, self.user)
        self.pauseButton = Button('stopButton.png', 0, 0)
        self.pauseButton.onClick(self.pauseSet)
        self.nextStepButton = Button('nextStepButton.png', 20, 0)
        self.nextStepButton.onClick(self.nextStepSet)
        self.saveStepButton = Button('nextStepButton.png', 40, 0)
        self.saveStepButton.onClick(self.save)

    def run(self):
        """Запуск редактора"""
        mouseClick = False
        mouseOnOtherObject = False
        while not self.end_app:
            self.screen.fill(WW_BACKGROUND_COLOR)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.user.mouse_wheel_control(event.button)
                    mouseClick = True
            mouseCoords = pg.mouse.get_pos()
            if self.pauseButton.chekHover(mouseCoords, mouseClick) or self.nextStepButton.chekHover(mouseCoords, mouseClick)\
                    or self.saveStepButton.chekHover(mouseCoords, mouseClick):
                mouseOnOtherObject = True
            mouseClick = False
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
            self.pauseButton.draw(self.screen)
            self.nextStepButton.draw(self.screen)
            self.saveStepButton.draw(self.screen)
            mouseOnOtherObject = False

            pg.display.flip()
            self.clock.tick(FPS)

    def pauseSet(self):
        self.pause = not self.pause

    def nextStepSet(self):
        self.nextStep = True
        self.pause = False

    def save(self):
        self.wire_world.save('RunnerStart')


if __name__ == '__main__':
    ww_editor = WW_Editor()
    ww_editor.run()
