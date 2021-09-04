from datetime import datetime
from datetime import datetime
from typing import Tuple, List

import requests
from flask import Flask

from Scheduler import Scheduler
from TimeFunctions import local_time_today


class Woodlamp:
	def __init__( self, app: Flask, scheduler: Scheduler, lamp_ip: List[str] ):
		self.scheduler: Scheduler = scheduler
		self.lamp_ips = lamp_ip
		self.next_sundown: datetime = None
		self.available_modes: List[ str ] = [ ]

		self.setup( app )

	def setup( self, app: Flask ):
		self.setup_routes( app )
		self.fetch_available_modes()

	def produce_main_page_content( self ):
		def make_link( mode ):
			return f'<button onclick="fetch(\'/woodlamp/mode/{mode}\')">{mode}</a>'

		mode_links = [ make_link( mode ) for mode in self.available_modes ]
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
		response = requests.get( f'http://{self.lamp_ips[0 ]}/getModes' )
		mode_names = response.text.split( ',' )
		mode_names = [ mode.strip() for mode in mode_names ]
		self.available_modes = mode_names

	def set_mode( self, mode: str ) -> Tuple[ str, int ]:
		response = None
		for lamp_ip in self.lamp_ips:
			response = requests.get( f'http://{lamp_ip}/setMode?newMode={mode}' )
		if response is None:
			return "No IPs", 500
		return response.text, response.status_code

	def setup_routes( self, app: Flask ):
		@app.route( '/woodlamp/mode/<string:mode>' )
		def set_mode( mode: str ):
			return self.set_mode( mode )
