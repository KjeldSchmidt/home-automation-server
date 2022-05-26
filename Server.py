from flask import Flask

import MqttClient
from Alarm import Alarm
from CeilingLights import CeilingLightsCollection
from Scheduler import make_scheduler
from Woodlamp import Woodlamp

app = Flask( __name__ )
make_scheduler( app )

mqtt_client: MqttClient.Client = MqttClient.get_client()

woodlamp = Woodlamp( app, '192.168.178.26' )
alarm = Alarm( app, woodlamp )

ceiling = CeilingLightsCollection(
	{
		"living room": [
			"0x2c1165fffe9552aa",
			"0x2c1165fffe97a7ca",
			"0x2c1165fffe8a6188",
			"0x50325ffffeaef44e",
			"0x2c1165fffe8f6498",
			"0x2c1165fffe954329"
		],
		"hall": [
			"0x680ae2fffe6a2ac5",
			"0xbc33acfffe59a606"
		],
		"bedroom": [
			"0x2c1165fffe875fb7",
			"0x50325ffffed2342b",
			"0x50325ffffebf9de2",
			"0x2c1165fffe2cb9bb",
			"0x50325ffffebc506f",
			"0x2c1165fffe8fa481"
		]
	},
	app,
	mqtt_client
)

controllers = [ woodlamp, alarm, ceiling ]


@app.route( '/' )
def main_page():
	return '<hr />'.join( [ controller.produce_main_page_content() for controller in controllers ] )


if __name__ == '__main__':
	app.run( host='0.0.0.0' )
