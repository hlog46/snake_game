"""障碍物生成（困难模式）"""
import random
from config.settings import COLS, ROWS


def generate_obstacles(count: int, occupied: set) -> set:
    """随机生成 count 个障碍物，避开 occupied 集合中的格子。"""
    if count == 0:
        return set()

    all_cells = {(c, r) for r in range(ROWS) for c in range(COLS)}
    available = list(all_cells - occupied)
    random.shuffle(available)
    return set(available[:count])
