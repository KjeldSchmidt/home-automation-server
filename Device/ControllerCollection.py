from Alarm import Alarm
from Device.CeilingLights import CeilingLightsCollection
from Device.GlobalState import GlobalState
from Device.Spotify import Spotify
from Device.EspNeopixelLight import EspNeopixelLight
from Presets.Preset import Preset


class ControllerCollection:
    def __init__(
        self,
        alarm: Alarm,
        ceiling_lights: CeilingLightsCollection,
        esp_neopixel_lights: dict[EspNeopixelLight],
        global_state: GlobalState,
        spotify: Spotify,
    ):
        self.controllers = [*esp_neopixel_lights.values(), alarm, ceiling_lights, global_state, spotify]
        self.alarm = alarm
        self.ceiling_lights = ceiling_lights
        self.esp_neopixel_lights = esp_neopixel_lights
        self.global_state = global_state

    def __iter__(self):
        return self.controllers.__iter__()

    def turn_off_all(self):
        for controller in self.controllers:
            controller.turn_off_all()

    def turn_on_all(self):
        for controller in self.controllers:
            controller.turn_on_all()

    def apply_preset(self, preset: Preset):
        self.turn_off_all()
        for name, ceiling_handler in preset.ceiling_handlers.items():
            lights = self.ceiling_lights.lights[name]
            ceiling_handler(lights)

        for name, esp_neopixel_light_handler in preset.esp_neopixel_light_handlers.items():
            lights = self.esp_neopixel_lights[name]
            esp_neopixel_light_handler(lights)
