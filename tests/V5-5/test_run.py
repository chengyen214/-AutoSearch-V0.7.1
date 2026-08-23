"""
tests/V5-5/test_run.py

AutoSearch V5

V5.5
P5.5.6

run.py Integration Tests

測試：

    - run.py main()
    - BatchExecutionService 建立
    - BatchExecutionService.run() 呼叫
    - Execution Result 回傳
    - 不直接執行 V4 Pipeline
"""


import run


# ==================================================
# Fake Batch Execution Service
# ==================================================


class FakeBatchExecutionService:
    """
    測試用 Fake BatchExecutionService。

    不連接：

        - MySQL
        - Crawler
        - Parser
        - Archive
        - AI
    """

    created = False
    run_called = False

    result = {
        "total": 2,
        "success": 2,
        "failed": 0,
    }

    def __init__(self):

        FakeBatchExecutionService.created = True

    def run(self):

        FakeBatchExecutionService.run_called = True

        return FakeBatchExecutionService.result


# ==================================================
# Fixtures
# ==================================================


def reset_fake_service():

    FakeBatchExecutionService.created = False
    FakeBatchExecutionService.run_called = False


# ==================================================
# Service Creation
# ==================================================


def test_main_creates_batch_execution_service(
    monkeypatch,
):

    reset_fake_service()

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    run.main()

    assert (
        FakeBatchExecutionService.created
        is True
    )


# ==================================================
# Service Run
# ==================================================


def test_main_calls_batch_execution_service_run(
    monkeypatch,
):

    reset_fake_service()

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    run.main()

    assert (
        FakeBatchExecutionService.run_called
        is True
    )


# ==================================================
# Result
# ==================================================


def test_main_returns_batch_result(
    monkeypatch,
):

    reset_fake_service()

    expected = {
        "total": 20,
        "success": 18,
        "failed": 2,
    }

    FakeBatchExecutionService.result = (
        expected
    )

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    result = run.main()

    assert result == expected


# ==================================================
# Empty Batch
# ==================================================


def test_main_returns_empty_batch_result(
    monkeypatch,
):

    reset_fake_service()

    expected = {
        "total": 0,
        "success": 0,
        "failed": 0,
    }

    FakeBatchExecutionService.result = (
        expected
    )

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    result = run.main()

    assert result == expected


# ==================================================
# Failure Result
# ==================================================


def test_main_returns_failed_batch_result(
    monkeypatch,
):

    reset_fake_service()

    expected = {
        "total": 3,
        "success": 1,
        "failed": 2,
    }

    FakeBatchExecutionService.result = (
        expected
    )

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    result = run.main()

    assert result == expected


# ==================================================
# No V4 Application
# ==================================================


def test_run_does_not_use_v4_application(
    monkeypatch,
):

    reset_fake_service()

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    # 如果 run.py 還存在舊的 V4 main，
    # 這個測試仍然不應該呼叫它。

    called = {
        "v4": False,
    }

    def fake_v4_main():

        called["v4"] = True

    if hasattr(
        run,
        "AutoSearchApplication",
    ):

        monkeypatch.setattr(
            run,
            "AutoSearchApplication",
            fake_v4_main,
        )

    run.main()

    assert (
        called["v4"]
        is False
    )


# ==================================================
# No Crawl
# ==================================================


def test_run_does_not_directly_execute_crawler(
    monkeypatch,
):

    reset_fake_service()

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    # run.py 不應該直接匯入或建立 Crawler。

    assert not hasattr(
        run,
        "Crawler",
    )

    run.main()

    assert (
        FakeBatchExecutionService.run_called
        is True
    )


# ==================================================
# No Parser
# ==================================================


def test_run_does_not_directly_execute_parser(
    monkeypatch,
):

    reset_fake_service()

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    assert not hasattr(
        run,
        "Parser",
    )

    run.main()

    assert (
        FakeBatchExecutionService.run_called
        is True
    )


# ==================================================
# No AI
# ==================================================


def test_run_does_not_directly_execute_ai(
    monkeypatch,
):

    reset_fake_service()

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        FakeBatchExecutionService,
    )

    assert not hasattr(
        run,
        "AIWorkerPool",
    )

    run.main()

    assert (
        FakeBatchExecutionService.run_called
        is True
    )


# ==================================================
# Single Run
# ==================================================


def test_main_runs_batch_runner_once(
    monkeypatch,
):

    class CountingBatchExecutionService:

        run_count = 0

        def __init__(self):
            pass

        def run(self):

            self.run_count += 1

            return {
                "total": 1,
                "success": 1,
                "failed": 0,
            }

    service_holder = {}

    class TrackingBatchExecutionService:

        def __init__(self):

            service = (
                CountingBatchExecutionService()
            )

            service_holder["service"] = service

        def run(self):

            return (
                service_holder["service"].run()
            )

    monkeypatch.setattr(
        run,
        "BatchExecutionService",
        TrackingBatchExecutionService,
    )

    result = run.main()

    assert result == {
        "total": 1,
        "success": 1,
        "failed": 0,
    }

    assert (
        service_holder["service"].run_count
        == 1
    )


# ==================================================
# Public Entry
# ==================================================


def test_main_is_available():

    assert callable(
        run.main
    )