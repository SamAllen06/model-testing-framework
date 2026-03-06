from enum import auto, Enum


class CheckStatus(Enum):
    PASSED = auto()
    SKIPPED = auto()
    FAILED = auto()
    ERROR = auto()
