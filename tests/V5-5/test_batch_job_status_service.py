"""
tests/V5-5/test_batch_job_status_service.py

AutoSearch V5

V5.5
P5.5.4

Batch Job Status Service Tests

測試：

    - Repository Injection
    - Job Retrieval
    - Job Status Query
    - Job Start
    - Job Complete
    - Job Fail
    - Status Helpers
    - Lifecycle Aliases
    - None Handling
    - Repository Delegation
"""


import pytest

from models.job import Job
from services.batch_job_status_service import (
    BatchJobStatusService,
)
from database.job_repository import JobRepository

# ==================================================
# Fake Repository
# ==================================================


class FakeJobRepository:
    """
    測試用 Fake Repository。

    不連接 MySQL。
    """

    def __init__(self):

        self.jobs = {}

        self.calls = []

    # ----------------------------------
    # Get
    # ----------------------------------

    def get_by_id(
        self,
        job_id,
    ):

        self.calls.append(
            (
                "get_by_id",
                job_id,
            )
        )

        return self.jobs.get(
            job_id
        )

    # ----------------------------------
    # Start
    # ----------------------------------

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

        job.status = (
            Job.STATUS_RUNNING
        )

        return True

    # ----------------------------------
    # Complete
    # ----------------------------------

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

        job.status = (
            Job.STATUS_DONE
        )

        return True

    # ----------------------------------
    # Fail
    # ----------------------------------

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

        job.status = (
            Job.STATUS_FAILED
        )

        job.retry_count += 1

        job.error_message = (
            error_message
        )

        return True


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def repository():

    return FakeJobRepository()


@pytest.fixture
def service(
    repository,
):

    return BatchJobStatusService(
        job_repository=repository
    )


@pytest.fixture
def job(
    repository,
):

    job = Job(
        target_id=1
    )

    job.id = 100

    repository.jobs[
        job.id
    ] = job

    return job


# ==================================================
# Constructor
# ==================================================


def test_service_uses_injected_repository(
    repository,
):

    service = BatchJobStatusService(
        job_repository=repository
    )

    assert (
        service.job_repository
        is repository
    )


def test_service_creates_default_repository():
    
    service = BatchJobStatusService()

    assert isinstance(
        service.job_repository,
        JobRepository,
    )


# ==================================================
# Get Job
# ==================================================


def test_get_job(
    service,
    job,
):

    result = service.get_job(
        job.id
    )

    assert result is job


def test_get_job_not_found(
    service,
):

    result = service.get_job(
        999999
    )

    assert result is None


def test_get_job_none(
    service,
):

    result = service.get_job(
        None
    )

    assert result is None


# ==================================================
# Get Status
# ==================================================


def test_get_status_waiting(
    service,
    job,
):

    result = service.get_status(
        job.id
    )

    assert (
        result
        == Job.STATUS_WAITING
    )


def test_get_status_not_found(
    service,
):

    result = service.get_status(
        999999
    )

    assert result is None


def test_get_status_none(
    service,
):

    result = service.get_status(
        None
    )

    assert result is None


# ==================================================
# Start
# ==================================================


def test_start_job(
    service,
    job,
):

    result = service.start_job(
        job.id
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_RUNNING
    )


def test_start_job_none(
    service,
):

    result = service.start_job(
        None
    )

    assert result is False


def test_start_alias(
    service,
    job,
):

    result = service.start(
        job.id
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_RUNNING
    )


# ==================================================
# Complete
# ==================================================


def test_complete_job(
    service,
    job,
):

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


def test_complete_job_none(
    service,
):

    result = service.complete_job(
        None
    )

    assert result is False


def test_complete_alias(
    service,
    job,
):

    result = service.complete(
        job.id
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_DONE
    )


# ==================================================
# Fail
# ==================================================


def test_fail_job(
    service,
    job,
):

    result = service.fail_job(
        job.id,
        "Crawl failed",
    )

    assert result is True

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
        == "Crawl failed"
    )


def test_fail_job_default_error(
    service,
    job,
):

    result = service.fail_job(
        job.id
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_FAILED
    )

    assert (
        job.error_message
        == ""
    )


def test_fail_job_none(
    service,
):

    result = service.fail_job(
        None,
        "error",
    )

    assert result is False


