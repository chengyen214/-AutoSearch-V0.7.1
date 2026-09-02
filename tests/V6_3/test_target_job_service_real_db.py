"""
tests/V6_3/test_target_job_service_real_db.py

AutoSearch V5

V5.6.3

Real DB Test

驗證：

    Target ID 16
        ↓
    TargetJobService
        ↓
    JobRepository
        ↓
    MySQL jobs

目的：

    確認真正 Database Repository
    是否可以為 Target 16 建立 WAITING Job。

注意：

    本測試不使用 Mock / Fake Repository。
"""


from services.target_job_service import (
    TargetJobService,
)

from database.target_repository import (
    TargetRepository,
)

from database.job_repository import (
    JobRepository,
)

from models.job import Job


# ==================================================
#
# Target ID
#
# ==================================================

TARGET_ID = 16


# ==================================================
#
# Test
#
# ==================================================

def test_create_real_job_for_target_16():
    """
    使用真正 MySQL 驗證：

        Target 16
            ↓
        TargetJobService
            ↓
        JobRepository
            ↓
        jobs
    """

    print()
    print("=" * 60)
    print("Target 16 Real DB Job Test")
    print("=" * 60)


    # ==================================================
    # Repository
    # ==================================================

    target_repository = TargetRepository()

    job_repository = JobRepository()


    # ==================================================
    # Target
    # ==================================================

    target = (
        target_repository.get_by_id(
            TARGET_ID
        )
    )


    assert target is not None, (
        f"Target {TARGET_ID} not found"
    )


    print()
    print("Target")
    print("-" * 60)
    print(
        f"ID          : "
        f"{target.id}"
    )
    print(
        f"Type        : "
        f"{getattr(target, 'target_type', None)}"
    )
    print(
        f"Keyword     : "
        f"{getattr(target, 'keyword', None)}"
    )
    print(
        f"Provider    : "
        f"{getattr(target, 'search_provider', None)}"
    )
    print(
        f"Status      : "
        f"{getattr(target, 'status', None)}"
    )


    # ==================================================
    # Before
    # ==================================================

    existing_jobs = (
        job_repository
        .find_by_target_id(
            TARGET_ID
        )
    )


    print()
    print("Before")
    print("-" * 60)
    print(
        f"Existing Jobs : "
        f"{len(existing_jobs)}"
    )


    for job in existing_jobs:

        print(
            f"  Job ID={job.id}, "
            f"Status={job.status}"
        )


    # ==================================================
    # Service
    # ==================================================

    service = TargetJobService(
        target_repository=target_repository,
        job_repository=job_repository,
    )


    # ==================================================
    # Create
    # ==================================================

    created_jobs = (
        service.create_pending_jobs()
    )


    print()
    print("Created Jobs")
    print("-" * 60)


    if not created_jobs:

        print(
            "No new Job was created."
        )


    for job in created_jobs:

        print(
            f"Job ID      : "
            f"{job.id}"
        )

        print(
            f"Target ID   : "
            f"{job.target_id}"
        )

        print(
            f"Status      : "
            f"{job.status}"
        )

        print(
            f"Retry Count : "
            f"{job.retry_count}"
        )

        print(
            f"Created At  : "
            f"{job.created_time}"
        )

        print(
            f"Started At  : "
            f"{job.started_time}"
        )

        print(
            f"Finished At : "
            f"{job.finished_time}"
        )

        print(
            f"Error       : "
            f"{job.error_message}"
        )

        print("-" * 60)


    # ==================================================
    # Find Target 16 Jobs Again
    # ==================================================

    jobs_after = (
        job_repository
        .find_by_target_id(
            TARGET_ID
        )
    )


    print()
    print("Database Verify")
    print("-" * 60)


    print(
        f"Total Jobs For Target 16 : "
        f"{len(jobs_after)}"
    )


    for job in jobs_after:

        print(
            f"Job ID      : "
            f"{job.id}"
        )

        print(
            f"Target ID   : "
            f"{job.target_id}"
        )

        print(
            f"Status      : "
            f"{job.status}"
        )

        print(
            f"Retry Count : "
            f"{job.retry_count}"
        )

        print(
            f"Created At  : "
            f"{job.created_time}"
        )

        print("-" * 60)


    # ==================================================
    # Assertion
    # ==================================================

    if created_jobs:

        target_jobs = [
            job
            for job in jobs_after
            if job.target_id == TARGET_ID
        ]

        assert target_jobs, (
            "Created Job was not found "
            "in database"
        )


        waiting_jobs = [
            job
            for job in target_jobs
            if job.status == Job.STATUS_WAITING
        ]

        assert waiting_jobs, (
            "Target 16 should have "
            "a WAITING Job"
        )


    print()
    print("=" * 60)

    if created_jobs:

        print(
            "RESULT: Target 16 created "
            "a real WAITING Job."
        )

    else:

        print(
            "RESULT: TargetJobService did "
            "not create a new Job."
        )

        print(
            "This means Target 16 already has "
            "a WAITING or RUNNING Job, "
            "or Target 16 was not returned "
            "by find_active()."
        )

    print("=" * 60)