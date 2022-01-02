from config import *
from sounds import *
import sys
from utils import *
import pygame


def choose_powerup():
    screen = pygame.display.get_surface()
    options = {
        'SHIELD': 'Protects from bullets [10 sec]',
        'FAST LASER': 'Rapid Lasers [20 sec]',
        'DESTROY': 'DESTROY all on-screen enemies'
    }
    selected = 0
    clock = pygame.time.Clock()
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return
                if e.key == pygame.K_p:
                    return
                if e.key == pygame.K_UP:
                    SoundManager.play('menu')
                    selected -= 1
                if e.key == pygame.K_DOWN:
                    SoundManager.play('menu')
                    selected += 1
                if e.key == pygame.K_RETURN:
                    SoundManager.play('menu')
                    return list(options.keys())[selected]
        selected %= len(options)
        screen.fill((58, 46, 63))
        for i in options:
            color = (255, 255, 255) if list(options.keys()).index(i) != selected else (0, 0, 255)
            screen.blit(text(i, size=75, color=color), (50, list(options.keys()).index(i) * 100 + 150))
            if list(options.keys()).index(i) == selected:
                t = text(options[i])
                screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 3 / 4)))
        pygame.display.update()
        clock.tick(FPS)


def end_screen(score):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return
                if e.key == pygame.K_RETURN:
                    return
        screen.fill((58, 46, 63))
        t = text('YOUR SCORE')
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 1 / 4)))
        t = text(str(score), size=100)
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 1 / 4 + 100)))
        t = text('Press ENTER to go back to Main Menu', size=25)
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 3 / 4)))
        pygame.display.update()
        clock.tick(FPS)


def help_screen():
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return
                if e.key == pygame.K_RETURN:
                    return
        screen.fill((58, 46, 63))
        t = text('Help Page', size=30)
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 1 / 4 - 100)))
        t = text('Your ship can mutate to get new abilities with every 100 points', size=25)
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 1 / 4)))
        t = text('Press P when mutant ability can be activated', size=25)
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 1 / 4 + 100)))
        t = text('You can press R to toggle RADAR view', size=25)
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 1 / 4 + 200)))
        t = text('Press ENTER to go back to Main Menu', size=25)
        screen.blit(t, t.get_rect(center=(screen_width // 2, screen_height * 3 / 4)))
        pygame.display.update()
        clock.tick(FPS)
