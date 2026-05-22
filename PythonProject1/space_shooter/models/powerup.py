# models/powerup.py
import random
import math
import pygame
from config import H, BLACK, WHITE, YELLOW, GREEN, PURPLE, RED

class PowerUp:
    TYPES = {
        'rapid': (YELLOW, '⚡ RAPID', '2x bắn nhanh'),
        'shield': (GREEN, '🛡 SHIELD', '+1 máu'),
        'triple': (PURPLE, '✦ TRIPLE', '3 viên đạn'),
        'bomb': (RED, '💣 BOMB', 'Diệt tất cả!'),
    }

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.kind = random.choice(list(self.TYPES.keys()))
        self.color, self.label, _ = self.TYPES[self.kind]
        self.vy = 2.0
        self.alive = True
        self.frame = 0
        self.radius = 16

    def update(self):
        self.y += self.vy
        self.frame += 1
        if self.y > H + 40:
            self.alive = False

    def draw(self, surf):
        bob = math.sin(self.frame * 0.07) * 4
        cx, cy = int(self.x), int(self.y + bob)
        ring_r = self.radius + abs(math.sin(self.frame * 0.05)) * 6
        pygame.draw.circle(surf, self.color, (cx, cy), self.radius)
        pygame.draw.circle(surf, WHITE, (cx, cy), self.radius, 2)
        pygame.draw.circle(surf, self.color[:3], (cx, cy), int(ring_r), 1)
        font = pygame.font.SysFont('Arial', 11, bold=True)
        lbl = font.render(self.kind[0].upper(), True, BLACK)
        surf.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))