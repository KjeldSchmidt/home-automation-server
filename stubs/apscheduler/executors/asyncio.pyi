from apscheduler.executors.base import (
    BaseExecutor as BaseExecutor,
    run_coroutine_job as run_coroutine_job,
    run_job as run_job,
)
from apscheduler.util import iscoroutinefunction_partial as iscoroutinefunction_partial

class AsyncIOExecutor(BaseExecutor):
    def start(self, scheduler, alias) -> None: ...
    def shutdown(self, wait: bool = True) -> None: ...
