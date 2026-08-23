"""
tests/V5-4/test_job_service.py

AutoSearch V5

V5.4 P4.3

Job Service Tests

用途：

    測試：

    - Job Create
    - Job Query
    - Job Status Query
    - Target Job Query
    - Job Start
    - Job Complete
    - Job Fail
    - Job Retry
    - Job Exists
    - Job Count
    - Repository Delegation

注意：

    本測試使用 Mock Repository。

    不直接操作 MySQL。

    JobService 只負責：

        Business Flow

    JobRepository 負責：

        Database Persistence
"""


from datetime import datetime

from models.job import Job
from services.job_service import JobService


# ==================================================
# Mock Repository
# ==================================================


class MockJobRepository:
    """
    Mock JobRepository。

    用於：

        JobService Unit Test

    不連接 MySQL。
    """

    def __init__(self):

        self.jobs = {}

        self.next_id = 1

        self.calls = []

    # ==================================
    # Create
    # ==================================

    def save(self, job):

        self.calls.append(
            (
                "save",
                job,
            )
        )

        job.id = self.next_id

        self.next_id += 1

        self.jobs[job.id] = job

        return job

    # ==================================
    # Get
    # ==================================

    def get_by_id(self, job_id):

        self.calls.append(
            (
                "get_by_id",
                job_id,
            )
        )

        return self.jobs.get(
            job_id
        )

    # ==================================
    # Find All
    # ==================================

    def find_all(self):

        self.calls.append(
            (
                "find_all",
            )
        )

        return list(
            self.jobs.values()
        )

    # ==================================
    # Find By Status
    # ==================================

    def find_by_status(self, status):

        self.calls.append(
            (
                "find_by_status",
                status,
            )
        )

        return [
            job
            for job in self.jobs.values()
            if job.status == status
        ]

    # ==================================
    # Find Waiting
    # ==================================

    def find_waiting(self):

        self.calls.append(
            (
                "find_waiting",
            )
        )

        return self.find_by_status(
            Job.STATUS_WAITING
        )

    # ==================================
    # Find Running
    # ==================================

    def find_running(self):

        self.calls.append(
            (
                "find_running",
            )
        )

        return self.find_by_status(
            Job.STATUS_RUNNING
        )

    # ==================================
    # Find Done
    # ==================================

    def find_done(self):

        self.calls.append(
            (
                "find_done",
            )
        )

        return self.find_by_status(
            Job.STATUS_DONE
        )

    # ==================================
    # Find Failed
    # ==================================

    def find_failed(self):

        self.calls.append(
            (
                "find_failed",
            )
        )

        return self.find_by_status(
            Job.STATUS_FAILED
        )

    # ==================================
    # Find By Target
    # ==================================

    def find_by_target_id(
        self,
        target_id,
    ):

        self.calls.append(
            (
                "find_by_target_id",
                target_id,
            )
        )

        return [
            job
            for job in self.jobs.values()
            if job.target_id == target_id
        ]

    # ==================================
    # Find Waiting By Target
    # ==================================

    def find_waiting_by_target(
        self,
        target_id,
    ):

        self.calls.append(
            (
                "find_waiting_by_target",
                target_id,
            )
        )

        return [
            job
            for job in self.jobs.values()
            if (
                job.target_id == target_id
                and job.status
                == Job.STATUS_WAITING
            )
        ]

    # ==================================
    # Start
    # ==================================

    def start(
        self,
        job_id,
    ):

        self.calls.append(
            (
                "start",
                job_id,
            )
        )

        job = self.jobs.get(
            job_id
        )

        if job is None:
            return False

        job.status = Job.STATUS_RUNNING

        job.started_time = datetime.now()

        return True

    # ==================================
    # Complete
    # ==================================

    def complete(
        self,
        job_id,
    ):

        self.calls.append(
            (
                "complete",
                job_id,
            )
        )

        job = self.jobs.get(
            job_id
        )

        if job is None:
            return False

        job.status = Job.STATUS_DONE

        job.finished_time = datetime.now()

        return True

    # ==================================
    # Fail
    # ==================================

    def fail(
        self,
        job_id,
        error_message="",
    ):

        self.calls.append(
            (
                "fail",
                job_id,
                error_message,
            )
        )

        job = self.jobs.get(
            job_id
        )

        if job is None:
            return False

        job.status = Job.STATUS_FAILED

        job.retry_count += 1

        job.error_message = (
            error_message
        )

        return True

    # ==================================
    # Retry
    # ==================================

    def retry(
        self,
        job_id,
    ):

        self.calls.append(
            (
                "retry",
                job_id,
            )
        )

        job = self.jobs.get(
            job_id
        )

        if job is None:
            return False

        if job.status != Job.STATUS_FAILED:
            return False

        job.status = Job.STATUS_WAITING

        job.error_message = ""

        job.started_time = None

        job.finished_time = None

        return True

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        job_id,
    ):

        self.calls.append(
            (
                "exists",
                job_id,
            )
        )

        return job_id in self.jobs

    # ==================================
    # Count
    # ==================================

    def count(self):

        self.calls.append(
            (
                "count",
            )
        )

        return len(
            self.jobs
        )

    # ==================================
    # Count By Status
    # ==================================

    def count_by_status(
        self,
        status,
    ):

        self.calls.append(
            (
                "count_by_status",
                status,
            )
        )

        return sum(
            1
            for job in self.jobs.values()
            if job.status == status
        )


