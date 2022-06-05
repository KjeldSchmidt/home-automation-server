from flask import Flask

import MqttClient
from Alarm import Alarm
from CeilingLights import CeilingLightsCollection
from ControllerCollection import ControllerCollection
from Remote import IkeaRemote
from Scheduler import make_scheduler
from Woodlamp import WoodlampCollection
from Devices import Devices

app = Flask(__name__)
make_scheduler(app)
mqtt_client: MqttClient.Client = MqttClient.get_client()

woodlamps = WoodlampCollection(Devices.woodlamps, app)
alarm = Alarm(app, woodlamps.lights["bedLamp"])
ceiling = CeilingLightsCollection(Devices.ceiling_lamps, app, mqtt_client)

controllers = ControllerCollection([woodlamps, alarm, ceiling])
remote = IkeaRemote(controllers, mqtt_client)


@app.route("/")
def main_page():
    return controllers.produce_main_page_content()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
