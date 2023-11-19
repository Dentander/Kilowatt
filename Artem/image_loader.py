import pygame
import os


def load_image(image, colorkey=None):
    """
    Загрузка изображения и переображение его в pygame.image

    :param image: путь до изображение из папки images
    :type image: str
    :param colorkey: colorkey
    :type colorkey: int
    """
    try:
        fullname = os.path.abspath(os.curdir) + '/images/' + image
        if not os.path.isfile(fullname):
            image = pygame.image.load(os.path.abspath(os.curdir) + "/images/error.png")
        else:
            image = pygame.image.load(fullname)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_alpha(colorkey)
        else:
            image = image.convert_alpha()
        return image
    except:
        pass
