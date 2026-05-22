# models/particle.py
import random
import math
import pygame
from config import W, H, ORANGE

class Particle:
    def __init__(self, x, y, color=ORANGE, speed=3.0, size=4, life=40):
        angle = random.uniform(0, 2 * math.pi)
        spd = random.uniform(speed * 0.3, speed)
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # Gravity nhẹ
        self.life -= 1
        self.vx *= 0.98
        return self.life > 0

    def draw(self, surf):
        alpha = self.life / self.max_life
        s = max(1, int(self.size * alpha))
        r, g, b = self.color
        col = (min(255, r), min(255, g), min(255, b))
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), s)


class Star:
    def __init__(self, speed_z=1.0):
        self.x = 0
        self.y = 0
        self.size = 1
        self.blink = 60
        self.timer = 0
        self.alpha = 255
        self.reset(new=True)
        self.speed = speed_z

    def reset(self, new=False):
        self.x = random.randint(0, W)
        self.y = random.randint(0, H) if new else 0
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2.5)
        self.blink = random.randint(30, 120)
        self.timer = random.randint(0, self.blink)
        self.alpha = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        self.timer += 1
        if self.timer > self.blink:
            self.timer = 0
            self.alpha = random.randint(100, 255)
        if self.y > H:
            self.reset()

    def draw(self, surf):
        c = (self.alpha,) * 3
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.size)