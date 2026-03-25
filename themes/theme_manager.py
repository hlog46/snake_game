"""主题管理器（单例）"""
from themes.classic import ClassicTheme
from themes.neon import NeonTheme
from themes.forest import ForestTheme


class ThemeManager:
    _instance = None

    def __init__(self):
        self._themes = {
            "classic": ClassicTheme(),
            "neon":    NeonTheme(),
            "forest":  ForestTheme(),
        }
        self._current_name = "classic"
        self.current = self._themes["classic"]

    @classmethod
    def get_instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def set_theme(self, name: str):
        if name in self._themes:
            self._current_name = name
            self.current = self._themes[name]

    @property
    def name(self) -> str:
        return self._current_name

    @property
    def theme(self):
        return self.current
