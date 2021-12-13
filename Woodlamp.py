import json
from typing import Tuple, List

import requests
from flask import Flask
from flask_apscheduler import APScheduler

import Scheduler
from TimeFunctions import parse_to_utc, local_time_today


class Woodlamp:
	def __init__( self, app: Flask, lamp_ip: str ):
		self.scheduler: APScheduler = Scheduler.scheduler
		self.lamp_ip = lamp_ip
		self.next_sundown: str = "No sundown time set"
		self.available_modes: List[ str ] = [ ]

		self.current_mode: str | None = None

		self.setup( app )

	def setup( self, app: Flask ):
		self.schedule_scheduling()
		self.schedule_irregular()
		self.setup_routes( app )
		self.fetch_available_modes()

	def produce_main_page_content( self ):
		def make_link( mode ):
			return f'<button onclick="fetch(\'/woodlamp/mode/{mode}\')">{mode}</button>'

		if self.available_modes == [ ]:
			self.fetch_available_modes()
			
		mode_links = [ make_link( mode ) for mode in self.available_modes ]
		modes_block = f'<div class="modes_block"> {"".join( mode_links )} </div>'
		color_wheel_block = self.make_color_wheel_block()

		return f"""
		Next sundown at: {self.next_sundown} </br>
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
		try:
			response = requests.get( f'http://{self.lamp_ip}/getModes' )
		except requests.exceptions.ConnectionError:
			return

		mode_names = response.text.split( ',' )
		mode_names = [ mode.strip() for mode in mode_names ]
		self.available_modes = mode_names

	def schedule_sundown_lamp( self ) -> None:
		sun_times_json = requests.get( 'https://api.sunrise-sunset.org/json?lat=51&lng=7&formatted=0' )
		sun_times_times_utc = json.loads( sun_times_json.text )[ 'results' ]
		twilight_start_string = sun_times_times_utc[ 'sunset' ][ :-6 ]
		twilight_start_utc = parse_to_utc( twilight_start_string, '%Y-%m-%dT%H:%M:%S' )

		self.next_sundown = local_time_today( twilight_start_utc )
		self.scheduler.add_job(
			"Turn on city lights",
			self.set_mode,
			args=[ 'CityAtSundown' ],
			next_run_time=twilight_start_utc
		)

	def schedule_scheduling( self ) -> None:
		self.scheduler.add_job(
			"Schedule Wood Lamp Controller",
			self.schedule_irregular,
			trigger="cron", hour=3, day="*"
		)

	def set_mode( self, mode: str ) -> Tuple[ str, int ]:
		self.current_mode = mode
		response = requests.get( f'http://{self.lamp_ip}/setMode?newMode={mode}' )
		return response.text, response.status_code

	def setup_routes( self, app: Flask ):
		@app.route( '/woodlamp/mode/<string:mode>' )
		def set_mode( mode: str ):
			return self.set_mode( mode )
