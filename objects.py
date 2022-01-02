import pathlib
import time
from random import randint, random, choice
from utils import *
from typing import Union
from sounds import *
from menu import *

from operator import attrgetter

import pygame
from math import sin, cos, radians, degrees

from config import *


class Objects:
    finished = False
    objects: list['BaseObject'] = []
    objects_to_add = []
    spawn_timer = time.time()
    spawn_time_k = 5

    @classmethod
    def add(cls, other: 'BaseObject'):
        cls.objects_to_add.append(other)

    @classmethod
    def generate(cls):
        cls.finished = False
        cls.objects_to_add = []
        cls.spawn_timer = time.time()
        cls.spawn_time_k = 5
        cls.objects = [Meteor() for _ in range(10)]
        cls.objects.append(Player())
        cls.objects.append(Radar())
        cls.objects.sort(key=attrgetter('z'))

    @classmethod
    def move_world(cls, dx, dy):
        for i in cls.objects:
            if not isinstance(i, Player):
                i.move(dx, dy)

    @classmethod
    def update(cls, events: list[pygame.event.Event]):
        if cls.finished:
            return False
        if time.time() - cls.spawn_timer > cls.spawn_time_k:
            cls.spawn_timer = time.time()
            cls.objects.append(Enemy())
            cls.spawn_time_k -= 0.25
            cls.spawn_time_k = clamp(cls.spawn_time_k, 0.5, 5)
        if cls.objects_to_add:
            for _ in range(len(cls.objects_to_add)):
                cls.objects.append(cls.objects_to_add.pop())
        cls.objects.sort(key=attrgetter('z'))
        cls.objects = [i for i in cls.objects if i.alive]
        for i in cls.objects:
            i.update(events)
        return True

    @classmethod
    def draw(cls, surf: pygame.Surface):
        for i in cls.objects:
            i.draw(surf)


class BaseObject:
    def __init__(self, x=None, y=None, z=1, sprite=None):
        if x is None:
            x = randint(0, screen_width)
        if y is None:
            y = randint(0, screen_height)
        self.x = x
        self.y = y
        self.z = z
        self.sprite = sprite
        self.angle = 0
        self.alive = True

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def update(self, events: list[pygame.event.Event]):
        pass

    def draw(self, surf: pygame.Surface):
        if self.sprite is not None:
            sprite = pygame.transform.rotate(self.sprite, angle=self.angle)
            surf.blit(sprite, sprite.get_rect(center=(self.x, self.y)))


