"""
tests/V7_6/test_context_formatter.py

AutoSearch V7

RAG-6.2

Context Formatter Functional Test

測試：

    RAG-5 RetrievalResult
            ↓
    ContextFormatter
            ↓
    Context
"""

from rag.context.config import (
    MAX_CONTEXT_CHUNKS,
    MAX_CONTEXT_CHARACTERS,
)

from rag.context.formatter import (
    ContextFormatter,
)

from rag.retriever.retrieval_result import (
    RetrievalResult,
)


# ============================================================
# Test Data
# ============================================================

def create_test_results():
    return [
        RetrievalResult(
            chunk="台灣半導體產業目前持續受到 AI 需求帶動。",
            distance=0.4557,
            similarity=None,
            document_id="101",
            chunk_index=0,
            metadata={
                "title": "台灣半導體產業分析",
                "url": "https://example.com/article/101",
            },
        ),
        RetrievalResult(
            chunk="2026 年 IC 產業仍受到先進製程需求影響。",
            distance=0.4821,
            similarity=None,
            document_id="102",
            chunk_index=1,
            metadata={
                "title": "2026 IC 產業展望",
                "url": "https://example.com/article/102",
            },
        ),
        RetrievalResult(
            chunk="台灣半導體供應鏈持續進行產能與技術布局。",
            distance=0.4852,
            similarity=None,
            document_id="103",
            chunk_index=2,
            metadata={
                "title": "台灣半導體供應鏈",
                "url": "https://example.com/article/103",
            },
        ),
        RetrievalResult(
            chunk="全球半導體市場在 2026 年維持成長。",
            distance=0.4873,
            similarity=None,
            document_id="104",
            chunk_index=0,
            metadata={
                "title": "2026 全球半導體展望",
                "url": "https://example.com/article/104",
            },
        ),
        RetrievalResult(
            chunk="AI 與 HPC 應用持續增加半導體需求。",
            distance=0.4906,
            similarity=None,
            document_id="105",
            chunk_index=3,
            metadata={
                "title": "AI Semiconductor Demand",
                "url": "https://example.com/article/105",
            },
        ),
    ]


# ============================================================
# Test 1
# ============================================================

def test_context_formatter_basic():
    results = create_test_results()

    formatter = ContextFormatter()

    context = formatter.format(results)

    assert isinstance(
        context,
        dict,
    )

    assert "entries" in context
    assert "context_text" in context
    assert "count" in context


# ============================================================
# Test 2
# ============================================================

def test_context_entry_count():
    results = create_test_results()

    formatter = ContextFormatter()

    context = formatter.format(results)

    assert context["count"] == 5
    assert len(context["entries"]) == 5

    assert context["count"] == MAX_CONTEXT_CHUNKS


# ============================================================
# Test 3
# ============================================================

def test_context_entry_fields():
    results = create_test_results()

    formatter = ContextFormatter()

    context = formatter.format(results)

    entry = context["entries"][0]

    assert entry["source_index"] == 1

    assert entry["document_id"] == "101"

    assert entry["chunk_index"] == 0

    assert entry["title"] == (
        "台灣半導體產業分析"
    )

    assert entry["url"] == (
        "https://example.com/article/101"
    )

    assert entry["content"] == (
        "台灣半導體產業目前持續受到 AI 需求帶動。"
    )


# ============================================================
# Test 4
# ============================================================

def test_context_source_order():
    results = create_test_results()

    formatter = ContextFormatter()

    context = formatter.format(results)

    entries = context["entries"]

    expected_document_ids = [
        "101",
        "102",
        "103",
        "104",
        "105",
    ]

    actual_document_ids = [
        entry["document_id"]
        for entry in entries
    ]

    assert actual_document_ids == (
        expected_document_ids
    )


# ============================================================
# Test 5
# ============================================================

def test_context_text():
    results = create_test_results()

    formatter = ContextFormatter()

    context = formatter.format(results)

    context_text = context["context_text"]

    assert isinstance(
        context_text,
        str,
    )

    assert "[Source 1]" in context_text

    assert "台灣半導體產業分析" in context_text

    assert "台灣半導體產業目前持續受到 AI 需求帶動。" in (
        context_text
    )

    assert "[Source 5]" in context_text

    assert "AI Semiconductor Demand" in context_text


# ============================================================
# Test 6
# ============================================================

def test_context_max_chunks():
    results = create_test_results()

    # 額外加入超過 TOP-K 的結果
    results.extend(
        [
            RetrievalResult(
                chunk="Extra chunk 1",
                distance=0.60,
                similarity=None,
                document_id="106",
                chunk_index=0,
                metadata={
                    "title": "Extra 1",
                    "url": "https://example.com/106",
                },
            ),
            RetrievalResult(
                chunk="Extra chunk 2",
                distance=0.70,
                similarity=None,
                document_id="107",
                chunk_index=0,
                metadata={
                    "title": "Extra 2",
                    "url": "https://example.com/107",
                },
            ),
        ]
    )

    formatter = ContextFormatter()

    context = formatter.format(results)

    assert context["count"] == (
        MAX_CONTEXT_CHUNKS
    )

    assert len(context["entries"]) == (
        MAX_CONTEXT_CHUNKS
    )

    assert (
        context["entries"][-1]["document_id"]
        == "105"
    )


# ============================================================
# Test 7
# ============================================================

def test_context_character_limit():
    long_results = []

    for index in range(5):
        long_results.append(
            RetrievalResult(
                chunk="A" * 10000,
                distance=0.4 + index * 0.01,
                similarity=None,
                document_id=str(
                    200 + index
                ),
                chunk_index=0,
                metadata={
                    "title": f"Long Article {index}",
                    "url": (
                        f"https://example.com/{200 + index}"
                    ),
                },
            )
        )

    formatter = ContextFormatter()

    context = formatter.format(
        long_results
    )

    assert len(
        context["context_text"]
    ) <= MAX_CONTEXT_CHARACTERS


# ============================================================
# Test 8
# ============================================================

def test_context_empty_results():
    formatter = ContextFormatter()

    context = formatter.format([])

    assert context["entries"] == []

    assert context["count"] == 0

    assert context["context_text"] == ""


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("RAG-6.2 Context Formatter Functional Test")
    print("=" * 60)

    test_context_formatter_basic()
    print("[PASS] Basic Context Formatting")

    test_context_entry_count()
    print("[PASS] Context Entry Count")

    test_context_entry_fields()
    print("[PASS] Context Entry Fields")

    test_context_source_order()
    print("[PASS] Context Source Order")

    test_context_text()
    print("[PASS] Context Text")

    test_context_max_chunks()
    print("[PASS] Maximum Context Chunks")

    test_context_character_limit()
    print("[PASS] Maximum Context Characters")

    test_context_empty_results()
    print("[PASS] Empty RetrievalResult")

    print()
    print("RAG-6.2 CONTEXT FORMATTER TEST PASSED")


if __name__ == "__main__":
    main()