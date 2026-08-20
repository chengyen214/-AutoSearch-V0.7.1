"""
tests/P4-5/test_archive_service.py

AutoSearch V4

ArchiveService Integration Logic Test

驗證：

1. Raw HTML 儲存到 RawHTMLRepository
2. 不再建立本地 archive/html HTML File
3. RawDocument Metadata 正常建立
4. ArchiveVersion 正常建立
5. Duplicate Detection 使用 URL + File Hash
6. 相同 URL + 相同 HTML 不建立新的 Version
"""

from types import SimpleNamespace

import services.archive_service as archive_service_module

from services.archive_service import (
    ArchiveService,
)


# ============================================================
# Fake Raw HTML Repository
# ============================================================

class FakeRawHTMLRepository:

    def __init__(self):

        self.saved = []

    def save(
        self,
        article_id,
        document_id,
        url,
        html
    ):

        self.saved.append(
            {
                "article_id": article_id,
                "document_id": document_id,
                "url": url,
                "html": html,
            }
        )

        return "mongo-test-id-001"


# ============================================================
# Fake Raw Document Repository
# ============================================================

class FakeRawDocumentRepository:

    def __init__(self):

        self.saved = []

    def save(
        self,
        raw_document
    ):

        raw_document.id = 101

        self.saved.append(
            raw_document
        )

        return raw_document

    def get_by_url_and_file_hash(
        self,
        url,
        file_hash
    ):

        return None


# ============================================================
# Fake Archive Version Repository
# ============================================================

class FakeArchiveVersionRepository:

    def __init__(self):

        self.saved = []

    def get_by_url_and_file_hash(
        self,
        url,
        file_hash
    ):

        return None

    def get_next_version_number(
        self,
        article_id
    ):

        return 1

    def save(
        self,
        archive_version
    ):

        self.saved.append(
            archive_version
        )

        return archive_version

    def get_by_article_id(
        self,
        article_id
    ):

        return []

    def get_latest_version(
        self,
        article_id
    ):

        return None


# ============================================================
# Test Helper
# ============================================================

def create_service(
    monkeypatch
):

    fake_raw_html = (
        FakeRawHTMLRepository()
    )

    fake_raw_document = (
        FakeRawDocumentRepository()
    )

    fake_version = (
        FakeArchiveVersionRepository()
    )

    monkeypatch.setattr(
        archive_service_module,
        "RawHTMLRepository",
        lambda: fake_raw_html
    )

    monkeypatch.setattr(
        archive_service_module,
        "RawDocumentRepository",
        lambda: fake_raw_document
    )

    monkeypatch.setattr(
        archive_service_module,
        "ArchiveVersionRepository",
        lambda: fake_version
    )

    service = ArchiveService()

    return (
        service,
        fake_raw_html,
        fake_raw_document,
        fake_version,
    )


# ============================================================
# Test 1
# ============================================================

def test_archive_service_saves_raw_html_to_repository(
    monkeypatch
):

    (
        service,
        fake_raw_html,
        fake_raw_document,
        fake_version,
    ) = create_service(
        monkeypatch
    )

    html = (
        "<html>"
        "<body>"
        "<h1>AutoSearch V4</h1>"
        "</body>"
        "</html>"
    )

    result = service.save_html(
        article_id=1,
        url="https://example.com/article",
        html=html,
        document_id="doc-001",
    )

    # Archive Version 必須建立

    assert result is not None

    assert len(
        fake_version.saved
    ) == 1

    # MongoDB Raw HTML 必須收到資料

    assert len(
        fake_raw_html.saved
    ) == 1

    saved = (
        fake_raw_html.saved[0]
    )

    assert (
        saved["article_id"]
        == 1
    )

    assert (
        saved["document_id"]
        == "doc-001"
    )

    assert (
        saved["url"]
        == "https://example.com/article"
    )

    assert (
        saved["html"]
        == html
    )

    # MySQL RawDocument 必須建立

    assert len(
        fake_raw_document.saved
    ) == 1

    raw_document = (
        fake_raw_document.saved[0]
    )

    assert (
        raw_document.article_id
        == 1
    )

    assert (
        raw_document.original_url
        == "https://example.com/article"
    )

    assert (
        raw_document.storage_path
        == "mongodb://raw_html/mongo-test-id-001"
    )

    assert (
        raw_document.mime_type
        == "text/html"
    )


# ============================================================
# Test 2
# ============================================================

def test_archive_service_does_not_use_local_archive_html(
    monkeypatch,
    tmp_path
):

    (
        service,
        fake_raw_html,
        fake_raw_document,
        fake_version,
    ) = create_service(
        monkeypatch
    )

    # 將 archive_root 指到 pytest temporary directory。
    #
    # 如果 ArchiveService 還會寫本地 HTML，
    # 這裡就會產生檔案。

    service.archive_root = (
        tmp_path / "archive" / "html"
    )

    html = (
        "<html>"
        "<body>"
        "test local archive"
        "</body>"
        "</html>"
    )

    result = service.save_html(
        article_id=2,
        url="https://example.com/local-test",
        html=html,
        document_id="doc-local-test",
    )

    assert result is not None

    # 本地 archive/html 不應該被建立
    # 或至少不應該有 HTML Archive File。

    if (
        service.archive_root.exists()
    ):

        html_files = list(
            service.archive_root.rglob(
                "*.html"
            )
        )

        assert html_files == []


