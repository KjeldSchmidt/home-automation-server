from flask import Flask

from Scheduler import Scheduler
from WoodLampController import WoodLampController

app = Flask( __name__ )
scheduler = Scheduler( app )
wood_lamp_controller = WoodLampController( scheduler, '192.168.178.26', app )


@app.route( '/' )
def main_page():
	return wood_lamp_controller.produce_main_page_content()


if __name__ == '__main__':
	app.run( host='0.0.0.0' )
