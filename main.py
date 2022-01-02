import pathlib
import sys

import pygame
from objects import *
from config import *
from random import random, randint

pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))  # , pygame.SCALED | pygame.FULLSCREEN)
pygame.display.set_caption('Mutant Spaceship')

clock = pygame.time.Clock()

scale = pygame.transform.scale
rotate = pygame.transform.rotate

Objects.generate()


def start_menu():
    visible = True
    timer = time.time()
    while True:
        if time.time() - timer > 0.5:
            timer = time.time()
            visible = not visible
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit(0)
                if e.key == pygame.K_RETURN:
                    return
        screen.fill((58, 46, 63))
        t = text('MUTANT SPACESHIP', size=75)
        screen.blit(t, t.get_rect(center=screen.get_rect().center))
        if visible:
            t = text('Press ENTER to Play', size=25)
            screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 3 / 4)))
        pygame.display.update()
        clock.tick(FPS)


def main_game():
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    help_screen()
        screen.fill((58, 46, 63))
        if not Objects.update(events):
            for i in Objects.objects:
                if isinstance(i, Player):
                    return i.score
            return 0
        Objects.draw(screen)
        pygame.display.update()
        clock.tick(FPS)


while True:
    Objects.generate()
    start_menu()
    help_screen()
    end_screen(main_game())
