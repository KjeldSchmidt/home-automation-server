from apscheduler.schedulers.base import BaseScheduler as BaseScheduler
from apscheduler.util import maybe_ref as maybe_ref

def run_in_event_loop(func): ...

class AsyncIOScheduler(BaseScheduler):
    def start(self, paused: bool = False) -> None: ...
    def shutdown(self, wait: bool = True) -> None: ...
    def wakeup(self) -> None: ...
