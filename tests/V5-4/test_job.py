"""
tests/V5-4/test_job.py

AutoSearch V5

V5.4 P4.1

Job Model Tests
"""


from datetime import datetime

from models.job import Job


# ==================================================
# Constructor
# ==================================================


def test_default_job():

    job = Job()

    assert job.id is None

    assert job.target_id is None

    assert (
        job.status
        == Job.STATUS_WAITING
    )

    assert (
        job.retry_count
        == 0
    )

    assert isinstance(
        job.created_time,
        datetime,
    )

    assert job.started_time is None

    assert job.finished_time is None

    assert job.error_message == ""


def test_job_with_target():

    job = Job(
        target_id=10,
    )

    assert (
        job.target_id
        == 10
    )

    assert job.is_waiting


# ==================================================
# Status
# ==================================================


def test_waiting_status():

    job = Job(
        target_id=1,
        status=Job.STATUS_WAITING,
    )

    assert job.is_waiting

    assert not job.is_running

    assert not job.is_done

    assert not job.is_failed


def test_running_status():

    job = Job(
        target_id=1,
        status=Job.STATUS_RUNNING,
    )

    assert job.is_running

    assert not job.is_waiting

    assert not job.is_done

    assert not job.is_failed


def test_done_status():

    job = Job(
        target_id=1,
        status=Job.STATUS_DONE,
    )

    assert job.is_done

    assert not job.is_waiting

    assert not job.is_running

    assert not job.is_failed


def test_failed_status():

    job = Job(
        target_id=1,
        status=Job.STATUS_FAILED,
    )

    assert job.is_failed

    assert not job.is_waiting

    assert not job.is_running

    assert not job.is_done


# ==================================================
# Retry
# ==================================================


def test_default_retry_count():

    job = Job(
        target_id=1,
    )

    assert (
        job.retry_count
        == 0
    )


def test_custom_retry_count():

    job = Job(
        target_id=1,
        retry_count=3,
    )

    assert (
        job.retry_count
        == 3
    )


def test_failed_job_can_retry():

    job = Job(
        target_id=1,
        status=Job.STATUS_FAILED,
    )

    assert job.can_retry


def test_waiting_job_cannot_retry():

    job = Job(
        target_id=1,
        status=Job.STATUS_WAITING,
    )

    assert not job.can_retry


def test_running_job_cannot_retry():

    job = Job(
        target_id=1,
        status=Job.STATUS_RUNNING,
    )

    assert not job.can_retry


def test_done_job_cannot_retry():

    job = Job(
        target_id=1,
        status=Job.STATUS_DONE,
    )

    assert not job.can_retry


# ==================================================
# Time
# ==================================================


def test_custom_times():

    created = datetime(
        2026,
        8,
        21,
        10,
        0,
    )

    started = datetime(
        2026,
        8,
        21,
        10,
        1,
    )

    finished = datetime(
        2026,
        8,
        21,
        10,
        2,
    )

    job = Job(
        target_id=1,
        created_time=created,
        started_time=started,
        finished_time=finished,
    )

    assert job.created_time == created

    assert job.started_time == started

    assert job.finished_time == finished


# ==================================================
# Error
# ==================================================


def test_error_message_default():

    job = Job(
        target_id=1,
    )

    assert job.error_message == ""


def test_error_message():

    job = Job(
        target_id=1,
        status=Job.STATUS_FAILED,
        error_message="Crawl failed",
    )

    assert (
        job.error_message
        == "Crawl failed"
    )


# ==================================================
# Dictionary
# ==================================================


def test_to_dict():

    job = Job(
        target_id=10,
        status=Job.STATUS_RUNNING,
        retry_count=2,
        error_message="",
    )

    job.id = 5

    result = job.to_dict()

    assert result["id"] == 5

    assert (
        result["target_id"]
        == 10
    )

    assert (
        result["status"]
        == Job.STATUS_RUNNING
    )

    assert (
        result["retry_count"]
        == 2
    )

    assert result["error_message"] == ""

    assert "finished_time" in result

    assert "error" not in result

    assert "completed_time" not in result


# ==================================================
# Representation
# ==================================================


def test_repr():

    job = Job(
        target_id=10,
        status=Job.STATUS_WAITING,
        retry_count=0,
    )

    job.id = 1

    result = repr(job)

    assert "Job(" in result

    assert "id=1" in result

    assert "target_id=10" in result

    assert "status=WAITING" in result

    assert "retry_count=0" in result
