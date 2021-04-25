from datetime import datetime

import pytz


def parse_to_utc( time: str, time_format: str ) -> datetime:
	time_naive = datetime.strptime( time, time_format )
	return time_naive.replace( tzinfo=pytz.utc )


def local_time_today( time: datetime ) -> str:
	time = time.astimezone()
	return time.strftime( '%H:%M' )
