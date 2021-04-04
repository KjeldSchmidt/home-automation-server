from flask_apscheduler import APScheduler


class Scheduler:
	def __init__( self, app ):
		self._scheduler = APScheduler()
		self._scheduler.api_enabled = True
		self._scheduler.init_app( app )
		self._scheduler.start()

	def add_job( self, job_id, func, **kwargs ):
		"""
		Add the given job to the job list and wakes up the scheduler if it's already running.

		:param str job_id: explicit identifier for the job (for modifying it later)
		:param func: callable (or a textual reference to one) to run at the given time
		"""
		return self._scheduler.add_job( job_id, func, **kwargs )
