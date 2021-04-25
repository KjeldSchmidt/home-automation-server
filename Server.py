from flask import Flask

from Scheduler import Scheduler
from TimeFunctions import local_time_today
from WoodLampController import WoodLampController

app = Flask( __name__ )
scheduler = Scheduler( app )
wood_lamp_controller = WoodLampController( scheduler, '192.168.178.26', app )


@app.route( '/' )
def main_page():
	if wood_lamp_controller.next_sundown is None:
		return 'The sun shall never vanish again. Cover before her glory, for she will scorch the earth'
	else:
		return 'Today\'s Sunset will be at ' + local_time_today( wood_lamp_controller.next_sundown )


if __name__ == '__main__':
	app.run( host='0.0.0.0' )
