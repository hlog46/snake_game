"""粒子系统：Particle + ParticleEmitter"""
import random
import math
import pygame
from config.settings import MAX_PARTICLES


class Particle:
    def __init__(self, pos: tuple, velocity: tuple, color: tuple,
                 lifetime: float, size: int = 4, shape: str = "circle"):
        self.pos = list(pos)           # [x, y] 浮点像素坐标
        self.vel = list(velocity)      # [vx, vy] 像素/秒
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.size = size
        self.shape = shape             # "circle" | "rect" | "diamond"
        self.gravity = 150.0           # 像素/秒²

    def update(self, dt: float) -> bool:
        self.age += dt
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        self.vel[1] += self.gravity * dt  # 重力
        return self.age < self.lifetime

    @property
    def alpha(self) -> int:
        if self.lifetime <= 0:
            return 0
        return int(255 * max(0.0, 1.0 - self.age / self.lifetime))

    def draw(self, surface):
        alpha = self.alpha
        if alpha <= 0:
            return
        r = max(1, int(self.size * (1 - self.age / self.lifetime * 0.5)))
        x, y = int(self.pos[0]), int(self.pos[1])
        color = (*self.color[:3], alpha)

        if self.shape == "circle":
            gsurf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, color, (r + 1, r + 1), r)
            surface.blit(gsurf, (x - r - 1, y - r - 1))
        elif self.shape == "rect":
            gsurf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            gsurf.fill(color)
            surface.blit(gsurf, (x - r, y - r))
        elif self.shape == "diamond":
            gsurf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pts = [(r + 1, 1), (r * 2 + 1, r + 1), (r + 1, r * 2 + 1), (1, r + 1)]
            pygame.draw.polygon(gsurf, color, pts)
            surface.blit(gsurf, (x - r - 1, y - r - 1))


class ParticleEmitter:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, pos: tuple, count: int,
             speed_range: tuple = (60, 150),
             color: tuple = (255, 255, 0),
             lifetime_range: tuple = (0.3, 0.6),
             size: int = 4,
             shape: str = "circle",
             spread: float = 360):
        """在 pos 处生成 count 个粒子，spread 为角度范围（度）。"""
        slots = MAX_PARTICLES - len(self.particles)
        if slots <= 0:
            return
        count = min(count, slots)

        start_angle = random.uniform(0, 360)
        for _ in range(count):
            angle = math.radians(start_angle + random.uniform(0, spread))
            speed = random.uniform(*speed_range)
            vel = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(*lifetime_range)
            self.particles.append(
                Particle(pos, vel, color, lifetime, size=size, shape=shape)
            )

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
