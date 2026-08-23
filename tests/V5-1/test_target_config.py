"""
tests/V5-1/test_target_config.py

AutoSearch V5

V5.1 P1.5

Target Configuration Tests

測試：

    - Default Configuration
    - Custom Configuration
    - Timeout
    - Max Results
    - Search Enabled
    - Validation
    - Normalize
    - to_dict
    - Representation
"""


import pytest

from models.target_config import TargetConfig


# ==================================
# Default
# ==================================


def test_default_config():

    config = TargetConfig()

    assert config.timeout == 7

    assert config.max_results == 20

    assert config.search_enabled is True


# ==================================
# Custom
# ==================================


def test_custom_config():

    config = TargetConfig(

        timeout=10,

        max_results=50,

        search_enabled=False
    )

    assert config.timeout == 10

    assert config.max_results == 50

    assert config.search_enabled is False


# ==================================
# Timeout
# ==================================


def test_timeout():

    config = TargetConfig(
        timeout=15
    )

    assert config.timeout == 15


def test_timeout_float():

    config = TargetConfig(
        timeout=2.5
    )

    assert config.timeout == 2.5


def test_invalid_timeout():

    with pytest.raises(ValueError):

        TargetConfig(
            timeout=0
        )


def test_invalid_timeout_negative():

    with pytest.raises(ValueError):

        TargetConfig(
            timeout=-1
        )


# ==================================
# Max Results
# ==================================


def test_max_results():

    config = TargetConfig(
        max_results=40
    )

    assert config.max_results == 40


def test_invalid_max_results():

    with pytest.raises(ValueError):

        TargetConfig(
            max_results=0
        )


def test_invalid_max_results_negative():

    with pytest.raises(ValueError):

        TargetConfig(
            max_results=-1
        )


# ==================================
# Search Enabled
# ==================================


def test_search_enabled():

    config = TargetConfig(
        search_enabled=False
    )

    assert config.search_enabled is False


def test_invalid_search_enabled():

    with pytest.raises(ValueError):

        TargetConfig(
            search_enabled="true"
        )


# ==================================
# Normalize
# ==================================


def test_normalize_max_results():

    config = TargetConfig(
        max_results="40"
    )

    assert config.max_results == 40


def test_normalize_timeout():

    config = TargetConfig(
        timeout="2.5"
    )

    assert config.timeout == 2.5


# ==================================
# Validation
# ==================================


def test_validate():

    config = TargetConfig(

        max_results=20,

        timeout=7,

        search_enabled=True
    )

    assert config.validate() is True


def test_invalid_max_results_type():

    with pytest.raises(ValueError):

        TargetConfig(
            max_results="invalid"
        )


def test_invalid_timeout_type():

    with pytest.raises(ValueError):

        TargetConfig(
            timeout="invalid"
        )


# ==================================
# To Dict
# ==================================


def test_to_dict():

    config = TargetConfig(

        timeout=10,

        max_results=30,

        search_enabled=False
    )

    result = config.to_dict()

    assert result["timeout"] == 10

    assert result["max_results"] == 30

    assert result["search_enabled"] is False


# ==================================
# Representation
# ==================================


def test_repr():

    config = TargetConfig(

        timeout=10,

        max_results=30,

        search_enabled=False
    )

    result = repr(config)

    assert "TargetConfig" in result

    assert "timeout=10" in result

    assert "max_results=30" in result

    assert "search_enabled=False" in result