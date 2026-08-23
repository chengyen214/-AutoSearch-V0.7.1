"""
tests/V5-4/test_job_repository.py

AutoSearch V5

V5.4 P4.2

Job Repository Tests

用途：

    測試：

    - Job Create
    - Job Query
    - Job Update
    - Job Status
    - Job Retry
    - Job Delete
    - Job Count
    - DB Row → Job Model

注意：

    本測試直接使用目前 MySQL
    jobs / targets Table。

    測試完成後會清理
    本測試建立的 Job。
"""


from datetime import datetime

import pytest

from database.connection import get_connection
from database.job_repository import JobRepository
from models.job import Job


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def repository():

    return JobRepository()


@pytest.fixture
def target_id():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT id
            FROM targets
            ORDER BY id ASC
            LIMIT 1
            """
        )

        result = cursor.fetchone()

    finally:

        cursor.close()
        conn.close()

    if result is None:

        pytest.skip(
            "No target exists in targets table."
        )

    return result[0]


@pytest.fixture
def job(
    repository,
    target_id,
):

    job = Job(
        target_id=target_id
    )

    saved = repository.save(
        job
    )

    yield saved

    repository.delete_by_id(
        saved.id
    )


# ==================================================
# Create
# ==================================================


def test_save(
    repository,
    target_id,
):

    job = Job(
        target_id=target_id
    )

    result = repository.save(
        job
    )

    try:

        assert result is job

        assert job.id is not None

        assert (
            job.target_id
            == target_id
        )

        assert (
            job.status
            == Job.STATUS_WAITING
        )

        assert job.retry_count == 0

    finally:

        repository.delete_by_id(
            job.id
        )


def test_insert_alias(
    repository,
    target_id,
):

    job = Job(
        target_id=target_id
    )

    result = repository.insert(
        job
    )

    try:

        assert result is job

        assert job.id is not None

    finally:

        repository.delete_by_id(
            job.id
        )


def test_save_none(
    repository,
):

    with pytest.raises(
        ValueError
    ):

        repository.save(
            None
        )


def test_save_invalid_type(
    repository,
):

    with pytest.raises(
        TypeError
    ):

        repository.save(
            {}
        )


def test_save_without_target(
    repository,
):

    job = Job()

    with pytest.raises(
        ValueError
    ):

        repository.save(
            job
        )


# ==================================================
# Get By ID
# ==================================================


def test_get_by_id(
    repository,
    job,
):

    result = repository.get_by_id(
        job.id
    )

    assert result is not None

    assert isinstance(
        result,
        Job
    )

    assert result.id == job.id

    assert (
        result.target_id
        == job.target_id
    )

    assert (
        result.status
        == Job.STATUS_WAITING
    )


def test_get_by_id_not_found(
    repository,
):

    result = repository.get_by_id(
        999999999
    )

    assert result is None


def test_get_by_id_none(
    repository,
):

    result = repository.get_by_id(
        None
    )

    assert result is None


# ==================================================
# Find All
# ==================================================


def test_find_all(
    repository,
    job,
):

    results = repository.find_all()

    assert isinstance(
        results,
        list
    )

    assert any(
        item.id == job.id
        for item in results
    )


# ==================================================
# Find By Status
# ==================================================


def test_find_waiting(
    repository,
    job,
):

    results = repository.find_waiting()

    assert isinstance(
        results,
        list
    )

    assert all(
        item.status
        == Job.STATUS_WAITING
        for item in results
    )


def test_find_running(
    repository,
    job,
):

    repository.start(
        job.id
    )

    results = repository.find_running()

    assert all(
        item.status
        == Job.STATUS_RUNNING
        for item in results
    )


def test_find_done(
    repository,
    job,
):

    repository.complete(
        job.id
    )

    results = repository.find_done()

    assert all(
        item.status
        == Job.STATUS_DONE
        for item in results
    )


def test_find_failed(
    repository,
    job,
):

    repository.fail(
        job.id,
        "test failure"
    )

    results = repository.find_failed()

    assert all(
        item.status
        == Job.STATUS_FAILED
        for item in results
    )


def test_find_by_status(
    repository,
    job,
):

    results = repository.find_by_status(
        Job.STATUS_WAITING
    )

    assert isinstance(
        results,
        list
    )

    assert all(
        item.status
        == Job.STATUS_WAITING
        for item in results
    )


def test_find_by_status_empty(
    repository,
):

    result = repository.find_by_status(
        ""
    )

    assert result == []


# ==================================================
# Find By Target
# ==================================================


def test_find_by_target_id(
    repository,
    job,
):

    results = repository.find_by_target_id(
        job.target_id
    )

    assert isinstance(
        results,
        list
    )

    assert any(
        item.id == job.id
        for item in results
    )


def test_find_by_target_id_none(
    repository,
):

    result = repository.find_by_target_id(
        None
    )

    assert result == []


def test_find_waiting_by_target(
    repository,
    job,
):

    results = repository.find_waiting_by_target(
        job.target_id
    )

    assert isinstance(
        results,
        list
    )

    assert any(
        item.id == job.id
        for item in results
    )

    assert all(
        item.status
        == Job.STATUS_WAITING
        for item in results
    )


# ==================================================
# Update
# ==================================================


def test_update(
    repository,
    job,
):

    job.status = Job.STATUS_RUNNING

    job.retry_count = 2

    job.started_time = datetime(
        2026,
        8,
        21,
        10,
        1,
    )

    job.error_message = (
        "updated error"
    )

    result = repository.update(
        job
    )

    assert result is True

    updated = repository.get_by_id(
        job.id
    )

    assert updated is not None

    assert (
        updated.status
        == Job.STATUS_RUNNING
    )

    assert updated.retry_count == 2

    assert (
        updated.started_time
        == job.started_time
    )

    assert (
        updated.error_message
        == "updated error"
    )


def test_update_without_id(
    repository,
    target_id,
):

    job = Job(
        target_id=target_id
    )

    with pytest.raises(
        ValueError
    ):

        repository.update(
            job
        )


# ==================================================
# Status
# ==================================================


def test_update_status_running(
    repository,
    job,
):

    result = repository.update_status(
        job.id,
        Job.STATUS_RUNNING,
    )

    assert result is True

    updated = repository.get_by_id(
        job.id
    )

    assert (
        updated.status
        == Job.STATUS_RUNNING
    )

    assert (
        updated.started_time
        is not None
    )


def test_update_status_done(
    repository,
    job,
):

    repository.start(
        job.id
    )

    result = repository.update_status(
        job.id,
        Job.STATUS_DONE,
    )

    assert result is True

    updated = repository.get_by_id(
        job.id
    )

    assert (
        updated.status
        == Job.STATUS_DONE
    )

    assert (
        updated.finished_time
        is not None
    )


def test_update_status_invalid(
    repository,
    job,
):

    assert (
        repository.update_status(
            job.id,
            ""
        )
        is False
    )

    assert (
        repository.update_status(
            None,
            Job.STATUS_RUNNING
        )
        is False
    )


# ==================================================
# Lifecycle
# ==================================================


def test_start(
    repository,
    job,
):

    result = repository.start(
        job.id
    )

    assert result is True

    updated = repository.get_by_id(
        job.id
    )

    assert (
        updated.status
        == Job.STATUS_RUNNING
    )

    assert (
        updated.started_time
        is not None
    )


def test_complete(
    repository,
    job,
):

    result = repository.complete(
        job.id
    )

    assert result is True

    updated = repository.get_by_id(
        job.id
    )

    assert (
        updated.status
        == Job.STATUS_DONE
    )

    assert (
        updated.finished_time
        is not None
    )


def test_fail(
    repository,
    job,
):

    result = repository.fail(
        job.id,
        "Crawl failed",
    )

    assert result is True

    updated = repository.get_by_id(
        job.id
    )

    assert (
        updated.status
        == Job.STATUS_FAILED
    )

    assert (
        updated.retry_count
        == 1
    )

    assert (
        updated.error_message
        == "Crawl failed"
    )


# ==================================================
# Retry
# ==================================================


def test_retry(
    repository,
    job,
):

    repository.fail(
        job.id,
        "temporary failure",
    )

    failed = repository.get_by_id(
        job.id
    )

    assert (
        failed.status
        == Job.STATUS_FAILED
    )

    retry_count = (
        failed.retry_count
    )

    result = repository.retry(
        job.id
    )

    assert result is True

    retried = repository.get_by_id(
        job.id
    )

    assert (
        retried.status
        == Job.STATUS_WAITING
    )

    assert (
        retried.retry_count
        == retry_count
    )

    assert (
        retried.error_message
        == ""
        or retried.error_message is None
    )

    assert (
        retried.started_time
        is None
    )

    assert (
        retried.finished_time
        is None
    )


def test_retry_only_failed(
    repository,
    job,
):

    result = repository.retry(
        job.id
    )

    assert result is False


def test_retry_none(
    repository,
):

    result = repository.retry(
        None
    )

    assert result is False


# ==================================================
# Delete
# ==================================================


def test_delete_by_id(
    repository,
    target_id,
):

    job = Job(
        target_id=target_id
    )

    repository.save(
        job
    )

    job_id = job.id

    result = repository.delete_by_id(
        job_id
    )

    assert result is True

    assert (
        repository.get_by_id(
            job_id
        )
        is None
    )


def test_delete_none(
    repository,
):

    result = repository.delete_by_id(
        None
    )

    assert result is False


# ==================================================
# Exists
# ==================================================


def test_exists(
    repository,
    job,
):

    assert (
        repository.exists(
            job.id
        )
        is True
    )


def test_exists_not_found(
    repository,
):

    assert (
        repository.exists(
            999999999
        )
        is False
    )


def test_exists_none(
    repository,
):

    assert (
        repository.exists(
            None
        )
        is False
    )


# ==================================================
# Count
# ==================================================


def test_count(
    repository,
    job,
):

    result = repository.count()

    assert isinstance(
        result,
        int
    )

    assert result >= 1


def test_count_by_status(
    repository,
    job,
):

    result = repository.count_by_status(
        Job.STATUS_WAITING
    )

    assert isinstance(
        result,
        int
    )

    assert result >= 1


def test_count_by_status_empty(
    repository,
):

    result = repository.count_by_status(
        ""
    )

    assert result == 0


# ==================================================
# DB Row → Job Model
# ==================================================


def test_database_row_mapping(
    repository,
    job,
):

    repository.fail(
        job.id,
        "mapping test"
    )

    result = repository.get_by_id(
        job.id
    )

    assert isinstance(
        result,
        Job
    )

    assert result.id == job.id

    assert (
        result.target_id
        == job.target_id
    )

    assert (
        result.status
        == Job.STATUS_FAILED
    )

    assert result.retry_count == 1

    assert (
        result.error_message
        == "mapping test"
    )


# ==================================================
# Cleanup Safety
# ==================================================


def test_repository_returns_job_model(
    repository,
    job,
):

    results = repository.find_all()

    assert all(
        isinstance(
            item,
            Job
        )
        for item in results
    )
