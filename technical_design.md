# 贪吃蛇游戏 —— 技术设计文档

**版本：** 1.0
**日期：** 2026-03-24
**对应需求文档：** requirements.md v1.0

---

## 1. 技术选型

| 项目 | 选型 | 理由 |
|------|------|------|
| 开发语言 | Python 3.10+ | 开发效率高，生态丰富 |
| 渲染引擎 | Pygame 2.x | 跨平台，2D 渲染能力完善，粒子特效实现方便 |
| 数据存储 | JSON 本地文件 | 轻量，无需数据库，适合单机最高分存储 |
| 字体 | Pygame 内置 + 自定义 TTF | 支持像素风/现代风格字体切换 |
| 依赖管理 | pip / requirements.txt | 标准 Python 依赖管理 |

**运行环境：**
- Python 3.10+
- pygame >= 2.1.0
- 操作系统：Windows / macOS / Linux

---

## 2. 项目结构

```
snake_game/
│
├── main.py                  # 程序入口，初始化并启动游戏主循环
│
├── game/
│   ├── __init__.py
│   ├── snake.py             # 蛇实体：位置、移动、增长
│   ├── food.py              # 食物实体：普通食物与特殊食物
│   ├── obstacle.py          # 障碍物实体（困难模式）
│   ├── board.py             # 棋盘管理：网格、碰撞检测
│   └── game_state.py        # 游戏状态机
│
├── effects/
│   ├── __init__.py
│   ├── particle.py          # 粒子系统（Particle + ParticleEmitter）
│   ├── screen_flash.py      # 屏幕闪光与红闪效果
│   ├── score_popup.py       # 分数浮动文字动画
│   ├── combo.py             # 连击特效（文字 + 震动）
│   └── death_effect.py      # 死亡碎裂动画
│
├── ui/
│   ├── __init__.py
│   ├── menu.py              # 主菜单、暂停菜单、游戏结束界面
│   └── hud.py               # 游戏内 HUD（分数、倒计时、道具状态）
│
├── themes/
│   ├── __init__.py
│   ├── base_theme.py        # 主题抽象基类
│   ├── classic.py           # 经典像素风主题
│   ├── neon.py              # 霓虹赛博风主题
│   ├── forest.py            # 自然森林风主题
│   └── theme_manager.py     # 主题管理器（单例）
│
├── config/
│   ├── __init__.py
│   └── settings.py          # 全局常量：难度参数、窗口尺寸、颜色等
│
├── data/
│   └── highscore.json       # 最高分本地持久化（自动生成）
│
└── assets/
    └── fonts/               # 字体文件
        ├── pixel.ttf        # 像素风字体
        └── modern.ttf       # 现代字体
```

---

## 3. 架构设计

### 3.1 状态机（GameState）

游戏使用有限状态机管理界面与逻辑流转：

```
┌─────────┐     开始游戏      ┌─────────┐     ESC/P      ┌─────────┐
│  MENU   │ ──────────────► │ PLAYING │ ────────────► │ PAUSED  │
└─────────┘                 └─────────┘               └─────────┘
     ▲                           │                         │
     │                    碰撞/死亡                      继续游戏
     │                           ▼                         │
     │                    ┌───────────┐                    │
     └────────────────── │ GAME_OVER │ ◄──────────────────┘
         返回主菜单        └───────────┘
```

**状态枚举：**
```python
class State(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
```

每个状态对应独立的 `handle_event()`、`update()`、`draw()` 方法。

---

### 3.2 主游戏循环

```python
# main.py 核心结构
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    game = GameController()

    while True:
        dt = clock.tick(60) / 1000.0      # delta time（秒）
        events = pygame.event.get()

        game.handle_events(events)
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()
```

- 固定 60FPS 上限，使用 `delta time` 确保游戏逻辑与帧率解耦
- 蛇的移动使用**累计时间计时器**，而非每帧移动，保证不同帧率下速度一致

---

## 4. 核心模块设计

### 4.1 蛇（Snake）

