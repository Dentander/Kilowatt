import pygame as pg


class Lighter:
    def __init__(self, enabled=True, max_strength=50, strength_speed=0.5):
        """
        Инициализация
        :param enabled: включён/выключен
        :param max_strength: максимальное значение блюра
        :param strength_speed: скорость увеличения блюра
        """
        self.enabled = enabled
        self.max_strength = max_strength
        self.strength_speed = strength_speed
        self.strength = 0

    def lighter(self, sc):
        """
        Осветление
        :param sc: экран отрисовки
        :return:
        """
        if self.enabled:
            self.strength += self.strength_speed
        else:
            self.strength -= self.strength_speed

        if self.strength < 0:
            self.strength = 0
        elif self.strength > self.max_strength:
            self.strength = self.max_strength

        if self.strength > 0:
            surf = pg.Surface(sc.get_size())
            surf.set_alpha(self.strength)
            surf.fill((255, 255, 255))
            sc.blit(surf, (0, 0))
