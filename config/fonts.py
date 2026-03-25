"""字体辅助：优先使用支持中文的系统字体"""
import os
import pygame

# Windows 常见中文字体路径（按优先级）
_CHINESE_FONT_CANDIDATES = [
    "C:/Windows/Fonts/simhei.ttf",       # 黑体
    "C:/Windows/Fonts/msyh.ttc",         # 微软雅黑
    "C:/Windows/Fonts/simsun.ttc",       # 宋体
]

_FONT_PATH = None
for _p in _CHINESE_FONT_CANDIDATES:
    if os.path.exists(_p):
        _FONT_PATH = _p
        break

_cache: dict = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    """
    返回支持中文的字体。
    优先使用系统中文字体，找不到则回退到 pygame 内置字体（中文会乱码）。
    """
    key = (size, bold)
    if key in _cache:
        return _cache[key]

    if _FONT_PATH:
        try:
            font = pygame.font.Font(_FONT_PATH, size)
            _cache[key] = font
            return font
        except Exception:
            pass

    # 回退：内置字体（不支持中文，但至少不崩溃）
    font = pygame.font.Font(None, size)
    _cache[key] = font
    return font
