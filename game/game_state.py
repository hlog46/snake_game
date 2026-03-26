"""游戏状态机 + 核心控制器"""
import json
import os
import sys
from datetime import date
from enum import Enum

import pygame

from config.settings import (
    COLS, ROWS, DIFFICULTY_CONFIG, DIFFICULTY_ORDER, THEME_ORDER,
    COMBO_MIN_COUNT, MAX_PARTICLES, HIGHSCORE_FILE,
    SCREEN_W, SCREEN_H, GAME_AREA_TOP
)
from game.board import Board
from game.snake import Snake
from game.food import FoodManager
from game.obstacle import generate_obstacles
from themes.theme_manager import ThemeManager
from effects.particle import ParticleEmitter
from effects.screen_flash import ScreenFlash
from effects.score_popup import ScorePopupManager
from effects.combo import ComboEffect
from effects.death_effect import DeathEffect
from ui.hud import draw_hud
from ui.menu import (
    MainMenu, draw_pause_menu, draw_game_over,
    PAUSE_ITEMS, GAMEOVER_ITEMS
)


# ──────────────────────────────────────────────
class State(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


# ──────────────────────────────────────────────
def _load_highscores() -> dict:
    path = HIGHSCORE_FILE
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_highscores(data: dict):
    os.makedirs(os.path.dirname(HIGHSCORE_FILE), exist_ok=True)
    with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
class GameController:
    def __init__(self):
        self.state = State.MENU

        # 主题 & 难度
        self.theme_manager = ThemeManager.get_instance()
        self.theme_manager.set_theme("classic")
        self.difficulty = "normal"

        # 最高分
        self.highscores = _load_highscores()

        # UI
        self.main_menu = MainMenu(self)
        self.pause_selected = 0
        self.gameover_selected = 0

        # 游戏对象（start_game 时初始化）
        self.board = Board()
        self.snake: Snake = None
        self.food_manager: FoodManager = None
        self.obstacles: set = set()

        # 特效
        self.emitter = ParticleEmitter()
        self.flash = ScreenFlash()
        self.popups = ScorePopupManager()
        self.combo = ComboEffect()
        self.death_effect = DeathEffect()

        # 分数
        self.score = 0
        self.score_display = 0.0    # 用于游戏结束时数字跳动

        # 道具状态
        self.power_up_type: str = None
        self.power_up_timer: float = 0.0

        # 计时器
        self.move_timer = 0.0
        self.game_time = 0.0
        self.death_timer = 0.0
        self._slow_mo_timer = 0.0   # 死亡慢动作

        # 最后一次方向输入（用于缓冲）
        self._queued_dir = None

    # ──────────────────── 开始游戏 ────────────────────
    def start_game(self):
        cfg = DIFFICULTY_CONFIG[self.difficulty]

        # 蛇：从棋盘中央出发
        start_col = COLS // 2
        start_row = ROWS // 2
        self.snake = Snake((start_col, start_row), cfg["initial_length"])

        # 障碍物
        self.obstacles = generate_obstacles(
            cfg["obstacles"], self.snake.body_set
        )

        # 食物
        self.food_manager = FoodManager(cfg)
        self.food_manager.spawn_normal(self.snake.body_set | self.obstacles)

        # 重置所有状态
        self.score = 0
        self.score_display = 0.0
        self.power_up_type = None
        self.power_up_timer = 0.0
        self.move_timer = 0.0
        self.game_time = 0.0
        self.death_timer = 0.0
        self._slow_mo_timer = 0.0
        self._queued_dir = None
        self.pause_selected = 0
        self.gameover_selected = 0

        self.emitter = ParticleEmitter()
        self.combo = ComboEffect()
        self.death_effect = DeathEffect()
        self.flash = ScreenFlash()

        # 清除旧的 "is_new" 标记
        for k in self.highscores:
            self.highscores[k].pop("is_new", None)

        self.state = State.PLAYING

    # ──────────────────── 事件处理 ────────────────────
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                _save_highscores(self.highscores)
                pygame.quit()
                sys.exit()

            if self.state == State.MENU:
                self.main_menu.handle_event(event)

            elif self.state == State.PLAYING:
                self._handle_playing_event(event)

            elif self.state == State.PAUSED:
                self._handle_paused_event(event)

            elif self.state == State.GAME_OVER:
                self._handle_gameover_event(event)

    def _handle_playing_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        DIR_MAP = {
            pygame.K_UP:    (0, -1),
            pygame.K_w:     (0, -1),
            pygame.K_DOWN:  (0,  1),
            pygame.K_s:     (0,  1),
            pygame.K_LEFT:  (-1, 0),
            pygame.K_a:     (-1, 0),
            pygame.K_RIGHT: (1,  0),
            pygame.K_d:     (1,  0),
        }
        if event.key in DIR_MAP:
            self._queued_dir = DIR_MAP[event.key]
        elif event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.state = State.PAUSED

    def _handle_paused_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.state = State.PLAYING
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.pause_selected = (self.pause_selected - 1) % len(PAUSE_ITEMS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pause_selected = (self.pause_selected + 1) % len(PAUSE_ITEMS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            action = PAUSE_ITEMS[self.pause_selected]
            if action == "继续游戏":
                self.state = State.PLAYING
            elif action == "更换风格":
                # 循环切换主题
                cur = self.theme_manager.name
                idx = (THEME_ORDER.index(cur) + 1) % len(THEME_ORDER)
                self.theme_manager.set_theme(THEME_ORDER[idx])
            elif action == "重新开始":
                self.start_game()
            elif action == "返回主菜单":
                self.state = State.MENU

    def _handle_gameover_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.death_timer < 0.6:   # 等死亡动画播完
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.gameover_selected = (self.gameover_selected - 1) % len(GAMEOVER_ITEMS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.gameover_selected = (self.gameover_selected + 1) % len(GAMEOVER_ITEMS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            action = GAMEOVER_ITEMS[self.gameover_selected]
            if action == "再来一局":
                self.start_game()
            elif action == "返回主菜单":
                self.state = State.MENU

    # ──────────────────── 更新逻辑 ────────────────────
    def update(self, dt: float):
        # 慢动作
        if self._slow_mo_timer > 0:
            self._slow_mo_timer -= dt
            dt *= 0.2  # 减速到 20%

        if self.state == State.PLAYING:
            self._update_playing(dt)
        elif self.state == State.GAME_OVER:
            self._update_game_over(dt)
        elif self.state == State.MENU:
            self.main_menu.update(dt)

        # 特效始终更新
        self.emitter.update(dt)
        self.flash.update(dt)
        self.popups.update(dt)
        self.combo.update(dt)
        self.death_effect.update(dt)

    def _update_playing(self, dt: float):
        cfg = DIFFICULTY_CONFIG[self.difficulty]
        self.game_time += dt

        # 道具计时
        if self.power_up_type:
            self.power_up_timer -= dt
            if self.power_up_timer <= 0:
                self.power_up_type = None

        # 计算有效速度
        speed = cfg["speed"]
        if self.power_up_type == "speed_up":
            speed *= 1.5
        elif self.power_up_type == "slow_down":
            speed *= 0.7

        self.move_timer += dt
        move_interval = 1.0 / speed

        if self.move_timer >= move_interval:
            self.move_timer -= move_interval
            # 应用缓冲方向
            if self._queued_dir:
                self.snake.set_direction(self._queued_dir)
                self._queued_dir = None
            self._tick_snake()

        # 蛇头闪光更新
        if self.snake:
            self.snake.update(dt)

        # 食物更新
        if self.food_manager:
            occupied = self.snake.body_set | self.obstacles
            self.food_manager.update(dt, occupied)

    def _tick_snake(self):
        new_head = self.snake.compute_next_head()

        # 边界碰撞
        if self.board.is_out_of_bounds(*new_head):
            self._trigger_death()
            return

        # 自碰（移动前排除将消失的尾部）
        check_set = set(self.snake.body)
        if self.snake.grow_pending == 0:
            check_set.discard(self.snake.tail)
        if new_head in check_set:
            self._trigger_death()
            return

        # 障碍物碰撞
        if new_head in self.obstacles:
            self._trigger_death()
            return

        # 检查是否吃到食物
        ate = False
        food_obj = None
        fm = self.food_manager

        if fm.normal_food and new_head == fm.normal_food.pos:
            food_obj = fm.normal_food
            fm.normal_food = None
            ate = True
        elif fm.special_food and new_head == fm.special_food.pos:
            food_obj = fm.special_food
            fm.special_food = None
            ate = True

        # 移动蛇
        if ate and food_obj:
            # 普通食物 +1 节，特殊食物 +3 节
            extra = 2 if food_obj.food_type != "normal" else 0
            self.snake.grow_pending += 1 + extra
        self.snake.move_to(new_head)

        if ate and food_obj:
            self._on_food_eaten(food_obj)

    def _on_food_eaten(self, food):
        cfg = DIFFICULTY_CONFIG[self.difficulty]
        self.snake.trigger_head_flash()

        # 记录吃食物前的道具状态，用于倍率计算
        prev_power_up = self.power_up_type

        # 基础分
        if food.food_type == "normal":
            base = 10
        elif food.food_type == "speed_up":
            base = 30
            self.power_up_type = "speed_up"
            self.power_up_timer = 5.0
            self.flash.trigger((255, 100, 0), 100, 0.3)
        else:  # slow_down
            base = 20
            self.power_up_type = "slow_down"
            self.power_up_timer = 5.0
            self.flash.trigger((0, 100, 255), 100, 0.3)

        # 分数倍率：基于吃食物前的道具状态，避免新道具被重复计算
        mult = cfg["score_multiplier"]
        if prev_power_up == "speed_up":
            mult *= 2.0
        elif prev_power_up == "slow_down":
            mult *= 1.5

        points = int(base * mult)

        # Combo 加成
        combo_bonus = self.combo.on_eat(self.game_time)
        points += combo_bonus
        self.score += points

        # 特效位置
        px, py = self.board.cell_to_pixel_center(*food.pos)
        theme = self.theme_manager.theme

        # 粒子数量（Combo 增强）
        count = 16
        speed_mult = 1.0
        if self.combo.combo_count >= COMBO_MIN_COUNT:
            count = int(count * 1.5)
            speed_mult = 1.3

        # 粒子形状随主题变化
        shape_map = {"classic": "rect", "neon": "circle", "forest": "diamond"}
        shape = shape_map.get(self.theme_manager.name, "circle")

        if len(self.emitter.particles) + count <= MAX_PARTICLES:
            self.emitter.emit(
                (px, py), count=count,
                speed_range=(60 * speed_mult, 160 * speed_mult),
                color=theme.particle_color,
                lifetime_range=(0.25, 0.55),
                size=4, shape=shape
            )

        # 分数浮动文字
        self.popups.add(f"+{points}", (px, py), theme.highlight_color)

        # 重新生成普通食物
        if food.food_type == "normal":
            occupied = self.snake.body_set | self.obstacles
            self.food_manager.spawn_normal(occupied)

    def _trigger_death(self):
        """触发死亡：特效 + 慢动作 + 更新最高分。"""
        theme = self.theme_manager.theme
        self.death_effect.trigger(list(self.snake.body), self.board, theme)
        self.flash.trigger((255, 0, 0), 153, 0.35)
        self._slow_mo_timer = 0.2   # 0.2s 慢动作

        # 更新最高分
        diff_key = self.difficulty
        best = self.highscores.get(diff_key, {}).get("score", 0)
        if self.score > best:
            self.highscores[diff_key] = {
                "score": self.score,
                "date": str(date.today()),
                "is_new": True,
            }
            _save_highscores(self.highscores)

        self.death_timer = 0.0
        self.state = State.GAME_OVER

    def _update_game_over(self, dt: float):
        self.death_timer += dt
        # 数字跳动动画：score_display 逐渐追上 score
        diff = self.score - self.score_display
        if diff > 0:
            self.score_display = min(float(self.score), self.score_display + diff * dt * 5 + 2)

    # ──────────────────── 绘制 ────────────────────
    def draw(self, screen):
        theme = self.theme_manager.theme
        shake = self.combo.shake_offset  # (ox, oy)

        if self.state == State.MENU:
            self.main_menu.draw(screen)
            return

        # 游戏画面（支持震动偏移）
        if shake != (0, 0):
            game_surf = pygame.Surface((SCREEN_W, SCREEN_H))
            self._draw_game(game_surf, theme)
            screen.blit(game_surf, shake)
        else:
            self._draw_game(screen, theme)

        # 特效层（始终绘制在最终 screen 上）
        self.death_effect.draw(screen)
        self.emitter.draw(screen)
        self.popups.draw(screen)
        self.flash.draw(screen)
        self.combo.draw(screen)

        # HUD
        draw_hud(screen, self)

        # 暂停菜单
        if self.state == State.PAUSED:
            draw_pause_menu(screen, self)

        # 游戏结束界面（等 0.5s 后显示）
        if self.state == State.GAME_OVER and self.death_timer >= 0.5:
            draw_game_over(screen, self)

    def _draw_game(self, surface, theme):
        """绘制游戏区域（背景、障碍物、食物、蛇）"""
        # HUD 背景（fill 掉顶底）
        surface.fill(theme.hud_bg_color)

        # 游戏区域背景
        theme.draw_background(surface)

        # 障碍物
        for pos in self.obstacles:
            theme.draw_obstacle(surface, pos, self.board)

        # 食物
        fm = self.food_manager
        if fm:
            if fm.normal_food:
                theme.draw_food(surface, fm.normal_food, self.board)
            if fm.special_food:
                theme.draw_food(surface, fm.special_food, self.board)

        # 蛇（游戏进行或暂停时）
        if self.snake and self.state in (State.PLAYING, State.PAUSED):
            theme.draw_snake(surface, self.snake, self.board, self.power_up_type)
