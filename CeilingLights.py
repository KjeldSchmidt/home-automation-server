import json
import time
from threading import Thread

from flask import Flask

import MqttClient
from Woodlamp import Woodlamp


class CeilingLights:
	def __init__( self, app: Flask, mqtt_client: MqttClient.Client, woodlamp: Woodlamp ):
		self.setup_routes( app )
		self.mqtt_client = mqtt_client
		self.mqtt_client.on_message = self.on_message()
		self.lamp_ids = [
			'0x680ae2fffe6a2ac5',
			'0xbc33acfffe59a606',
		]
		self.woodlamp = woodlamp
		self.light_mode_to_restore = None

		self.poll_thread = Thread( target=self.ping_lamps )
		self.poll_thread.start()

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
			self.mqtt_client.publish(
				topic=f"zigbee2mqtt/{lamp_id}/set",
				payload=payload
			)

	def setup_routes( self, app: Flask ):
		@app.route( '/ceiling/brightness/<int:brightness>' )
		def ceiling_lights_brightness( brightness: int ):
			self.send_to_all_lamps( f'{{ "brightness": "{brightness}" }}' )
			self.ping_lamps()
			return "Ok", 200

		@app.route( '/ceiling/temp/<int:color_temp>' )
		def ceiling_lights_color( color_temp: int ):
			self.send_to_all_lamps( f'{{ "color_temp": "{color_temp}" }}' )
			return "Ok", 200

	def ping_lamps( self ):
		while True:
			mid = self.mqtt_client.publish(
				topic=f"zigbee2mqtt/{self.lamp_ids[ 0 ]}/get",
				payload='{ "brightness": "" }'
			)

			time.sleep( 5 )

	def on_message( self ):
		def on_message( client, userdata, msg ):
			payload: str = msg.payload.decode()
			payload_dict = json.loads( payload )

			match payload_dict:
				case { 'level': 'error', 'message': message, **rest }:
					if self.lamp_ids[ 0 ] in message:
						self.light_mode_to_restore = self.woodlamp.current_mode
						self.woodlamp.set_mode( 'LightsOut' )
				case { 'message': 'announce', 'meta': { 'friendly_name': friendly_name }, 'type': 'device_announced' }:
					if friendly_name == self.lamp_ids[ 0 ]:
						self.woodlamp.set_mode( self.light_mode_to_restore )
						self.light_mode_to_restore = None

		return on_message
