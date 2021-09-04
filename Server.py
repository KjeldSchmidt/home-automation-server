from flask import Flask

import MQTTClient
from Alarm import Alarm
from CeilingLights import CeilingLights
from Scheduler import make_scheduler
from Woodlamp import Woodlamp
from IkeaRemote import IkeaRemote

app = Flask( __name__ )
make_scheduler( app )

mqtt_client = MQTTClient.get_client()

woodlamp = Woodlamp( app, ['192.168.178.24', '192.168.178.28', '192.168.178.27' ] )
alarm = Alarm( app, woodlamp )
ceiling = CeilingLights( app, mqtt_client )
controllers = [ woodlamp, alarm, ceiling ]

IkeaRemote(ceiling, woodlamp, mqtt_client)


@app.route( '/' )
def main_page():
	return '<hr />'.join( [ controller.produce_main_page_content() for controller in controllers ] )


if __name__ == '__main__':
	app.run( host='0.0.0.0' )