# ==================================================
# Fixtures
# ==================================================


def create_service():

    repository = MockJobRepository()

    service = JobService(
        repository=repository
    )

    return service, repository


# ==================================================
# Create
# ==================================================


def test_create_job():

    service, repository = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    assert isinstance(
        job,
        Job
    )

    assert job.id == 1

    assert job.target_id == 10

    assert (
        job.status
        == Job.STATUS_WAITING
    )

    assert job.retry_count == 0

    assert (
        repository.calls[0][0]
        == "save"
    )


def test_create_job_none_target():

    service, _ = (
        create_service()
    )

    try:

        service.create_job(
            None
        )

        assert False

    except ValueError:

        assert True


def test_create_alias():

    service, _ = (
        create_service()
    )

    job = service.create(
        target_id=20
    )

    assert isinstance(
        job,
        Job
    )

    assert job.target_id == 20


# ==================================================
# Get
# ==================================================


def test_get_job():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    result = service.get_job(
        job.id
    )

    assert result is job


def test_get_by_id_alias():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    result = service.get_by_id(
        job.id
    )

    assert result is job


def test_get_job_none():

    service, _ = (
        create_service()
    )

    result = service.get_job(
        None
    )

    assert result is None


# ==================================================
# Find All
# ==================================================


def test_find_all():

    service, _ = (
        create_service()
    )

    service.create_job(
        target_id=1
    )

    service.create_job(
        target_id=2
    )

    results = service.find_all()

    assert isinstance(
        results,
        list
    )

    assert len(results) == 2


# ==================================================
# Status Query
# ==================================================


def test_find_waiting():

    service, _ = (
        create_service()
    )

    service.create_job(
        target_id=1
    )

    results = service.find_waiting()

    assert len(results) == 1

    assert (
        results[0].status
        == Job.STATUS_WAITING
    )


def test_find_running():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=1
    )

    service.start_job(
        job.id
    )

    results = service.find_running()

    assert len(results) == 1

    assert (
        results[0].status
        == Job.STATUS_RUNNING
    )


def test_find_done():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=1
    )

    service.complete_job(
        job.id
    )

    results = service.find_done()

    assert len(results) == 1

    assert (
        results[0].status
        == Job.STATUS_DONE
    )


def test_find_failed():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=1
    )

    service.fail_job(
        job.id,
        "test failure"
    )

    results = service.find_failed()

    assert len(results) == 1

    assert (
        results[0].status
        == Job.STATUS_FAILED
    )


# ==================================================
# Target Query
# ==================================================


