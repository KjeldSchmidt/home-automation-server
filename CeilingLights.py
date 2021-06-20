from flask import Flask

import MQTTClient


class CeilingLights:
	def __init__( self, app: Flask ):
		self.setup_routes( app )
		self.client = MQTTClient.client

	@staticmethod
	def produce_main_page_content():
		return f"""
			<button onclick="fetch('ceiling/on')">On</button>
			<button onclick="fetch('ceiling/off')">Off</button>
		"""

	def setup_routes( self, app: Flask ):
		@app.route( '/ceiling/on' )
		def ceiling_lights_on():
			self.client.publish(
				topic="zigbee2mqtt/0x680ae2fffe6a2ac5/set",
				payload='{ "state": "ON" }'
			)

		@app.route( '/ceiling/off' )
		def ceiling_lights_off():
			self.client.publish(
				topic="zigbee2mqtt/0x680ae2fffe6a2ac5/set",
				payload='{ "state": "OFF" }'
			)
