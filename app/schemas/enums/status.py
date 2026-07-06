from enum import StrEnum, auto


class Status(StrEnum):
    TRACKING = auto()
    CANCELLED = auto()
    PURCHASED = auto()
    PAUSED = auto()