```python
# game/snake.py
class Snake:
    def __init__(self, start_pos: tuple, initial_length: int):
        self.body: deque[tuple]   # 双端队列，头在左
        self.direction: tuple     # (dx, dy)
        self.body_set: set        # 快速碰撞检测用

    def move(self) -> tuple:
        """移动蛇，返回新蛇头位置"""

    def grow(self, n: int = 1):
        """增长 n 节（下次移动时保留尾部）"""

    def set_direction(self, new_dir: tuple) -> bool:
        """设置方向，忽略 180° 掉头，返回是否成功"""

    def check_self_collision(self) -> bool:
        """蛇头是否碰到蛇身"""

    @property
    def head(self) -> tuple:
        return self.body[0]
```

**关键实现：**
- `body` 使用 `collections.deque`，头部插入/尾部删除均为 O(1)
- `body_set` 与 `body` 同步维护，碰撞检测 O(1)

---

### 4.2 棋盘（Board）

```python
# game/board.py
class Board:
    CELL_SIZE = 20          # 每格像素大小
    COLS = 40               # 列数（800px / 20px）
    ROWS = 30               # 行数（600px / 20px）

    def is_out_of_bounds(self, pos: tuple) -> bool:
        """检测是否超出边界"""

    def get_empty_cells(self, snake: Snake, obstacles: list) -> list:
        """返回所有空白格，用于食物生成"""

    def cell_to_pixel(self, pos: tuple) -> tuple:
        """网格坐标转屏幕像素坐标（左上角）"""
```

---

### 4.3 食物（Food）

```python
# game/food.py
class Food:
    def __init__(self, pos: tuple, food_type: str = "normal"):
        self.pos: tuple
        self.food_type: str    # "normal" | "speed_up" | "slow_down"
        self.timeout: float    # None 或剩余存活秒数

    def update(self, dt: float) -> bool:
        """更新倒计时，返回 False 表示已超时需消失"""

class FoodManager:
    def spawn_normal(self, board: Board, snake: Snake):
        """在空白格随机生成普通食物"""

    def try_spawn_special(self, elapsed: float):
        """根据时间间隔尝试生成特殊食物"""
```

---

### 4.4 难度配置（Settings）

```python
# config/settings.py

SCREEN_W, SCREEN_H = 800, 600
CELL_SIZE = 20

DIFFICULTY_CONFIG = {
    "easy": {
        "speed":           8,       # 格/秒
        "initial_length":  3,
        "food_timeout":    None,    # 无倒计时
        "obstacles":       0,
        "score_multiplier": 1.0,
        "special_interval": 30,    # 特殊食物间隔（秒）
    },
    "normal": {
        "speed":           12,
        "initial_length":  3,
        "food_timeout":    None,
        "obstacles":       0,
        "score_multiplier": 1.5,
        "special_interval": 20,
    },
    "hard": {
        "speed":           18,
        "initial_length":  5,
        "food_timeout":    6,       # 6秒后消失
        "obstacles":       5,
        "score_multiplier": 2.5,
        "special_interval": 15,
    },
}

COMBO_WINDOW = 3.0          # Combo 判定时间窗口（秒）
COMBO_MIN_COUNT = 3         # 触发 Combo 的最低连击数
```

---

## 5. 主题系统

### 5.1 基类接口

```python
# themes/base_theme.py
from abc import ABC, abstractmethod

class BaseTheme(ABC):
    # 颜色属性
    bg_color: tuple
    snake_head_color: tuple
    snake_body_color: tuple
    food_color: tuple
    obstacle_color: tuple
    particle_color: tuple
    text_color: tuple

    @abstractmethod
    def draw_snake(self, surface, snake: Snake):
        """绘制蛇（允许各主题自定义形状/渐变/发光）"""

    @abstractmethod
    def draw_food(self, surface, food: Food):
        """绘制食物"""

    @abstractmethod
    def draw_background(self, surface):
        """绘制背景（纯色/纹理/网格线）"""

    def draw_obstacle(self, surface, pos: tuple):
        """绘制障碍物（默认实现，子类可覆盖）"""
```

### 5.2 各主题渲染差异

| 元素 | 经典像素风 | 霓虹赛博风 | 自然森林风 |
|------|-----------|-----------|-----------|
| 背景 | 纯色 + 网格线 | 纯色（近黑） | 纯色 + 轻微噪声纹理 |
| 蛇身 | 实心矩形 | 圆角矩形 + gfxdraw 发光轮廓 | 圆角矩形 + 头尾颜色渐变 |
| 食物 | 实心矩形 | 发光圆形（多层 alpha 叠加） | 带高光的圆形 |
| 特效粒子 | 方形粒子 | 圆形发光粒子 | 菱形"落叶"粒子 |

