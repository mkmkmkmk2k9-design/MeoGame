# models/bullet.py
import pygame
from config import H, W, WHITE, RED, ORANGE, CYAN

class Bullet:
    def __init__(self, x, y, dy=-12, dx=0, color=CYAN, radius=4, damage=1.5):
        self.x, self.y = float(x), float(y)
        self.dx, self.dy = dx, dy
        self.color = color
        self.radius = radius
        self.damage = damage
        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.y < -20 or self.y > H + 20 or self.x < -20 or self.x > W + 20:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), max(1, self.radius - 2))


class EnemyBullet:
    def __init__(self, x, y, dy=5, dx=0):
        self.x, self.y = float(x), float(y)
        self.dx, self.dy = dx, dy
        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.y > H + 20:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, RED, (int(self.x), int(self.y)), 5)
        pygame.draw.circle(surf, ORANGE, (int(self.x), int(self.y)), 3)
