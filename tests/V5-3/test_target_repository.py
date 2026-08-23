"""
tests/V5-3/test_target_repository.py

AutoSearch V5

V5.3 P3.3

Target Repository Test

測試：

    - TargetRepository
    - URL Target CRUD
    - Search Target CRUD
    - Keyword
    - Search Provider
    - Target Query
    - Target Status
    - Target Type Query
    - Count
    - DB Row -> Target Model
"""


from datetime import datetime

import pytest

from database.target_repository import (
    TargetRepository,
)

from models.target import Target


# ============================================================
#
# Helpers
#
# ============================================================


class FakeCursor:

    def __init__(
        self,
        fetchone_result=None,
        fetchall_result=None,
        rowcount=1,
        lastrowid=1,
    ):

        self.fetchone_result = (
            fetchone_result
        )

        self.fetchall_result = (
            fetchall_result
        )

        self.rowcount = rowcount

        self.lastrowid = lastrowid

        self.executed = []

    def execute(
        self,
        sql,
        params=None,
    ):

        self.executed.append(
            (
                sql,
                params,
            )
        )

    def fetchone(self):

        return self.fetchone_result

    def fetchall(self):

        if self.fetchall_result is None:

            return []

        return self.fetchall_result

    def close(self):

        pass


class FakeConnection:

    def __init__(
        self,
        cursor,
    ):

        self._cursor = cursor

        self.committed = False

        self.rolled_back = False

        self.closed = False

    def cursor(
        self,
        dictionary=False,
    ):

        return self._cursor

    def commit(self):

        self.committed = True

    def rollback(self):

        self.rolled_back = True

    def close(self):

        self.closed = True


# ============================================================
#
# Fixtures
#
# ============================================================


@pytest.fixture
def repository():

    return TargetRepository()


@pytest.fixture
def url_target():

    return Target(

        name="Example Website",

        target_type="url",

        url="https://example.com",

        keyword="",

        search_provider="",

        status="active",

        description="Example URL Target",
    )


@pytest.fixture
def search_target():

    return Target(

        name="Semiconductor News",

        target_type="search",

        url="",

        keyword="semiconductor",

        search_provider="google_news",

        status="active",

        description="Google News Search Target",
    )


@pytest.fixture
def db_row():

    return {

        "id": 10,

        "name": "Semiconductor News",

        "target_type": "search",

        "url": "",

        "keyword": "semiconductor",

        "search_provider": "google_news",

        "description": "Google News Search Target",

        "status": "active",

        "created_time": datetime(2026, 8, 21, 10, 0, 0),

        "updated_time": datetime(2026, 8, 21, 10, 0, 0),
    }


# ============================================================
#
# Model / Repository
#
# ============================================================


def test_repository_instance(
    repository,
):

    assert isinstance(
        repository,
        TargetRepository,
    )


# ============================================================
#
# Save URL Target
#
# ============================================================