### 5.3 主题管理器

```python
# themes/theme_manager.py
class ThemeManager:
    _instance = None

    @classmethod
    def get_instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def set_theme(self, name: str):
        themes = {
            "classic": ClassicTheme(),
            "neon":    NeonTheme(),
            "forest":  ForestTheme(),
        }
        self.current = themes[name]

    @property
    def theme(self) -> BaseTheme:
        return self.current
```

---

## 6. 特效系统

### 6.1 粒子系统

```python
# effects/particle.py

class Particle:
    def __init__(self, pos, velocity, color, lifetime):
        self.pos = list(pos)          # [x, y] 浮点坐标
        self.vel = list(velocity)     # [vx, vy] 像素/秒
        self.color = color
        self.lifetime = lifetime      # 总生命周期（秒）
        self.age = 0.0                # 当前年龄

    def update(self, dt: float) -> bool:
        """更新位置和年龄，返回 False 表示已消亡"""
        self.age += dt
        self.pos[0] += self.vel[0] * dt
        self.pos[1] += self.vel[1] * dt
        # 重力效果（可选）
        self.vel[1] += 200 * dt
        return self.age < self.lifetime

    @property
    def alpha(self) -> int:
        """根据生命周期计算透明度（线性衰减）"""
        return int(255 * (1 - self.age / self.lifetime))

    def draw(self, surface):
        if self.alpha <= 0:
            return
        # 使用 pygame.draw 或 gfxdraw 绘制

class ParticleEmitter:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, pos, count, speed_range, color, lifetime_range, spread=360):
        """在 pos 位置生成 count 个粒子，向 spread 度范围扩散"""
        import random, math
        for _ in range(count):
            angle = math.radians(random.uniform(0, spread))
            speed = random.uniform(*speed_range)
            vel = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(*lifetime_range)
            self.particles.append(Particle(pos, vel, color, lifetime))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
```

### 6.2 屏幕特效

```python
# effects/screen_flash.py

class ScreenFlash:
    def __init__(self):
        self.active = False
        self.color = (255, 0, 0)
        self.alpha = 0.0
        self.decay_rate = 0.0

    def trigger(self, color: tuple, initial_alpha: float, duration: float):
        self.active = True
        self.color = color
        self.alpha = initial_alpha
        self.decay_rate = initial_alpha / duration

    def update(self, dt: float):
        if self.active:
            self.alpha -= self.decay_rate * dt
            if self.alpha <= 0:
                self.alpha = 0
                self.active = False

    def draw(self, surface):
        if not self.active or self.alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, int(self.alpha)))
        surface.blit(overlay, (0, 0))
```

### 6.3 连击特效

```python
# effects/combo.py

class ComboEffect:
    def __init__(self):
        self.combo_count = 0
        self.last_eat_time = 0.0
        self.display_text = ""
        self.display_timer = 0.0
        self.shake_timer = 0.0
        self.shake_offset = (0, 0)

    def on_eat(self, current_time: float) -> int:
        """返回当前连击加分"""
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
        self.display_text = f"COMBO ×{self.combo_count}"
        self.display_timer = 0.8
        self.shake_timer = 0.2

    def update(self, dt: float):
        self.display_timer = max(0, self.display_timer - dt)
        self.shake_timer = max(0, self.shake_timer - dt)
        if self.shake_timer > 0:
            import random
            self.shake_offset = (random.randint(-3, 3), random.randint(-3, 3))
        else:
            self.shake_offset = (0, 0)
```

### 6.4 死亡特效

```python
# effects/death_effect.py

class DeathEffect:
    def __init__(self):
        self.fragments: list  # 每节蛇身的碎片
        self.active = False
        self.timer = 0.0
        self.duration = 0.8

    def trigger(self, snake_body: list, theme: BaseTheme):
        """根据蛇身位置生成碎片粒子"""
        self.active = True
        self.timer = self.duration
        # 为每节蛇身生成随机速度的碎片
        ...

    def update(self, dt: float):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False
            # 更新所有碎片位置

    def draw(self, surface):
        ...
```

