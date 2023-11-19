import pygame


def play_music(path, volume=1, loops=-1):
    """
    Воспроизводит музыку

    :param path: Путь до файла с музыкой
    :type path: str
    :param volume: Громкость музыки
    :type volume: float
    :param loops: Колличество повторов (изначально стоит бесконечность)
    :type loops: int
    """
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=loops, start=0)
    except:
        pass

def play_sound(path, volume=1):
    """
    Воспроизводит звуки

    :param path: Путь до файла с музыкой
    :type path: str
    :param volume: Громкость звука
    :type volume: float
    """
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        sound.play()
    except:
        pass
