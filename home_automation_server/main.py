import importlib

from flask import Flask, render_template

import env
from Device.GlobalState import GlobalState
from MqttHandler import MqttHandler
from Alarm import Alarm
from Device.ZigbeeLight import ZigbeeLight
from Device.ControllerCollection import ControllerCollection
from Remote import IkeaRemote
from Scheduler import make_scheduler
from Device.Spotify import Spotify
from Device.EspNeopixelLight import EspNeopixelLight

DeviceGroup = importlib.import_module(env.DEVICE_GROUP_MODULE)


app = Flask(__name__)
make_scheduler(app)
mqtt_handler: MqttHandler = MqttHandler()

global_state = GlobalState(app)

esp_neopixel_lights = {
    name: EspNeopixelLight(app, name, ip, global_state) for name, ip in DeviceGroup.Devices.esp_neopixel_lights.items()
}

alarm = Alarm(app, esp_neopixel_lights["bedLamp"])
zigbee_lights = {
    name: ZigbeeLight(app, name, lamp_ids, mqtt_handler) for name, lamp_ids in DeviceGroup.Devices.zigbee_lights.items()
}
spotify = Spotify(app)


controllers = ControllerCollection(alarm, zigbee_lights, esp_neopixel_lights, global_state, spotify)
remote = IkeaRemote(controllers, mqtt_handler)


@app.route("/")
def main_page():
    return render_template("index.html", controllers=controllers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
