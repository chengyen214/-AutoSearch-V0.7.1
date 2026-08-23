"""
tests/V5-1/test_target_repository.py

AutoSearch V5

V5.1 P1.2

Target Repository Test

測試：

    - Target Create
    - Target Query
    - Target URL Query
    - Target Active Query
    - Target Exists
    - Target Update
    - Target Status
    - Target Enable
    - Target Disable
    - Target Delete
    - Target Count
    - Target Model Conversion

注意：

    使用目前既有 MySQL Database。

    不修改 V4 Article / Archive / AI Pipeline。
"""


from datetime import datetime

import pytest

from models.target import Target
from database.target_repository import TargetRepository


# ==================================================
# Fixture
# ==================================================


@pytest.fixture
def repository():

    return TargetRepository()


@pytest.fixture
def target():

    return Target(

        name="Test Target",

        target_type="website",

        url="https://example.com/v5-test",

        description="V5.1 P1.2 Repository Test",

        status="active"

    )


# ==================================================
# Save
# ==================================================


def test_save(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        assert saved is target

        assert saved.id is not None

        assert saved.id > 0

        assert saved.url == (
            "https://example.com/v5-test"
        )

    finally:

        if saved.id is not None:

            repository.delete_by_id(
                saved.id
            )


# ==================================================
# Insert Alias
# ==================================================


def test_insert_alias(
    repository,
    target
):

    saved = repository.insert(
        target
    )

    try:

        assert saved is target

        assert saved.id is not None

    finally:

        if saved.id is not None:

            repository.delete_by_id(
                saved.id
            )


# ==================================================
# Get By ID
# ==================================================


def test_get_by_id(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        result = repository.get_by_id(
            saved.id
        )

        assert result is not None

        assert isinstance(
            result,
            Target
        )

        assert result.id == saved.id

        assert result.name == (
            "Test Target"
        )

        assert result.url == (
            "https://example.com/v5-test"
        )

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Get By URL
# ==================================================


def test_get_by_url(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        result = repository.get_by_url(
            "https://example.com/v5-test"
        )

        assert result is not None

        assert isinstance(
            result,
            Target
        )

        assert result.id == saved.id

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Find All
# ==================================================


def test_find_all(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        results = repository.find_all()

        assert isinstance(
            results,
            list
        )

        assert any(
            item.id == saved.id
            for item in results
        )

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Find Active
# ==================================================


def test_find_active(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        results = repository.find_active()

        assert isinstance(
            results,
            list
        )

        assert any(
            item.id == saved.id
            for item in results
        )

        assert all(
            item.status == "active"
            for item in results
        )

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Exists
# ==================================================


def test_exists(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        assert repository.exists(
            saved.id
        ) is True

        assert repository.exists(
            999999999
        ) is False

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Exists By URL
# ==================================================


def test_exists_by_url(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        assert repository.exists_by_url(
            saved.url
        ) is True

        assert repository.exists_by_url(
            "https://example.com/not-exists"
        ) is False

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Update
# ==================================================


def test_update(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        saved.name = (
            "Updated Target"
        )

        saved.description = (
            "Updated Description"
        )

        saved.url = (
            "https://example.com/v5-updated"
        )

        result = repository.update(
            saved
        )

        assert result is True

        updated = repository.get_by_id(
            saved.id
        )

        assert updated is not None

        assert updated.name == (
            "Updated Target"
        )

        assert updated.description == (
            "Updated Description"
        )

        assert updated.url == (
            "https://example.com/v5-updated"
        )

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Update Status
# ==================================================


def test_update_status(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        result = repository.update_status(
            saved.id,
            "inactive"
        )

        assert result is True

        updated = repository.get_by_id(
            saved.id
        )

        assert updated.status == (
            "inactive"
        )

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Disable
# ==================================================


def test_disable(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        result = repository.disable(
            saved.id
        )

        assert result is True

        updated = repository.get_by_id(
            saved.id
        )

        assert updated.status == (
            "inactive"
        )

        assert updated.is_active is False

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Enable
# ==================================================


def test_enable(
    repository,
    target
):

    saved = repository.save(
        target
    )

    try:

        repository.disable(
            saved.id
        )

        result = repository.enable(
            saved.id
        )

        assert result is True

        updated = repository.get_by_id(
            saved.id
        )

        assert updated.status == (
            "active"
        )

        assert updated.is_active is True

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Delete
# ==================================================


def test_delete_by_id(
    repository,
    target
):

    saved = repository.save(
        target
    )

    target_id = saved.id

    result = repository.delete_by_id(
        target_id
    )

    assert result is True

    assert repository.exists(
        target_id
    ) is False

    assert repository.get_by_id(
        target_id
    ) is None


# ==================================================
# Count
# ==================================================


def test_count(
    repository,
    target
):

    before = repository.count()

    saved = repository.save(
        target
    )

    try:

        after = repository.count()

        assert after == before + 1

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Count Active
# ==================================================


def test_count_active(
    repository,
    target
):

    before = repository.count_active()

    saved = repository.save(
        target
    )

    try:

        after = repository.count_active()

        assert after == before + 1

        repository.disable(
            saved.id
        )

        disabled = repository.count_active()

        assert disabled == before

    finally:

        repository.delete_by_id(
            saved.id
        )


# ==================================================
# Validation
# ==================================================


def test_save_none(
    repository
):

    with pytest.raises(
        ValueError
    ):

        repository.save(
            None
        )


def test_save_invalid_type(
    repository
):

    with pytest.raises(
        TypeError
    ):

        repository.save(
            "invalid"
        )


def test_save_empty_url(
    repository
):

    target = Target(
        name="Invalid Target",
        url=""
    )

    with pytest.raises(
        ValueError
    ):

        repository.save(
            target
        )


# ==================================================
# Update Validation
# ==================================================


def test_update_without_id(
    repository
):

    target = Target(
        name="No ID",
        url="https://example.com/no-id"
    )

    with pytest.raises(
        ValueError
    ):

        repository.update(
            target
        )


def test_update_none(
    repository
):

    with pytest.raises(
        ValueError
    ):

        repository.update(
            None
        )


# ==================================================
# Finished
# ==================================================