"""
tests/P4-5/test_raw_html_model.py

AutoSearch V4

P4.5

RawHTML Model Test

測試:

1. RawHTML Model 建立
2. RawHTML → MongoDB Document
3. MongoDB Document → RawHTML
4. MongoDB _id 正確保留
5. HTML 本體與 Metadata 正確保留
"""

from datetime import datetime

from models.raw_html import RawHTML


# ======================================
# Test RawHTML Model
# ======================================

def test_raw_html_model():

    created_time = datetime.now()

    html = """
    <html>
        <body>
            <h1>AutoSearch V4</h1>
        </body>
    </html>
    """

    # ----------------------------------
    # 建立 Model
    # ----------------------------------

    raw_html = RawHTML(

        document_id="test-document-001",

        article_id=123,

        url="https://example.com/test",

        html=html,

        content_hash="abc123",

        mime_type="text/html",

        file_size=len(
            html.encode("utf-8")
        ),

        created_time=created_time

    )

    # ----------------------------------
    # Model 基本驗證
    # ----------------------------------

    assert (
        raw_html.document_id
        == "test-document-001"
    )

    assert (
        raw_html.article_id
        == 123
    )

    assert (
        raw_html.url
        == "https://example.com/test"
    )

    assert (
        raw_html.html
        == html
    )

    assert (
        raw_html.content_hash
        == "abc123"
    )

    assert (
        raw_html.mime_type
        == "text/html"
    )

    assert (
        raw_html.file_size
        == len(html.encode("utf-8"))
    )

    assert (
        raw_html.created_time
        == created_time
    )


# ======================================
# Test To Dict
# ======================================

def test_raw_html_to_dict():

    created_time = datetime.now()

    raw_html = RawHTML(

        document_id="test-document-002",

        article_id=456,

        url="https://example.com/article",

        html="<html>Test</html>",

        content_hash="hash456",

        mime_type="text/html",

        file_size=18,

        created_time=created_time

    )

    document = (
        raw_html.to_dict()
    )

    # ----------------------------------
    # MongoDB Document
    # ----------------------------------

    assert isinstance(
        document,
        dict
    )

    assert (
        document["document_id"]
        == "test-document-002"
    )

    assert (
        document["article_id"]
        == 456
    )

    assert (
        document["url"]
        == "https://example.com/article"
    )

    assert (
        document["html"]
        == "<html>Test</html>"
    )

    assert (
        document["content_hash"]
        == "hash456"
    )

    assert (
        document["mime_type"]
        == "text/html"
    )

    assert (
        document["file_size"]
        == 18
    )

    assert (
        document["created_time"]
        == created_time
    )

    # ----------------------------------
    # 新建立的 Model
    #
    # 尚未進 MongoDB
    #
    # 不應該有 _id
    # ----------------------------------

    assert "_id" not in document


# ======================================
# Test From Dict
# ======================================

def test_raw_html_from_dict():

    created_time = datetime.now()

    mongo_document = {

        "_id": "test-mongo-id",

        "document_id":
            "test-document-003",

        "article_id":
            789,

        "url":
            "https://example.com/news",

        "html":
            "<html><body>News</body></html>",

        "content_hash":
            "hash789",

        "mime_type":
            "text/html",

        "file_size":
            31,

        "created_time":
            created_time

    }

    raw_html = (
        RawHTML.from_dict(
            mongo_document
        )
    )

    # ----------------------------------
    # Model 還原
    # ----------------------------------

    assert isinstance(
        raw_html,
        RawHTML
    )

    assert (
        raw_html.mongo_id
        == "test-mongo-id"
    )

    assert (
        raw_html.document_id
        == "test-document-003"
    )

    assert (
        raw_html.article_id
        == 789
    )

    assert (
        raw_html.url
        == "https://example.com/news"
    )

    assert (
        raw_html.html
        == "<html><body>News</body></html>"
    )

    assert (
        raw_html.content_hash
        == "hash789"
    )

    assert (
        raw_html.mime_type
        == "text/html"
    )

    assert (
        raw_html.file_size
        == 31
    )

    assert (
        raw_html.created_time
        == created_time
    )


# ======================================
# Test Model Round Trip
# ======================================

def test_raw_html_round_trip():

    created_time = datetime.now()

    original = RawHTML(

        document_id="round-trip-001",

        article_id=999,

        url="https://example.com/round-trip",

        html="<html>Round Trip</html>",

        content_hash="round-trip-hash",

        mime_type="text/html",

        file_size=25,

        created_time=created_time

    )

    # ----------------------------------
    # Model
    # ↓
    # Dictionary
    # ----------------------------------

    document = (
        original.to_dict()
    )

    # ----------------------------------
    # Dictionary
    # ↓
    # Model
    # ----------------------------------

    restored = (
        RawHTML.from_dict(
            document
        )
    )

    # ----------------------------------
    # Verify
    # ----------------------------------

    assert (
        restored.document_id
        == original.document_id
    )

    assert (
        restored.article_id
        == original.article_id
    )

    assert (
        restored.url
        == original.url
    )

    assert (
        restored.html
        == original.html
    )

    assert (
        restored.content_hash
        == original.content_hash
    )

    assert (
        restored.mime_type
        == original.mime_type
    )

    assert (
        restored.file_size
        == original.file_size
    )

    assert (
        restored.created_time
        == original.created_time
    )


# ======================================
# Test None
# ======================================

def test_raw_html_from_dict_none():

    result = (
        RawHTML.from_dict(
            None
        )
    )

    assert result is None