def test_find_by_target():

    service, _ = (
        create_service()
    )

    job1 = service.create_job(
        target_id=10
    )

    job2 = service.create_job(
        target_id=10
    )

    service.create_job(
        target_id=20
    )

    results = service.find_by_target(
        10
    )

    assert len(results) == 2

    assert job1 in results

    assert job2 in results


def test_find_by_target_none():

    service, _ = (
        create_service()
    )

    result = service.find_by_target(
        None
    )

    assert result == []


def test_find_waiting_by_target():

    service, _ = (
        create_service()
    )

    waiting_job = service.create_job(
        target_id=10
    )

    running_job = service.create_job(
        target_id=10
    )

    service.start_job(
        running_job.id
    )

    results = (
        service.find_waiting_by_target(
            10
        )
    )

    assert len(results) == 1

    assert (
        results[0].id
        == waiting_job.id
    )

    assert (
        results[0].status
        == Job.STATUS_WAITING
    )


def test_find_waiting_by_target_none():

    service, _ = (
        create_service()
    )

    result = (
        service.find_waiting_by_target(
            None
        )
    )

    assert result == []


# ==================================================
# Start
# ==================================================


def test_start_job():

    service, repository = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    result = service.start_job(
        job.id
    )

    assert result is True

    assert job.status == (
        Job.STATUS_RUNNING
    )

    assert (
        job.started_time
        is not None
    )

    assert (
        repository.calls[-1][0]
        == "start"
    )


def test_start_job_none():

    service, _ = (
        create_service()
    )

    result = service.start_job(
        None
    )

    assert result is False


# ==================================================
# Complete
# ==================================================


def test_complete_job():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    service.start_job(
        job.id
    )

    result = service.complete_job(
        job.id
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_DONE
    )

    assert (
        job.finished_time
        is not None
    )


def test_complete_job_none():

    service, _ = (
        create_service()
    )

    result = service.complete_job(
        None
    )

    assert result is False


# ==================================================
# Fail
# ==================================================


def test_fail_job():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    result = service.fail_job(
        job.id,
        "Crawl failed"
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_FAILED
    )

    assert job.retry_count == 1

    assert (
        job.error_message
        == "Crawl failed"
    )


def test_fail_job_none():

    service, _ = (
        create_service()
    )

    result = service.fail_job(
        None,
        "error"
    )

    assert result is False


# ==================================================
# Retry
# ==================================================


def test_retry_job():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    service.fail_job(
        job.id,
        "temporary failure"
    )

    retry_count = (
        job.retry_count
    )

    result = service.retry_job(
        job.id
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_WAITING
    )

    assert (
        job.retry_count
        == retry_count
    )

    assert (
        job.error_message
        == ""
    )

    assert (
        job.started_time
        is None
    )

    assert (
        job.finished_time
        is None
    )


def test_retry_waiting_job_rejected():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    result = service.retry_job(
        job.id
    )

    assert result is False


def test_retry_running_job_rejected():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    service.start_job(
        job.id
    )

    result = service.retry_job(
        job.id
    )

    assert result is False


def test_retry_done_job_rejected():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    service.complete_job(
        job.id
    )

    result = service.retry_job(
        job.id
    )

    assert result is False


def test_retry_not_found():

    service, _ = (
        create_service()
    )

    result = service.retry_job(
        999999
    )

    assert result is False


def test_retry_none():

    service, _ = (
        create_service()
    )

    result = service.retry_job(
        None
    )

    assert result is False


# ==================================================
# Exists
# ==================================================


def test_exists():

    service, _ = (
        create_service()
    )

    job = service.create_job(
        target_id=10
    )

    assert (
        service.exists(
            job.id
        )
        is True
    )


def test_exists_not_found():

    service, _ = (
        create_service()
    )

    assert (
        service.exists(
            999999
        )
        is False
    )


def test_exists_none():

    service, _ = (
        create_service()
    )

    assert (
        service.exists(
            None
        )
        is False
    )


# ==================================================
# Count
# ==================================================


