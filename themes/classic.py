"""经典像素风主题"""
import pygame
from themes.base_theme import BaseTheme
from config.settings import SCREEN_W, SCREEN_H, GAME_AREA_TOP, GAME_AREA_H, CELL_SIZE


class ClassicTheme(BaseTheme):
    name = "经典像素风"
    bg_color = (26, 46, 26)
    grid_color = (32, 56, 32)
    snake_head_color = (80, 220, 80)
    snake_body_color = (50, 180, 50)
    snake_power_color = (255, 220, 50)
    food_color = (220, 50, 50)
    special_speed_color = (255, 100, 50)
    special_slow_color = (80, 150, 255)
    obstacle_color = (140, 140, 140)
    particle_color = (200, 240, 60)
    text_color = (180, 230, 180)
    highlight_color = (255, 255, 100)
    hud_bg_color = (15, 30, 15)

    def draw_background(self, surface):
        # 游戏区域纯色背景
        pygame.draw.rect(surface, self.bg_color,
                         (0, GAME_AREA_TOP, SCREEN_W, GAME_AREA_H))
        # 网格线
        if self.grid_color:
            for col in range(0, SCREEN_W, CELL_SIZE):
                pygame.draw.line(surface, self.grid_color,
                                 (col, GAME_AREA_TOP), (col, GAME_AREA_TOP + GAME_AREA_H))
            for row in range(GAME_AREA_TOP, GAME_AREA_TOP + GAME_AREA_H, CELL_SIZE):
                pygame.draw.line(surface, self.grid_color,
                                 (0, row), (SCREEN_W, row))

    def draw_snake(self, surface, snake, board, power_up: str = None):
        cs = board.CELL_SIZE
        for i, pos in enumerate(snake.body):
            x, y = board.cell_to_pixel(*pos)
            if i == 0:
                # 蛇头
                if snake.is_head_flashing:
                    color = (200, 255, 200)
                    size = int(cs * 1.2)
                    offset = (cs - size) // 2
                    pygame.draw.rect(surface, color,
                                     (x + offset, y + offset, size, size))
                else:
                    color = self.snake_power_color if power_up else self.snake_head_color
                    pygame.draw.rect(surface, color,
                                     (x + 1, y + 1, cs - 2, cs - 2))
                # 眼睛
                self._draw_eyes(surface, x, y, cs, snake.direction)
            else:
                color = self.snake_power_color if power_up else self.snake_body_color
                pygame.draw.rect(surface, color,
                                 (x + 2, y + 2, cs - 4, cs - 4))

    def _draw_eyes(self, surface, x, y, cs, direction):
        dc, dr = direction
        # 根据方向计算眼睛位置
        if dc == 1:   eye_positions = [(x + cs - 5, y + 4), (x + cs - 5, y + cs - 7)]
        elif dc == -1: eye_positions = [(x + 3, y + 4), (x + 3, y + cs - 7)]
        elif dr == -1: eye_positions = [(x + 4, y + 3), (x + cs - 7, y + 3)]
        else:          eye_positions = [(x + 4, y + cs - 5), (x + cs - 7, y + cs - 5)]
        for ep in eye_positions:
            pygame.draw.circle(surface, (0, 0, 0), ep, 2)

    def draw_food(self, surface, food, board):
        x, y = board.cell_to_pixel(*food.pos)
        cs = board.CELL_SIZE

        if food.food_type == "normal":
            pygame.draw.rect(surface, self.food_color,
                             (x + 3, y + 3, cs - 6, cs - 6))
        elif food.food_type == "speed_up":
            # 红色闪光：交替明暗
            blink = int(food.blink_timer * 6) % 2 == 0
            color = self.special_speed_color if blink else (200, 60, 30)
            pygame.draw.rect(surface, color, (x + 2, y + 2, cs - 4, cs - 4))
            pygame.draw.rect(surface, (255, 180, 100), (x + 2, y + 2, cs - 4, cs - 4), 2)
        elif food.food_type == "slow_down":
            blink = int(food.blink_timer * 6) % 2 == 0
            color = self.special_slow_color if blink else (50, 100, 200)
            pygame.draw.rect(surface, color, (x + 2, y + 2, cs - 4, cs - 4))
            pygame.draw.rect(surface, (150, 200, 255), (x + 2, y + 2, cs - 4, cs - 4), 2)

    def draw_obstacle(self, surface, pos, board):
        x, y = board.cell_to_pixel(*pos)
        cs = board.CELL_SIZE
        pygame.draw.rect(surface, self.obstacle_color, (x + 1, y + 1, cs - 2, cs - 2))
        pygame.draw.rect(surface, (80, 80, 80), (x + 1, y + 1, cs - 2, cs - 2), 1)
