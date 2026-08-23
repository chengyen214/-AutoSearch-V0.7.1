"""
tests/V5-5/test_batch_execution_service.py

AutoSearch V5

V5.5
P5.5.5

Batch Execution Service Tests

測試：

    - Repository / Service Injection
    - Batch Size
    - WAITING Job Retrieval
    - Batch Size Limitation
    - Target Retrieval
    - Single Job Execution
    - Job Lifecycle
    - Executor Success
    - Executor Failure
    - Executor Exception
    - Missing Target
    - Missing Executor
    - Empty Batch
    - Batch Execution
    - Run Alias
    - No Direct Crawl Responsibility
"""


import pytest

from config.batch_config import BatchConfig
from models.job import Job
from services.batch_execution_service import (
    BatchExecutionService,
)


# ==================================================
# Fake Job Service
# ==================================================


class FakeJobService:
    """
    測試用 Fake Job Service。

    不連接 MySQL。
    """

    def __init__(
        self,
        jobs=None,
    ):

        self.jobs = (
            list(jobs)
            if jobs is not None
            else []
        )

        self.calls = []

    # ----------------------------------
    # Find Waiting
    # ----------------------------------

    def find_waiting(self):

        self.calls.append(
            (
                "find_waiting",
            )
        )

        return list(
            self.jobs
        )


# ==================================================
# Fake Target Service
# ==================================================


class FakeTargetService:
    """
    測試用 Fake Target Service。
    """

    def __init__(
        self,
        targets=None,
    ):

        self.targets = (
            targets
            if targets is not None
            else {}
        )

        self.calls = []

    # ----------------------------------
    # Get Target For Job
    # ----------------------------------

    def get_target_for_job(
        self,
        job,
    ):

        self.calls.append(
            (
                "get_target_for_job",
                job,
            )
        )

        if job is None:
            return None

        return self.targets.get(
            job.target_id
        )


# ==================================================
# Fake Status Service
# ==================================================


class FakeStatusService:
    """
    測試用 Fake Job Status Service。
    """

    def __init__(self):

        self.calls = []

        self.status = {}

    # ----------------------------------
    # Start
    # ----------------------------------

    def start_job(
        self,
        job_id,
    ):

        self.calls.append(
            (
                "start_job",
                job_id,
            )
        )

        self.status[
            job_id
        ] = Job.STATUS_RUNNING

        return True

    # ----------------------------------
    # Complete
    # ----------------------------------

    def complete_job(
        self,
        job_id,
    ):

        self.calls.append(
            (
                "complete_job",
                job_id,
            )
        )

        self.status[
            job_id
        ] = Job.STATUS_DONE

        return True

    # ----------------------------------
    # Fail
    # ----------------------------------

    def fail_job(
        self,
        job_id,
        error_message="",
    ):

        self.calls.append(
            (
                "fail_job",
                job_id,
                error_message,
            )
        )

        self.status[
            job_id
        ] = Job.STATUS_FAILED

        return True


# ==================================================
# Fake Executor
# ==================================================


class FakeExecutor:
    """
    測試用 Executor。

    可以控制：

        True
            成功

        False
            失敗

        Exception
            執行例外
    """

    def __init__(
        self,
        result=True,
        exception=None,
    ):

        self.result = result

        self.exception = exception

        self.calls = []

    def __call__(
        self,
        job,
        target,
    ):

        self.calls.append(
            (
                job,
                target,
            )
        )

        if self.exception is not None:

            raise self.exception

        return self.result


# ==================================================
# Helpers
# ==================================================


def create_job(
    job_id,
    target_id,
):

    job = Job(
        target_id=target_id
    )

    job.id = job_id

    return job


def create_service(
    jobs=None,
    targets=None,
    batch_size=20,
    executor=None,
):

    job_service = FakeJobService(
        jobs=jobs
    )

    target_service = FakeTargetService(
        targets=targets
    )

    status_service = FakeStatusService()

    config = BatchConfig(
        batch_size=batch_size
    )

    service = BatchExecutionService(
        batch_config=config,
        job_service=job_service,
        target_service=target_service,
        status_service=status_service,
        executor=executor,
    )

    return (
        service,
        job_service,
        target_service,
        status_service,
    )


# ==================================================
# Fixtures
# ==================================================


@pytest.fixture
def job():

    return create_job(
        job_id=1,
        target_id=10,
    )


@pytest.fixture
def target():

    return {
        "id": 10,
        "name": "Test Target",
    }


@pytest.fixture
def executor():

    return FakeExecutor(
        result=True
    )


@pytest.fixture
def service(
    job,
    target,
    executor,
):

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        batch_size=20,
        executor=executor,
    )

    return service


# ==================================================
# Constructor
# ==================================================


