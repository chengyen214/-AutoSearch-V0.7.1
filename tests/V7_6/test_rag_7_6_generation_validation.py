"""
tests/V7_6/test_rag_7_6_generation_validation.py

AutoSearch V7

RAG-7.6

RAG-5 → RAG-6 → RAG-7.2 → RAG-7.4 → RAG-7.5 → RAG-7.6

Generation Validation

不使用 Mock。
使用目前實際：

    RetrievalContext
    PromptBuilder
    LLMInvoker
    AnswerGenerator
    ChromaDB
    Groq LLM
"""

import re

from rag.retrieval_context import RetrievalContext
from rag.generation.prompt_builder import PromptBuilder
from rag.generation.llm_invoker import LLMInvoker
from rag.generation.answer_generator import AnswerGenerator


# ============================================================
# Test Query
# ============================================================

TEST_QUERY = (
    "請整理 2026 年 9 月半導體產業的重要發展，"
    "列出主要事件，並說明這些事件對台灣半導體產業可能造成的影響。"
)


# ============================================================
# Validation Helpers
# ============================================================

def validate_answer_text(answer_text):
    """
    RAG-7.6.1

    Validate generated answer.
    """

    assert isinstance(
        answer_text,
        str,
    )

    assert len(
        answer_text.strip()
    ) > 0

    print(
        "[PASS] Answer Text exists"
    )

    print(
        "[PASS] Answer Text is non-empty"
    )


def validate_source_references(
    source_references,
    context,
):
    """
    RAG-7.6.2

    Validate Source References structure
    and mapping to RAG-6 Context.
    """

    assert isinstance(
        source_references,
        list,
    )

    print(
        f"[PASS] Source References is list "
        f"({len(source_references)} source(s))"
    )

    context_source_indexes = {
        entry["source_index"]
        for entry in context["entries"]
    }

    for source in source_references:

        assert isinstance(
            source,
            dict,
        )

        required_fields = [
            "source_index",
            "document_id",
            "chunk_index",
            "title",
            "url",
        ]

        for field in required_fields:

            assert field in source, (
                f"Source Reference missing field: "
                f"{field}"
            )

        source_index = source[
            "source_index"
        ]

        assert isinstance(
            source_index,
            int,
        )

        assert (
            source_index
            in context_source_indexes
        ), (
            f"Invalid Source Reference: "
            f"{source_index}"
        )

        print(
            f"[PASS] Source {source_index} "
            f"maps to RAG-6 Context"
        )


def validate_answer_citations(
    answer_text,
    context,
):
    """
    RAG-7.6.3

    Validate [Source N] citations appearing
    inside the generated answer.
    """

    source_pattern = re.compile(
        r"\[Source\s+(\d+)\]",
        re.IGNORECASE,
    )

    cited_sources = {
        int(index)
        for index in source_pattern.findall(
            answer_text
        )
    }

    context_source_indexes = {
        entry["source_index"]
        for entry in context["entries"]
    }

    print(
        f"[INFO] Answer cited Source(s): "
        f"{sorted(cited_sources)}"
    )

    for source_index in cited_sources:

        assert (
            source_index
            in context_source_indexes
        ), (
            f"Answer contains invalid "
            f"[Source {source_index}]"
        )

        print(
            f"[PASS] [Source {source_index}] "
            f"exists in RAG-6 Context"
        )


def validate_source_consistency(
    answer_text,
    source_references,
):
    """
    RAG-7.6.4

    Validate that parsed Source References
    correspond to citations in the answer.

    If the LLM does not explicitly cite
    [Source N], source_references may be empty.
    """

    source_pattern = re.compile(
        r"\[Source\s+(\d+)\]",
        re.IGNORECASE,
    )

    cited_sources = {
        int(index)
        for index in source_pattern.findall(
            answer_text
        )
    }

    referenced_sources = {
        source["source_index"]
        for source in source_references
    }

    print(
        f"[INFO] Answer citations: "
        f"{sorted(cited_sources)}"
    )

    print(
        f"[INFO] Parsed references: "
        f"{sorted(referenced_sources)}"
    )

    if cited_sources:

        assert cited_sources == referenced_sources, (
            "Answer citations and parsed "
            "source references do not match"
        )

        print(
            "[PASS] Answer citations and "
            "Source References are consistent"
        )

    else:

        assert not referenced_sources, (
            "Source References exist even though "
            "answer contains no [Source N] citation"
        )

        print(
            "[INFO] No explicit [Source N] "
            "citations in answer"
        )


