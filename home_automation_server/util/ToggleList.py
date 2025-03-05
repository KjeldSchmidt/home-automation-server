from collections import deque
from typing import Iterable, TypeVar, Generic

Type = TypeVar("Type")


class ToggleList(Generic[Type]):
    def __init__(self, values: Iterable[Type]) -> None:
        self.values = deque(values)

    def next(self) -> Type:
        next_value = self.values.popleft()
        self.values.append(next_value)
        return next_value
