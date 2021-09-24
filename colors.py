from enum import Enum


class Colors(Enum):
    RED = '\033[31m'  # red
    GREEN = '\033[32m'  # green
    CYAN = '\033[36m'  # cyan
    WHITE = '\033[0m'  # white

    def __str__(self):
        return f"{self.value}"
