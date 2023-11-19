import unittest
import pygame as pg
from blur import Blur
from game_of_life import get_n_cells
from image_loader import load_image
from sound import play_music, play_sound


class Tests(unittest.TestCase):
    def test1(self):
        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)
        screen.fill((0, 0, 0))

    def test2(self):
        screen = pg.display.set_mode((0, 0), pg.RESIZABLE)
        blur = Blur()
        blur.blur(screen)

    def test3(self):
        play_music('adadadad')

    def test4(self):
        play_sound(999)

    def test5(self):
        a = get_n_cells((0, 0))
        self.assertEqual(a, [(1, 1), (-1, 1), (1, -1), (-1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)])

    def test6(self):
        a = get_n_cells(None)
        self.assertEqual(a, None)

    def test7(self):
        load_image('asdad')
