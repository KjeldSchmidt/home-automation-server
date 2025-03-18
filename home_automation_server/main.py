import importlib

from flask import Flask

from DeviceGroup.DeviceGroup import DeviceGroup
import env
from MqttHandler import MqttHandler
from Scheduler import make_scheduler

UserConfig = importlib.import_module(f"{env.USER_CONFIG_MODULE}")


app = Flask(__name__)
make_scheduler(app)
mqtt_handler: MqttHandler = MqttHandler()
main_device_group: DeviceGroup = UserConfig.initialize(app, mqtt_handler)


@app.route("/")
def main_page() -> str:
    return main_device_group.get_frontend_html()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
