"""
tests/V7/test_rag_content_cleaner.py

AutoSearch V7

RAG-1.1
RAG-1.4

Article Source + Content Cleaning Test

測試內容：

    1. 透過 MCP ArticleSource 真正取得 Article
    2. 取得既有 Parser 結果 Article.content
    3. ContentCleaner 清理 content
    4. 驗證換行標準化
    5. 驗證每行頭尾空白清理
    6. 驗證連續空白行清理
    7. 驗證正文內容沒有被任意刪除
    8. Invalid Content validation

實際資料流程：

    MCP
      ↓
    ArticleSource
      ↓
    Article.content
      ↓
    ContentCleaner
      ↓
    Clean Content

本階段不負責：

    1. Document Model
    2. Metadata
    3. Chunking
    4. Embedding
    5. ChromaDB
    6. Retriever
    7. LLM
"""


from rag.article_source import (
    ArticleSource
)

from rag.content_cleaner import (
    ContentCleaner
)


# ============================================================
# Test Article
# ============================================================

TEST_DOCUMENT_ID = (
    "d9ce4740c3f0b6f1d260c094c0549f68727187b0a2b57c94f6308b4df9fd9d13"
)


# ============================================================
# Get Real Article
# ============================================================

def get_real_article():
    """
    透過 MCP ArticleSource
    真正取得 Article。
    """

    source = ArticleSource()

    article = source.get_by_document_id(
        TEST_DOCUMENT_ID
    )

    assert article is not None, (
        "MCP ArticleSource returned no Article."
    )

    assert isinstance(
        article,
        dict
    ), (
        "MCP ArticleSource must return dict."
    )

    assert article.get(
        "content"
    ), (
        "Article content is missing."
    )

    return article


# ============================================================
# Test Real Article Content
# ============================================================

def test_real_article_content():
    """
    確認 ContentCleaner 使用的是
    MCP 真實取得的 Article.content。
    """

    article = get_real_article()

    content = article["content"]

    assert isinstance(
        content,
        str
    )

    assert content.strip()

    print(
        "PASS: Real MCP Article content retrieval"
    )

    print(
        f"      Document ID: "
        f"{article['document_id']}"
    )

    print(
        f"      Content length: "
        f"{len(content)}"
    )


# ============================================================
# Test Basic Cleaning
# ============================================================

def test_basic_cleaning():
    """
    測試基本 Content Cleaning。
    """

    article = get_real_article()

    original_content = article[
        "content"
    ]

    cleaned_content = ContentCleaner.clean(
        original_content
    )

    assert cleaned_content is not None

    assert isinstance(
        cleaned_content,
        str
    )

    assert cleaned_content.strip()

    print(
        "PASS: Basic content cleaning"
    )

    print(
        f"      Original length: "
        f"{len(original_content)}"
    )

    print(
        f"      Cleaned length: "
        f"{len(cleaned_content)}"
    )


# ============================================================
# Test Newline Normalization
# ============================================================

def test_newline_normalization():
    """
    測試換行標準化。
    """

    article = get_real_article()

    cleaned_content = ContentCleaner.clean(
        article["content"]
    )

    assert "\r" not in cleaned_content

    print(
        "PASS: Newline normalization"
    )


# ============================================================
# Test Consecutive Blank Lines
# ============================================================

def test_consecutive_blank_lines():
    """
    確認不會存在超過一個連續空白行。
    """

    article = get_real_article()

    cleaned_content = ContentCleaner.clean(
        article["content"]
    )

    assert "\n\n\n" not in cleaned_content

    print(
        "PASS: Consecutive blank line cleaning"
    )


# ============================================================
# Test Leading / Trailing Whitespace
# ============================================================

def test_whitespace_cleaning():
    """
    確認全文頭尾沒有多餘空白。
    """

    article = get_real_article()

    cleaned_content = ContentCleaner.clean(
        article["content"]
    )

    assert (
        cleaned_content
        == cleaned_content.strip()
    )

    for line in cleaned_content.split(
        "\n"
    ):

        assert (
            line
            == line.strip()
        )

    print(
        "PASS: Whitespace cleaning"
    )


