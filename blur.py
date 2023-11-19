import pygame as pg


class Blur:
    def __init__(self, enabled=True, max_strength=3, strength_speed=0.05):
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

    def blur(self, sc):
        """
        Блюр
        :param sc: экран отрисовки
        :return:
        """
        if self.enabled:
            self.strength += self.strength_speed
        else:
            self.strength -= self.strength_speed

        if self.strength < 1:
            self.strength = 1
        elif self.strength > self.max_strength:
            self.strength = self.max_strength

        if self.strength > 1:
            w, h = sc.get_size()
            surf = pg.transform.smoothscale(sc, (int(w / self.strength), int(h / self.strength)))
            surf = pg.transform.smoothscale(surf, (w, h))
            sc.blit(surf, (0, 0))
