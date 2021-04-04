import json
from datetime import datetime

import requests

from Scheduler import Scheduler
from TimeFunctions import parse_to_utc


class WoodLampController:
	def __init__( self, scheduler: Scheduler ):
		self.scheduler: Scheduler = scheduler
		self.next_sundown: datetime = None
		self.schedule_all()

	def schedule_all( self ) -> None:
		self.schedule_sundown_lamp()
		self.schedule_scheduling()

	def schedule_sundown_lamp( self ):
		sun_times_json = requests.get( 'https://api.sunrise-sunset.org/json?lat=51&lng=7&formatted=0' )
		sun_times_times_utc = json.loads( sun_times_json.text )[ 'results' ]
		twilight_start_string = sun_times_times_utc[ 'nautical_twilight_end' ][ :-6 ]
		twilight_start_utc = parse_to_utc( twilight_start_string, '%Y-%m-%dT%H:%M:%S' )

		self.next_sundown = twilight_start_utc
		self.scheduler.add_job( "turn on city lights", self.schedule_sundown_lamp, next_run_time=self.next_sundown )

	def schedule_scheduling( self ) -> None:
		self.scheduler.add_job( "Schedule Wood Lamp Controller", self.schedule_all, trigger="cron", hour=0, day="*" )

	def CityAtSundown( self ):
		requests.get( 'http://192.168.178.26/setMode?newMode=CityAtSundown' )