# ============================================================
# Test 3
# ============================================================

def test_archive_service_creates_version(
    monkeypatch
):

    (
        service,
        fake_raw_html,
        fake_raw_document,
        fake_version,
    ) = create_service(
        monkeypatch
    )

    result = service.save_html(
        article_id=10,
        url="https://example.com/version",
        html="<html>version 1</html>",
        document_id="doc-version-001",
    )

    assert result is not None

    assert len(
        fake_version.saved
    ) == 1

    version = (
        fake_version.saved[0]
    )

    assert (
        version.article_id
        == 10
    )

    assert (
        version.raw_document_id
        == 101
    )

    assert (
        version.version_number
        == 1
    )

    assert (
        version.storage_path
        == "mongodb://raw_html/mongo-test-id-001"
    )

    assert (
        version.mime_type
        == "text/html"
    )


# ============================================================
# Test 4
# ============================================================

def test_archive_service_duplicate_uses_url_and_hash(
    monkeypatch
):

    (
        service,
        fake_raw_html,
        fake_raw_document,
        fake_version,
    ) = create_service(
        monkeypatch
    )

    existing_version = (
        SimpleNamespace(
            article_id=999,
            version_number=5,
        )
    )

    # 模擬：
    #
    # URL + Hash 已經存在。
    #
    # 注意：
    # 不使用 article_id。

    def fake_find_existing_version(
        url,
        file_hash
    ):

        return existing_version

    monkeypatch.setattr(
        service,
        "_find_existing_version",
        fake_find_existing_version,
    )

    result = service.save_html(
        article_id=12345,
        url="https://example.com/duplicate",
        html="<html>duplicate</html>",
        document_id="doc-duplicate",
    )

    assert (
        result
        is existing_version
    )

    # Duplicate Detection 在最前面發現，
    # 所以不應該寫 MongoDB。

    assert (
        len(fake_raw_html.saved)
        == 0
    )

    # 也不應該建立 RawDocument。

    assert (
        len(fake_raw_document.saved)
        == 0
    )

    # 也不應該建立新的 Version。

    assert (
        len(fake_version.saved)
        == 0
    )


# ============================================================
# Test 5
# ============================================================

def test_archive_service_same_url_same_html_does_not_create_version(
    monkeypatch
):

    (
        service,
        fake_raw_html,
        fake_raw_document,
        fake_version,
    ) = create_service(
        monkeypatch
    )

    html = (
        "<html>"
        "<body>"
        "same content"
        "</body>"
        "</html>"
    )

    existing_version = (
        SimpleNamespace(
            article_id=1,
            version_number=1,
        )
    )

    call_count = {
        "count": 0
    }

    def fake_find_existing_version(
        url,
        file_hash
    ):

        call_count["count"] += 1

        # 第一次：
        # 尚未存在
        #
        # 第二次：
        # 已存在

        if call_count["count"] == 1:

            return None

        return existing_version

    monkeypatch.setattr(
        service,
        "_find_existing_version",
        fake_find_existing_version,
    )

    # --------------------------------------------------------
    # First Archive
    # --------------------------------------------------------

    first = service.save_html(
        article_id=1,
        url="https://example.com/same",
        html=html,
        document_id="doc-same-001",
    )

    assert first is not None

    assert (
        len(fake_version.saved)
        == 1
    )

    # --------------------------------------------------------
    # Second Archive
    # --------------------------------------------------------

    second = service.save_html(
        article_id=1,
        url="https://example.com/same",
        html=html,
        document_id="doc-same-002",
    )

    assert (
        second
        is existing_version
    )

    # 不應該建立第二個 Version。

    assert (
        len(fake_version.saved)
        == 1
    )


# ============================================================
# Test 6
# ============================================================

def test_archive_service_article_id_not_used_for_duplicate_detection(
    monkeypatch
):

    (
        service,
        fake_raw_html,
        fake_raw_document,
        fake_version,
    ) = create_service(
        monkeypatch
    )

    captured = {}

    def fake_find_existing_version(
        url,
        file_hash
    ):

        captured["url"] = url

        captured["file_hash"] = file_hash

        return None

    monkeypatch.setattr(
        service,
        "_find_existing_version",
        fake_find_existing_version,
    )

    result = service.save_html(
        article_id=987654,
        url="https://example.com/policy",
        html="<html>policy test</html>",
        document_id="doc-policy",
    )

    assert result is not None

    # Duplicate Detection API
    # 只收到：
    #
    #     url
    #     file_hash
    #
    # 沒有 article_id。

    assert (
        captured["url"]
        == "https://example.com/policy"
    )

    assert (
        captured["file_hash"]
    )

    assert (
        len(fake_version.saved)
        == 1
    )