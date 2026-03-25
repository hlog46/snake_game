"""主题抽象基类"""
from abc import ABC, abstractmethod


class BaseTheme(ABC):
    # 颜色属性（子类必须设置）
    bg_color: tuple = (0, 0, 0)
    grid_color: tuple = None           # None 表示不绘制网格线
    snake_head_color: tuple = (0, 200, 0)
    snake_body_color: tuple = (0, 160, 0)
    snake_power_color: tuple = (255, 200, 0)   # 道具激活时蛇身颜色
    food_color: tuple = (220, 50, 50)
    special_speed_color: tuple = (255, 80, 80)
    special_slow_color: tuple = (80, 130, 255)
    obstacle_color: tuple = (120, 120, 120)
    particle_color: tuple = (200, 230, 50)
    text_color: tuple = (220, 220, 220)
    highlight_color: tuple = (255, 255, 100)
    hud_bg_color: tuple = (20, 20, 20)

    name: str = "Base"

    @abstractmethod
    def draw_background(self, surface):
        """绘制游戏区域背景"""

    @abstractmethod
    def draw_snake(self, surface, snake, board, power_up: str = None):
        """绘制蛇"""

    @abstractmethod
    def draw_food(self, surface, food, board):
        """绘制食物"""

    def draw_obstacle(self, surface, pos: tuple, board):
        """绘制障碍物（子类可覆盖）"""
        import pygame
        x, y = board.cell_to_pixel(*pos)
        cs = board.CELL_SIZE
        pygame.draw.rect(surface, self.obstacle_color,
                         (x + 1, y + 1, cs - 2, cs - 2))
