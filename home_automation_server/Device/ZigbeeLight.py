from enum import Enum

from flask import Flask, render_template

from MqttHandler import MqttHandler
from Device.Device import Device


class ZigbeeLight(Device):
    def __init__(self, app: Flask, name: str, lamp_ids: list[str], mqtt_handler: MqttHandler):
        self.mqtt_handler = mqtt_handler
        self.name = name
        self.lamp_ids = lamp_ids
        self.state: LampState = LampState.OFF

        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route(
            f"/zigbee_light/{self.name}/brightness/<int:brightness>",
            endpoint=f"brightness_{self.name}",
        )
        def zigbee_lights_brightness(brightness: int):
            self.set_brightness_all(brightness)
            return "Ok", 200

        @app.route(
            f"/zigbee_light/{self.name}/temp/<int:color_temp>",
            endpoint=f"color_{self.name}",
        )
        def zigbee_lights_color(color_temp: int):
            self.set_color_temp_all(color_temp)
            return "Ok", 200

        @app.route(f"/zigbee_light/{self.name}/toggle", endpoint=f"toggle_{self.name}")
        def zigbee_lights_toggle():
            self.toggle()
            return "Ok", 200

    def send_to_all_lamps(self, payload):
        for lamp_id in self.lamp_ids:
            self.mqtt_handler.publish(topic=f"zigbee2mqtt/{lamp_id}/set", payload=payload)

    def set_brightness_all(self, brightness: int):
        self.state = LampState.get_closest(brightness)
        self.send_to_all_lamps(f'{{ "brightness": "{brightness}" }}')

    def set_color_temp_all(self, color_temp: int):
        self.send_to_all_lamps(f'{{ "color_temp": "{color_temp}" }}')

    def toggle(self):
        self.state = self.state.next()
        self.set_brightness_all(self.state.value)

    def turn_off_all(self):
        self.set_brightness_all(0)

    def turn_on_all(self):
        self.set_brightness_all(127)

    def get_frontend_html(self):
        return render_template("zigbee_light.html", lamp_name=self.name)


class LampState(Enum):
    ON = 255
    HALF = 127
    OFF = 0

    def next(self) -> "LampState":
        return {
            LampState.ON: LampState.HALF,
            LampState.HALF: LampState.OFF,
            LampState.OFF: LampState.ON,
        }[self]

    @staticmethod
    def get_closest(brightness: int) -> "LampState":
        if brightness == 0:
            return LampState.OFF
        if brightness < 159:
            return LampState.HALF
        else:
            return LampState.ON
