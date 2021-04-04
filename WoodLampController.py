import json
from datetime import datetime

import requests

from TimeFunctions import parse_to_utc


class WoodLampController:
	def __init__( self ):
		self.next_sundown: datetime = None
		self.schedule_all()

	def schedule_all( self ) -> None:
		self.schedule_sundown_lamp()
		self.schedule_scheduling()

	def schedule_sundown_lamp( self ):
		sun_times_json = requests.get( 'https://api.sunrise-sunset.org/json?lat=51&lng=7&formatted=0' )
		sun_times_times_utc = json.loads( sun_times_json.text )[ 'results' ]
		twilight_start_string = sun_times_times_utc[ 'nautical_twilight_end' ][ :-6 ]
		self.next_sundown = parse_to_utc( twilight_start_string, '%Y-%m-%dT%H:%M:%S' )

	def schedule_scheduling( self ) -> None:
		pass
