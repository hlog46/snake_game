"""全局配置常量"""

SCREEN_W = 800
SCREEN_H = 600
HUD_TOP_H = 50       # 顶部 HUD 高度
HUD_BOTTOM_H = 50    # 底部状态栏高度
GAME_AREA_TOP = HUD_TOP_H
GAME_AREA_H = SCREEN_H - HUD_TOP_H - HUD_BOTTOM_H   # 500
CELL_SIZE = 20
COLS = SCREEN_W // CELL_SIZE   # 40
ROWS = GAME_AREA_H // CELL_SIZE  # 25
FPS = 60

DIFFICULTY_CONFIG = {
    "easy": {
        "speed": 8,
        "initial_length": 3,
        "food_timeout": None,
        "obstacles": 0,
        "score_multiplier": 1.0,
        "special_interval": 30,
    },
    "normal": {
        "speed": 12,
        "initial_length": 3,
        "food_timeout": None,
        "obstacles": 0,
        "score_multiplier": 1.5,
        "special_interval": 20,
    },
    "hard": {
        "speed": 18,
        "initial_length": 5,
        "food_timeout": 6,
        "obstacles": 5,
        "score_multiplier": 2.5,
        "special_interval": 15,
    },
}

DIFFICULTY_NAMES = {
    "easy":   "简单",
    "normal": "普通",
    "hard":   "困难",
}

THEME_NAMES = {
    "classic": "经典像素风",
    "neon":    "霓虹赛博风",
    "forest":  "自然森林风",
}

DIFFICULTY_ORDER = ["easy", "normal", "hard"]
THEME_ORDER = ["classic", "neon", "forest"]

COMBO_WINDOW = 3.0      # Combo 判定时间窗口（秒）
COMBO_MIN_COUNT = 3     # 最低连击数
MAX_PARTICLES = 250

HIGHSCORE_FILE = "data/highscore.json"
