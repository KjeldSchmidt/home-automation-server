from typing_extensions import Self

from flask import Flask, render_template

from Device.Device import Device
from Alarm import Alarm
from Device.ZigbeeLight import ZigbeeLight
from Device.GlobalState import GlobalState
from Device.Spotify import Spotify
from Device.EspNeopixelLight import EspNeopixelLight
from Presets.Preset import Preset
from DeviceGroup.DeviceGroup import DeviceGroup
from main import mqtt_handler


class KjeldApartment(DeviceGroup):
    def __init__(
        self,
        app: Flask,
        name: str,
        alarm: Alarm,
        zigbee_lights: dict[str, ZigbeeLight],
        esp_neopixel_lights: dict[str, EspNeopixelLight],
        global_state: GlobalState,
        spotify: Spotify,
    ):
        self.controllers: list[Device] = [
            *esp_neopixel_lights.values(),
            *zigbee_lights.values(),
            global_state,
            spotify,
        ]

        self.gui_elements = [
            *esp_neopixel_lights.values(),
            alarm,
            *zigbee_lights.values(),
            global_state,
            spotify,
        ]

        super().__init__(app, name, self.controllers, self.gui_elements)
        self.alarm = alarm
        self.zigbee_lights = zigbee_lights
        self.esp_neopixel_lights = esp_neopixel_lights
        self.global_state = global_state

        self.configure_lights_to_be_full_brightness_when_they_connect()

    def configure_lights_to_be_full_brightness_when_they_connect(self):
        def turn_on_newly_connected_ceiling_lights(client, userdata, payload):
            connected_device = payload["data"]["friendly_name"]
            if not payload["type"] == "device_announce":
                return

            if "ceiling" in connected_device:
                self.zigbee_lights[connected_device].set_brightness_all(255)

        mqtt_handler.add_message_handler(turn_on_newly_connected_ceiling_lights, "zigbee2mqtt/bridge/event")

    def turn_off_all(self: Self) -> None:
        for controller in self.controllers:
            controller.turn_off_all()

    def turn_on_all(self: Self) -> None:
        for controller in self.controllers:
            controller.turn_on_all()

    def apply_preset(self: Self, preset: Preset) -> None:
        self.turn_off_all()
        for name, zigbee_light_handler in preset.zigbee_light_handlers.items():
            zigbee_lights = self.zigbee_lights[name]
            zigbee_light_handler(zigbee_lights)

        for (
            name,
            esp_neopixel_light_handler,
        ) in preset.esp_neopixel_light_handlers.items():
            esp_lights = self.esp_neopixel_lights[name]
            esp_neopixel_light_handler(esp_lights)

    def get_frontend_html(self: Self) -> str:
        return render_template("index.html", gui_elements=self.gui_elements)
