"""游戏内 HUD（分数、难度、主题、倒计时、道具状态）"""
import pygame
from config.settings import (
    SCREEN_W, SCREEN_H, HUD_TOP_H, HUD_BOTTOM_H,
    DIFFICULTY_NAMES, THEME_NAMES, GAME_AREA_TOP, GAME_AREA_H
)
from config.fonts import get_font


def _get_fonts():
    """返回 (大字体, 小字体)"""
    big = get_font(24)
    small = get_font(18)
    return big, small


def draw_hud(surface, ctrl):
    """绘制顶部 HUD 和底部状态栏。ctrl 为 GameController 实例。"""
    theme = ctrl.theme_manager.theme
    big_font, small_font = _get_fonts()

    # ---- 顶部 HUD 背景 ----
    pygame.draw.rect(surface, theme.hud_bg_color, (0, 0, SCREEN_W, HUD_TOP_H))
    pygame.draw.line(surface, theme.snake_body_color,
                     (0, HUD_TOP_H - 1), (SCREEN_W, HUD_TOP_H - 1), 1)

    # 当前分数
    score_text = big_font.render(f"SCORE  {ctrl.score}", True, theme.text_color)
    surface.blit(score_text, (10, 8))

    # 最高分
    best = ctrl.highscores.get(ctrl.difficulty, {}).get("score", 0)
    best_text = small_font.render(f"BEST  {best}", True, (150, 150, 150))
    surface.blit(best_text, (10, 32))

    # 难度标签
    diff_label = DIFFICULTY_NAMES.get(ctrl.difficulty, ctrl.difficulty)
    diff_surf = small_font.render(f"[{diff_label}]", True, theme.highlight_color)
    surface.blit(diff_surf, (SCREEN_W - diff_surf.get_width() - 10, 8))

    # 主题名
    theme_label = THEME_NAMES.get(ctrl.theme_manager.name, "")
    theme_surf = small_font.render(theme_label, True, (140, 140, 160))
    surface.blit(theme_surf, (SCREEN_W - theme_surf.get_width() - 10, 28))

    # ---- 底部状态栏 背景 ----
    bottom_y = GAME_AREA_TOP + GAME_AREA_H
    pygame.draw.rect(surface, theme.hud_bg_color,
                     (0, bottom_y, SCREEN_W, HUD_BOTTOM_H))
    pygame.draw.line(surface, theme.snake_body_color,
                     (0, bottom_y), (SCREEN_W, bottom_y), 1)

    bar_y = bottom_y + 10
    bar_h = 12

    # 困难模式：普通食物倒计时进度条
    if ctrl.difficulty == "hard" and ctrl.food_manager and ctrl.food_manager.normal_food:
        food = ctrl.food_manager.normal_food
        if food.timeout is not None:
            ratio = max(0.0, food.time_left / food.timeout)
            bar_w = 200
            pygame.draw.rect(surface, (60, 60, 60),
                             (10, bar_y, bar_w, bar_h), border_radius=4)
            fill_color = (
                int(220 * (1 - ratio) + 50 * ratio),
                int(50 * (1 - ratio) + 200 * ratio),
                50
            )
            pygame.draw.rect(surface, fill_color,
                             (10, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
            label = small_font.render("食物倒计时", True, (160, 160, 160))
            surface.blit(label, (218, bar_y))

    # 道具状态条
    if ctrl.power_up_type:
        max_dur = 5.0
        ratio = max(0.0, ctrl.power_up_timer / max_dur)
        bar_x = SCREEN_W // 2 - 80
        bar_w = 160

        if ctrl.power_up_type == "speed_up":
            icon_text = "⚡ 加速"
            bar_color = (255, 120, 50)
        else:
            icon_text = "❄ 减速"
            bar_color = (80, 150, 255)

        pygame.draw.rect(surface, (60, 60, 60),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(surface, bar_color,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        icon_surf = small_font.render(icon_text, True, bar_color)
        surface.blit(icon_surf, (bar_x + bar_w + 8, bar_y))
