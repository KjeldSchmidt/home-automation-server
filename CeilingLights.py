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
			<button onclick="fetch('ceiling/dim')">Dim</button>
			<button onclick="fetch('ceiling/off')">Off</button>
		"""

	def setup_routes( self, app: Flask ):
		@app.route( '/ceiling/on' )
		def ceiling_lights_on():
			self.client.publish(
				topic="zigbee2mqtt/0x680ae2fffe6a2ac5/set",
				payload='{ "brightness": "254" }'
			)
			self.client.publish(
				topic="zigbee2mqtt/0xbc33acfffe59a606/set",
				payload='{ "brightness": "254" }'
			)

		@app.route( '/ceiling/off' )
		def ceiling_lights_off():
			self.client.publish(
				topic="zigbee2mqtt/0x680ae2fffe6a2ac5/set",
				payload='{ "brightness": "0" }'
			)
			self.client.publish(
				topic="zigbee2mqtt/0xbc33acfffe59a606/set",
				payload='{ "brightness": "0" }'
			)

		@app.route( '/ceiling/dim' )
		def ceiling_lights_dim():
			self.client.publish(
				topic="zigbee2mqtt/0x680ae2fffe6a2ac5/set",
				payload='{ "brightness": "127" }'
			)
			self.client.publish(
				topic="zigbee2mqtt/0xbc33acfffe59a606/set",
				payload='{ "brightness": "127" }'
			)
