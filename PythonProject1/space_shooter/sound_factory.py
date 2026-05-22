# sound_factory.py
import pygame
import math
import random

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

def make_sound(freq=440, duration=0.1, vol=0.3, wave='sine', decay=True):
    """Tạo âm thanh procedural – không cần file ngoài."""
    sample_rate = 44100
    n = int(sample_rate * duration)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sample_rate
        if wave == 'sine':
            v = math.sin(2 * math.pi * freq * t)
        elif wave == 'square':
            v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif wave == 'noise':
            v = random.uniform(-1, 1)
        else:
            v = math.sin(2 * math.pi * freq * t)
        if decay:
            v *= max(0.0, 1 - (i / n))
        amp = int(v * vol * 32767)
        amp = max(-32768, min(32767, amp))
        buf[i*2]   = amp & 0xFF
        buf[i*2+1] = (amp >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

# Khởi tạo từ điển SFX âm thanh gốc của bạn
SFX = {
    'shoot'    : make_sound(600,  0.10, 0.25, 'square'),
    'explode'  : make_sound(80,   0.35, 0.40, 'noise'),
    'powerup'  : make_sound(880,  0.25, 0.30, 'sine',  decay=False),
    'hit'      : make_sound(200,  0.15, 0.30, 'noise'),
    'gameover' : make_sound(120,  0.60, 0.40, 'square'),
    'levelup'  : make_sound(1200, 0.30, 0.30, 'sine'),
    'bomb'     : make_sound(60,   0.50, 0.45, 'noise'),
    'triple'   : make_sound(750,  0.08, 0.20, 'square'),
}

def play(name):
    """Bắn âm thanh nếu tên âm thanh hợp lệ trong từ điển SFX."""
    if name in SFX:
        SFX[name].play()