---

## 7. HUD 与菜单

### 7.1 HUD 布局

```
┌──────────────────────────────────────────┐
│ SCORE: 1250    [HARD] [Neon Cyber]       │  ← 顶部 HUD 栏（40px 高）
│ BEST:  2400                              │
├──────────────────────────────────────────┤
│                                          │
│            游戏区域                       │
│          (800×520px)                     │
│                                          │
├──────────────────────────────────────────┤
│ [食物倒计时进度条（困难模式）]              │  ← 底部状态栏（40px 高）
│ [道具状态图标 + 剩余时间]                  │
└──────────────────────────────────────────┘
```

### 7.2 菜单组件

```python
# ui/menu.py

class MenuItem:
    def __init__(self, label: str, action: callable):
        self.label = label
        self.action = action
        self.is_selected = False

class Menu:
    def __init__(self, items: list[MenuItem]):
        self.items = items
        self.selected_index = 0

    def handle_input(self, event):
        """上下键切换选项，Enter/Space 确认"""

    def draw(self, surface, theme: BaseTheme):
        """绘制菜单，选中项高亮"""
```

---

## 8. 数据持久化

```python
# 最高分存储结构（data/highscore.json）
{
    "easy":   {"score": 500,  "date": "2026-03-24"},
    "normal": {"score": 1200, "date": "2026-03-24"},
    "hard":   {"score": 800,  "date": "2026-03-24"}
}
```

读写通过简单的 `json.load` / `json.dump` 实现，文件不存在时自动创建。

---

## 9. 关键算法

### 9.1 蛇移动时序控制

```python
# 在 GameController.update() 中
self.move_timer += dt
move_interval = 1.0 / self.difficulty["speed"]   # 例：speed=12 → 1/12 秒/格

if self.move_timer >= move_interval:
    self.move_timer -= move_interval
    self._tick_snake()    # 执行一次蛇移动逻辑
```

此方案确保无论帧率如何波动，蛇的移动速度恒定。

### 9.2 碰撞检测（O(1)）

```python
new_head = snake.compute_next_head()

# 边界检测
if board.is_out_of_bounds(new_head):
    self._trigger_death()

# 自碰检测（排除即将消失的尾部）
effective_body = snake.body_set - {snake.tail} if not snake.growing else snake.body_set
if new_head in effective_body:
    self._trigger_death()

# 障碍物检测
if new_head in obstacle_set:
    self._trigger_death()
```

### 9.3 食物随机生成

```python
def spawn_food(board: Board, snake: Snake, obstacles: set) -> tuple:
    occupied = snake.body_set | obstacles
    all_cells = set((r, c) for r in range(board.ROWS) for c in range(board.COLS))
    empty_cells = list(all_cells - occupied)
    return random.choice(empty_cells)
```

空白格计算基于集合差运算，效率高且代码简洁。

---

## 10. 验证方案

### 10.1 功能验证清单

| 测试项 | 操作 | 预期结果 |
|--------|------|---------|
| 难度切换 | 主菜单选择三档难度并开始游戏 | 速度/障碍物/倒计时符合配置表 |
| 主题切换 | 主菜单和暂停菜单切换主题 | 颜色、形状立即变化 |
| 吃食物特效 | 游戏中吃一个食物 | 粒子爆炸 + 分数浮动动画播放 |
| Combo 特效 | 3 秒内连吃 3 个食物 | "COMBO ×3" 文字 + 屏幕震动 |
| 死亡特效 | 让蛇撞墙 | 蛇身碎裂 + 红色屏幕闪光 |
| 特殊食物 | 等待 20 秒后吃特殊食物 | 全屏光晕 + 蛇身渲染变化 |
| 最高分存储 | 打出历史最高分后退出重启 | 最高分保留 |
| 游戏结束 UI | 刷新最高分 | 显示"NEW RECORD!" 金色特效 |

### 10.2 运行方式

```bash
# 安装依赖
pip install pygame

# 启动游戏
python main.py
```

### 10.3 性能基准

- 粒子数量上限：屏幕同时最多 200 个粒子，超出则不再新增
- 每帧绘制调用数：控制在 500 次以内（避免 Pygame 绘制过多拖慢帧率）
