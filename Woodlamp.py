import json
from datetime import datetime
from typing import Tuple, List

import requests
from flask import Flask

from Scheduler import Scheduler
from TimeFunctions import parse_to_utc, local_time_today


class Woodlamp:
	def __init__( self, app: Flask, scheduler: Scheduler, lamp_ip: str ):
		self.scheduler: Scheduler = scheduler
		self.lamp_ip = lamp_ip
		self.next_sundown: datetime = None
		self.available_modes: List[ str ] = [ ]

		self.setup( app )

	def setup( self, app: Flask ):
		self.schedule_scheduling()
		self.schedule_irregular()
		self.setup_routes( app )
		self.fetch_available_modes()

	def produce_main_page_content( self ):
		def make_link( mode ):
			return f'<button onclick="fetch(\'/woodlamp/mode/{mode}\')">{mode}</a>'

		mode_links = [ make_link( mode ) for mode in self.available_modes ]
		modes_block = f'<div class="modes_block"> {"<br />".join( mode_links )} </div>'
		color_wheel_block = self.make_color_wheel_block()
		sundown_time_string = local_time_today( self.next_sundown )

		return f"""
		Next sundown at: {sundown_time_string} </br>
		Set color mode:	{modes_block} </br>
		{color_wheel_block}
		"""

	@staticmethod
	def make_color_wheel_block():
		return """
			<div id="picker"></div>
		<script src="https://cdn.jsdelivr.net/npm/@jaames/iro@5"></script>
		<script type="text/javascript">
			var colorPicker = new iro.ColorPicker('#picker', {
				layoutDirection: "horizontal"
			});
	
			colorPicker.on('color:change', color => {
				const colorString = "0x" + color.hexString.substring(1);
				fetch( "/woodlamp/mode/SingleColor&color=" + colorString );
			});
		</script>
		"""

	def schedule_irregular( self ) -> None:
		self.schedule_sundown_lamp()

	def fetch_available_modes( self ) -> None:
		response = requests.get( f'http://{self.lamp_ip}/getModes' )
		mode_names = response.text.split( ',' )
		mode_names = [ mode.strip() for mode in mode_names ]
		self.available_modes = mode_names

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
