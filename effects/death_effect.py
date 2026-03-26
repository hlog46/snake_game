"""死亡碎裂特效：蛇身每节变成飞散碎片"""
import pygame
import random
import math


class Fragment:
    def __init__(self, pos: tuple, color: tuple, size: int):
        self.pos = list(pos)           # 像素坐标
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 250)
        self.vel = [math.cos(angle) * speed, math.sin(angle) * speed]
        self.color = color
        self.size = size
        self.lifetime = random.uniform(0.5, 0.9)
        self.age = 0.0
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-300, 300)
        self.gravity = 200.0

    def update(self, dt: float) -> bool:
        self.age += dt
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        self.vel[1] += self.gravity * dt
        self.rotation += self.rot_speed * dt
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
        s = max(2, int(self.size * (1 - self.age / self.lifetime * 0.5)))
        fsurf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        fsurf.fill((*self.color[:3], alpha))
        # 旋转
        rotated = pygame.transform.rotate(fsurf, self.rotation)
        rect = rotated.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        surface.blit(rotated, rect)


class DeathEffect:
    def __init__(self):
        self.fragments: list[Fragment] = []
        self.active = False

    def trigger(self, snake_body, board, theme):
        """根据蛇身格子列表生成碎片。"""
        self.fragments.clear()
        self.active = True
        cs = board.CELL_SIZE

        for i, pos in enumerate(snake_body):
            cx, cy = board.cell_to_pixel_center(*pos)
            # 每节 2~4 个碎片
            count = random.randint(2, 4)
            # 颜色：头部亮色，身体渐变
            if i == 0:
                color = theme.snake_head_color
            else:
                t = min(1.0, i / max(len(snake_body) - 1, 1))
                r = int(theme.snake_head_color[0] * (1 - t) + theme.snake_body_color[0] * t)
                g = int(theme.snake_head_color[1] * (1 - t) + theme.snake_body_color[1] * t)
                b = int(theme.snake_head_color[2] * (1 - t) + theme.snake_body_color[2] * t)
                color = (r, g, b)

            for _ in range(count):
                jitter_x = cx + random.randint(-cs // 4, cs // 4)
                jitter_y = cy + random.randint(-cs // 4, cs // 4)
                self.fragments.append(
                    Fragment((jitter_x, jitter_y), color, cs // 2)
                )

    def update(self, dt: float):
        if self.active:
            self.fragments = [f for f in self.fragments if f.update(dt)]
            if not self.fragments:
                self.active = False

    def draw(self, surface):
        for f in self.fragments:
            f.draw(surface)