def test_service_uses_injected_services():

    job = create_job(
        1,
        10,
    )

    target = {
        "id": 10,
    }

    executor = FakeExecutor()

    (
        service,
        job_service,
        target_service,
        status_service,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    assert (
        service.job_service
        is job_service
    )

    assert (
        service.target_service
        is target_service
    )

    assert (
        service.status_service
        is status_service
    )

    assert (
        service.executor
        is executor
    )


def test_service_creates_default_services():

    service = BatchExecutionService()

    assert service.batch_config is not None

    assert service.job_service is not None

    assert service.target_service is not None

    assert service.status_service is not None

    assert service.executor is None


# ==================================================
# Batch Size
# ==================================================


def test_get_batch_size():

    config = BatchConfig(
        batch_size=20
    )

    service = BatchExecutionService(
        batch_config=config
    )

    assert (
        service.get_batch_size()
        == 20
    )


def test_custom_batch_size():

    config = BatchConfig(
        batch_size=5
    )

    service = BatchExecutionService(
        batch_config=config
    )

    assert (
        service.get_batch_size()
        == 5
    )


# ==================================================
# Waiting Job Retrieval
# ==================================================


def test_get_waiting_jobs(
    job,
    target,
    executor,
):

    (
        service,
        job_service,
        _,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.get_waiting_jobs()
    )

    assert isinstance(
        result,
        list
    )

    assert result == [job]

    assert (
        job_service.calls[-1]
        == (
            "find_waiting",
        )
    )


def test_get_waiting_jobs_empty():

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=[],
        executor=FakeExecutor(),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert result == []


# ==================================================
# Batch Size Limitation
# ==================================================


def test_get_waiting_jobs_respects_batch_size():

    jobs = [
        create_job(
            job_id=i,
            target_id=i + 100,
        )
        for i in range(1, 11)
    ]

    targets = {
        i + 100: {
            "id": i + 100,
        }
        for i in range(1, 11)
    }

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=jobs,
        targets=targets,
        batch_size=3,
        executor=FakeExecutor(),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert len(result) == 3

    assert result == jobs[:3]


def test_batch_size_twenty():

    jobs = [
        create_job(
            job_id=i,
            target_id=i + 100,
        )
        for i in range(1, 31)
    ]

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=jobs,
        batch_size=20,
        executor=FakeExecutor(),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert len(result) == 20

    assert result == jobs[:20]


def test_batch_size_one():

    jobs = [
        create_job(
            job_id=1,
            target_id=101,
        ),
        create_job(
            job_id=2,
            target_id=102,
        ),
    ]

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=jobs,
        batch_size=1,
        executor=FakeExecutor(),
    )

    result = (
        service.get_waiting_jobs()
    )

    assert len(result) == 1

    assert result[0] is jobs[0]


# ==================================================
# Target Retrieval
# ==================================================


def test_get_target_for_job(
    service,
    job,
    target,
):

    service.target_service.targets[
        job.target_id
    ] = target

    result = (
        service.get_target_for_job(
            job
        )
    )

    assert result is target


def test_get_target_for_job_none(
    service,
):

    result = (
        service.get_target_for_job(
            None
        )
    )

    assert result is None


# ==================================================
# Execute One Job
# ==================================================