def validate_generation_result(
    result,
):
    """
    RAG-7.6.5

    Validate final RAG-7.5 result structure.
    """

    assert isinstance(
        result,
        dict,
    )

    assert "answer_text" in result
    assert "source_references" in result

    assert isinstance(
        result["answer_text"],
        str,
    )

    assert isinstance(
        result["source_references"],
        list,
    )

    print(
        "[PASS] Generation Result structure valid"
    )


# ============================================================
# Real Integration Test
# ============================================================

def test_rag_7_6_generation_validation():

    print("=" * 70)
    print(
        "RAG-7.6 GENERATION VALIDATION TEST"
    )
    print("=" * 70)

    print()
    print(
        f"User Query: {TEST_QUERY}"
    )

    # ========================================================
    # RAG-5 → RAG-6
    # ========================================================

    print()
    print(
        "[1] Running RAG-5 → RAG-6..."
    )

    retrieval_context = RetrievalContext()

    context = retrieval_context.build(
        TEST_QUERY
    )

    assert isinstance(
        context,
        dict,
    )

    assert "entries" in context
    assert "context_text" in context
    assert "count" in context

    assert context["count"] > 0
    assert len(
        context["entries"]
    ) > 0

    print(
        f"[PASS] RAG-6 Context contains "
        f"{context['count']} source(s)"
    )

    # ========================================================
    # RAG-7.2
    # ========================================================

    print()
    print(
        "[2] Running RAG-7.2 Prompt Construction..."
    )

    prompt_builder = PromptBuilder()

    prompt = prompt_builder.build(
        query=TEST_QUERY,
        context=context,
    )

    assert isinstance(
        prompt,
        str,
    )

    assert len(
        prompt.strip()
    ) > 0

    assert TEST_QUERY in prompt
    assert context["context_text"] in prompt

    print(
        f"[PASS] Prompt generated "
        f"({len(prompt)} characters)"
    )

    # ========================================================
    # RAG-7.4
    # ========================================================

    print()
    print(
        "[3] Running RAG-7.4 LLM Invocation..."
    )

    llm_invoker = LLMInvoker()

    llm_response = llm_invoker.invoke(
        prompt
    )

    assert isinstance(
        llm_response,
        str,
    )

    assert len(
        llm_response.strip()
    ) > 0

    print(
        "[PASS] LLM Response received"
    )

    # ========================================================
    # RAG-7.5
    # ========================================================

    print()
    print(
        "[4] Running RAG-7.5 Answer Generation..."
    )

    answer_generator = AnswerGenerator()

    result = answer_generator.generate(
        llm_response=llm_response,
        context=context,
    )

    validate_generation_result(
        result
    )

    answer_text = result[
        "answer_text"
    ]

    source_references = result[
        "source_references"
    ]

    # ========================================================
    # RAG-7.6.1
    # ========================================================

    print()
    print(
        "-" * 70
    )
    print(
        "RAG-7.6.1 Answer Text Validation"
    )
    print(
        "-" * 70
    )

    validate_answer_text(
        answer_text
    )

    # ========================================================
    # RAG-7.6.2
    # ========================================================

    print()
    print(
        "-" * 70
    )
    print(
        "RAG-7.6.2 Source Reference Validation"
    )
    print(
        "-" * 70
    )

    validate_source_references(
        source_references,
        context,
    )

    # ========================================================
    # RAG-7.6.3
    # ========================================================

    print()
    print(
        "-" * 70
    )
    print(
        "RAG-7.6.3 Answer Citation Validation"
    )
    print(
        "-" * 70
    )

    validate_answer_citations(
        answer_text,
        context,
    )

    # ========================================================
    # RAG-7.6.4
    # ========================================================

    print()
    print(
        "-" * 70
    )
    print(
        "RAG-7.6.4 Answer ↔ Source Consistency"
    )
    print(
        "-" * 70
    )

    validate_source_consistency(
        answer_text,
        source_references,
    )

    # ========================================================
    # Display Final Answer
    # ========================================================

    print()
    print("=" * 70)
    print(
        "FINAL ANSWER"
    )
    print("=" * 70)

    print(
        answer_text
    )

    # ========================================================
    # Final
    # ========================================================

    print()
    print("=" * 70)
    print(
        "RAG-7.6 GENERATION VALIDATION PASSED"
    )
    print("=" * 70)


# ============================================================
# Main
# ============================================================

def main():

    test_rag_7_6_generation_validation()


if __name__ == "__main__":
    main()