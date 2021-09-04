import json

from paho.mqtt.client import Client as MqttClient

from CeilingLights import CeilingLights
from Woodlamp import Woodlamp


class IkeaRemote:
	def __init__(self, ceiling_lights, led_lamps, mqtt_client: MqttClient):
		self.ceiling_lights: CeilingLights = ceiling_lights
		self.led_lamps: Woodlamp = led_lamps
		self.mqtt_client: MqttClient = mqtt_client

		self.mqtt_client.on_message = self.on_message()

		self.lights_on: bool = False

	def toggle( self ):
		if self.lights_on:
			self.ceiling_lights.send_to_all_lamps( f'{{ "brightness": "254" }}' )
			self.led_lamps.set_mode('CityAtSundown')
			self.lights_on = False
		else:
			self.ceiling_lights.send_to_all_lamps( f'{{ "brightness": "0" }}' )
			self.led_lamps.set_mode('LightsOut')
			self.lights_on = True

	def on_message( self ):
		def on_message( client, userdata, msg ):
			payload: str = msg.payload.decode()
			if payload == "online":
				return

			payload_dict = json.loads( payload )
			if 'action' not in payload_dict:
				return

			if payload_dict['action'] == "toggle":
				self.toggle()

		return on_message