def test_execute_job_success(
    job,
    target,
):

    executor = FakeExecutor(
        result=True
    )

    (
        service,
        _,
        _,
        status_service,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is True

    assert executor.calls == [
        (
            job,
            target,
        )
    ]

    assert (
        status_service.calls
        == [
            (
                "start_job",
                job.id,
            ),
            (
                "complete_job",
                job.id,
            ),
        ]
    )


def test_execute_job_failure(
    job,
    target,
):

    executor = FakeExecutor(
        result=False
    )

    (
        service,
        _,
        _,
        status_service,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is False

    assert (
        status_service.calls
        == [
            (
                "start_job",
                job.id,
            ),
            (
                "fail_job",
                job.id,
                "Job execution failed",
            ),
        ]
    )


def test_execute_job_exception(
    job,
    target,
):

    executor = FakeExecutor(
        exception=RuntimeError(
            "test exception"
        )
    )

    (
        service,
        _,
        _,
        status_service,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is False

    assert (
        status_service.calls
        == [
            (
                "start_job",
                job.id,
            ),
            (
                "fail_job",
                job.id,
                "test exception",
            ),
        ]
    )


def test_execute_job_none(
    service,
):

    result = (
        service.execute_job(
            None
        )
    )

    assert result is False


def test_execute_job_without_id(
    service,
):

    job = Job(
        target_id=1
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is False


# ==================================================
# Missing Target
# ==================================================


def test_execute_job_target_not_found(
    job,
    executor,
):

    (
        service,
        _,
        _,
        status_service,
    ) = create_service(
        jobs=[job],
        targets={},
        executor=executor,
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is False

    assert (
        executor.calls
        == []
    )

    assert (
        status_service.calls
        == [
            (
                "fail_job",
                job.id,
                "Target not found",
            )
        ]
    )


# ==================================================
# Missing Executor
# ==================================================


def test_execute_job_without_executor(
    job,
    target,
):

    (
        service,
        _,
        _,
        status_service,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=None,
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is False

    assert (
        status_service.calls
        == [
            (
                "start_job",
                job.id,
            ),
            (
                "fail_job",
                job.id,
                "Job executor is not configured",
            ),
        ]
    )


# ==================================================
# Start Failure
# ==================================================


def test_execute_job_start_failure(
    job,
    target,
):

    class StartFailStatusService(
        FakeStatusService
    ):

        def start_job(
            self,
            job_id,
        ):

            self.calls.append(
                (
                    "start_job",
                    job_id,
                )
            )

            return False

    job_service = FakeJobService(
        jobs=[job]
    )

    target_service = FakeTargetService(
        targets={
            10: target,
        }
    )

    status_service = (
        StartFailStatusService()
    )

    executor = FakeExecutor()

    service = BatchExecutionService(
        batch_config=BatchConfig(
            batch_size=20
        ),
        job_service=job_service,
        target_service=target_service,
        status_service=status_service,
        executor=executor,
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is False

    assert (
        executor.calls
        == []
    )

    assert (
        status_service.calls
        == [
            (
                "start_job",
                job.id,
            )
        ]
    )


# ==================================================
# Execute Batch
# ==================================================


def test_execute_batch_empty():

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=[],
        executor=FakeExecutor(),
    )

    result = (
        service.execute_batch()
    )

    assert result == {
        "total": 0,
        "success": 0,
        "failed": 0,
    }


def test_execute_batch_single_success(
    job,
    target,
):

    executor = FakeExecutor(
        result=True
    )

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.execute_batch()
    )

    assert result == {
        "total": 1,
        "success": 1,
        "failed": 0,
    }

    assert len(
        executor.calls
    ) == 1


def test_execute_batch_single_failure(
    job,
    target,
):

    executor = FakeExecutor(
        result=False
    )

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.execute_batch()
    )

    assert result == {
        "total": 1,
        "success": 0,
        "failed": 1,
    }


def test_execute_batch_respects_batch_size():

    jobs = [
        create_job(
            job_id=i,
            target_id=i + 100,
        )
        for i in range(1, 11)
    ]

    targets = {
        i + 100: {
            "id": i + 100,
        }
        for i in range(1, 11)
    }

    executor = FakeExecutor(
        result=True
    )

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=jobs,
        targets=targets,
        batch_size=3,
        executor=executor,
    )

    result = (
        service.execute_batch()
    )

    assert result == {
        "total": 3,
        "success": 3,
        "failed": 0,
    }

    assert len(
        executor.calls
    ) == 3


def test_execute_batch_mixed_results():

    jobs = [
        create_job(
            job_id=1,
            target_id=101,
        ),
        create_job(
            job_id=2,
            target_id=102,
        ),
        create_job(
            job_id=3,
            target_id=103,
        ),
    ]

    targets = {
        101: {
            "id": 101,
        },
        102: {
            "id": 102,
        },
        103: {
            "id": 103,
        },
    }

    class MixedExecutor:

        def __init__(self):

            self.calls = []

        def __call__(
            self,
            job,
            target,
        ):

            self.calls.append(
                (
                    job,
                    target,
                )
            )

            return (
                job.id != 2
            )

    executor = MixedExecutor()

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=jobs,
        targets=targets,
        batch_size=3,
        executor=executor,
    )

    result = (
        service.execute_batch()
    )

    assert result == {
        "total": 3,
        "success": 2,
        "failed": 1,
    }

    assert len(
        executor.calls
    ) == 3


# ==================================================
# Run Alias
# ==================================================


def test_run_alias(
    job,
    target,
):

    executor = FakeExecutor(
        result=True
    )

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.run()
    )

    assert result == {
        "total": 1,
        "success": 1,
        "failed": 0,
    }


# ==================================================
# Delegation
# ==================================================


def test_get_waiting_jobs_delegates_to_job_service(
    job,
    target,
):

    (
        service,
        job_service,
        _,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=FakeExecutor(),
    )

    service.get_waiting_jobs()

    assert (
        job_service.calls
        == [
            (
                "find_waiting",
            )
        ]
    )


def test_get_target_for_job_delegates(
    job,
    target,
):

    (
        service,
        _,
        target_service,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=FakeExecutor(),
    )

    service.get_target_for_job(
        job
    )

    assert (
        target_service.calls
        == [
            (
                "get_target_for_job",
                job,
            )
        ]
    )


# ==================================================
# No Direct Crawl Responsibility
# ==================================================


def test_batch_execution_uses_executor_only(
    job,
    target,
):

    executor = FakeExecutor(
        result=True
    )

    (
        service,
        _,
        _,
        _,
    ) = create_service(
        jobs=[job],
        targets={
            10: target,
        },
        executor=executor,
    )

    result = (
        service.execute_job(
            job
        )
    )

    assert result is True

    assert len(
        executor.calls
    ) == 1

    # BatchExecutionService
    # 不直接執行：
    #
    # crawler
    # parser
    # search
    # archive
    # ai
    #
    # 實際工作全部交給 executor。


# ==================================================
# Public API
# ==================================================


def test_public_api():

    from services.batch_execution_service import (
        __all__,
    )

    assert (
        "BatchExecutionService"
        in __all__
    )