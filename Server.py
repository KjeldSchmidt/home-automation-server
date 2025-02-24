from flask import Flask, render_template

from Controller.GlobalState import GlobalState
from MqttHandler import MqttHandler
from Controller.Alarm import Alarm
from Controller.CeilingLights import CeilingLightsCollection
from Controller.ControllerCollection import ControllerCollection
from Remote import IkeaRemote
from Scheduler import make_scheduler
from Controller.Spotify import Spotify
from Controller.Woodlamp import WoodlampCollection
from Devices import Devices

app = Flask(__name__)
make_scheduler(app)
mqtt_handler: MqttHandler = MqttHandler()

global_state = GlobalState(app)
woodlamps = WoodlampCollection(Devices.woodlamps, app, global_state)
alarm = Alarm(app, woodlamps.lights["bedLamp"])
ceiling = CeilingLightsCollection(Devices.ceiling_lamps, app, mqtt_handler)
spotify = Spotify(app)

controllers = ControllerCollection(alarm, ceiling, woodlamps, global_state, spotify)
remote = IkeaRemote(controllers, mqtt_handler)


@app.route("/")
def main_page():
    return render_template("index.html", controllers=controllers)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
