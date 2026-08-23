"""
tests/V5-5/test_batch_config.py

AutoSearch V5

P5.5.1

Batch Configuration Tests

測試：

    - Default Batch Size
    - Custom Batch Size
    - Validation
    - Batch Size Property
    - Dictionary
"""


import pytest

from config.batch_config import BatchConfig


# ==================================================
# Default
# ==================================================


def test_default_batch_size():

    config = BatchConfig()

    assert config.batch_size == 20


# ==================================================
# Custom
# ==================================================


def test_custom_batch_size():

    config = BatchConfig(
        batch_size=10
    )

    assert config.batch_size == 10


def test_custom_large_batch_size():

    config = BatchConfig(
        batch_size=100
    )

    assert config.batch_size == 100


# ==================================================
# Validation
# ==================================================


def test_batch_size_must_be_positive():

    with pytest.raises(
        ValueError
    ):

        BatchConfig(
            batch_size=0
        )


def test_negative_batch_size_rejected():

    with pytest.raises(
        ValueError
    ):

        BatchConfig(
            batch_size=-1
        )


def test_batch_size_must_be_integer():

    with pytest.raises(
        (TypeError, ValueError)
    ):

        BatchConfig(
            batch_size="20"
        )


def test_float_batch_size_rejected():

    with pytest.raises(
        (TypeError, ValueError)
    ):

        BatchConfig(
            batch_size=20.5
        )


# ==================================================
# Property
# ==================================================


def test_batch_size_property():

    config = BatchConfig(
        batch_size=5
    )

    assert config.batch_size == 5


def test_batch_size_can_be_updated():

    config = BatchConfig(
        batch_size=5
    )

    config.batch_size = 10

    assert config.batch_size == 10


def test_updated_batch_size_cannot_be_zero():

    config = BatchConfig(
        batch_size=5
    )

    with pytest.raises(
        ValueError
    ):

        config.batch_size = 0


def test_updated_batch_size_cannot_be_negative():

    config = BatchConfig(
        batch_size=5
    )

    with pytest.raises(
        ValueError
    ):

        config.batch_size = -10


# ==================================================
# Dictionary
# ==================================================


def test_to_dict():

    config = BatchConfig(
        batch_size=20
    )

    result = config.to_dict()

    assert isinstance(
        result,
        dict
    )

    assert (
        result["batch_size"]
        == 20
    )


# ==================================================
# Representation
# ==================================================


def test_repr():

    config = BatchConfig(
        batch_size=20
    )

    result = repr(config)

    assert "BatchConfig" in result

    assert "20" in result


# ==================================================
# Independence
# ==================================================


def test_multiple_configs_are_independent():

    config_a = BatchConfig(
        batch_size=10
    )

    config_b = BatchConfig(
        batch_size=30
    )

    assert config_a.batch_size == 10

    assert config_b.batch_size == 30

    config_a.batch_size = 15

    assert config_a.batch_size == 15

    assert config_b.batch_size == 30