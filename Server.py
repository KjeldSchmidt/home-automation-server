from flask import Flask
from datetime import datetime
from Scheduler import Scheduler
import requests
import json

app = Flask( __name__ )
scheduler = Scheduler(app)


@app.route( '/' )
def main_page():
	r = requests.get('https://api.sunrise-sunset.org/json?lat=51&lng=7&formatted=0')
	times = json.loads(r.text)['results']
	twilight_start_string = times['nautical_twilight_end'][:-6]
	twilight_start_time = datetime.strptime(twilight_start_string, '%Y-%m-%dT%H:%M:%S')
	time_display_string = str(twilight_start_time.hour) + ':' + str(twilight_start_time.minute)
	return 'Today\'s Sunset will be at ' + time_display_string


if __name__ == '__main__':
	app.run(host='0.0.0.0')
