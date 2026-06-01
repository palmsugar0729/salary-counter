"""班级费率配置和常量，可手动修改新增。"""

CLASS_RATES: dict[str, float] = {
    "1对1": 80,
    "1对2": 100,
    "1对3": 100,
    "1对4": 110,
    "1对5": 120,
}

DEFAULT_RATE: float = 100

WEEKDAY_NAMES: dict[int, str] = {
    0: "一",
    1: "二",
    2: "三",
    3: "四",
    4: "五",
    5: "六",
    6: "日",
}

# 同班级同色用的背景色调色板
COLOR_PALETTE: list[str] = [
    "FFD4E6F1",
    "FFD5F5E3",
    "FFFDEBD0",
    "FFE8DAEF",
    "FFFADBD8",
    "FFD1F2EB",
    "FFFCF3CF",
    "FFD6EAF8",
]
