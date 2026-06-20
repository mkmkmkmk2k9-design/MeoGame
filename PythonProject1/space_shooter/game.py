# game.py
import pygame
import random
import sys
import math
import json
import os

from config import W, H, FPS, DARK, CYAN, YELLOW, WHITE, RED, GRAY, GREEN, PURPLE, ORANGE
from sound_factory import play
from models import Player, Enemy, PowerUp, Particle, Star


class Game:
    def __init__(self):
        self.leaderboard_file = "leaderboard.json"
        self.leaderboard = self.load_leaderboard()

        self.screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption(" ALIEN INVASION – Neo Cyber ")
        self.clock = pygame.time.Clock()

        # Hệ thống Font chữ hiện đại
        self.font_big = pygame.font.SysFont('Segoe UI', 54, bold=True)
        self.font_med = pygame.font.SysFont('Segoe UI', 24, bold=True)
        self.font_sm = pygame.font.SysFont('Segoe UI', 16, bold=True)
        self.font_xs = pygame.font.SysFont('Consolas', 13)

        self.hi_score = 0
        self.player = None
        self.enemies = []
        self.p_bullets = []
        self.e_bullets = []
        self.powerups = []
        self.particles = []
        self.level = 0
        self.wave = 0
        self.wave_cd = 0
        self.state = 'menu'
        self.flash_msg = ''
        self.flash_t = 0
        self.screen_shake = 0
        self.countdown_timer = 0  # Bộ đếm ngược 3, 2, 1 trước khi vào trận

        self.stars = [Star() for _ in range(120)]
        self.reset()

    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, "r") as f:
                    return json.load(f)
            except:
                return [0, 0, 0, 0, 0]
        return [0, 0, 0, 0, 0]

    def update_leaderboard(self, new_score):
        if new_score <= 0:
            return
        self.leaderboard.append(new_score)
        self.leaderboard.sort(reverse=True)
        self.leaderboard = self.leaderboard[:5]
        try:
            with open(self.leaderboard_file, "w") as f:
                json.dump(self.leaderboard, f)
        except Exception as e:
            print("Lỗi ghi file bảng xếp hạng:", e)

    def reset(self):
        self.player = Player()
        self.enemies = []
        self.p_bullets = []
        self.e_bullets = []
        self.powerups = []
        self.particles = []
        self.level = 0
        self.wave = 0
        self.wave_cd = 0
        self.hi_score = getattr(self, 'hi_score', 0)
        self.flash_msg = ''
        self.flash_t = 0
        self.screen_shake = 0
        self.countdown_timer = 0

    def start_with_countdown(self):
        self.state = 'playing'
        self.countdown_timer = 180  # 3 giây đếm ngược (180 frames ở 60 FPS)
        self.enemies.clear()

    def spawn_wave(self):
        rows = min(3, 1 + self.wave // 2)
        cols = min(8, 4 + self.wave)
        for row in range(rows):
            for col in range(cols):
                x = 80 + col * ((W - 120) // max(cols - 1, 1))
                y = 70 + row * 80
                atype = (row + self.level) % 3
                self.enemies.append(Enemy(x, y, atype, self.level))

    def explode(self, x, y, color=ORANGE, n=20, big=False):
        for _ in range(n):
            size = random.randint(2, 6 if big else 4)
            speed = random.uniform(2, 8 if big else 5)
            life = random.randint(20, 50)
            r, g, b = color
            c = (max(0, min(255, r + random.randint(-40, 40))),
                 max(0, min(255, g + random.randint(-40, 40))),
                 max(0, min(255, b + random.randint(-40, 40))))
            self.particles.append(Particle(int(x), int(y), c, speed, size, life))
        play('explode')
        if big: self.screen_shake = 10

    def run(self):
        while True:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_q:
                        if self.state in ('menu', 'gameover'):
                            pygame.quit()
                            sys.exit()
                        elif self.state == 'pause':
                            self.state = 'menu'
                            self.reset()

                    if event.key == pygame.K_ESCAPE:
                        if self.state == 'playing':
                            self.state = 'pause'
                        elif self.state == 'pause':
                            self.state = 'playing'
                        elif self.state == 'gameover':
                            self.state = 'menu'
                            self.reset()
                        elif self.state == 'menu':
                            pygame.quit()
                            sys.exit()

                    if self.state == 'menu':
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.reset()
                            self.start_with_countdown()

                    elif self.state == 'playing':
                        if event.key == pygame.K_b and self.player.has_bomb and self.countdown_timer <= 0:
                            self.use_bomb()

                    elif self.state == 'pause':
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.state = 'playing'
                        elif event.key == pygame.K_r:
                            self.reset()
                            self.start_with_countdown()

                    elif self.state == 'gameover':
                        if event.key == pygame.K_RETURN:
                            self.reset()
                            self.start_with_countdown()

            if self.state != 'pause':
                for s in self.stars: s.update()

            if self.state == 'playing':
                self.update_game(keys)

            self.draw()

    def update_game(self, keys):
        if self.countdown_timer > 0:
            self.countdown_timer -= 1
            if self.countdown_timer == 0:
                self.spawn_wave()
            return

        if not self.player.alive:
            if self.state != 'gameover':
                self.update_leaderboard(self.player.score)
            self.hi_score = max(self.hi_score, self.player.score)
            self.state = 'gameover'
            self.screen_shake = 0
            return

        self.player.update(keys)

        new_b = self.player.shoot()
        self.p_bullets.extend(new_b)

        for b in self.p_bullets: b.update()
        self.p_bullets = [b for b in self.p_bullets if b.alive]

        for b in self.e_bullets: b.update()
        self.e_bullets = [b for b in self.e_bullets if b.alive]

        for b in self.e_bullets:
            if b.alive:
                dx = b.x - self.player.x
                dy = b.y - self.player.y
                if math.hypot(dx, dy) < 20:
                    b.alive = False
                    self.player.take_damage()
                    self.explode(self.player.x, self.player.y, color=CYAN, n=12)

        # === ĐÃ SỬA: SỬ DỤNG WAS_HIT ĐỂ CHẶN LỖI TÍNH ĐIỂM KHI QUÁI LỌT ĐƯỜNG ===
        for e in self.enemies:
            new_shots, was_hit = e.update(self.p_bullets)
            self.e_bullets.extend(new_shots)

            # Nếu quái vật không còn sống (alive == False) sau khi update
            if not e.alive:
                # TRƯỜNG HỢP 1: Chết vì dính đạn (was_hit trúng vào frame này) -> Cộng điểm!
                if was_hit:
                    self.explode(int(e.x), int(e.y), [GREEN, RED, PURPLE][e.atype % 3], n=22, big=True)

                    pts = [10, 20, 40][e.atype % 3] * (self.level + 1)
                    self.player.score += pts

                    if random.random() < 0.20:
                        self.powerups.append(PowerUp(int(e.x), int(e.y)))
                else:
                    # TRƯỜNG HỢP 2: Tự biến mất do đi hết đường (was_hit = False) -> Bỏ qua không cộng điểm
                    pass

            # Nếu quái dính đạn nhưng lượng máu vẫn còn lớn hơn 0
            elif was_hit:
                self.explode(int(e.x), int(e.y), ORANGE, n=6)

            # TRƯỜNG HỢP 3: Quái húc thẳng vào người chơi (Không cộng điểm)
            if e.alive:
                dx = e.x - self.player.x
                dy = e.y - self.player.y
                if math.hypot(dx, dy) < 26:
                    e.alive = False
                    self.player.take_damage()
                    self.explode(int(e.x), int(e.y), ORANGE, n=25, big=True)

        # Lọc sạch danh sách: Giữ lại những con thực sự còn sống và đang ở trên màn hình
        self.enemies = [e for e in self.enemies if e.alive]

        for pu in self.powerups:
            pu.update()
            if pu.alive:
                dx = pu.x - self.player.x
                dy = pu.y - self.player.y
                if math.hypot(dx, dy) < 24:
                    pu.alive = False
                    self.player.apply_powerup(pu.kind)
                    self.flash_msg = PowerUp.TYPES[pu.kind][1]
                    self.flash_t = 20
        self.powerups = [p for p in self.powerups if p.alive]

        self.particles = [p for p in self.particles if p.update()]

        if self.screen_shake > 0:
            if self.state == 'gameover':
                self.screen_shake = 0
            else:
                self.screen_shake -= 1

        if not self.enemies:
            if self.wave_cd > 0:
                self.wave_cd -= 1
            else:
                self.wave_cd = 80
                self.level += 1
                self.wave = self.level
                self.flash_msg = f"STAGE {self.level}"
                self.flash_t = 50
                try:
                    play('levelup')
                except:
                    pass
                self.spawn_wave()

    def use_bomb(self):
        self.player.has_bomb = False
        play('bomb')
        for e in self.enemies:
            self.explode(int(e.x), int(e.y), [GREEN, RED, PURPLE][e.atype % 3], n=25, big=True)
            self.player.score += 10 * (self.level + 1)
        self.enemies.clear()
        self.e_bullets.clear()
        self.screen_shake = 18
        self.flash_msg = " BOMB DETONATED!"
        self.flash_t = 30

    def draw(self):
        sx = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        sy = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0

        surf = pygame.Surface((W, H))
        surf.fill(DARK)

        for s in self.stars: s.draw(surf)

        if self.state == 'menu':
            self.draw_menu_on(surf)
        elif self.state == 'playing':
            self.draw_playing(surf)
            self.draw_countdown_overlay(surf)
        elif self.state == 'gameover':
            self.draw_playing(surf)
            self.draw_gameover_on(surf)

        elif self.state == 'pause':
            self.draw_playing(surf)
            self.draw_countdown_overlay(surf)

            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((10, 10, 18, 210))
            surf.blit(overlay, (0, 0))

            panel_w, panel_h = 640, 300
            panel_x = W // 2 - panel_w // 2
            panel_y = H // 2 - panel_h // 2

            pygame.draw.rect(surf, YELLOW, (panel_x, panel_y, panel_w, panel_h), 1, border_radius=12)

            p_text = self.font_big.render("GAME PAUSED", True, YELLOW)
            surf.blit(p_text, (W // 2 - p_text.get_width() // 2, panel_y + 25))

            content_y = panel_y + 110

            left_x = panel_x + 40

            def draw_pause_left(text, font, color, y_offset):
                lbl = font.render(text, True, color)
                surf.blit(lbl, (left_x, content_y + y_offset))

            draw_pause_left("TÙY CHỌN:", self.font_sm, CYAN, 0)

            t = pygame.time.get_ticks() / 1000
            resume_color = GREEN if int(t * 1.5) % 2 == 0 else (0, 150, 0)

            draw_pause_left("[ESC / SPACE] - Tiếp Tục Trận Đấu", self.font_xs, resume_color, 40)
            draw_pause_left("[R]           - Làm Lại (Stage 0)", self.font_xs, YELLOW, 75)
            draw_pause_left("[Q]           - Quay Lại Menu Chính", self.font_xs, WHITE, 110)

            right_x = panel_x + 380

            lead_title = self.font_sm.render("- TOP 5 LEADERBOARD -", True, PURPLE)
            surf.blit(lead_title, (right_x, content_y))

            for i, score in enumerate(self.leaderboard):
                rank_text = f"#{i + 1}   {score:06d} PTS"
                color = GREEN if (score == self.player.score and score > 0) else CYAN
                score_txt = self.font_xs.render(rank_text, True, color)
                surf.blit(score_txt, (right_x, content_y + 35 + i * 25))

        self.screen.blit(surf, (sx, sy))
        pygame.display.flip()

    def draw_countdown_overlay(self, surf):
        if self.countdown_timer <= 0:
            return

        if self.countdown_timer > 120:
            txt_str = "3"
            color = RED
        elif self.countdown_timer > 60:
            txt_str = "2"
            color = ORANGE
        elif self.countdown_timer > 10:
            txt_str = "1"
            color = YELLOW
        else:
            txt_str = "GO!"
            color = GREEN

        font_huge = pygame.font.SysFont('Segoe UI', 100, bold=True)
        shadow_lbl = font_huge.render(txt_str, True, (20, 20, 30))
        surf.blit(shadow_lbl, (W // 2 - shadow_lbl.get_width() // 2 + 4, H // 2 - shadow_lbl.get_height() // 2 + 4))

        lbl = font_huge.render(txt_str, True, color)
        surf.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 - lbl.get_height() // 2))

    def draw_menu_on(self, surf):
        t = pygame.time.get_ticks() / 1000

        pygame.draw.rect(surf, PURPLE, (20, 20, W - 40, H - 40), 2, border_radius=15)
        pygame.draw.rect(surf, CYAN, (24, 24, W - 48, H - 48), 1, border_radius=12)

        title_str = "ALIEN INVASION"
        total_width = sum(self.font_big.render(ch, True, (0, 0, 0)).get_width() for ch in title_str)
        start_x = W // 2 - total_width // 2

        current_x = start_x
        for i, ch in enumerate(title_str):
            hue = (i * 18 + t * 90) % 360
            c = pygame.Color(0)
            c.hsva = (hue, 85, 100, 100)

            lbl = self.font_big.render(ch, True, c)
            surf.blit(lbl, (current_x, 120))
            current_x += lbl.get_width()

        sub = self.font_sm.render(" NEO CYBER SPACE SHOOTER ", True, CYAN)
        surf.blit(sub, (W // 2 - sub.get_width() // 2, 195))

        box_x = W // 2 - 200
        box_y = 250
        box_w = 400
        box_h = 320
        pygame.draw.rect(surf, (20, 20, 40), (box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(surf, CYAN, (box_x, box_y, box_w, box_h), 1, border_radius=10)

        lines = [
            ("ĐIỀU KHIỂN:", "", YELLOW),
            ("WASD / Phím mũi tên", " - Di chuyển", WHITE),
            ("Vũ khí", " - TỰ ĐỘNG BẮN", CYAN),
            ("Phím [B]", " - Kích hoạt Bom", RED),
            ("-----------------------------------", "", GRAY),
            ("VẬT PHẨM (POWER-UP):", "", YELLOW),
            ("RAPID", " - Tăng tốc bắn", YELLOW),
            ("SHIELD", " - Bổ sung giáp", GREEN),
            ("TRIPLE", " - Đạn tỏa 3 tia", PURPLE),
            ("BOMB", " - Quét sạch map", RED),
        ]

        text_start_x = box_x + 35
        COL_WIDTH = 20

        for i, item in enumerate(lines):
            label, value, col = item
            if value != "":
                final_text = f"{label.ljust(COL_WIDTH)}{value}"
            else:
                final_text = label

            t2 = self.font_xs.render(final_text, True, col)
            surf.blit(t2, (text_start_x, box_y + 20 + i * 28))

        if int(t * 2) % 2 == 0:
            s = self.font_med.render("[ ẤN ENTER ĐỂ CHIẾN ]", True, GREEN)
            surf.blit(s, (W // 2 - s.get_width() // 2, 610))

    def draw_playing(self, surf):
        for p in self.particles:  p.draw(surf)
        for pu in self.powerups:  pu.draw(surf)
        for b in self.p_bullets:  b.draw(surf)
        for b in self.e_bullets:  b.draw(surf)
        for e in self.enemies:    e.draw(surf)
        if self.player.alive:     self.player.draw(surf)

        hud_y = 15
        start_x = 20
        block_w = 18
        block_h = 14
        gap = 6

        hp_lbl = self.font_xs.render("HP", True, WHITE)
        surf.blit(hp_lbl, (start_x, hud_y - 1))

        for i in range(self.player.max_hp):
            bx = start_x + 25 + i * (block_w + gap)
            if i < self.player.hp:
                hp_color = GREEN if self.player.hp > 1 else RED
                pygame.draw.rect(surf, hp_color, (bx, hud_y, block_w, block_h), border_radius=3)
            else:
                pygame.draw.rect(surf, (60, 60, 70), (bx, hud_y, block_w, block_h), 1, border_radius=3)

        sc = self.font_med.render(f"{self.player.score:06d}", True, CYAN)
        surf.blit(sc, (W // 2 - sc.get_width() // 2, 8))

        hi = self.font_xs.render(f"HI-SCORE: {self.hi_score:06d}", True, GRAY)
        surf.blit(hi, (W // 2 - hi.get_width() // 2, 38))

        lv = self.font_med.render(f"STG {self.level}", True, WHITE)
        surf.blit(lv, (W - lv.get_width() - 20, 8))

        px2 = 20
        py2 = H - 36

        if self.player.rapid_timer > 0:
            pygame.draw.rect(surf, (80, 70, 20), (px2, py2, 85, 22), border_radius=5)
            t2 = self.font_xs.render(f"Rapid: {self.player.rapid_timer // 60}s", True, YELLOW)
            surf.blit(t2, (px2 + 6, py2 + 3))
            px2 += 95

        if self.player.triple_timer > 0:
            pygame.draw.rect(surf, (50, 20, 80), (px2, py2, 90, 22), border_radius=5)
            t2 = self.font_xs.render(f"Triple: {self.player.triple_timer // 60}s", True, PURPLE)
            surf.blit(t2, (px2 + 6, py2 + 3))
            px2 += 100

        if self.player.has_bomb:
            pygame.draw.rect(surf, (80, 20, 20), (px2, py2, 75, 22), border_radius=5)
            pygame.draw.rect(surf, RED, (px2, py2, 75, 22), 1, border_radius=5)
            t2 = self.font_xs.render("Bomb [B]", True, WHITE)
            surf.blit(t2, (px2 + 8, py2 + 3))

        if self.flash_t > 0 and self.countdown_timer <= 0:
            txt = self.font_big.render(self.flash_msg, True, YELLOW)
            shadow = self.font_big.render(self.flash_msg, True, (40, 30, 0))
            surf.blit(shadow, (W // 2 - txt.get_width() // 2 + 3, H // 2 - 60 + 3))
            surf.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 60))
            self.flash_t -= 1

    def draw_gameover_on(self, surf):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((5, 5, 15, 200))
        surf.blit(overlay, (0, 0))

        pygame.draw.rect(surf, RED, (W // 2 - 220, H // 2 - 250, 440, 480), 1, border_radius=12)

        ov = self.font_big.render("MISSION FAILED", True, RED)
        surf.blit(ov, (W // 2 - ov.get_width() // 2, H // 2 - 220))

        sc = self.font_med.render(f"FINAL SCORE: {self.player.score:06d}", True, WHITE)
        surf.blit(sc, (W // 2 - sc.get_width() // 2, H // 2 - 140))

        hi = self.font_sm.render(f"RECORD TO BEAT: {self.hi_score:06d}", True, YELLOW)
        surf.blit(hi, (W // 2 - hi.get_width() // 2, H // 2 - 90))

        lead_title = self.font_sm.render("- TOP 5 LEADERBOARD -", True, PURPLE)
        surf.blit(lead_title, (W // 2 - lead_title.get_width() // 2, H // 2 - 40))

        for i, score in enumerate(self.leaderboard):
            rank_text = f"#{i + 1}   {score:06d} PTS"
            color = GREEN if (score == self.player.score and score > 0) else CYAN
            score_txt = self.font_xs.render(rank_text, True, color)
            surf.blit(score_txt, (W // 2 - score_txt.get_width() // 2, H // 2 + i * 30))

        t = pygame.time.get_ticks() / 1000
        if int(t * 1.5) % 2 == 0:
            rs = self.font_med.render("[ PRESS ENTER TO RESTART ]", True, GREEN)
            surf.blit(rs, (W // 2 - rs.get_width() // 2, H // 2 + 180))
