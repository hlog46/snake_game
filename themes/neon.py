"""霓虹赛博风主题"""
import pygame
import math
from themes.base_theme import BaseTheme
from config.settings import SCREEN_W, SCREEN_H, GAME_AREA_TOP, GAME_AREA_H, CELL_SIZE


def _draw_glow_circle(surface, color, center, radius, max_alpha=80):
    """多层半透明圆形叠加模拟发光效果"""
    glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    layers = 6
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        alpha = int(max_alpha * (1 - i / layers) * 0.8 + max_alpha * 0.2)
        pygame.draw.circle(glow_surf, (*color, alpha),
                           (radius * 2, radius * 2), r)
    # 实心核心
    pygame.draw.circle(glow_surf, (*color, 200),
                       (radius * 2, radius * 2), max(2, radius // 3))
    surface.blit(glow_surf, (center[0] - radius * 2, center[1] - radius * 2),
                 special_flags=pygame.BLEND_ADD)


class NeonTheme(BaseTheme):
    name = "霓虹赛博风"
    bg_color = (13, 13, 26)
    grid_color = None
    snake_head_color = (0, 255, 220)       # 青色
    snake_body_color = (120, 0, 200)       # 紫色
    snake_power_color = (255, 200, 0)
    food_color = (255, 50, 180)            # 品红
    special_speed_color = (255, 80, 50)
    special_slow_color = (50, 150, 255)
    obstacle_color = (60, 0, 100)
    particle_color = (0, 255, 255)
    text_color = (180, 240, 255)
    highlight_color = (255, 255, 80)
    hud_bg_color = (8, 8, 20)

    def draw_background(self, surface):
        pygame.draw.rect(surface, self.bg_color,
                         (0, GAME_AREA_TOP, SCREEN_W, GAME_AREA_H))
        # 微弱网格
        grid_c = (20, 20, 40)
        for col in range(0, SCREEN_W, CELL_SIZE):
            pygame.draw.line(surface, grid_c,
                             (col, GAME_AREA_TOP), (col, GAME_AREA_TOP + GAME_AREA_H))
        for row in range(GAME_AREA_TOP, GAME_AREA_TOP + GAME_AREA_H, CELL_SIZE):
            pygame.draw.line(surface, grid_c,
                             (0, row), (SCREEN_W, row))

    def draw_snake(self, surface, snake, board, power_up: str = None):
        cs = board.CELL_SIZE
        length = len(snake.body)

        for i, pos in enumerate(snake.body):
            x, y = board.cell_to_pixel(*pos)
            cx, cy = x + cs // 2, y + cs // 2
            t = i / max(length - 1, 1)

            if i == 0:
                # 蛇头：青色，带发光
                color = self.snake_power_color if power_up else self.snake_head_color
                if snake.is_head_flashing:
                    r = int(cs * 0.6)
                else:
                    r = cs // 2 - 1
                _draw_glow_circle(surface, color, (cx, cy), r, 100)
                pygame.draw.circle(surface, color, (cx, cy), max(3, cs // 2 - 3))
            else:
                # 蛇身：从青色渐变到紫色
                if power_up:
                    r_val = self.snake_power_color[0]
                    g_val = self.snake_power_color[1]
                    b_val = self.snake_power_color[2]
                else:
                    r_val = int(self.snake_head_color[0] * (1 - t) + self.snake_body_color[0] * t)
                    g_val = int(self.snake_head_color[1] * (1 - t) + self.snake_body_color[1] * t)
                    b_val = int(self.snake_head_color[2] * (1 - t) + self.snake_body_color[2] * t)
                color = (r_val, g_val, b_val)
                radius = max(3, cs // 2 - 2 - i // 10)
                pygame.draw.circle(surface, color, (cx, cy), radius)
                # 轮廓发光
                if i < 5:
                    pygame.draw.circle(surface, color, (cx, cy), radius + 1, 1)

    def draw_food(self, surface, food, board):
        x, y = board.cell_to_pixel(*food.pos)
        cs = board.CELL_SIZE
        cx, cy = x + cs // 2, y + cs // 2

        if food.food_type == "normal":
            pulse = 0.5 + 0.5 * math.sin(food.blink_timer * 4)
            r = int(cs // 2 - 2 + pulse * 2)
            _draw_glow_circle(surface, self.food_color, (cx, cy), r, 120)
            pygame.draw.circle(surface, self.food_color, (cx, cy), max(3, r - 2))
        elif food.food_type == "speed_up":
            pulse = 0.5 + 0.5 * math.sin(food.blink_timer * 8)
            r = int(cs // 2 - 1 + pulse * 3)
            _draw_glow_circle(surface, self.special_speed_color, (cx, cy), r, 150)
            pygame.draw.circle(surface, self.special_speed_color, (cx, cy), max(3, r - 2))
        elif food.food_type == "slow_down":
            pulse = 0.5 + 0.5 * math.sin(food.blink_timer * 4)
            r = int(cs // 2 - 1 + pulse * 2)
            _draw_glow_circle(surface, self.special_slow_color, (cx, cy), r, 150)
            pygame.draw.circle(surface, self.special_slow_color, (cx, cy), max(3, r - 2))

    def draw_obstacle(self, surface, pos, board):
        x, y = board.cell_to_pixel(*pos)
        cs = board.CELL_SIZE
        pygame.draw.rect(surface, self.obstacle_color,
                         (x + 1, y + 1, cs - 2, cs - 2))
        # 霓虹边框
        neon_color = (140, 0, 220)
        pygame.draw.rect(surface, neon_color,
                         (x + 1, y + 1, cs - 2, cs - 2), 1)
