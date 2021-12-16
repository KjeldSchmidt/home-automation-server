from threading import Thread
from typing import List

import requests
from flask import Flask
from flask_apscheduler import APScheduler

from Scheduler import scheduler


class Woodlamp:
	def __init__( self, app: Flask, lamp_ips: List[ str ] ):
		self.scheduler: APScheduler = scheduler
		self.lamp_ips = lamp_ips
		self.available_modes: List[ str ] = [ ]

		self.setup( app )

	def setup( self, app: Flask ):
		self.setup_routes( app )
		self.fetch_available_modes()

	def produce_main_page_content( self ):
		def make_link( mode ):
			return f'<button onclick="fetch(\'/woodlamp/mode/{mode}\')">{mode}</a>'

		mode_links = [ make_link( mode ) for mode in self.available_modes[ :-1 ] ]
		modes_block = f'<div class="modes_block"> {"<br />".join( mode_links )} </div>'
		color_wheel_block = self.make_color_wheel_block()

		return f"""
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

	def fetch_available_modes( self ) -> None:
		self.available_modes = ["CityAtSundown", "GlobalColorTick", "LightsOut", "WakeUp", "Pacifica", "ColorPulse", "DiscoStrobo"]

	def set_mode( self, mode: str ):
		def set_individual_mode( ip ):
			requests.get( f'http://{ip}/setMode?newMode={mode}' )

		for lamp_ip in self.lamp_ips:
			Thread( target=set_individual_mode, args=(lamp_ip,) ).start()

	def setup_routes( self, app: Flask ):
		@app.route( '/woodlamp/mode/<string:mode>' )
		def set_mode( mode: str ):
			self.set_mode( mode )
			return 'Ok', 200
