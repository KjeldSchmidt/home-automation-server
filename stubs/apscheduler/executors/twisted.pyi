from apscheduler.executors.base import BaseExecutor as BaseExecutor, run_job as run_job

class TwistedExecutor(BaseExecutor):
    def start(self, scheduler, alias) -> None: ...
