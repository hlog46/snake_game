"""分数浮动文字动画"""
import pygame
from config.fonts import get_font


class ScorePopup:
    def __init__(self, text: str, pos: tuple, color: tuple,
                 lifetime: float = 1.0, rise_speed: float = 40):
        self.text = text
        self.pos = list(pos)           # [x, y] 浮点像素坐标
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.rise_speed = rise_speed   # 每秒上升像素数

    def update(self, dt: float) -> bool:
        self.age += dt
        self.pos[1] -= self.rise_speed * dt
        return self.age < self.lifetime

    @property
    def alpha(self) -> int:
        # 先停留，后渐出
        fade_start = self.lifetime * 0.5
        if self.age < fade_start:
            return 255
        t = (self.age - fade_start) / (self.lifetime - fade_start)
        return int(255 * max(0.0, 1.0 - t))

    def draw(self, surface, font):
        alpha = self.alpha
        if alpha <= 0:
            return
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        surface.blit(text_surf, rect)


class ScorePopupManager:
    def __init__(self):
        self.popups: list[ScorePopup] = []
        self._font = None

    def _get_font(self):
        if self._font is None:
            self._font = get_font(20)
        return self._font

    def add(self, text: str, pos: tuple, color: tuple):
        self.popups.append(ScorePopup(text, pos, color))

    def update(self, dt: float):
        self.popups = [p for p in self.popups if p.update(dt)]

    def draw(self, surface):
        font = self._get_font()
        for p in self.popups:
            p.draw(surface, font)
