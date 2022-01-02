import pygame
from config import *


class SoundManager:
    config = {
        'shoot1': 'sfx_laser1.ogg',
        'shoot2': 'sfx_laser2.ogg',
        'explode': 'explode.ogg',
        'menu': 'menu.ogg'
    }
    for i in config:
        config[i] = ASSETS / 'sounds' / config[i]
    current = ''

    @classmethod
    def load(cls, sound):
        pygame.mixer.music.load(sound)

    @classmethod
    def play(cls, sound):
        for i in range(8):
            if not pygame.mixer.Channel(i).get_busy():
                cls.current = sound
                cls.load(cls.config[sound])
                pygame.mixer.Channel(i).play(pygame.mixer.Sound(cls.config[sound]))
                return
        if sound == cls.current and pygame.mixer.music.get_busy():
            return
        cls.current = sound
        cls.load(cls.config[sound])
        pygame.mixer.music.play()
