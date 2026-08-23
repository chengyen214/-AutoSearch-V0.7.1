"""
tests/V5-5/test_batch_job_service.py

AutoSearch V5

V5.5
P5.5.3

Batch Job Retrieval Service Tests

測試：

    - Repository Injection
    - Default Repository
    - WAITING Job Retrieval
    - Batch Size Limit
    - Empty Jobs
    - Batch Size = 1
    - Batch Size > Waiting Jobs
    - Job Order Preservation
    - No Job Modification
    - Alias
    - Waiting Job Count
    - Public API
"""


from config.batch_config import BatchConfig
from models.job import Job
from services.batch_job_service import (
    BatchJobService,
)


# ==================================================
# Fake Repository
# ==================================================


class FakeJobRepository:
    """
    P5.5.3 測試用 Repository。

    不連接 MySQL。
    """

    def __init__(
        self,
        jobs=None,
    ):

        self.jobs = (
            jobs
            if jobs is not None
            else []
        )

        self.find_waiting_called = 0

        self.count_by_status_called = 0

        self.last_count_status = None

    def find_waiting(self):

        self.find_waiting_called += 1

        return list(
            self.jobs
        )

    def count_by_status(
        self,
        status,
    ):

        self.count_by_status_called += 1

        self.last_count_status = status

        return len(
            [
                job
                for job in self.jobs
                if job.status == status
            ]
        )


# ==================================================
# Fixtures / Helpers
# ==================================================


def make_job(
    job_id,
    target_id,
    status=Job.STATUS_WAITING,
):

    job = Job(
        target_id=target_id,
        status=status,
    )

    job.id = job_id

    return job


# ==================================================
# Constructor
# ==================================================


def test_service_uses_injected_repository():

    repository = FakeJobRepository()

    service = BatchJobService(
        job_repository=repository,
    )

    assert (
        service.job_repository
        is repository
    )


def test_service_creates_default_repository():

    service = BatchJobService()

    assert (
        service.job_repository
        is not None
    )


def test_service_uses_injected_batch_config():

    repository = FakeJobRepository()

    config = BatchConfig(
        batch_size=5,
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=config,
    )

    assert (
        service.batch_config
        is config
    )


def test_service_creates_default_batch_config():

    repository = FakeJobRepository()

    service = BatchJobService(
        job_repository=repository,
    )

    assert (
        service.batch_config
        is not None
    )


# ==================================================
# Waiting Job Retrieval
# ==================================================


def test_get_waiting_jobs():

    jobs = [
        make_job(1, 101),
        make_job(2, 102),
        make_job(3, 103),
    ]

    repository = FakeJobRepository(
        jobs
    )

    config = BatchConfig(
        batch_size=20,
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=config,
    )

    result = (
        service.get_waiting_jobs()
    )

    assert isinstance(
        result,
        list,
    )

    assert len(result) == 3

    assert result == jobs


def test_get_waiting_jobs_delegates_to_repository():

    repository = FakeJobRepository(
        [
            make_job(1, 101),
        ]
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=20,
        ),
    )

    service.get_waiting_jobs()

    assert (
        repository.find_waiting_called
        == 1
    )


# ==================================================
# Batch Size
# ==================================================


def test_batch_size_limits_jobs():

    jobs = [
        make_job(1, 101),
        make_job(2, 102),
        make_job(3, 103),
        make_job(4, 104),
        make_job(5, 105),
    ]

    repository = FakeJobRepository(
        jobs
    )

    config = BatchConfig(
        batch_size=3,
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=config,
    )

    result = (
        service.get_waiting_jobs()
    )

    assert len(result) == 3

    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3


def test_batch_size_one():

    jobs = [
        make_job(1, 101),
        make_job(2, 102),
        make_job(3, 103),
    ]

    repository = FakeJobRepository(
        jobs
    )

    config = BatchConfig(
        batch_size=1,
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=config,
    )

    result = (
        service.get_waiting_jobs()
    )

    assert len(result) == 1

    assert result[0].id == 1


def test_batch_size_larger_than_waiting_jobs():

    jobs = [
        make_job(1, 101),
        make_job(2, 102),
    ]

    repository = FakeJobRepository(
        jobs
    )

    config = BatchConfig(
        batch_size=20,
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=config,
    )

    result = (
        service.get_waiting_jobs()
    )

    assert len(result) == 2

    assert result == jobs


# ==================================================
# Empty
# ==================================================


def test_no_waiting_jobs_returns_empty_list():

    repository = FakeJobRepository(
        []
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=20,
        ),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert result == []


def test_none_repository_result_returns_empty_list():

    class NoneRepository:

        def find_waiting(self):

            return None

    repository = NoneRepository()

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=20,
        ),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert result == []


# ==================================================
# Order
# ==================================================


def test_job_order_is_preserved():

    jobs = [
        make_job(30, 300),
        make_job(10, 100),
        make_job(20, 200),
    ]

    repository = FakeJobRepository(
        jobs
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=20,
        ),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert [
        job.id
        for job in result
    ] == [
        30,
        10,
        20,
    ]


# ==================================================
# No Modification
# ==================================================


def test_retrieval_does_not_modify_job():

    job = make_job(
        1,
        101,
        Job.STATUS_WAITING,
    )

    repository = FakeJobRepository(
        [job]
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=20,
        ),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert result[0] is job

    assert (
        job.status
        == Job.STATUS_WAITING
    )


def test_retrieval_does_not_change_job_count():

    jobs = [
        make_job(1, 101),
        make_job(2, 102),
        make_job(3, 103),
    ]

    repository = FakeJobRepository(
        jobs
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=2,
        ),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert len(result) == 2

    assert len(repository.jobs) == 3


# ==================================================
# Alias
# ==================================================


def test_get_jobs_alias():

    jobs = [
        make_job(1, 101),
        make_job(2, 102),
    ]

    repository = FakeJobRepository(
        jobs
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=20,
        ),
    )

    result = service.get_jobs()

    assert result == jobs


# ==================================================
# Count
# ==================================================


def test_count_waiting_jobs():

    jobs = [
        make_job(
            1,
            101,
            Job.STATUS_WAITING,
        ),
        make_job(
            2,
            102,
            Job.STATUS_WAITING,
        ),
        make_job(
            3,
            103,
            Job.STATUS_DONE,
        ),
        make_job(
            4,
            104,
            Job.STATUS_FAILED,
        ),
    ]

    repository = FakeJobRepository(
        jobs
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=2,
        ),
    )

    result = (
        service.count_waiting_jobs()
    )

    assert result == 2

    assert (
        repository.count_by_status_called
        == 1
    )

    assert (
        repository.last_count_status
        == Job.STATUS_WAITING
    )


def test_count_waiting_jobs_is_not_limited_by_batch_size():

    jobs = [
        make_job(1, 101),
        make_job(2, 102),
        make_job(3, 103),
        make_job(4, 104),
        make_job(5, 105),
    ]

    repository = FakeJobRepository(
        jobs
    )

    service = BatchJobService(
        job_repository=repository,
        batch_config=BatchConfig(
            batch_size=2,
        ),
    )

    result = (
        service.count_waiting_jobs()
    )

    assert result == 5


# ==================================================
# Public API
# ==================================================


def test_public_api():

    import services.batch_job_service as module

    assert (
        "BatchJobService"
        in module.__all__
    )