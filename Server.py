from flask import Flask

import MqttClient
from Alarm import Alarm
from CeilingLights import CeilingLights
from Scheduler import make_scheduler
from Woodlamp import Woodlamp

app = Flask( __name__ )
make_scheduler( app )

mqtt_client: MqttClient.Client = MqttClient.get_client()

woodlamp = Woodlamp( app, '192.168.178.26' )
alarm = Alarm( app, woodlamp )
ceiling = CeilingLights( app, mqtt_client, woodlamp )

controllers = [ woodlamp, alarm, ceiling ]


@app.route( '/' )
def main_page():
	return '<hr />'.join( [ controller.produce_main_page_content() for controller in controllers ] )


if __name__ == '__main__':
	app.run( host='0.0.0.0' )
