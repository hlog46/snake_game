"""主菜单、暂停菜单、游戏结束界面"""
import pygame
import math
import random
from config.settings import (
    SCREEN_W, SCREEN_H, COLS, ROWS, CELL_SIZE,
    GAME_AREA_TOP, HUD_TOP_H, HUD_BOTTOM_H,
    DIFFICULTY_ORDER, THEME_ORDER,
    DIFFICULTY_NAMES, THEME_NAMES
)
from config.fonts import get_font


# ──────────────────────────────────────────────
# 辅助：在背景画一条游走的装饰蛇
# ──────────────────────────────────────────────
class _DemoSnake:
    """菜单背景装饰蛇（自动游走）"""
    LENGTH = 24
    SPEED = 6  # 格/秒

    def __init__(self):
        self._reset()

    def _reset(self):
        col, row = COLS // 4, ROWS // 2
        self.body = [(col - i, row) for i in range(self.LENGTH)]
        self.direction = (1, 0)
        self._timer = 0.0
        self._turn_cd = 0.0

    def update(self, dt: float):
        self._timer += dt
        self._turn_cd -= dt
        interval = 1.0 / self.SPEED

        if self._timer >= interval:
            self._timer -= interval
            # 随机转向（冷却 0.5s 内不转）
            if self._turn_cd <= 0 and random.random() < 0.25:
                dc, dr = self.direction
                choices = [(dr, -dc), (-dr, dc)]   # 左转 / 右转
                self.direction = random.choice(choices)
                self._turn_cd = 0.4

            col, row = self.body[0]
            dc, dr = self.direction
            nc, nr = col + dc, row + dr
            # 边界反弹
            if nc < 0 or nc >= COLS or nr < 0 or nr >= ROWS:
                dc, dr = self.direction
                choices = [(dr, -dc), (-dr, dc)]
                random.shuffle(choices)
                for d in choices:
                    tc, tr = col + d[0], row + d[1]
                    if 0 <= tc < COLS and 0 <= tr < ROWS:
                        self.direction = d
                        nc, nr = tc, tr
                        break
                else:
                    self._reset()
                    return

            self.body.insert(0, (nc, nr))
            if len(self.body) > self.LENGTH:
                self.body.pop()

    def draw(self, surface, theme):
        cs = CELL_SIZE
        for i, (col, row) in enumerate(self.body):
            x = col * cs
            y = GAME_AREA_TOP + row * cs
            t = i / max(len(self.body) - 1, 1)
            alpha = int(160 * (1 - t) + 20 * t)
            c = theme.snake_body_color
            surf = pygame.Surface((cs - 2, cs - 2), pygame.SRCALPHA)
            surf.fill((*c, alpha))
            surface.blit(surf, (x + 1, y + 1))


# ──────────────────────────────────────────────
# 通用菜单渲染工具
# ──────────────────────────────────────────────
def _make_fonts():
    title_font = get_font(52, bold=True)
    menu_font  = get_font(32)
    small_font = get_font(20)
    return title_font, menu_font, small_font


def _draw_overlay(surface, alpha=160):
    """半透明黑色遮罩"""
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, alpha))
    surface.blit(ov, (0, 0))


