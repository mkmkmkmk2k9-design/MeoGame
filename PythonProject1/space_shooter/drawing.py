# drawing.py
import pygame
import math
from config import WHITE, RED, YELLOW, BLACK, GREEN, PURPLE, GRAY, ORANGE, CYAN


def draw_ship(surf, x, y, size=1.0, color=CYAN, damaged=False):
    """Vẽ tàu vũ trụ của người chơi."""
    s = size
    pts = [
        (x, y - 28 * s),
        (x - 18 * s, y + 20 * s),
        (x - 8 * s, y + 10 * s),
        (x + 8 * s, y + 10 * s),
        (x + 18 * s, y + 20 * s),
    ]
    col = RED if damaged else color
    pygame.draw.polygon(surf, col, pts)

    # cockpit
    pygame.draw.ellipse(surf, WHITE if not damaged else ORANGE,
                        (x - 6 * s, y - 14 * s, 12 * s, 16 * s))
    # engine glow
    t = pygame.time.get_ticks()
    glow = abs(math.sin(t * 0.008)) * 6 + 4
    pygame.draw.ellipse(surf, ORANGE,
                        (x - 5 * s, y + 12 * s, 10 * s, glow * s))


def draw_alien(surf, x, y, atype=0, frame=0, hp_ratio=1.0):
    """Vẽ kẻ thù với 3 kiểu dáng khác nhau."""
    bob = math.sin(frame * 0.08) * 3  # lắc lư
    y = y + bob
    c = [GREEN, RED, PURPLE][atype % 3]
    if hp_ratio < 0.4: c = ORANGE  # sắp chết → đỏ cam

    if atype == 0:  # UFO tròn
        pygame.draw.ellipse(surf, c, (x - 22, y - 10, 44, 20))
        pygame.draw.ellipse(surf, WHITE, (x - 10, y - 18, 20, 16))
        for dx in [-12, -6, 0, 6, 12]:
            pygame.draw.circle(surf, YELLOW, (int(x + dx), int(y + 10)), 3)

    elif atype == 1:  # Bug mắt to
        pygame.draw.ellipse(surf, c, (x - 18, y - 14, 36, 28))
        pygame.draw.circle(surf, WHITE, (int(x - 8), int(y - 2)), 7)
        pygame.draw.circle(surf, WHITE, (int(x + 8), int(y - 2)), 7)
        pygame.draw.circle(surf, BLACK, (int(x - 8), int(y - 2)), 4)
        pygame.draw.circle(surf, BLACK, (int(x + 8), int(y - 2)), 4)
        # antenna
        pygame.draw.line(surf, c, (int(x - 10), int(y - 14)), (int(x - 14), int(y - 24)), 2)
        pygame.draw.line(surf, c, (int(x + 10), int(y - 14)), (int(x + 14), int(y - 24)), 2)

    else:  # Robot vuông
        pygame.draw.rect(surf, c, (x - 16, y - 16, 32, 32))
        pygame.draw.rect(surf, BLACK, (x - 10, y - 10, 8, 8))
        pygame.draw.rect(surf, BLACK, (x + 2, y - 10, 8, 8))
        # blink
        if (frame // 20) % 2 == 0:
            pygame.draw.rect(surf, YELLOW, (x - 10, y - 10, 8, 8))
            pygame.draw.rect(surf, YELLOW, (x + 2, y - 10, 8, 8))
        pygame.draw.rect(surf, GRAY, (x - 12, y + 8, 24, 6))