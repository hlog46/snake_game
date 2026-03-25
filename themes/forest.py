"""自然森林风主题"""
import pygame
import math
from themes.base_theme import BaseTheme
from config.settings import SCREEN_W, SCREEN_H, GAME_AREA_TOP, GAME_AREA_H, CELL_SIZE


class ForestTheme(BaseTheme):
    name = "自然森林风"
    bg_color = (45, 31, 14)
    grid_color = (55, 39, 18)
    snake_head_color = (80, 160, 50)
    snake_body_color = (55, 120, 35)
    snake_power_color = (200, 180, 50)
    food_color = (210, 70, 40)
    special_speed_color = (230, 90, 30)
    special_slow_color = (70, 130, 200)
    obstacle_color = (100, 65, 30)
    particle_color = (240, 180, 40)
    text_color = (220, 200, 150)
    highlight_color = (255, 220, 80)
    hud_bg_color = (30, 18, 8)

    def draw_background(self, surface):
        pygame.draw.rect(surface, self.bg_color,
                         (0, GAME_AREA_TOP, SCREEN_W, GAME_AREA_H))
        # 轻微网格纹理
        if self.grid_color:
            for col in range(0, SCREEN_W, CELL_SIZE):
                pygame.draw.line(surface, self.grid_color,
                                 (col, GAME_AREA_TOP), (col, GAME_AREA_TOP + GAME_AREA_H))
            for row in range(GAME_AREA_TOP, GAME_AREA_TOP + GAME_AREA_H, CELL_SIZE):
                pygame.draw.line(surface, self.grid_color,
                                 (0, row), (SCREEN_W, row))

    def draw_snake(self, surface, snake, board, power_up: str = None):
        cs = board.CELL_SIZE
        length = len(snake.body)

        for i, pos in enumerate(snake.body):
            x, y = board.cell_to_pixel(*pos)
            t = i / max(length - 1, 1)

            if i == 0:
                # 蛇头：较亮的绿色圆角矩形
                if snake.is_head_flashing:
                    color = (160, 255, 100)
                    size = int(cs * 1.1)
                    off = (cs - size) // 2
                    pygame.draw.rect(surface, color,
                                     (x + off, y + off, size, size),
                                     border_radius=5)
                else:
                    color = self.snake_power_color if power_up else self.snake_head_color
                    pygame.draw.rect(surface, color,
                                     (x + 1, y + 1, cs - 2, cs - 2),
                                     border_radius=6)
                # 眼睛
                self._draw_eyes(surface, x, y, cs, snake.direction)
            else:
                # 蛇身：从头到尾颜色渐变（亮→暗）
                if power_up:
                    color = self.snake_power_color
                else:
                    r = int(self.snake_head_color[0] * (1 - t) + self.snake_body_color[0] * t)
                    g = int(self.snake_head_color[1] * (1 - t) + self.snake_body_color[1] * t)
                    b = int(self.snake_head_color[2] * (1 - t) + self.snake_body_color[2] * t)
                    color = (r, g, b)
                pygame.draw.rect(surface, color,
                                 (x + 2, y + 2, cs - 4, cs - 4),
                                 border_radius=5)
                # 鳞片高光
                if i % 2 == 0:
                    hl = (min(color[0] + 40, 255),
                          min(color[1] + 40, 255),
                          min(color[2] + 20, 255))
                    pygame.draw.rect(surface, hl,
                                     (x + 3, y + 3, cs // 2 - 2, cs // 2 - 2),
                                     border_radius=3)

    def _draw_eyes(self, surface, x, y, cs, direction):
        dc, dr = direction
        eo = max(2, cs // 5)   # 眼睛距格子边缘的偏移
        eg = max(2, cs // 4)   # 两眼的横/纵间距
        er = max(1, cs // 10)  # 眼睛半径
        if dc == 1:    eye_positions = [(x + cs - eo, y + eg), (x + cs - eo, y + cs - eg - 1)]
        elif dc == -1: eye_positions = [(x + eo, y + eg), (x + eo, y + cs - eg - 1)]
        elif dr == -1: eye_positions = [(x + eg, y + eo), (x + cs - eg - 1, y + eo)]
        else:          eye_positions = [(x + eg, y + cs - eo), (x + cs - eg - 1, y + cs - eo)]
        for ep in eye_positions:
            pygame.draw.circle(surface, (0, 0, 0), ep, er)
            pygame.draw.circle(surface, (255, 255, 150), ep, max(1, er - 1))

    def draw_food(self, surface, food, board):
        x, y = board.cell_to_pixel(*food.pos)
        cs = board.CELL_SIZE
        cx, cy = x + cs // 2, y + cs // 2

        if food.food_type == "normal":
            # 橙红圆形带高光（苹果）
            r = cs // 2 - 3
            pygame.draw.circle(surface, self.food_color, (cx, cy), r)
            # 高光
            hl_pos = (cx - r // 3, cy - r // 3)
            pygame.draw.circle(surface, (255, 180, 150), hl_pos, max(2, r // 3))
            # 叶子（一个小绿色矩形）
            pygame.draw.rect(surface, (60, 140, 40),
                             (cx - 1, y + 2, 3, 4), border_radius=2)
        elif food.food_type == "speed_up":
            pulse = 0.5 + 0.5 * math.sin(food.blink_timer * 8)
            r = int(cs // 2 - 2 + pulse * 2)
            pygame.draw.circle(surface, self.special_speed_color, (cx, cy), r)
            pygame.draw.circle(surface, (255, 200, 100), (cx, cy), r, 2)
        elif food.food_type == "slow_down":
            pulse = 0.5 + 0.5 * math.sin(food.blink_timer * 4)
            r = int(cs // 2 - 2 + pulse * 2)
            pygame.draw.circle(surface, self.special_slow_color, (cx, cy), r)
            pygame.draw.circle(surface, (180, 220, 255), (cx, cy), r, 2)

    def draw_obstacle(self, surface, pos, board):
        """树桩样式障碍物"""
        x, y = board.cell_to_pixel(*pos)
        cs = board.CELL_SIZE
        # 树桩主体
        pygame.draw.rect(surface, self.obstacle_color,
                         (x + 2, y + 2, cs - 4, cs - 4), border_radius=4)
        # 年轮（同心圆）
        cx, cy = x + cs // 2, y + cs // 2
        pygame.draw.circle(surface, (80, 50, 20), (cx, cy), cs // 2 - 4, 1)
        pygame.draw.circle(surface, (80, 50, 20), (cx, cy), cs // 4, 1)
