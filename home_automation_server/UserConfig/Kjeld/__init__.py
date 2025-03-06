from flask import Flask

from home_automation_server.MqttHandler import MqttHandler
from .DeviceConfig import DeviceConfig
from home_automation_server.Device.GlobalState import GlobalState
from home_automation_server.Alarm import Alarm
from home_automation_server.Device.ZigbeeLight import ZigbeeLight
from .ControllerCollection import ControllerCollection
from home_automation_server.Device.Spotify import Spotify
from home_automation_server.Device.EspNeopixelLight import EspNeopixelLight


def initialize(app: Flask, mqtt_handler: MqttHandler) -> ControllerCollection:
    global_state = GlobalState(app)

    esp_neopixel_lights = {
        name: EspNeopixelLight(app, name, ip, global_state) for name, ip in DeviceConfig.esp_neopixel_lights.items()
    }

    alarm = Alarm(app, lambda: esp_neopixel_lights["bedLamp"].set_mode("WakeUp"))
    zigbee_lights = {
        name: ZigbeeLight(app, name, lamp_ids, mqtt_handler) for name, lamp_ids in DeviceConfig.zigbee_lights.items()
    }
    spotify = Spotify(app)

    main_device_group = ControllerCollection(
        app, "kjeld", alarm, zigbee_lights, esp_neopixel_lights, global_state, spotify
    )
    return main_device_group
