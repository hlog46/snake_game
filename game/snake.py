"""蛇实体：位置、移动、增长"""
from collections import deque


class Snake:
    def __init__(self, start_pos: tuple, initial_length: int):
        col, row = start_pos
        # 双端队列，头在索引 0，向右初始排列
        self.body: deque = deque()
        for i in range(initial_length):
            self.body.append((col - i, row))
        self.body_set: set = set(self.body)
        self.direction = (1, 0)   # (dc, dr)，初始向右
        self.grow_pending = 0     # 待增长节数
        self.head_flash_timer = 0.0  # 吃食物时头部闪光计时

    @property
    def head(self) -> tuple:
        return self.body[0]

    @property
    def tail(self) -> tuple:
        return self.body[-1]

    def set_direction(self, new_dir: tuple) -> bool:
        """设置方向，拒绝 180° 掉头。返回是否成功。"""
        if (new_dir[0] == -self.direction[0] and
                new_dir[1] == -self.direction[1]):
            return False
        self.direction = new_dir
        return True

    def compute_next_head(self) -> tuple:
        col, row = self.head
        dc, dr = self.direction
        return (col + dc, row + dr)

    def move_to(self, new_head: tuple):
        """
        将蛇头移动到 new_head。
        若 grow_pending > 0，本次不移除尾部（蛇增长一节），并将 grow_pending - 1。
        """
        self.body.appendleft(new_head)
        self.body_set.add(new_head)

        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            removed = self.body.pop()
            self.body_set.discard(removed)

    def trigger_head_flash(self):
        self.head_flash_timer = 0.12

    def update(self, dt: float):
        if self.head_flash_timer > 0:
            self.head_flash_timer = max(0.0, self.head_flash_timer - dt)

    @property
    def is_head_flashing(self) -> bool:
        return self.head_flash_timer > 0
