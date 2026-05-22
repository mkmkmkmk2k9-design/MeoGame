# models/enemy.py
import random
import math
import pygame
from config import W, H, GREEN, RED, PURPLE, ORANGE, GRAY, BLUE
from drawing import draw_alien
from .bullet import EnemyBullet

class Enemy:
    def __init__(self, x, y, atype=0, level=1):
        self.x, self.y = float(x), float(y)
        self.atype = atype
        self.frame = random.randint(0, 100)
        self.max_hp = [1, 2, 3][atype % 3] + (level // 3)
        self.hp = self.max_hp
        self.shoot_cd = random.randint(70, 185)
        self.shoot_timer = random.randint(0, self.shoot_cd)
        self.alive = True
        self.pattern = random.choice(['straight', 'wave', 'zigzag'])
        self.t = random.uniform(0, 100)
        self.base_x = float(x)
        self.speed_y = 1.2 + level * 0.15
        self.speed_x = random.uniform(0.8, 2.0)
        self.dir = random.choice([-1, 1])

    def update(self, player_bullets):
        self.frame += 1
        self.t += 0.03

        if self.pattern == 'wave':
            self.x = self.base_x + math.sin(self.t) * 60
            self.y += self.speed_y
        elif self.pattern == 'zigzag':
            self.x += self.dir * self.speed_x
            self.y += self.speed_y * 0.7
            if self.x < 20 or self.x > W - 20:
                self.dir *= -1
        else:
            self.y += self.speed_y

        self.x = max(20.0, min(float(W - 20), self.x))

        self.shoot_timer += 1
        bullets_shot = []
        if self.shoot_timer >= self.shoot_cd:
            self.shoot_timer = 0
            bullets_shot.append(EnemyBullet(int(self.x), int(self.y) + 20))

        if self.y > H + 50:
            self.alive = False

        hits = []
        for b in player_bullets:
            if b.alive:
                dx = b.x - self.x
                dy = b.y - self.y
                if math.hypot(dx, dy) < 22:
                    b.alive = False
                    self.hp -= b.damage
                    hits.append(True)

        if self.hp <= 0:
            self.alive = False

        return bullets_shot, len(hits) > 0

    def draw(self, surf):
        draw_alien(surf, int(self.x), int(self.y), self.atype, self.frame, self.hp / self.max_hp)
        if self.max_hp > 1:
            bar_w = 36
            ratio = self.hp / self.max_hp
            pygame.draw.rect(surf, GRAY, (int(self.x) - bar_w // 2, int(self.y) - 26, bar_w, 5))
            pygame.draw.rect(surf, GREEN if ratio > 0.5 else ORANGE, (int(self.x) - bar_w // 2, int(self.y) - 26, int(bar_w * ratio), 5))