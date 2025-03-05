from _typeshed import Incomplete
from apscheduler.triggers.base import BaseTrigger as BaseTrigger
from apscheduler.util import (
    astimezone as astimezone,
    convert_to_datetime as convert_to_datetime,
    datetime_repr as datetime_repr,
)

class IntervalTrigger(BaseTrigger):
    interval: Incomplete
    interval_length: Incomplete
    timezone: Incomplete
    start_date: Incomplete
    end_date: Incomplete
    jitter: Incomplete
    def __init__(
        self,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        start_date: Incomplete | None = None,
        end_date: Incomplete | None = None,
        timezone: Incomplete | None = None,
        jitter: Incomplete | None = None,
    ) -> None: ...
    def get_next_fire_time(self, previous_fire_time, now): ...