def test_fail_alias(
    service,
    job,
):

    result = service.fail(
        job.id,
        "alias error",
    )

    assert result is True

    assert (
        job.status
        == Job.STATUS_FAILED
    )

    assert (
        job.error_message
        == "alias error"
    )


# ==================================================
# Status Helpers
# ==================================================


def test_is_waiting(
    service,
    job,
):

    assert service.is_waiting(
        job.id
    )

    assert not service.is_running(
        job.id
    )

    assert not service.is_done(
        job.id
    )

    assert not service.is_failed(
        job.id
    )


def test_is_running(
    service,
    job,
):

    service.start_job(
        job.id
    )

    assert service.is_running(
        job.id
    )

    assert not service.is_waiting(
        job.id
    )

    assert not service.is_done(
        job.id
    )

    assert not service.is_failed(
        job.id
    )


def test_is_done(
    service,
    job,
):

    service.complete_job(
        job.id
    )

    assert service.is_done(
        job.id
    )

    assert not service.is_waiting(
        job.id
    )

    assert not service.is_running(
        job.id
    )

    assert not service.is_failed(
        job.id
    )


def test_is_failed(
    service,
    job,
):

    service.fail_job(
        job.id,
        "failure",
    )

    assert service.is_failed(
        job.id
    )

    assert not service.is_waiting(
        job.id
    )

    assert not service.is_running(
        job.id
    )

    assert not service.is_done(
        job.id
    )


# ==================================================
# Status Helpers - None
# ==================================================


def test_status_helpers_none(
    service,
):

    assert not service.is_waiting(
        None
    )

    assert not service.is_running(
        None
    )

    assert not service.is_done(
        None
    )

    assert not service.is_failed(
        None
    )


# ==================================================
# Status Helpers - Not Found
# ==================================================


def test_status_helpers_not_found(
    service,
):

    job_id = 999999

    assert not service.is_waiting(
        job_id
    )

    assert not service.is_running(
        job_id
    )

    assert not service.is_done(
        job_id
    )

    assert not service.is_failed(
        job_id
    )


# ==================================================
# Repository Delegation
# ==================================================


def test_get_job_delegates_to_repository(
    service,
    repository,
    job,
):

    service.get_job(
        job.id
    )

    assert (
        repository.calls[-1]
        == (
            "get_by_id",
            job.id,
        )
    )


def test_start_job_delegates_to_repository(
    service,
    repository,
    job,
):

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


def test_complete_job_delegates_to_repository(
    service,
    repository,
    job,
):

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


def test_fail_job_delegates_to_repository(
    service,
    repository,
    job,
):

    service.fail_job(
        job.id,
        "test error",
    )

    assert (
        repository.calls[-1]
        == (
            "fail",
            job.id,
            "test error",
        )
    )


# ==================================================
# Lifecycle
# ==================================================


def test_full_job_lifecycle(
    service,
    job,
):

    # WAITING
    assert service.is_waiting(
        job.id
    )

    # WAITING → RUNNING
    assert service.start_job(
        job.id
    )

    assert service.is_running(
        job.id
    )

    # RUNNING → DONE
    assert service.complete_job(
        job.id
    )

    assert service.is_done(
        job.id
    )


def test_failed_job_lifecycle(
    service,
    job,
):

    # WAITING
    assert service.is_waiting(
        job.id
    )

    # WAITING → RUNNING
    assert service.start_job(
        job.id
    )

    assert service.is_running(
        job.id
    )

    # RUNNING → FAILED
    assert service.fail_job(
        job.id,
        "crawl failed",
    )

    assert service.is_failed(
        job.id
    )

    assert (
        job.retry_count
        == 1
    )


# ==================================================
# No Execution Responsibility
# ==================================================


def test_status_service_does_not_execute_job(
    service,
    repository,
    job,
):

    service.start_job(
        job.id
    )

    service.complete_job(
        job.id
    )

    # Status Service 只能呼叫
    # JobRepository。
    #
    # 不應該出現：
    #
    # crawler
    # parser
    # search
    # archive
    # ai

    method_names = [
        call[0]
        for call in repository.calls
    ]

    assert all(
        method in {
            "get_by_id",
            "start",
            "complete",
            "fail",
        }
        for method in method_names
    )


# ==================================================
# Public API
# ==================================================


def test_public_api():

    from services.batch_job_status_service import (
        __all__,
    )

    assert (
        "BatchJobStatusService"
        in __all__
    )