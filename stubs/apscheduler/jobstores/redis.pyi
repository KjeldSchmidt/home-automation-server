from _typeshed import Incomplete
from apscheduler.job import Job as Job
from apscheduler.jobstores.base import (
    BaseJobStore as BaseJobStore,
    ConflictingIdError as ConflictingIdError,
    JobLookupError as JobLookupError,
)
from apscheduler.util import (
    datetime_to_utc_timestamp as datetime_to_utc_timestamp,
    utc_timestamp_to_datetime as utc_timestamp_to_datetime,
)

class RedisJobStore(BaseJobStore):
    pickle_protocol: Incomplete
    jobs_key: Incomplete
    run_times_key: Incomplete
    redis: Incomplete
    def __init__(
        self,
        db: int = 0,
        jobs_key: str = "apscheduler.jobs",
        run_times_key: str = "apscheduler.run_times",
        pickle_protocol=...,
        **connect_args
    ) -> None: ...
    def lookup_job(self, job_id): ...
    def get_due_jobs(self, now): ...
    def get_next_run_time(self): ...
    def get_all_jobs(self): ...
    def add_job(self, job) -> None: ...
    def update_job(self, job) -> None: ...
    def remove_job(self, job_id) -> None: ...
    def remove_all_jobs(self) -> None: ...
    def shutdown(self) -> None: ...
