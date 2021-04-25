import json
from datetime import datetime
from typing import Tuple

import requests
from flask import Flask

from Scheduler import Scheduler
from TimeFunctions import parse_to_utc


class WoodLampController:
	def __init__( self, scheduler: Scheduler, lamp_ip: str, app: Flask ):
		self.scheduler: Scheduler = scheduler
		self.lamp_ip = lamp_ip
		self.next_sundown: datetime = None
		self.schedule_scheduling()
		self.schedule_irregular()
		self.available_modes = None

		self.setup( app )

	def setup( self, app: Flask ):
		self.setup_routes( app )

	def schedule_irregular( self ) -> None:
		self.schedule_sundown_lamp()

	def schedule_sundown_lamp( self ) -> None:
		sun_times_json = requests.get( 'https://api.sunrise-sunset.org/json?lat=51&lng=7&formatted=0' )
		sun_times_times_utc = json.loads( sun_times_json.text )[ 'results' ]
		twilight_start_string = sun_times_times_utc[ 'nautical_twilight_end' ][ :-6 ]
		twilight_start_utc = parse_to_utc( twilight_start_string, '%Y-%m-%dT%H:%M:%S' )

		self.next_sundown = twilight_start_utc
		self.scheduler.add_job(
			"Turn on city lights",
			self.set_mode,
			args=[ 'CityAtSundown' ],
			next_run_time=self.next_sundown
		)

	def schedule_scheduling( self ) -> None:
		self.scheduler.add_job(
			"Schedule Wood Lamp Controller",
			self.schedule_irregular,
			trigger="cron", hour=3, day="*"
		)

	def set_mode( self, mode: str ) -> Tuple[ str, int ]:
		response = requests.get( f'http://{self.lamp_ip}/setMode?newMode={mode}' )
		return response.text, response.status_code

	def setup_routes( self, app: Flask ):
		@app.route( '/woodlamp/mode/<string:mode>' )
		def set_mode( mode: str ):
			return self.set_mode( mode )