def test_save_url_target(
    repository,
    url_target,
    monkeypatch,
):

    cursor = FakeCursor(
        lastrowid=101,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.save(
        url_target,
    )

    assert result is url_target

    assert result.id == 101

    assert result.target_type == "url"

    assert result.url == (
        "https://example.com"
    )

    assert result.keyword == ""

    assert result.search_provider == ""

    assert connection.committed is True


# ============================================================
#
# Save Search Target
#
# ============================================================


def test_save_search_target(
    repository,
    search_target,
    monkeypatch,
):

    cursor = FakeCursor(
        lastrowid=102,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.save(
        search_target,
    )

    assert result is search_target

    assert result.id == 102

    assert result.target_type == "search"

    assert result.keyword == (
        "semiconductor"
    )

    assert result.search_provider == (
        "google_news"
    )

    assert connection.committed is True


# ============================================================
#
# Save Validation
#
# ============================================================


def test_save_none_target(
    repository,
):

    with pytest.raises(
        ValueError,
    ):

        repository.save(
            None,
        )


def test_save_invalid_target(
    repository,
):

    with pytest.raises(
        TypeError,
    ):

        repository.save(
            object(),
        )


# ============================================================
#
# Insert Alias
#
# ============================================================


def test_insert_alias(
    repository,
    url_target,
    monkeypatch,
):

    cursor = FakeCursor(
        lastrowid=103,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.insert(
        url_target,
    )

    assert result is url_target

    assert result.id == 103


# ============================================================
#
# Get By ID
#
# ============================================================


def test_get_by_id(
    repository,
    db_row,
    monkeypatch,
):

    cursor = FakeCursor(
        fetchone_result=db_row,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.get_by_id(
        10,
    )

    assert isinstance(
        result,
        Target,
    )

    assert result.id == 10

    assert result.keyword == (
        "semiconductor"
    )

    assert result.search_provider == (
        "google_news"
    )


def test_get_by_id_none(
    repository,
):

    result = repository.get_by_id(
        None,
    )

    assert result is None


# ============================================================
#
# Get By URL
#
# ============================================================


def test_get_by_url(
    repository,
    monkeypatch,
):

    row = {

        "id": 20,

        "name": "Example",

        "target_type": "url",

        "url": "https://example.com",

        "keyword": "",

        "search_provider": "",

        "description": "",

        "status": "active",

        "created_time": None,

        "updated_time": None,
    }

    cursor = FakeCursor(
        fetchone_result=row,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.get_by_url(
        "https://example.com",
    )

    assert result is not None

    assert result.target_type == "url"

    assert result.url == (
        "https://example.com"
    )


def test_get_by_url_empty(
    repository,
):

    assert (
        repository.get_by_url("")
        is None
    )

    assert (
        repository.get_by_url(None)
        is None
    )


# ============================================================
#
# Get By Keyword
#
# ============================================================


def test_get_by_keyword(
    repository,
    search_target,
    monkeypatch,
):

    row = {

        "id": 30,

        "name": search_target.name,

        "target_type": "search",

        "url": "",

        "keyword": "semiconductor",

        "search_provider": "google_news",

        "description": "",

        "status": "active",

        "created_time": None,

        "updated_time": None,
    }

    cursor = FakeCursor(
        fetchone_result=row,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.get_by_keyword(
        "semiconductor",
    )

    assert result is not None

    assert result.keyword == (
        "semiconductor"
    )

    assert result.search_provider == (
        "google_news"
    )


def test_get_by_keyword_empty(
    repository,
):

    assert (
        repository.get_by_keyword("")
        is None
    )

    assert (
        repository.get_by_keyword(None)
        is None
    )


# ============================================================
#
# Get By Search
#
# ============================================================


def test_get_by_search(
    repository,
    monkeypatch,
):

    row = {

        "id": 40,

        "name": "Google News",

        "target_type": "search",

        "url": "",

        "keyword": "semiconductor",

        "search_provider": "google_news",

        "description": "",

        "status": "active",

        "created_time": None,

        "updated_time": None,
    }

    cursor = FakeCursor(
        fetchone_result=row,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.get_by_search(
        "semiconductor",
        "google_news",
    )

    assert result is not None

    assert result.target_type == "search"

    assert result.keyword == (
        "semiconductor"
    )

    assert result.search_provider == (
        "google_news"
    )


def test_get_by_search_empty_keyword(
    repository,
):

    assert (
        repository.get_by_search(
            "",
            "google_news",
        )
        is None
    )


def test_get_by_search_empty_provider(
    repository,
):

    assert (
        repository.get_by_search(
            "semiconductor",
            "",
        )
        is None
    )


# ============================================================
#
# Exists By Search
#
# ============================================================


def test_exists_by_search(
    repository,
    monkeypatch,
):

    row = {

        "id": 50,

        "name": "Google News",

        "target_type": "search",

        "url": "",

        "keyword": "semiconductor",

        "search_provider": "google_news",

        "description": "",

        "status": "active",

        "created_time": None,

        "updated_time": None,
    }

    cursor = FakeCursor(
        fetchone_result=row,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    assert (
        repository.exists_by_search(
            "semiconductor",
            "google_news",
        )
        is True
    )


# ============================================================
#
# Find All
#
# ============================================================


def test_find_all(
    repository,
    monkeypatch,
):

    rows = [

        {

            "id": 1,

            "name": "URL Target",

            "target_type": "url",

            "url": "https://example.com",

            "keyword": "",

            "search_provider": "",

            "description": "",

            "status": "active",

            "created_time": None,

            "updated_time": None,
        },

        {

            "id": 2,

            "name": "News",

            "target_type": "search",

            "url": "",

            "keyword": "AI",

            "search_provider": "google_news",

            "description": "",

            "status": "active",

            "created_time": None,

            "updated_time": None,
        },
    ]

    cursor = FakeCursor(
        fetchall_result=rows,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    results = repository.find_all()

    assert len(results) == 2

    assert results[0].target_type == (
        "url"
    )

    assert results[1].target_type == (
        "search"
    )

    assert results[1].keyword == "AI"


# ============================================================
#
# Find Active
#
# ============================================================


def test_find_active(
    repository,
    monkeypatch,
):

    rows = [

        {

            "id": 1,

            "name": "News",

            "target_type": "search",

            "url": "",

            "keyword": "AI",

            "search_provider": "google_news",

            "description": "",

            "status": "active",

            "created_time": None,

            "updated_time": None,
        },
    ]

    cursor = FakeCursor(
        fetchall_result=rows,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    results = repository.find_active()

    assert len(results) == 1

    assert results[0].is_active is True


# ============================================================
#
# Find By Type
#
# ============================================================


def test_find_by_type(
    repository,
    monkeypatch,
):

    rows = [

        {

            "id": 1,

            "name": "News",

            "target_type": "search",

            "url": "",

            "keyword": "AI",

            "search_provider": "google_news",

            "description": "",

            "status": "active",

            "created_time": None,

            "updated_time": None,
        },
    ]

    cursor = FakeCursor(
        fetchall_result=rows,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    results = repository.find_by_type(
        "search",
    )

    assert len(results) == 1

    assert results[0].target_type == (
        "search"
    )


def test_find_search_targets(
    repository,
    monkeypatch,
):

    monkeypatch.setattr(
        repository,
        "find_by_type",
        lambda target_type: [
            Target(
                target_type=target_type,
            )
        ],
    )

    results = (
        repository.find_search_targets()
    )

    assert len(results) == 1

    assert results[0].target_type == (
        "search"
    )


def test_find_url_targets(
    repository,
    monkeypatch,
):

    monkeypatch.setattr(
        repository,
        "find_by_type",
        lambda target_type: [
            Target(
                target_type=target_type,
            )
        ],
    )

    results = (
        repository.find_url_targets()
    )

    assert len(results) == 1

    assert results[0].target_type == (
        "url"
    )


# ============================================================
#
# Exists
#
# ============================================================


def test_exists(
    repository,
    monkeypatch,
):

    cursor = FakeCursor(
        fetchone_result=(10,),
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    assert (
        repository.exists(10)
        is True
    )


def test_exists_none(
    repository,
):

    assert (
        repository.exists(None)
        is False
    )


# ============================================================
#
# Exists By URL
#
# ============================================================


def test_exists_by_url(
    repository,
    monkeypatch,
):

    monkeypatch.setattr(
        repository,
        "get_by_url",
        lambda url: Target(
            target_type="url",
            url=url,
        ),
    )

    assert (
        repository.exists_by_url(
            "https://example.com"
        )
        is True
    )


# ============================================================
#
# Update
#
# ============================================================


def test_update_search_target(
    repository,
    search_target,
    monkeypatch,
):

    search_target.id = 100

    cursor = FakeCursor(
        rowcount=1,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.update(
        search_target,
    )

    assert result is True

    assert (
        search_target.updated_time
        is not None
    )

    assert connection.committed is True


def test_update_without_id(
    repository,
    search_target,
):

    with pytest.raises(
        ValueError,
    ):

        repository.update(
            search_target,
        )


def test_update_invalid_target(
    repository,
):

    with pytest.raises(
        TypeError,
    ):

        repository.update(
            object(),
        )


# ============================================================
#
# Status
#
# ============================================================


def test_update_status(
    repository,
    monkeypatch,
):

    cursor = FakeCursor(
        rowcount=1,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.update_status(
        100,
        "inactive",
    )

    assert result is True

    assert connection.committed is True


def test_update_status_invalid_id(
    repository,
):

    assert (
        repository.update_status(
            None,
            "active",
        )
        is False
    )


def test_update_status_invalid_status(
    repository,
):

    assert (
        repository.update_status(
            100,
            "",
        )
        is False
    )


# ============================================================
#
# Enable / Disable
#
# ============================================================


def test_enable(
    repository,
    monkeypatch,
):

    monkeypatch.setattr(
        repository,
        "update_status",
        lambda target_id, status:
            (
                target_id == 100
                and status == "active"
            ),
    )

    assert (
        repository.enable(100)
        is True
    )


def test_disable(
    repository,
    monkeypatch,
):

    monkeypatch.setattr(
        repository,
        "update_status",
        lambda target_id, status:
            (
                target_id == 100
                and status == "inactive"
            ),
    )

    assert (
        repository.disable(100)
        is True
    )


# ============================================================
#
# Delete
#
# ============================================================


def test_delete_by_id(
    repository,
    monkeypatch,
):

    cursor = FakeCursor(
        rowcount=1,
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    result = repository.delete_by_id(
        100,
    )

    assert result is True

    assert connection.committed is True


def test_delete_by_id_none(
    repository,
):

    assert (
        repository.delete_by_id(None)
        is False
    )


# ============================================================
#
# Count
#
# ============================================================


def test_count(
    repository,
    monkeypatch,
):

    cursor = FakeCursor(
        fetchone_result=(5,),
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    assert (
        repository.count()
        == 5
    )


def test_count_active(
    repository,
    monkeypatch,
):

    cursor = FakeCursor(
        fetchone_result=(3,),
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    assert (
        repository.count_active()
        == 3
    )


def test_count_by_type(
    repository,
    monkeypatch,
):

    cursor = FakeCursor(
        fetchone_result=(2,),
    )

    connection = FakeConnection(
        cursor,
    )

    monkeypatch.setattr(
        "database.target_repository.get_connection",
        lambda: connection,
    )

    assert (
        repository.count_by_type(
            "search"
        )
        == 2
    )


def test_count_by_type_empty(
    repository,
):

    assert (
        repository.count_by_type("")
        == 0
    )


# ============================================================
#
# DB Row -> Target
#
# ============================================================


def test_to_model_search_target(
    repository,
    db_row,
):

    result = repository._to_model(
        db_row,
    )

    assert isinstance(
        result,
        Target,
    )

    assert result.id == 10

    assert result.name == (
        "Semiconductor News"
    )

    assert result.target_type == (
        "search"
    )

    assert result.keyword == (
        "semiconductor"
    )

    assert result.search_provider == (
        "google_news"
    )

    assert result.url == ""

    assert result.status == (
        "active"
    )


def test_to_model_url_target(
    repository,
):

    row = {

        "id": 11,

        "name": "Example",

        "target_type": "url",

        "url": "https://example.com",

        "keyword": "",

        "search_provider": "",

        "description": "",

        "status": "active",

        "created_time": None,

        "updated_time": None,
    }

    result = repository._to_model(
        row,
    )

    assert result.target_type == (
        "url"
    )

    assert result.url == (
        "https://example.com"
    )

    assert result.keyword == ""

    assert result.search_provider == ""


def test_to_model_none(
    repository,
):

    assert (
        repository._to_model(None)
        is None
    )


# ============================================================
#
# Backward Compatibility
#
# ============================================================


def test_to_model_without_new_fields(
    repository,
):

    """
    確認舊版 targets row
    沒有 keyword / search_provider 時，
    Repository 不會直接崩潰。
    """

    row = {

        "id": 20,

        "name": "Legacy",

        "target_type": "url",

        "url": "https://example.com",

        "description": "",

        "status": "active",

        "created_time": None,

        "updated_time": None,
    }

    result = repository._to_model(
        row,
    )

    assert result is not None

    assert result.keyword == ""

    assert result.search_provider == ""