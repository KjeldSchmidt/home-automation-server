from _typeshed import Incomplete
from apscheduler.triggers.base import BaseTrigger as BaseTrigger
from apscheduler.util import asdate as asdate, astimezone as astimezone, timezone_repr as timezone_repr
from datetime import date, datetime, tzinfo

class CalendarIntervalTrigger(BaseTrigger):
    timezone: Incomplete
    years: Incomplete
    months: Incomplete
    weeks: Incomplete
    days: Incomplete
    start_date: Incomplete
    end_date: Incomplete
    jitter: Incomplete
    def __init__(
        self,
        *,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        timezone: str | tzinfo | None = None,
        jitter: int | None = None
    ) -> None: ...
    def get_next_fire_time(self, previous_fire_time: datetime | None, now: datetime) -> datetime | None: ...