def _draw_menu_items(surface, items, selected, font, theme,
                     cx: int, start_y: int, spacing: int = 44):
    for i, label in enumerate(items):
        if i == selected:
            color = theme.highlight_color
            # 选中项：左侧小箭头
            arrow = font.render("▶", True, color)
            surface.blit(arrow, (cx - 180, start_y + i * spacing))
        else:
            color = theme.text_color
        text = font.render(label, True, color)
        surface.blit(text, (cx - text.get_width() // 2, start_y + i * spacing))


# ──────────────────────────────────────────────
# 主菜单
# ──────────────────────────────────────────────
class MainMenu:
    ITEMS = ["开始游戏", "选择难度", "选择风格", "排行榜", "退出"]

    def __init__(self, ctrl):
        self.ctrl = ctrl
        self.selected = 0
        self._demo = _DemoSnake()
        self._sub = None          # 当前子菜单 ("difficulty" | "theme" | "scores")
        self._sub_selected = 0
        self._title_timer = 0.0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self._sub:
            self._handle_sub_event(event)
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self.ITEMS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self.ITEMS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._confirm()
        elif event.key == pygame.K_ESCAPE:
            pass

    def _confirm(self):
        action = self.ITEMS[self.selected]
        if action == "开始游戏":
            self.ctrl.start_game()
        elif action == "选择难度":
            self._sub = "difficulty"
            self._sub_selected = DIFFICULTY_ORDER.index(self.ctrl.difficulty)
        elif action == "选择风格":
            self._sub = "theme"
            self._sub_selected = THEME_ORDER.index(self.ctrl.theme_manager.name)
        elif action == "排行榜":
            self._sub = "scores"
        elif action == "退出":
            import sys
            pygame.quit()
            sys.exit()

    def _handle_sub_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self._sub = None
            return

        if self._sub == "difficulty":
            items = DIFFICULTY_ORDER
            if event.key in (pygame.K_UP, pygame.K_w):
                self._sub_selected = (self._sub_selected - 1) % len(items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._sub_selected = (self._sub_selected + 1) % len(items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.ctrl.difficulty = items[self._sub_selected]
                self._sub = None

        elif self._sub == "theme":
            items = THEME_ORDER
            if event.key in (pygame.K_UP, pygame.K_w):
                self._sub_selected = (self._sub_selected - 1) % len(items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._sub_selected = (self._sub_selected + 1) % len(items)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.ctrl.theme_manager.set_theme(items[self._sub_selected])
                self._sub = None

        elif self._sub == "scores":
            if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                self._sub = None

    def update(self, dt: float):
        self._demo.update(dt)
        self._title_timer += dt

    def draw(self, surface):
        theme = self.ctrl.theme_manager.theme
        title_font, menu_font, small_font = _make_fonts()

        # 背景
        surface.fill(theme.bg_color)
        self._demo.draw(surface, theme)

        # 遮罩
        _draw_overlay(surface, 120)

        cx = SCREEN_W // 2

        # 标题（波动效果）
        wave = math.sin(self._title_timer * 2) * 4
        title_text = title_font.render("贪  吃  蛇", True, theme.highlight_color)
        surface.blit(title_text, (cx - title_text.get_width() // 2, 60 + int(wave)))

        subtitle = small_font.render("Snake Deluxe", True, theme.snake_body_color)
        surface.blit(subtitle, (cx - subtitle.get_width() // 2, 128))

        if self._sub:
            self._draw_sub(surface, theme, title_font, menu_font, small_font, cx)
        else:
            _draw_menu_items(surface, self.ITEMS, self.selected,
                             menu_font, theme, cx, 190, 46)
            # 操作提示
            hint = small_font.render("↑↓ 移动  Enter 确认  ESC 返回", True, (100, 100, 120))
            surface.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 30))

    def _draw_sub(self, surface, theme, title_font, menu_font, small_font, cx):
        if self._sub == "difficulty":
            title = menu_font.render("选择难度", True, theme.highlight_color)
            surface.blit(title, (cx - title.get_width() // 2, 175))
            labels = [DIFFICULTY_NAMES[k] for k in DIFFICULTY_ORDER]
            _draw_menu_items(surface, labels, self._sub_selected,
                             menu_font, theme, cx, 240, 50)

        elif self._sub == "theme":
            title = menu_font.render("选择风格", True, theme.highlight_color)
            surface.blit(title, (cx - title.get_width() // 2, 175))
            labels = [THEME_NAMES[k] for k in THEME_ORDER]
            _draw_menu_items(surface, labels, self._sub_selected,
                             menu_font, theme, cx, 240, 50)

        elif self._sub == "scores":
            title = menu_font.render("排行榜", True, theme.highlight_color)
            surface.blit(title, (cx - title.get_width() // 2, 160))
            scores = self.ctrl.highscores
            y = 225
            for diff_key in DIFFICULTY_ORDER:
                diff_name = DIFFICULTY_NAMES[diff_key]
                score_val = scores.get(diff_key, {}).get("score", 0)
                date_val  = scores.get(diff_key, {}).get("date", "--")
                line = small_font.render(
                    f"{diff_name}:  {score_val} 分    {date_val}", True, theme.text_color)
                surface.blit(line, (cx - line.get_width() // 2, y))
                y += 44
            hint = small_font.render("按 Enter / ESC 返回", True, (100, 100, 120))
            surface.blit(hint, (cx - hint.get_width() // 2, y + 20))


# ──────────────────────────────────────────────
# 暂停菜单
# ──────────────────────────────────────────────
PAUSE_ITEMS = ["继续游戏", "更换风格", "重新开始", "返回主菜单"]


def draw_pause_menu(surface, ctrl):
    """在当前画面上叠加暂停菜单。"""
    _draw_overlay(surface, 170)
    theme = ctrl.theme_manager.theme
    _, menu_font, small_font = _make_fonts()
    cx = SCREEN_W // 2

    title = menu_font.render("— 暂 停 —", True, theme.highlight_color)
    surface.blit(title, (cx - title.get_width() // 2, 160))

    _draw_menu_items(surface, PAUSE_ITEMS, ctrl.pause_selected,
                     menu_font, theme, cx, 225, 46)

    hint = small_font.render("↑↓ 移动  Enter 确认  ESC/P 继续", True, (100, 100, 120))
    surface.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 40))


# ──────────────────────────────────────────────
# 游戏结束界面
# ──────────────────────────────────────────────
GAMEOVER_ITEMS = ["再来一局", "返回主菜单"]


def draw_game_over(surface, ctrl):
    """在当前画面上叠加游戏结束界面。"""
    _draw_overlay(surface, 180)
    theme = ctrl.theme_manager.theme
    title_font, menu_font, small_font = _make_fonts()
    cx = SCREEN_W // 2

    # 标题
    title = title_font.render("GAME OVER", True, (220, 50, 50))
    surface.blit(title, (cx - title.get_width() // 2, 130))

    # 本次分数（带跳动动画）
    bounce = abs(math.sin(ctrl.death_timer * 3)) * 5
    score_str = str(int(ctrl.score_display))
    score_surf = menu_font.render(f"得分：{score_str}", True, theme.highlight_color)
    surface.blit(score_surf,
                 (cx - score_surf.get_width() // 2, 210 + int(bounce)))

    # 是否刷新最高分
    is_new = ctrl.highscores.get(ctrl.difficulty, {}).get("is_new", False)
    if is_new:
        rec_font = get_font(28)
        rec_surf = rec_font.render("★  NEW RECORD!  ★", True, (255, 215, 0))
        rec_surf.set_alpha(int(200 + 55 * math.sin(ctrl.death_timer * 5)))
        surface.blit(rec_surf, (cx - rec_surf.get_width() // 2, 260))

    _draw_menu_items(surface, GAMEOVER_ITEMS, ctrl.gameover_selected,
                     menu_font, theme, cx, 320, 50)

    hint = small_font.render("↑↓ 移动  Enter 确认", True, (100, 100, 120))
    surface.blit(hint, (cx - hint.get_width() // 2, SCREEN_H - 40))
