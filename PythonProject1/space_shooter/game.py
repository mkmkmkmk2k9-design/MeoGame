# game.py
import pygame
import random
import sys
import math

from config import W, H, FPS, DARK, CYAN, YELLOW, WHITE, RED, GRAY, GREEN, PURPLE, ORANGE
from sound_factory import play
from models import Player, Enemy, PowerUp, Particle, Star


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
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
        self.level = 1
        self.wave = 0
        self.wave_cd = 0
        self.state = 'menu'
        self.flash_msg = ''
        self.flash_t = 0
        self.screen_shake = 0

        self.stars = [Star() for _ in range(120)]
        self.reset()

    def reset(self):
        self.player = Player()
        self.enemies = []
        self.p_bullets = []
        self.e_bullets = []
        self.powerups = []
        self.particles = []
        self.level = 1
        self.wave = 0
        self.wave_cd = 0
        self.hi_score = getattr(self, 'hi_score', 0)
        self.flash_msg = ''
        self.flash_t = 0
        self.screen_shake = 0

    def spawn_wave(self):
        self.wave += 1
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
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        pygame.quit()
                        sys.exit()

                    if self.state == 'menu':
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.state = 'playing'
                            self.spawn_wave()

                    elif self.state == 'playing':
                        # Chỉ giữ nút B thủ công để kích hoạt bom nguyên tử khẩn cấp
                        if event.key == pygame.K_b and self.player.has_bomb:
                            self.use_bomb()

                    elif self.state == 'gameover':
                        if event.key == pygame.K_RETURN:
                            self.reset()
                            self.state = 'playing'
                            self.spawn_wave()

            for s in self.stars: s.update()

            if self.state == 'playing':
                self.update_game(keys)

            self.draw()

    def update_game(self, keys):
        # --- ĐÃ SỬA: Khóa chết hoàn toàn screen_shake về 0 khi die ---
        if not self.player.alive:
            self.hi_score = max(self.hi_score, self.player.score)
            self.state = 'gameover'
            self.screen_shake = 0
            return

        self.player.update(keys)

        # --- CƠ CHẾ TỰ ĐỘNG BẮN ĐẠN (AUTO-FIRE) ---
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

        for e in self.enemies:
            new_shots, was_hit = e.update(self.p_bullets)
            self.e_bullets.extend(new_shots)
            if not e.alive:
                self.explode(int(e.x), int(e.y), [GREEN, RED, PURPLE][e.atype % 3], n=22, big=True)
                pts = [10, 20, 40][e.atype % 3] * self.level
                self.player.score += pts
                if random.random() < 0.20:
                    self.powerups.append(PowerUp(int(e.x), int(e.y)))
            elif was_hit:
                self.explode(int(e.x), int(e.y), ORANGE, n=6)

            if e.alive:
                dx = e.x - self.player.x
                dy = e.y - self.player.y
                if math.hypot(dx, dy) < 26:
                    e.alive = False
                    self.player.take_damage()
                    self.explode(int(e.x), int(e.y), ORANGE, n=25, big=True)

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

        # Đảm bảo dọn dẹp biến shake khi không ở trạng thái gameover
        if self.screen_shake > 0:
            if self.state == 'gameover':
                self.screen_shake = 0
            else:
                self.screen_shake -= 1

        if not self.enemies:
            if self.wave_cd > 0:
                self.wave_cd -= 1
            else:
                if self.wave >= 3 and self.wave % 3 == 0:
                    self.level += 1
                    self.flash_msg = f"STAGE {self.level}"
                    self.flash_t = 50
                    play('levelup')
                else:
                    self.flash_msg = f"WAVE {self.wave + 1}"
                    self.flash_t = 30
                self.wave_cd = 80
                self.spawn_wave()

    def use_bomb(self):
        self.player.has_bomb = False
        play('bomb')
        for e in self.enemies:
            self.explode(int(e.x), int(e.y), [GREEN, RED, PURPLE][e.atype % 3], n=25, big=True)
            self.player.score += 10 * self.level
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
        elif self.state == 'gameover':
            self.draw_playing(surf)
            self.draw_gameover_on(surf)

        self.screen.blit(surf, (sx, sy))
        pygame.display.flip()

    def draw_menu_on(self, surf):
        # --- GUI MENU THIẾT KẾ MỚI (CYBERPUNK NEON) ---
        t = pygame.time.get_ticks() / 1000

        # Vẽ khung viền phát sáng trang trí ngoài viền màn hình chính
        pygame.draw.rect(surf, PURPLE, (20, 20, W - 40, H - 40), 2, border_radius=15)
        pygame.draw.rect(surf, CYAN, (24, 24, W - 48, H - 48), 1, border_radius=12)

        # === 1. SỬA LỖI TIÊU ĐỀ: Tính tổng chiều rộng thực tế để chữ không bị đè nhau ===
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
            current_x += lbl.get_width()  # Cộng dồn chiều rộng thực tế của từng chữ

        sub = self.font_sm.render(" NEO CYBER SPACE SHOOTER ", True, CYAN)
        surf.blit(sub, (W // 2 - sub.get_width() // 2, 195))

        # Khung hộp chứa hướng dẫn nút bấm (Glassmorphism card)
        box_x = W // 2 - 200
        box_y = 250
        box_w = 400
        box_h = 320
        pygame.draw.rect(surf, (20, 20, 40), (box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(surf, CYAN, (box_x, box_y, box_w, box_h), 1, border_radius=10)

        # === 2. SỬA LỖI CĂN HÀNG: Cấu trúc lại danh sách theo dạng (Label, Value, Color) ===
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

        text_start_x = box_x + 35  # Ghim lề trái thụt vào trong hộp 35px
        COL_WIDTH = 20  # Số lượng ký tự cố định dành cho cột bên trái

        for i, item in enumerate(lines):
            label, value, col = item

            if value != "":
                # Tự động bù dấu cách vào bên phải nhãn (Label) cho đủ 20 ký tự
                final_text = f"{label.ljust(COL_WIDTH)}{value}"
            else:
                final_text = label

            # SỬ DỤNG self.font_xs (Consolas) là font chữ đơn cách để căn lề chuẩn 100%
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

        # === ĐÃ SỬA: Chuyển thanh máu cũ thành các Ô BLOCK năng lượng xếp hàng ngang ===
        hud_y = 15
        start_x = 20
        block_w = 18  # Độ rộng của mỗi ô máu
        block_h = 14  # Chiều cao của mỗi ô máu
        gap = 6  # Khoảng cách giữa các ô

        # Vẽ chữ "HP" nhỏ ở đầu làm nhãn định vị
        hp_lbl = self.font_xs.render("HP", True, WHITE)
        surf.blit(hp_lbl, (start_x, hud_y - 1))

        # Vòng lặp chạy từ 0 đến max_hp (Số lượng ô máu tối đa của người chơi)
        for i in range(self.player.max_hp):
            # Tính toán tọa độ X dịch dần sang phải cho từng ô
            bx = start_x + 25 + i * (block_w + gap)

            if i < self.player.hp:
                # Nếu i nhỏ hơn số HP hiện tại -> Ô máu này đang đầy (Người chơi còn sống)
                hp_color = GREEN if self.player.hp > 1 else RED

                # [LỰA CHỌN 1]: Kiểu ô vuông góc cạnh nguyên khối chuẩn Cyberpunk
                pygame.draw.rect(surf, hp_color, (bx, hud_y, block_w, block_h), border_radius=3)

                # [LỰA CHỌN 2]: Nếu bạn muốn đổi sang hình THOI (Trái tim công nghệ),
                # hãy xóa ký tự # ở 3 dòng dưới này đi và thêm dấu # vào dòng pygame.draw.rect ở trên:
                # points = [(bx + block_w//2, hud_y), (bx + block_w, hud_y + block_h//2),
                #           (bx + block_w//2, hud_y + block_h), (bx, hud_y + block_h//2)]
                # pygame.draw.polygon(surf, hp_color, points)
            else:
                # Nếu i lớn hơn hoặc bằng HP hiện tại -> Ô máu đã bị mất do dính đạn
                # Vẽ một khung viền rỗng màu xám mờ để báo hiệu mất mạng
                pygame.draw.rect(surf, (60, 60, 70), (bx, hud_y, block_w, block_h), 1, border_radius=3)

        # Hiển thị Điểm số & Kỷ lục dạng Digital sắc nét chính giữa HUD
        sc = self.font_med.render(f"{self.player.score:06d}", True, CYAN)
        surf.blit(sc, (W // 2 - sc.get_width() // 2, 8))

        hi = self.font_xs.render(f"HI-SCORE: {self.hi_score:06d}", True, GRAY)
        surf.blit(hi, (W // 2 - hi.get_width() // 2, 38))

        # Cấp độ màn chơi
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
        # =====================================================================

        # Dòng chữ thông báo Sự kiện lớn (Wave mới, Level up) dạng phóng to thu nhỏ
        if self.flash_t > 0:
            txt = self.font_big.render(self.flash_msg, True, YELLOW)
            shadow = self.font_big.render(self.flash_msg, True, (40, 30, 0))
            surf.blit(shadow, (W // 2 - txt.get_width() // 2 + 3, H // 2 - 60 + 3))
            surf.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 60))
            self.flash_t -= 1

    def draw_gameover_on(self, surf):
        # Hiệu ứng là mờ phủ kính mờ sẫm màu
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((5, 5, 15, 200))
        surf.blit(overlay, (0, 0))

        # Panel Gameover lồng viền tinh tế
        pygame.draw.rect(surf, RED, (W // 2 - 220, H // 2 - 160, 440, 290), 1, border_radius=12)

        ov = self.font_big.render("MISSION FAILED", True, RED)
        surf.blit(ov, (W // 2 - ov.get_width() // 2, H // 2 - 130))

        sc = self.font_med.render(f"FINAL SCORE: {self.player.score:06d}", True, WHITE)
        surf.blit(sc, (W // 2 - sc.get_width() // 2, H // 2 - 40))

        hi = self.font_sm.render(f"RECORD TO BEAT: {self.hi_score:06d}", True, YELLOW)
        surf.blit(hi, (W // 2 - hi.get_width() // 2, H // 2 + 5))

        t = pygame.time.get_ticks() / 1000
        if int(t * 1.5) % 2 == 0:
            rs = self.font_med.render("[ PRESS ENTER TO RESTART ]", True, GREEN)
            surf.blit(rs, (W // 2 - rs.get_width() // 2, H // 2 + 70))
