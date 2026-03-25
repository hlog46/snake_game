"""食物实体与生成管理"""
import random
from config.settings import COLS, ROWS, DIFFICULTY_CONFIG


class Food:
    def __init__(self, pos: tuple, food_type: str = "normal", timeout: float = None):
        self.pos = pos                 # (col, row)
        self.food_type = food_type     # "normal" | "speed_up" | "slow_down"
        self.timeout = timeout         # None 或倒计时秒数
        self._age = 0.0
        self.blink_timer = 0.0        # 用于特殊食物闪烁

    @property
    def time_left(self) -> float:
        if self.timeout is None:
            return float("inf")
        return max(0.0, self.timeout - self._age)

    def update(self, dt: float) -> bool:
        """更新倒计时。返回 False 表示已超时，需要消失。"""
        self._age += dt
        self.blink_timer += dt
        if self.timeout is not None and self._age >= self.timeout:
            return False
        return True


def spawn_food_pos(occupied: set) -> tuple:
    """在空白格中随机选取一个位置。"""
    all_cells = {(c, r) for r in range(ROWS) for c in range(COLS)}
    empty = list(all_cells - occupied)
    if not empty:
        return None
    return random.choice(empty)


class FoodManager:
    def __init__(self, difficulty_cfg: dict):
        self.cfg = difficulty_cfg
        self.normal_food: Food = None
        self.special_food: Food = None
        self._special_timer = 0.0   # 距下次生成特殊食物的计时

    def spawn_normal(self, occupied: set):
        pos = spawn_food_pos(occupied)
        if pos:
            timeout = self.cfg.get("food_timeout")
            self.normal_food = Food(pos, "normal", timeout)

    def update(self, dt: float, occupied: set):
        # 更新普通食物（困难模式有超时）
        if self.normal_food:
            if not self.normal_food.update(dt):
                # 超时，先清空再刷新位置
                self.normal_food = None
                self.spawn_normal(occupied)

        # 更新特殊食物
        if self.special_food:
            if not self.special_food.update(dt):
                self.special_food = None

        # 特殊食物生成计时
        self._special_timer += dt
        if self._special_timer >= self.cfg["special_interval"] and self.special_food is None:
            self._special_timer = 0.0
            self._spawn_special(occupied)

    def _spawn_special(self, occupied: set):
        pos = spawn_food_pos(occupied)
        if pos:
            food_type = random.choice(["speed_up", "slow_down"])
            self.special_food = Food(pos, food_type, timeout=8.0)
