from _typeshed import Incomplete
from apscheduler.job import Job as Job
from apscheduler.jobstores.base import (
    BaseJobStore as BaseJobStore,
    ConflictingIdError as ConflictingIdError,
    JobLookupError as JobLookupError,
)
from apscheduler.util import (
    datetime_to_utc_timestamp as datetime_to_utc_timestamp,
    maybe_ref as maybe_ref,
    utc_timestamp_to_datetime as utc_timestamp_to_datetime,
)

class RethinkDBJobStore(BaseJobStore):
    database: Incomplete
    table_name: Incomplete
    table: Incomplete
    client: Incomplete
    pickle_protocol: Incomplete
    connect_args: Incomplete
    r: Incomplete
    conn: Incomplete
    def __init__(
        self,
        database: str = "apscheduler",
        table: str = "jobs",
        client: Incomplete | None = None,
        pickle_protocol=...,
        **connect_args
    ) -> None: ...
    def start(self, scheduler, alias) -> None: ...
    def lookup_job(self, job_id): ...
    def get_due_jobs(self, now): ...
    def get_next_run_time(self): ...
    def get_all_jobs(self): ...
    def add_job(self, job) -> None: ...
    def update_job(self, job): ...
    def remove_job(self, job_id) -> None: ...
    def remove_all_jobs(self) -> None: ...
    def shutdown(self) -> None: ...
