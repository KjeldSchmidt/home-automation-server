import json

from paho.mqtt.client import Client as MqttClient

from CeilingLights import CeilingLights
from Woodlamp import Woodlamp
from util.ToggleList import ToggleList


class IkeaRemote:
	def __init__(self, ceiling_lights, led_lamps, mqtt_client: MqttClient):
		self.ceiling_lights: CeilingLights = ceiling_lights
		self.led_lamps: Woodlamp = led_lamps
		self.mqtt_client: MqttClient = mqtt_client
		self.mqtt_client.on_message = self.on_message()
		self.color_temperatures = ToggleList(["coolest", "neutral", "warmest"])
		self.brightness_increments = ToggleList([1, 128, 192, 254])

		self.lights_on: bool = False

	def toggle( self ):
		if self.lights_on:
			self.ceiling_lights.set_brightness( 254 )
			self.led_lamps.set_mode('CityAtSundown')
			self.lights_on = False
		else:
			self.ceiling_lights.set_brightness( 0 )
			self.led_lamps.set_mode('LightsOut')
			self.lights_on = True

	def next_temperature( self ):
		self.ceiling_lights.set_color_temperature( self.color_temperatures.next() )

	def next_brightness_increment( self ):
		self.ceiling_lights.set_brightness( self.brightness_increments.next() )

	def on_message( self ):
		def on_message( client, userdata, msg ):
			payload: str = msg.payload.decode()
			if payload == "online":
				return

			payload_dict = json.loads( payload )
			if 'action' not in payload_dict:
				return

			action = payload_dict[ 'action' ]
			action_map = {
				"toggle": self.toggle,
				"arrow_left_click": None,
				"arrow_right_click": self.next_temperature,
				"brightness_down_click": None,
				"brightness_up_click": self.next_brightness_increment,
			}

			action_callback = action_map.get(action)
			if action_callback is None:
				print(f"{action} is not mapped")
			else:
				action_callback()

		return on_message


