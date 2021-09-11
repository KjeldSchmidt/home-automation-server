from typing import Iterable, Union

from flask import Flask

from paho.mqtt.client import Client as MqttClient


class CeilingLights:
	def __init__( self, app: Flask, mqtt_client: MqttClient, lamp_ids: Iterable[ str ] ):
		self.setup_routes( app )
		self.client: MqttClient = mqtt_client
		self.lamp_ids: Iterable[ str ] = lamp_ids

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

	def set_brightness( self, brightness: int ):
		self.send_to_all_lamps( f'{{ "brightness": "{brightness}" }}' )

	def set_color_temperature( self, color_temperature: Union[int, str] ):
		self.send_to_all_lamps( f'{{ "color_temp": "{color_temperature}" }}' )

	def setup_routes( self, app: Flask ):
		@app.route( '/ceiling/brightness/<int:brightness>' )
		def ceiling_lights_brightness( brightness: int ):
			self.set_brightness(brightness)
			return "Ok", 200

		@app.route( '/ceiling/temp/<int:color_temp>' )
		def ceiling_lights_color( color_temp: int ):
			self.set_color_temperature( color_temp )
			return "Ok", 200
