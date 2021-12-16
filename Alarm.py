import os
import pickle
from datetime import datetime, timedelta
from typing import Tuple, Dict, Union

from flask import Flask, request, redirect
from flask_apscheduler import APScheduler

import Scheduler
from CeilingLights import CeilingLights
from TimeFunctions import get_next_valid_time, local_time_today
from Woodlamp import Woodlamp


def load_config():
	filename = 'alarm_config.pickle'
	if not os.path.isfile( filename ):
		with open( filename, 'wb' ) as file:
			pickle.dump(
				{
					"morning_lights_id": None,
					"morning_lights_off_id": None,
					"evening_lights_id": None,
					"night_lights_id": None,
				},
				file
			)

	return pickle.load( open( filename, 'rb' ) )


class Alarm:
	def __init__( self, app: Flask, woodlamp: Woodlamp, ceiling_lights: CeilingLights ):
		self.scheduler: APScheduler = Scheduler.scheduler
		self.woodlamp = woodlamp
		self.ceiling_lights = ceiling_lights
		self.config: Dict[ str, Union[ None, Tuple[ datetime, str, int, int ] ] ] = load_config()
		self.schedule_lights()
		self.setup_routes( app )

	def produce_main_page_content( self ):
		morning_value = ""
		if self.config.get( "morning_lights_id" ) is not None:
			morning: datetime = self.config[ "morning_lights_id" ][ 0 ]
			morning_value = local_time_today( morning )

		evening_value = ""
		if self.config.get( "evening_lights_id" ) is not None:
			evening: datetime = self.config[ "evening_lights_id" ][ 0 ]
			evening_value = local_time_today( evening )

		night_value = ""
		if self.config.get( "night_lights_id" ) is not None:
			night: datetime = self.config[ "night_lights_id" ][ 0 ]
			night_value = local_time_today( night )

		return f'''
			<form class="alarm-form" method="post" action="/morning">
				<input type="time" name="time" value="{morning_value}" />
				<input type="submit" value="Set Morning Light Time" />
				<input type="button" value="Delete Morning Light Time" onclick="fetch('/morning', {{method: 'DELETE'}})" />
			</form>
			<form class="alarm-form" method="post" action="/evening">
				<input type="time" name="time" value="{evening_value}" />
				<input type="submit" value="Set Evening Light Time" />
				<input type="button" value="Delete Evening Light Time" onclick="fetch('/evening', {{method: 'DELETE'}})" />
			</form>
			<form class="alarm-form" method="post" action="/night">
				<input type="time" name="time" value="{night_value}" />
				<input type="submit" value="Set Night Light Time" />
				<input type="button" value="Delete Night Light Time" onclick="fetch('/night', {{method: 'DELETE'}})" />
			</form>
		'''

	def reset_jobs( self ):
		for job_id, value in self.config.items():
			if self.scheduler.get_job( job_id ) is None:
				continue

			self.scheduler.remove_job( job_id )

	def perform_alarm( self, mode: str, brightness: int, color_temp: int ) -> None:
		self.woodlamp.set_mode( mode )
		self.ceiling_lights.set_brightness( brightness )
		self.ceiling_lights.set_color_temperature( color_temp )

	def schedule_lights( self ):

		for job_id, value in self.config.items():
			if value is None:
				continue
			time, mode, brightness, color_temp = value

			self.scheduler.add_job(
				job_id,
				self.perform_alarm,
				args=[ mode, brightness, color_temp ],
				trigger="cron", hour=time.hour, minute=time.minute, day="*"
			)

	def save_config( self ):
		filename = 'alarm_config.pickle'
		pickle.dump( self.config, open( filename, 'wb' ) )

	def setup_routes( self, app ):
		def post_handler( key: str, mode: str, brightness: int, color_temp: int = 350 ):
			alarm_time = get_next_valid_time( request.form[ 'time' ] )
			self.config[ key ] = (alarm_time, mode, brightness, color_temp)

			if key == "morning_lights_id":
				off_time = alarm_time + timedelta( hours = 1)
				self.config[ "morning_lights_off_id" ] = (off_time, "LightsOut", 0, color_temp)

			self.reset_jobs()
			self.save_config()
			self.schedule_lights()
			return redirect( "/" )

		def delete_handler( key: str ):
			self.config[ key ] = None

			if key == "morning_lights_id":
				self.config[ "morning_lights_off_id" ] = None

			self.reset_jobs()
			self.schedule_lights()
			self.save_config()
			return redirect( "/" )

		@app.route( '/morning', methods=[ 'POST' ] )
		def set_morning_alarm():
			return post_handler( "morning_lights_id", "WakeUp", 255, 250 )

		@app.route( '/evening', methods=[ 'POST' ] )
		def set_evening_alarm():
			return post_handler( "evening_lights_id", "CityAtSundown", 100, 254 )

		@app.route( '/night', methods=[ 'POST' ] )
		def set_night_alarm():
			return post_handler( "night_lights_id", "LightsOut", 0 )

		@app.route( '/morning', methods=[ 'DELETE' ] )
		def remove_morning_alarm():
			return delete_handler( "morning_lights_id" )

		@app.route( '/evening', methods=[ 'DELETE' ] )
		def remove_evening_alarm():
			return delete_handler( "evening_lights_id" )

		@app.route( '/night', methods=[ 'DELETE' ] )
		def remove_night_alarm():
			return delete_handler( "night_lights_id" )