# ============================================================
# Test Content Preservation
# ============================================================

def test_content_preservation():
    """
    確認 ContentCleaner
    沒有任意刪除原始正文文字。

    測試方式：

        將原始內容依換行拆開，
        對每一行做 strip 後，
        確認其文字仍存在於清理結果。

    注意：

        空白本身可以被標準化，
        但實際文字內容不應被刪除。
    """

    article = get_real_article()

    original_content = article[
        "content"
    ]

    cleaned_content = ContentCleaner.clean(
        original_content
    )

    original_lines = (
        original_content
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .split("\n")
    )

    meaningful_lines = []

    for line in original_lines:

        normalized_line = line.strip()

        if normalized_line:
            meaningful_lines.append(
                normalized_line
            )

    for line in meaningful_lines:

        assert line in cleaned_content, (
            "Content text was removed unexpectedly: "
            f"{line}"
        )

    print(
        "PASS: Content preservation"
    )


# ============================================================
# Test Sample Content
# ============================================================

def test_sample_content():
    """
    確認清理後內容仍保留
    真實文章的重要文字。
    """

    article = get_real_article()

    cleaned_content = ContentCleaner.clean(
        article["content"]
    )

    expected_texts = (
        "Navitas",
        "GaN",
        "AI",
        "半導體",
    )

    for text in expected_texts:

        assert text in cleaned_content, (
            f"Expected article text not found: {text}"
        )

    print(
        "PASS: Real content sample preservation"
    )


# ============================================================
# Test None Content
# ============================================================

def test_none_content():
    """
    測試 content=None。
    """

    try:

        ContentCleaner.clean(
            None
        )

    except ValueError:

        print(
            "PASS: None content validation"
        )

        return

    raise AssertionError(
        "None content should raise ValueError."
    )


# ============================================================
# Test Invalid Content Type
# ============================================================

def test_invalid_content_type():
    """
    測試 content 不是 str。
    """

    try:

        ContentCleaner.clean(
            12345
        )

    except TypeError:

        print(
            "PASS: Content type validation"
        )

        return

    raise AssertionError(
        "Non-string content should raise TypeError."
    )


# ============================================================
# Test Empty Content
# ============================================================

def test_empty_content():
    """
    測試空白 content。
    """

    try:

        ContentCleaner.clean(
            "   \n   "
        )

    except ValueError:

        print(
            "PASS: Empty content validation"
        )

        return

    raise AssertionError(
        "Empty content should raise ValueError."
    )


# ============================================================
# Test Artificial Formatting
# ============================================================

def test_artificial_formatting():
    """
    使用小型測試資料確認
    ContentCleaner 的格式標準化行為。
    """

    content = (
        "  第一段  \r\n"
        "\r\n"
        "\r\n"
        "  第二段  \r\n"
        "第三段   "
    )

    cleaned = ContentCleaner.clean(
        content
    )

    assert cleaned == (
        "第一段\n\n"
        "第二段\n"
        "第三段"
    )

    print(
        "PASS: Artificial formatting normalization"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-1.4 Content Cleaning Test。
    """

    print("=" * 60)
    print(
        "RAG-1.4 Content Cleaning Test"
    )
    print("=" * 60)

    print()

    print(
        "Testing real MCP Article content..."
    )

    print()

    test_real_article_content()

    print()

    test_basic_cleaning()

    test_newline_normalization()

    test_consecutive_blank_lines()

    test_whitespace_cleaning()

    test_content_preservation()

    test_sample_content()

    test_none_content()

    test_invalid_content_type()

    test_empty_content()

    test_artificial_formatting()

    print()

    print("=" * 60)
    print(
        "ALL RAG-1.4 CONTENT CLEANING TESTS PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()