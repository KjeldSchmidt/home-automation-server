from Alarm import Alarm
from CeilingLights import CeilingLightsCollection
from Presets.Preset import Preset
from Woodlamp import WoodlampCollection


class ControllerCollection:
    def __init__(self, alarm: Alarm, ceiling_lights: CeilingLightsCollection, woodlamps: WoodlampCollection):
        self.controllers = [woodlamps, alarm, ceiling_lights]
        self.alarm = alarm
        self.ceiling_lights = ceiling_lights
        self.woodlamps = woodlamps

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

        for name, woodlamp_handler in preset.woodlamp_handlers.items():
            lights = self.woodlamps.lights[name]
            woodlamp_handler(lights)
