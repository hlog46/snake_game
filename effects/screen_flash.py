"""屏幕闪光与红闪效果"""
import pygame


class ScreenFlash:
    def __init__(self):
        self.active = False
        self.color = (255, 0, 0)
        self.alpha = 0.0
        self.decay_rate = 0.0

    def trigger(self, color: tuple, initial_alpha: float, duration: float):
        """触发屏幕闪光。color=RGB, initial_alpha=0~255, duration=秒。"""
        if duration <= 0:
            return
        self.active = True
        self.color = color
        self.alpha = float(initial_alpha)
        self.decay_rate = initial_alpha / duration

    def update(self, dt: float):
        if self.active:
            self.alpha -= self.decay_rate * dt
            if self.alpha <= 0:
                self.alpha = 0.0
                self.active = False

    def draw(self, surface):
        if not self.active or self.alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color[:3], int(self.alpha)))
        surface.blit(overlay, (0, 0))
