import importlib

from flask import Flask

from home_automation_server.DeviceGroup.DeviceGroup import DeviceGroup
from home_automation_server import env
from home_automation_server.MqttHandler import MqttHandler
from home_automation_server.Scheduler import make_scheduler

UserConfig = importlib.import_module(f"home_automation_server.{env.USER_CONFIG_MODULE}")


app = Flask(__name__)
make_scheduler(app)
mqtt_handler: MqttHandler = MqttHandler()
main_device_group: DeviceGroup = UserConfig.initialize(app, mqtt_handler)


@app.route("/")
def main_page() -> str:
    return main_device_group.get_frontend_html()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
