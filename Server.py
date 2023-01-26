from flask import Flask, render_template

from MqttClient import MqttClient
from Alarm import Alarm
from CeilingLights import CeilingLightsCollection
from ControllerCollection import ControllerCollection
from Remote import IkeaRemote
from Scheduler import make_scheduler
from Spotify import Spotify
from Woodlamp import WoodlampCollection
from Devices import Devices

app = Flask(__name__)
make_scheduler(app)
mqtt_client: MqttClient = MqttClient()

woodlamps = WoodlampCollection(Devices.woodlamps, app)
alarm = Alarm(app, woodlamps.lights["bedLamp"])
ceiling = CeilingLightsCollection(Devices.ceiling_lamps, app, mqtt_client)
spotify = Spotify(app)

controllers = ControllerCollection(alarm, ceiling, woodlamps)
remote = IkeaRemote(controllers, mqtt_client)


@app.route("/")
def main_page():
    return render_template("index.html", controllers=controllers)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
