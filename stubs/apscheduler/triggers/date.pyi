from _typeshed import Incomplete
from apscheduler.triggers.base import BaseTrigger as BaseTrigger
from apscheduler.util import (
    astimezone as astimezone,
    convert_to_datetime as convert_to_datetime,
    datetime_repr as datetime_repr,
)

class DateTrigger(BaseTrigger):
    run_date: Incomplete
    def __init__(self, run_date: Incomplete | None = None, timezone: Incomplete | None = None) -> None: ...
    def get_next_fire_time(self, previous_fire_time, now): ...
