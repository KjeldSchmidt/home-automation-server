import json

from MqttHandler import MqttHandler

from Device.ControllerCollection import ControllerCollection
from util.ToggleList import ToggleList
from Presets import Preset


class IkeaRemote:
    def __init__(
        self,
        controllers: ControllerCollection,
        mqtt_handler: MqttHandler,
    ):
        self.controllers: ControllerCollection = controllers
        self.mqtt_handler: MqttHandler = mqtt_handler
        self.mqtt_handler.add_message_handler(self.on_message())
        self.color_temperatures = ToggleList(["coolest", "neutral", "warmest"])
        self.brightness_increments = ToggleList([1, 64, 128, 192, 254])
        self.system_state = ToggleList([True, False])
        self.presets = ToggleList(
            [
                Preset.Daylight,
                Preset.EveningChillAlone,
                Preset.EveningChillFriends,
                Preset.Darkness,
            ]
        )

        self.lights_on: bool = False

    def toggle_system_on_off(self):
        if self.system_state.next():
            self.controllers.turn_off_all()
        else:
            self.controllers.turn_on_all()

    def toggle_preset(self):
        self.controllers.apply_preset(self.presets.next())

    def on_message(self):
        def on_message(client, userdata, msg):
            payload: str = msg.payload.decode()
            if payload == "online":
                return

            payload_dict = json.loads(payload)
            if "action" not in payload_dict:
                return

            action = payload_dict["action"]
            action_map = {
                "toggle": self.toggle_preset,
                "toggle_hold": self.toggle_system_on_off,
                "arrow_left_click": None,
                "arrow_right_click": None,
                "brightness_down_click": None,
                "brightness_up_click": None,
            }

            action_callback = action_map.get(action)
            if action_callback is None:
                print(f"{action} is not mapped")
            else:
                action_callback()

        return on_message
