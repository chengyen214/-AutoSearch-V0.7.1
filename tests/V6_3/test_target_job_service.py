from services.target_job_service import TargetJobService
from models.job import Job


class FakeTarget:

    def __init__(
        self,
        target_id,
    ):
        self.id = target_id


class FakeTargetRepository:

    def __init__(self):
        self.targets = [
            FakeTarget(16),
        ]

    def find_active(self):

        return self.targets

    def get_by_id(
        self,
        target_id,
    ):

        for target in self.targets:

            if target.id == target_id:

                return target

        return None


class FakeJobRepository:

    def __init__(self):

        self.jobs = []

    def find_by_target_id(
        self,
        target_id,
    ):

        return [
            job
            for job in self.jobs
            if job.target_id == target_id
        ]

    def find_waiting_by_target(
        self,
        target_id,
    ):

        return [
            job
            for job in self.jobs
            if (
                job.target_id == target_id
                and
                job.status == Job.STATUS_WAITING
            )
        ]

    def save(
        self,
        job,
    ):

        if getattr(job, "id", None) is None:

            job.id = len(self.jobs) + 1

        self.jobs.append(job)

        return job


def test_create_pending_job_for_active_target():

    target_repository = (
        FakeTargetRepository()
    )

    job_repository = (
        FakeJobRepository()
    )

    service = TargetJobService(
        target_repository=target_repository,
        job_repository=job_repository,
    )

    created_jobs = (
        service.create_pending_jobs()
    )

    # ==================================================
    # Print Result
    # ==================================================

    print("")
    print("=" * 60)
    print("Created Jobs")
    print("=" * 60)

    for job in created_jobs:

        print(
            f"Job ID      : {getattr(job, 'id', None)}"
        )

        print(
            f"Target ID   : {getattr(job, 'target_id', None)}"
        )

        print(
            f"Status      : {getattr(job, 'status', None)}"
        )

        print(
            f"Created At  : {getattr(job, 'created_at', None)}"
        )

        print(
            f"Updated At  : {getattr(job, 'updated_at', None)}"
        )

        print("-" * 60)

    print(
        f"Total Jobs  : {len(created_jobs)}"
    )

    print("=" * 60)
    print("")

    # ==================================================
    # Assertions
    # ==================================================

    assert len(created_jobs) == 1

    job = created_jobs[0]

    assert job.target_id == 16

    assert job.status == Job.STATUS_WAITING