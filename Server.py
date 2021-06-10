from flask import Flask

from Alarm import Alarm
from Scheduler import make_scheduler
from Woodlamp import Woodlamp

app = Flask( __name__ )
scheduler = make_scheduler( app )

woodlamp = Woodlamp( app, scheduler, '192.168.178.26' )
alarm = Alarm( scheduler, app, woodlamp )

controllers = [ woodlamp, alarm ]


@app.route( '/' )
def main_page():
	return '<hr />'.join( [ controller.produce_main_page_content() for controller in controllers ] )


if __name__ == '__main__':
	app.run( host='0.0.0.0' )
