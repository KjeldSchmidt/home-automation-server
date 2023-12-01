from enum import Enum, auto

from flask import Flask, render_template

from MqttClient import MqttClient
from Controller import Controller


class CeilingLightsCollection(Controller):
    def __init__(
        self,
        lamp_config: dict[str, list[str]],
        app: Flask,
        mqtt_client: MqttClient,
    ):
        self.lights = {}
        for name, lamp_ids in lamp_config.items():
            self.lights[name] = CeilingLights(name, lamp_ids, mqtt_client)

        self.setup_routes(app)

    def setup_routes(self, app: Flask):
        @app.route(f"/ceiling/<string:name>/brightness/<int:brightness>")
        def ceiling_lights_brightness(name: str, brightness: int):
            self.lights[name].set_brightness_all(brightness)
            return "Ok", 200

        @app.route(f"/ceiling/<string:name>/temp/<int:color_temp>")
        def ceiling_lights_color(name: str, color_temp: int):
            self.lights[name].set_color_temp_all(color_temp)
            return "Ok", 200

        @app.route(f"/ceiling/<string:name>/toggle")
        def ceiling_lights_toggle(name: str):
            self.lights[name].toggle()
            return "Ok", 200

    def produce_main_page_content(self):
        return render_template("ceiling_lights.html", lamps=self.lights)

    def turn_off_all(self):
        for light in self.lights.values():
            light.set_brightness_all(0)

    def turn_on_all(self):
        for light in self.lights.values():
            light.set_brightness_all(127)


class LampState(Enum):
    ON = auto()
    HALF = auto()
    OFF = auto()

    def next(self):
        return {
            LampState.ON: LampState.HALF,
            LampState.HALF: LampState.OFF,
            LampState.OFF: LampState.ON,
        }[self]


class CeilingLights:
    def __init__(self, name: str, lamp_ids: list[str], mqtt_client: MqttClient):
        self.mqtt_client = mqtt_client
        self.name = name
        self.lamp_ids = lamp_ids
        self.state: LampState = LampState.OFF

    def send_to_all_lamps(self, payload):
        for lamp_id in self.lamp_ids:
            self.mqtt_client.publish(
                topic=f"zigbee2mqtt/{lamp_id}/set", payload=payload
            )

    def set_brightness_all(self, brightness: int):
        self.send_to_all_lamps(f'{{ "brightness": "{brightness}" }}')

    def set_color_temp_all(self, color_temp: int):
        self.send_to_all_lamps(f'{{ "color_temp": "{color_temp}" }}')

    def toggle(self):
        self.state = self.state.next()
        brightness_map = {
            LampState.ON: 255,
            LampState.HALF: 127,
            LampState.OFF: 0,
        }
        self.set_brightness_all(brightness_map[self.state])
