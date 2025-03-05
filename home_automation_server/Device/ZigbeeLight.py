from enum import Enum

from flask import Flask, render_template

from home_automation_server.MqttHandler import MqttHandler
from home_automation_server.Device.Device import Device


class ZigbeeLight(Device):
    def __init__(self, app: Flask, name: str, lamp_ids: list[str], mqtt_handler: MqttHandler):
        self.mqtt_handler = mqtt_handler
        self.name = name
        self.lamp_ids = lamp_ids
        self.state: LampState = LampState.OFF

        self._setup_routes(app)

    def _setup_routes(self, app: Flask) -> None:
        @app.route(
            f"/zigbee_light/{self.name}/brightness/<int:brightness>",
            endpoint=f"brightness_{self.name}",
        )
        def zigbee_lights_brightness(brightness: int) -> tuple[str, int]:
            self.set_brightness_all(brightness)
            return "Ok", 200

        @app.route(
            f"/zigbee_light/{self.name}/temp/<int:color_temp>",
            endpoint=f"color_{self.name}",
        )
        def zigbee_lights_color(color_temp: int) -> tuple[str, int]:
            self.set_color_temp_all(color_temp)
            return "Ok", 200

        @app.route(f"/zigbee_light/{self.name}/toggle", endpoint=f"toggle_{self.name}")
        def zigbee_lights_toggle() -> tuple[str, int]:
            self.toggle()
            return "Ok", 200

    def send_to_all_lamps(self, payload: str) -> None:
        for lamp_id in self.lamp_ids:
            self.mqtt_handler.publish(topic=f"zigbee2mqtt/{lamp_id}/set", payload=payload)

    def set_brightness_all(self, brightness: int) -> None:
        self.state = LampState.get_closest(brightness)
        self.send_to_all_lamps(f'{{ "brightness": "{brightness}" }}')

    def set_color_temp_all(self, color_temp: int) -> None:
        self.send_to_all_lamps(f'{{ "color_temp": "{color_temp}" }}')

    def toggle(self) -> None:
        self.state = self.state.next()
        self.set_brightness_all(self.state.value)

    def turn_off_all(self) -> None:
        self.set_brightness_all(0)

    def turn_on_all(self) -> None:
        self.set_brightness_all(127)

    def get_frontend_html(self) -> str:
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
