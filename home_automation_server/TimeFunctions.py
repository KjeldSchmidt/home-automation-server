from datetime import datetime, timedelta

import pytz


def parse_to_utc(time: str, time_format: str) -> datetime:
    time_naive = datetime.strptime(time, time_format)
    return time_naive.replace(tzinfo=pytz.utc)


def local_time_today(time: datetime) -> str:
    time = time.astimezone()
    return time.strftime("%H:%M")


def get_next_valid_time(time_str: str, time_format: str = "%H:%M") -> datetime:
    time_of_day = datetime.strptime(time_str, time_format)
    now = datetime.now()
    candidate = now.replace(
        hour=time_of_day.hour, minute=time_of_day.minute, second=0, microsecond=0
    )
    if candidate > now:
        return candidate
    else:
        return candidate + timedelta(days=1)
