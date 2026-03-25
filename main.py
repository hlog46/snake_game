"""贪吃蛇游戏 —— 程序入口

运行方式：
    cd snake_game
    python main.py

依赖：
    pip install pygame
"""
import sys
import os

# 确保项目根目录在 Python 路径中（支持从任意位置运行）
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
from config.settings import SCREEN_W, SCREEN_H, FPS
from game.game_state import GameController


def main():
    pygame.init()
    pygame.display.set_caption("贪吃蛇 Snake Deluxe")

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    ctrl = GameController()

    while True:
        dt = clock.tick(FPS) / 1000.0
        # 防止 dt 过大（如窗口拖动等卡顿导致逻辑跳帧）
        dt = min(dt, 0.05)

        events = pygame.event.get()
        ctrl.handle_events(events)
        ctrl.update(dt)
        ctrl.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
