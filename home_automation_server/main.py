import importlib

from flask import Flask, render_template

from home_automation_server import env
from home_automation_server.MqttHandler import MqttHandler
from home_automation_server.Scheduler import make_scheduler

UserConfig = importlib.import_module(f"home_automation_server.{env.USER_CONFIG_MODULE}")


app = Flask(__name__)
make_scheduler(app)
mqtt_handler: MqttHandler = MqttHandler()
controllers = UserConfig.initialize(app, mqtt_handler)


@app.route("/")
def main_page():
    return render_template("index.html", controllers=controllers)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