def test_count():

    service, _ = (
        create_service()
    )

    service.create_job(
        target_id=1
    )

    service.create_job(
        target_id=2
    )

    assert (
        service.count()
        == 2
    )


def test_count_by_status():

    service, _ = (
        create_service()
    )

    job1 = service.create_job(
        target_id=1
    )

    job2 = service.create_job(
        target_id=2
    )

    service.start_job(
        job2.id
    )

    assert (
        service.count_by_status(
            Job.STATUS_WAITING
        )
        == 1
    )

    assert (
        service.count_by_status(
            Job.STATUS_RUNNING
        )
        == 1
    )

    assert job1.status == (
        Job.STATUS_WAITING
    )


def test_count_by_status_empty():

    service, _ = (
        create_service()
    )

    assert (
        service.count_by_status(
            ""
        )
        == 0
    )


# ==================================================
# Full Lifecycle
# ==================================================


def test_full_job_lifecycle():

    service, _ = (
        create_service()
    )

    # Target → Job

    job = service.create_job(
        target_id=100
    )

    assert (
        job.status
        == Job.STATUS_WAITING
    )

    # WAITING → RUNNING

    assert service.start_job(
        job.id
    )

    assert (
        job.status
        == Job.STATUS_RUNNING
    )

    assert (
        job.started_time
        is not None
    )

    # RUNNING → DONE

    assert service.complete_job(
        job.id
    )

    assert (
        job.status
        == Job.STATUS_DONE
    )

    assert (
        job.finished_time
        is not None
    )


def test_failed_retry_lifecycle():

    service, _ = (
        create_service()
    )

    # Target → Job

    job = service.create_job(
        target_id=100
    )

    assert (
        job.status
        == Job.STATUS_WAITING
    )

    # WAITING → RUNNING

    service.start_job(
        job.id
    )

    assert (
        job.status
        == Job.STATUS_RUNNING
    )

    # RUNNING → FAILED

    service.fail_job(
        job.id,
        "temporary failure"
    )

    assert (
        job.status
        == Job.STATUS_FAILED
    )

    assert (
        job.retry_count
        == 1
    )

    assert (
        job.error_message
        == "temporary failure"
    )

    # FAILED → WAITING

    assert service.retry_job(
        job.id
    )

    assert (
        job.status
        == Job.STATUS_WAITING
    )

    assert (
        job.retry_count
        == 1
    )

    assert (
        job.error_message
        == ""
    )


# ==================================================
# Repository Delegation
# ==================================================


def test_service_uses_injected_repository():

    service, repository = (
        create_service()
    )

    assert (
        service.repository
        is repository
    )


def test_create_job_delegates_to_repository():

    service, repository = (
        create_service()
    )

    service.create_job(
        target_id=50
    )

    assert (
        repository.calls[0][0]
        == "save"
    )


def test_start_job_delegates_to_repository():

    service, repository = (
        create_service()
    )

    job = service.create_job(
        target_id=50
    )

    service.start_job(
        job.id
    )

    assert (
        repository.calls[-1]
        == (
            "start",
            job.id,
        )
    )


def test_complete_job_delegates_to_repository():

    service, repository = (
        create_service()
    )

    job = service.create_job(
        target_id=50
    )

    service.complete_job(
        job.id
    )

    assert (
        repository.calls[-1]
        == (
            "complete",
            job.id,
        )
    )


def test_fail_job_delegates_to_repository():

    service, repository = (
        create_service()
    )

    job = service.create_job(
        target_id=50
    )

    service.fail_job(
        job.id,
        "test error"
    )

    assert (
        repository.calls[-1]
        == (
            "fail",
            job.id,
            "test error",
        )
    )


def test_retry_job_delegates_to_repository():

    service, repository = (
        create_service()
    )

    job = service.create_job(
        target_id=50
    )

    service.fail_job(
        job.id,
        "temporary error"
    )

    service.retry_job(
        job.id
    )

    assert (
        repository.calls[-1]
        == (
            "retry",
            job.id,
        )
    )