class Meteor(BaseObject):
    def __init__(self, x=None, y=None, size=None):
        if size is None:
            size = 'abcd'[randint(0, 3)]
        index = randint(1, 2)
        image = pygame.image.load(ASSETS / 'images' / 'asteroids' / f'{size}{index}.png').convert_alpha()
        if x is None:
            x = choice([randint(-75, 0), randint(screen_width, screen_width + 75)])
        if y is None:
            y = choice([randint(-75, 0), randint(screen_height, screen_height + 75)])
        super().__init__(x, y, sprite=image)
        angle = radians(randint(0, 360))
        self.angle_k = random() * randint(1, 2)
        self.dx = cos(angle)
        self.dy = sin(angle)
        self.speed = randint(1, 5)
        self.size = 'abcd'.index(size)
        self.hitbox_r = self.sprite.get_rect().width * 0.75

    def update(self, events: list[pygame.event.Event]):
        self.x += self.dx
        self.y += self.dy
        self.angle += self.angle_k
        self.angle %= 360
        # if self.x < -100 or self.x > screen_width + 100:
        #     self.__init__()
        if distance((self.x, self.y), (screen_width // 2, screen_height // 2)) > 2250:
            if len([i for i in Objects.objects if isinstance(i, self.__class__)]) > 15:
                self.__init__()
            else:
                for _ in range(randint(2, 5)):
                    self.__init__()

    def destroy(self):
        self.alive = False
        if self.size < 3:
            new_size = clamp(self.size + randint(1, 3), self.size, 3)
            Objects.add(Meteor(self.x, self.y, 'abcd'[new_size]))
            Objects.add(Meteor(self.x, self.y, 'abcd'[new_size]))


class Laser(BaseObject):
    def __init__(self, x, y, angle, origin=None):
        super().__init__(x, y, z=0, sprite=pygame.image.load(ASSETS / 'images' / 'player' / 'laser.png').convert_alpha())
        self.angle = angle + 90
        self.dx = -cos(radians(angle))
        self.dy = sin(radians(angle))
        self.speed = 20
        self.timer = time.time()
        self.origin = origin

    def update(self, events: list[pygame.event.Event]):
        if time.time() - self.timer > 3:
            self.alive = False
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        for i in Objects.objects:
            if i is self.origin:
                continue
            if isinstance(i, Meteor):
                if distance((self.x, self.y), (i.x, i.y)) < i.hitbox_r:
                    i.destroy()
                    self.alive = False
            if isinstance(i, Enemy):
                if isinstance(self.origin, Enemy):
                    continue
                if distance((self.x, self.y), (i.x, i.y)) < 50:
                    # if isinstance(self.origin, Player):
                    #     self.origin.powerup_value += 25
                    #     self.origin.score += 25
                    #     if self.origin.powerup_value >= 100:
                    #         self.origin.powerup += 1
                    #         self.origin.powerup_value = 0
                    i.destroy()
                    self.alive = False
            if isinstance(i, Player):
                if distance((self.x, self.y), (i.x, i.y)) < 50:
                    i.damage()
                    self.alive = False


class Player(BaseObject):
    def __init__(self):
        img = pygame.image.load(ASSETS / 'images' / 'player' / 'player.png').convert_alpha()
        super().__init__(screen_width // 2, screen_height // 2, sprite=img)
        self.acc = 0
        self.flame = [pygame.image.load(ASSETS / 'images' / 'player' / f'fire{i + 1}.png').convert_alpha() for i in range(2)]
        self.index = 0
        self.timer = time.time()
        self.exhaust = False
        self.bullet_timer = time.time()
        self.lives = 30
        self.powerup = 0
        self.powerup_text_timer = time.time()
        self.powerup_visible = False
        self.powerup_value = 0
        self.powerup_timer = time.time()
        self.powerup_time_k = 5
        self.powerup_name = ''
        self.shield = False
        self.shield_img = pygame.image.load(ASSETS / 'images' / 'player' / 'shield.png').convert_alpha()
        self.laser_time_gap = 0.2
        self.score = 0

    def set_powerup(self, powerup):
        self.restore_mode()
        self.powerup_timer = time.time()
        self.powerup_name = powerup
        if powerup == 'SHIELD':
            self.shield = True
            self.powerup_time_k = 10
        elif powerup == 'FAST LASER':
            self.laser_time_gap = 0.05
            self.powerup_time_k = 20
        elif powerup == 'DESTROY':
            for i in Objects.objects:
                if isinstance(i, Enemy):
                    if distance((i.x, i.y), (self.x, self.y)) < 2000:
                        i.destroy()

    def restore_mode(self):
        if self.powerup_name == 'SHIELD':
            self.shield = False
        if self.powerup_name == 'FAST LASER':
            self.laser_time_gap = 0.2

    def damage(self):
        if self.shield:
            return
        self.lives -= 1
        if self.lives < 0:
            self.alive = False
            Objects.finished = True

    def accelerate(self):
        self.exhaust = True
        self.acc += 0.1
        if self.acc > 10:
            self.acc = 10

    def decelerate(self):
        self.exhaust = True
        self.acc -= 0.1
        if self.acc < -10:
            self.acc = -10

    def stabilize(self):
        self.exhaust = False
        self.acc *= 0.99

    def fire(self):
        if time.time() - self.bullet_timer < self.laser_time_gap:
            return
        SoundManager.play('shoot1')
        self.bullet_timer = time.time()
        Objects.add(Laser(self.x, self.y, self.angle - 90, origin=self))

    def update(self, events: list[pygame.event.Event]):
        if time.time() - self.powerup_timer > self.powerup_time_k:
            self.restore_mode()
        for i in Objects.objects:
            if isinstance(i, Meteor):
                if distance((self.x, self.y), (i.x, i.y)) < i.hitbox_r:
                    i.destroy()
        self.stabilize()
        if time.time() - self.timer > 0.1:
            self.index += 1
            self.index %= len(self.flame)
            self.timer = time.time()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += 3
        if keys[pygame.K_RIGHT]:
            self.angle -= 3
        angle = self.angle - 90
        if keys[pygame.K_UP]:
            self.accelerate()
        if keys[pygame.K_DOWN]:
            self.decelerate()
        if keys[pygame.K_SPACE]:
            self.fire()
        dx = cos(radians(angle))
        dy = -sin(radians(angle))
        Objects.move_world(dx * self.acc, dy * self.acc)
        self.angle %= 360

        if self.powerup > 0:
            if time.time() - self.powerup_text_timer > 0.5:
                self.powerup_text_timer = time.time()
                self.powerup_visible = not self.powerup_visible
        else:
            self.powerup_visible = False

        if self.powerup > 0:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                        powerup = choose_powerup()
                        if powerup is not None:
                            self.powerup -= 1
                            self.set_powerup(powerup)
        # pygame.display.set_caption(str(self.acc))

    def draw(self, surf: pygame.Surface):
        if self.exhaust:
            angle = self.angle - 90
            dx = cos(radians(angle))
            dy = -sin(radians(angle))
            img = pygame.transform.rotate(self.flame[self.index], self.angle)
            surf.blit(img, img.get_rect(center=(self.x + dx * 50, self.y + dy * 50)))
        if self.shield:
            surf.blit(self.shield_img, self.shield_img.get_rect(center=(self.x, self.y)))
        super().draw(surf)
        t = text('Lives: ' + str(self.lives))
        surf.blit(t, t.get_rect(midright=(screen_width - 50, 50)))
        if self.powerup_visible:
            t = text('[Mutation Available]')
            surf.blit(t, t.get_rect(midright=(screen_width - 50, 150)))
            t = text('[Press P to Activate]')
            surf.blit(t, t.get_rect(midright=(screen_width - 50, 200)))
        t = text('Score: ' + str(self.score))
        surf.blit(t, t.get_rect(midright=(screen_width - 50, 100)))


class Enemy(BaseObject):
    def __init__(self):
        number = randint(0, 3) + 1
        img = pygame.image.load(ASSETS / 'images' / 'enemies' / f'enemy{number}.png').convert_alpha()
        img = pygame.transform.flip(img, False, True)
        x = choice([randint(-500, -400), randint(screen_width + 400, screen_width + 500)])
        y = choice([randint(-500, -400), randint(screen_height + 400, screen_height + 500)])
        super().__init__(x, y, sprite=img)
        self.acc = 0
        self.flame = [pygame.image.load(ASSETS / 'images' / 'player' / f'fire{i + 1}.png').convert_alpha() for i in range(2)]
        self.index = 0
        self.timer = time.time()
        self.exhaust = False
        self.bullet_timer = time.time()
        self.speed = number

    def destroy(self):
        for i in Objects.objects:
            if isinstance(i, Player):
                i.score += 25
                i.powerup_value += 25
                if i.powerup_value >= 100:
                    i.powerup += 1
                    i.powerup_value = 0
        SoundManager.play('explode')
        self.alive = False

    def accelerate(self):
        self.exhaust = True
        self.acc += 0.1
        if self.acc > self.speed:
            self.acc = self.speed

    def decelerate(self):
        self.exhaust = True
        self.acc -= 0.1
        if self.acc < -self.speed:
            self.acc = -self.speed

    def stabilize(self):
        self.exhaust = False
        self.acc *= 0.99
        if self.acc < 0.001:
            self.acc = 0

    def fire(self):
        if time.time() - self.bullet_timer < 0.75:
            return
        SoundManager.play('shoot2')
        self.bullet_timer = time.time()
        Objects.add(Laser(self.x, self.y, self.angle - 90, origin=self))

    def update(self, events: list[pygame.event.Event]):
        for i in Objects.objects:
            if isinstance(i, Meteor):
                if distance((self.x, self.y), (i.x, i.y)) < i.hitbox_r:
                    i.destroy()
        self.stabilize()
        if time.time() - self.timer > 0.1:
            self.index += 1
            self.index %= len(self.flame)
            self.timer = time.time()
        self.angle += 5
        self.angle %= 360
        angle = self.angle - 90
        dx = cos(radians(angle))
        dy = -sin(radians(angle))
        self.x -= dx * self.acc
        self.y -= dy * self.acc
        self.use_ai()

    def draw(self, surf: pygame.Surface):
        if self.exhaust:
            angle = self.angle - 90
            dx = cos(radians(angle))
            dy = -sin(radians(angle))
            img = pygame.transform.rotate(self.flame[self.index], self.angle + 180)
            surf.blit(img, img.get_rect(center=(self.x + dx * 50, self.y + dy * 50)))
        super().draw(surf)

    def use_ai(self):
        player = None
        for i in Objects.objects:
            if isinstance(i, Player):
                player = i
        if player is None:
            return
        target_angle = -degrees(math.atan2((player.y - self.y), (player.x - self.x))) - 90
        self.angle = target_angle
        if abs(target_angle - self.angle) < self.speed * 10:
            if distance((self.x, self.y), (player.x, player.y)) > 550:
                self.accelerate()
            else:
                self.decelerate()
                self.fire()


class Radar(BaseObject):
    def __init__(self):
        super().__init__(z=5)
        self.surf = pygame.Surface((500, 500), pygame.SRCALPHA)
        self.visible = True
        pygame.draw.circle(self.surf, (0, 0, 0, 50), self.surf.get_rect().center, self.surf.get_width() // 2)

    def update(self, events: list[pygame.event.Event]):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    self.visible = not self.visible

    def draw(self, surf: pygame.Surface):
        if not self.visible:
            return
        self.surf = pygame.Surface((500, 500), pygame.SRCALPHA)
        pygame.draw.circle(self.surf, (0, 0, 0, 50), self.surf.get_rect().center, self.surf.get_width() // 2)
        cx, cy = self.surf.get_rect().center
        for i in range(0, 360, 45):
            a = radians(i)
            pygame.draw.line(self.surf, (255, 150, 255, 150), (cx, cy), (cx + self.surf.get_width() / 2 * cos(a), cy + self.surf.get_height() / 2 * sin(a)))
        pygame.draw.circle(self.surf, (255, 255, 255, 200), self.surf.get_rect().center, 20, 2)
        for i in Objects.objects:
            if isinstance(i, Enemy):
                d = distance((cx, cy), (i.x, i.y))
                if d <= 2500:
                    angle = math.atan2((i.y - cy), (i.x - cx))
                    r = map_to_range(d, 0, 2500, 0, self.surf.get_width() // 2)
                    # r = self.surf.get_width() // 2
                    pygame.draw.circle(self.surf, (255, 0, 0), (cx + r * cos(angle), cy + r * sin(angle)), 20, 2)
        surf.blit(self.surf, (0, 0))
