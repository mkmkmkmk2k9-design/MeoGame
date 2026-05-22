# main.py
import sys
import os
import pygame

# Đoạn mã bọc lót chống lỗi "ModuleNotFoundError: No module named 'config'" triệt để trên mọi IDE
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game

if __name__ == "__main__":
    # Khởi tạo lõi đồ họa phần cứng Pygame
    pygame.init()

    print("🚀 Đang khởi động Alien Invasion...")
    game = Game()
    game.run()