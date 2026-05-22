# models/player.py
import math
import pygame
from config import W, H, CYAN, PURPLE, ORANGE, YELLOW
from sound_factory import play
from drawing import draw_ship
from .bullet import Bullet


class Player:
    def __init__(self):
        self.x = W // 2
        self.y = H - 120  # Vị trí xuất phát thấp hơn một chút
        self.speed = 6  # Tăng tốc độ di chuyển một chút cho mượt
        self.hp = 3
        self.max_hp = 5
        self.score = 0
        self.alive = True
        self.invul = 0
        self.shoot_cd = 0
        self.shoot_delay = 16  # Tốc độ bắn cơ bản nhanh hơn một chút
        self.rapid_timer = 0
        self.triple_timer = 0
        self.has_bomb = False
        self.frame = 0
        self.damaged = False
        self.dmg_flash = 0

    def shoot(self):
        # Tự động tính toán cooldown đạn
        delay = self.shoot_delay // 2 if self.rapid_timer > 0 else self.shoot_delay
        if self.shoot_cd > 0:
            return []

        self.shoot_cd = delay
        bullets = []
        if self.triple_timer > 0:
            bullets.append(Bullet(self.x, self.y - 22, dy=-14, dx=0, color=PURPLE, damage=1))
            bullets.append(Bullet(self.x - 15, self.y - 12, dy=-12, dx=-2, color=PURPLE, damage=1))
            bullets.append(Bullet(self.x + 15, self.y - 12, dy=-12, dx=2, color=PURPLE, damage=1))
            play('triple')
        else:
            bullets.append(Bullet(self.x, self.y - 22, dy=-14, color=CYAN, damage=1))
            play('shoot')
        return bullets

    def take_damage(self):
        if self.invul > 0: return False
        self.hp -= 1
        self.invul = 90
        self.damaged = True
        self.dmg_flash = 15
        play('hit')
        if self.hp <= 0:
            self.alive = False
            play('gameover')
        return True

    def apply_powerup(self, kind):
        play('powerup')
        if kind == 'rapid':
            self.rapid_timer = 400
        elif kind == 'shield':
            self.hp = min(self.hp + 1, self.max_hp)
        elif kind == 'triple':
            self.triple_timer = 400
        elif kind == 'bomb':
            self.has_bomb = True

    def update(self, keys):
        self.frame += 1

        # --- HỆ THỐNG DI CHUYỂN 8 HƯỚNG (MŨI TÊN + WASD) ---
        move_x = 0
        move_y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]: move_y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_y = 1

        # Chuẩn hóa vector di chuyển chéo để không bị chạy nhanh hơn bình thường
        if move_x != 0 and move_y != 0:
            factor = 0.7071
            move_x *= factor
            move_y *= factor

        self.x += move_x * self.speed
        self.y += move_y * self.speed

        # Giới hạn không cho tàu bay ra khỏi rìa màn hình hiển thị
        self.x = max(30, min(W - 30, self.x))
        self.y = max(40, min(H - 40, self.y))

        # Cập nhật các bộ đếm thời gian
        if self.shoot_cd > 0: self.shoot_cd -= 1
        if self.invul > 0: self.invul -= 1
        if self.rapid_timer > 0: self.rapid_timer -= 1
        if self.triple_timer > 0: self.triple_timer -= 1
        if self.dmg_flash > 0: self.dmg_flash -= 1
        self.damaged = self.dmg_flash > 0

    def draw(self, surf):
        if self.invul > 0 and (self.invul // 6) % 2 == 0:
            return
        draw_ship(surf, self.x, self.y, damaged=self.damaged)

        # Hiệu ứng lửa phản lực phía sau đuôi tàu sinh động
        t = pygame.time.get_ticks()
        fl = abs(math.sin(t * 0.02)) * 12 + 10
        pygame.draw.polygon(surf, ORANGE,
                            [(self.x - 6, self.y + 14), (self.x + 6, self.y + 14), (self.x, self.y + 14 + int(fl))])
        pygame.draw.polygon(surf, YELLOW, [(self.x - 3, self.y + 14), (self.x + 3, self.y + 14),
                                           (self.x, self.y + 14 + int(fl * 0.6))])