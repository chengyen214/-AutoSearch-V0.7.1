"""
tests/V5-5/test_batch_target_service.py

AutoSearch V5

V5.5
P5.5.2

Batch Target Retrieval Service Tests

用途：

    測試：

    - Job → Target
    - target_id → Target
    - Repository Injection
    - None Handling
    - Invalid Job Handling
    - Target Not Found
    - Alias API

注意：

    本測試使用 Mock Repository，
    不直接操作 MySQL。

    P5.5.2 不負責：

    - Job Execution
    - Batch Execution
    - Search
    - Crawler
    - Parser
    - Archive
    - AI
"""


from unittest.mock import Mock

import pytest

from models.job import Job
from services.batch_target_service import (
    BatchTargetService,
)


# ==================================================
# Fake Target
# ==================================================


class FakeTarget:
    """
    P5.5.2 測試用 Target。

    只需要確認 Repository 回傳的
    Target 是否被 Service 正確傳遞。
    """

    def __init__(
        self,
        target_id,
    ):

        self.id = target_id


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def target_repository():

    repository = Mock()

    return repository


@pytest.fixture
def service(
    target_repository,
):

    return BatchTargetService(
        target_repository=target_repository
    )


@pytest.fixture
def target():

    return FakeTarget(
        target_id=10
    )


@pytest.fixture
def job():

    return Job(
        target_id=10
    )


# ==================================================
# Constructor
# ==================================================


def test_service_uses_injected_repository(
    target_repository,
):

    service = BatchTargetService(
        target_repository=target_repository
    )

    assert (
        service.target_repository
        is target_repository
    )


def test_service_creates_default_repository():

    service = BatchTargetService()

    assert (
        service.target_repository
        is not None
    )


# ==================================================
# Get Target By ID
# ==================================================


def test_get_target_by_id(
    service,
    target_repository,
    target,
):

    target_repository.get_by_id.return_value = (
        target
    )

    result = service.get_target_by_id(
        10
    )

    assert result is target

    target_repository.get_by_id.assert_called_once_with(
        10
    )


def test_get_target_by_id_not_found(
    service,
    target_repository,
):

    target_repository.get_by_id.return_value = None

    result = service.get_target_by_id(
        999999
    )

    assert result is None

    target_repository.get_by_id.assert_called_once_with(
        999999
    )


def test_get_target_by_id_none(
    service,
    target_repository,
):

    result = service.get_target_by_id(
        None
    )

    assert result is None

    target_repository.get_by_id.assert_not_called()


# ==================================================
# Get Target For Job
# ==================================================


def test_get_target_for_job(
    service,
    target_repository,
    job,
    target,
):

    target_repository.get_by_id.return_value = (
        target
    )

    result = service.get_target_for_job(
        job
    )

    assert result is target

    target_repository.get_by_id.assert_called_once_with(
        job.target_id
    )


def test_get_target_for_job_none(
    service,
    target_repository,
):

    result = service.get_target_for_job(
        None
    )

    assert result is None

    target_repository.get_by_id.assert_not_called()


def test_get_target_for_job_without_target_id(
    service,
    target_repository,
):

    job = Job(
        target_id=None
    )

    result = service.get_target_for_job(
        job
    )

    assert result is None

    target_repository.get_by_id.assert_not_called()


def test_get_target_for_job_target_not_found(
    service,
    target_repository,
):

    job = Job(
        target_id=999999
    )

    target_repository.get_by_id.return_value = None

    result = service.get_target_for_job(
        job
    )

    assert result is None

    target_repository.get_by_id.assert_called_once_with(
        999999
    )


# ==================================================
# Invalid Job
# ==================================================


def test_get_target_for_job_invalid_type(
    service,
):

    with pytest.raises(
        TypeError
    ):

        service.get_target_for_job(
            {}
        )


def test_get_target_for_job_invalid_list(
    service,
):

    with pytest.raises(
        TypeError
    ):

        service.get_target_for_job(
            []
        )


# ==================================================
# Alias
# ==================================================


def test_get_target_alias(
    service,
    target_repository,
    job,
    target,
):

    target_repository.get_by_id.return_value = (
        target
    )

    result = service.get_target(
        job
    )

    assert result is target

    target_repository.get_by_id.assert_called_once_with(
        job.target_id
    )


# ==================================================
# Repository Delegation
# ==================================================


def test_get_target_for_job_delegates_to_repository(
    service,
    target_repository,
):

    job = Job(
        target_id=25
    )

    expected_target = FakeTarget(
        target_id=25
    )

    target_repository.get_by_id.return_value = (
        expected_target
    )

    result = service.get_target_for_job(
        job
    )

    assert result is expected_target

    target_repository.get_by_id.assert_called_once_with(
        25
    )


def test_get_target_by_id_delegates_to_repository(
    service,
    target_repository,
):

    expected_target = FakeTarget(
        target_id=50
    )

    target_repository.get_by_id.return_value = (
        expected_target
    )

    result = service.get_target_by_id(
        50
    )

    assert result is expected_target

    target_repository.get_by_id.assert_called_once_with(
        50
    )


# ==================================================
# No Execution
# ==================================================


def test_target_retrieval_does_not_execute_job(
    service,
    target_repository,
    job,
    target,
):

    target_repository.get_by_id.return_value = (
        target
    )

    result = service.get_target_for_job(
        job
    )

    assert result is target

    assert job.status == Job.STATUS_WAITING

    assert job.started_time is None

    assert job.finished_time is None


def test_target_retrieval_does_not_modify_job(
    service,
    target_repository,
    job,
    target,
):

    original_target_id = job.target_id
    original_status = job.status
    original_retry_count = job.retry_count

    target_repository.get_by_id.return_value = (
        target
    )

    service.get_target_for_job(
        job
    )

    assert (
        job.target_id
        == original_target_id
    )

    assert (
        job.status
        == original_status
    )

    assert (
        job.retry_count
        == original_retry_count
    )


# ==================================================
# Repository Result Passthrough
# ==================================================


def test_repository_result_is_returned_unchanged(
    service,
    target_repository,
    job,
):

    target = Mock()

    target_repository.get_by_id.return_value = (
        target
    )

    result = service.get_target_for_job(
        job
    )

    assert result is target


# ==================================================
# Public API
# ==================================================


def test_public_api():

    from services.batch_target_service import (
        __all__,
    )

    assert (
        "BatchTargetService"
        in __all__
    )