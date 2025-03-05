from _typeshed import Incomplete

__all__ = ["MIN_VALUES", "MAX_VALUES", "DEFAULT_VALUES", "BaseField", "WeekField", "DayOfMonthField", "DayOfWeekField"]

MIN_VALUES: Incomplete
MAX_VALUES: Incomplete
DEFAULT_VALUES: Incomplete

class BaseField:
    REAL: bool
    COMPILERS: Incomplete
    name: Incomplete
    is_default: Incomplete
    def __init__(self, name, exprs, is_default: bool = False) -> None: ...
    def get_min(self, dateval): ...
    def get_max(self, dateval): ...
    def get_value(self, dateval): ...
    def get_next_value(self, dateval): ...
    expressions: Incomplete
    def compile_expressions(self, exprs) -> None: ...
    def compile_expression(self, expr) -> None: ...
    def __eq__(self, other): ...

class WeekField(BaseField):
    REAL: bool
    def get_value(self, dateval): ...

class DayOfMonthField(BaseField):
    COMPILERS: Incomplete
    def get_max(self, dateval): ...

class DayOfWeekField(BaseField):
    REAL: bool
    COMPILERS: Incomplete
    def get_value(self, dateval): ...

class MonthField(BaseField):
    COMPILERS: Incomplete
