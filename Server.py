from flask import Flask

import MQTTClient
from Alarm import Alarm
from CeilingLights import CeilingLights
from IkeaRemote import IkeaRemote
from Scheduler import make_scheduler
from Woodlamp import Woodlamp

app = Flask( __name__ )
make_scheduler( app )

mqtt_client = MQTTClient.get_client()

woodlamp = Woodlamp( app, [ '192.168.178.24', '192.168.178.28', '192.168.178.27' ] )
ceiling = CeilingLights( app, mqtt_client, [ '0x000d6ffffe35eed7' ] )
alarm = Alarm( app, woodlamp, ceiling )
controllers = [ woodlamp, alarm, ceiling ]

IkeaRemote( ceiling, woodlamp, mqtt_client )

style = """
	<style>
		body {
			font-size: 1.5rem;
			max-width: 80%;
			width: 1100px;
			margin: auto;
			padding: 1rem;
		}
		button {
			padding: 0.5rem;
		}
	</style>
	"""


@app.route( '/' )
def main_page():
	content = '<hr />'.join( [ controller.produce_main_page_content() for controller in controllers ] )
	return style + content


if __name__ == '__main__':
	app.run( host='0.0.0.0' )
