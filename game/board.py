"""棋盘管理：网格坐标与像素坐标转换、边界检测"""
from config.settings import CELL_SIZE, COLS, ROWS, GAME_AREA_TOP


class Board:
    CELL_SIZE = CELL_SIZE
    COLS = COLS
    ROWS = ROWS

    def is_out_of_bounds(self, col: int, row: int) -> bool:
        return col < 0 or col >= self.COLS or row < 0 or row >= self.ROWS

    def cell_to_pixel(self, col: int, row: int) -> tuple:
        """返回格子左上角的像素坐标"""
        return (col * self.CELL_SIZE, GAME_AREA_TOP + row * self.CELL_SIZE)

    def cell_to_pixel_center(self, col: int, row: int) -> tuple:
        """返回格子中心的像素坐标"""
        x, y = self.cell_to_pixel(col, row)
        half = self.CELL_SIZE // 2
        return (x + half, y + half)
