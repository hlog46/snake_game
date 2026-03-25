"""连击特效：Combo 文字 + 屏幕震动"""
import pygame
import random
from config.settings import COMBO_WINDOW, COMBO_MIN_COUNT, SCREEN_W, SCREEN_H
from config.fonts import get_font


class ComboEffect:
    def __init__(self):
        self.combo_count = 0
        self.last_eat_time = -999.0
        self.display_text = ""
        self.display_timer = 0.0
        self.shake_timer = 0.0
        self.shake_offset = (0, 0)
        self._font = None

    def _get_font(self):
        if self._font is None:
            self._font = get_font(48)
        return self._font

    def on_eat(self, current_time: float) -> int:
        """调用于每次吃到食物时。返回额外连击加分。"""
        if current_time - self.last_eat_time <= COMBO_WINDOW:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.last_eat_time = current_time

        if self.combo_count >= COMBO_MIN_COUNT:
            self._trigger_combo()
            return 5 * (self.combo_count - COMBO_MIN_COUNT + 1)
        return 0

    def _trigger_combo(self):
        self.display_text = f"COMBO x{self.combo_count}!"
        self.display_timer = 0.8
        self.shake_timer = 0.2

    def update(self, dt: float):
        if self.display_timer > 0:
            self.display_timer = max(0.0, self.display_timer - dt)
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)
            self.shake_offset = (random.randint(-3, 3), random.randint(-3, 3))
        else:
            self.shake_offset = (0, 0)

    def draw(self, surface):
        if self.display_timer <= 0 or not self.display_text:
            return

        font = self._get_font()
        # 颜色随连击数变化：3→黄，5→橙，8→红
        t = min(1.0, (self.combo_count - COMBO_MIN_COUNT) / 6.0)
        r = int(255)
        g = int(200 * (1 - t))
        b = 0
        color = (r, g, b)

        # 淡出效果
        alpha = int(255 * min(1.0, self.display_timer / 0.4))
        text_surf = font.render(self.display_text, True, color)
        text_surf.set_alpha(alpha)

        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        rect = text_surf.get_rect(center=(cx, cy))
        surface.blit(text_surf, rect)
