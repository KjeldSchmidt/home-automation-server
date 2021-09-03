from flask import Flask

import MQTTClient


class CeilingLights:
	def __init__( self, app: Flask ):
		self.setup_routes( app )
		self.client = MQTTClient.client
		self.lamp_ids = [
			'0x680ae2fffe6a2ac5',
			'0xbc33acfffe59a606',
		]

	@staticmethod
	def produce_main_page_content():
		return """
			<details>
				<summary>
					<button onclick="fetch('ceiling/brightness/254')">On</button>
					<button onclick="fetch('ceiling/brightness/127')">Dim</button>
					<button onclick="fetch('ceiling/brightness/0')">Off</button>
				</summary> 
				<br /><input type=range min=250 max=454 onchange="fetch(`ceiling/temp/${this.value}`)" />
				<br /><input type=range min=0 max=254 onchange="fetch(`ceiling/brightness/${this.value}`)" />
			</details>
		"""

	def send_to_all_lamps( self, payload ):
		for lamp_id in self.lamp_ids:
			self.client.publish(
				topic=f"zigbee2mqtt/{lamp_id}/set",
				payload=payload
			)

	def setup_routes( self, app: Flask ):
		@app.route( '/ceiling/brightness/<int:brightness>' )
		def ceiling_lights_brightness( brightness: int ):
			self.send_to_all_lamps( f'{{ "brightness": "{brightness}" }}' )
			return "Ok", 200

		@app.route( '/ceiling/temp/<int:color_temp>' )
		def ceiling_lights_color( color_temp: int ):
			self.send_to_all_lamps( f'{{ "color_temp": "{color_temp}" }}' )
			return "Ok", 200
