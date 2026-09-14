"""
tests/V7_6/test_rag_7_5_generation.py

AutoSearch V7

RAG-7.5

RAG-5 → RAG-6 → RAG-7.2 → RAG-7.4 → RAG-7.5
Real Integration Test

不使用 Mock。
使用目前實際：

    RAGRetriever
    ContextBuilder
    PromptBuilder
    LLMInvoker
    AnswerGenerator
    ChromaDB
    Groq LLM
"""

from rag.retrieval_context import RetrievalContext
from rag.generation.prompt_builder import PromptBuilder
from rag.generation.llm_invoker import LLMInvoker
from rag.generation.answer_generator import AnswerGenerator


# ============================================================
# Test Query
# ============================================================

TEST_QUERY = (
    "分析半導體產業目前的重要發展趨勢，"
    "並根據 Retrieved Context 說明主要變化。"
)


# ============================================================
# Real Integration Test
# ============================================================

def test_rag_7_5_real_integration():

    print("=" * 70)
    print(
        "RAG-5 → RAG-6 → RAG-7.2 → "
        "RAG-7.4 → RAG-7.5 REAL INTEGRATION TEST"
    )
    print("=" * 70)

    print()
    print(f"User Query: {TEST_QUERY}")

    # ========================================================
    # RAG-5 → RAG-6
    # ========================================================

    print()
    print("[1] Running RAG-5 → RAG-6...")

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
    assert len(context["entries"]) > 0

    print(
        f"[PASS] RAG-6 Context contains "
        f"{context['count']} source(s)"
    )

    # ========================================================
    # RAG-7.2 Prompt Construction
    # ========================================================

    print()
    print("[2] Running RAG-7.2 Prompt Construction...")

    prompt_builder = PromptBuilder()

    prompt = prompt_builder.build(
        query=TEST_QUERY,
        context=context,
    )

    assert isinstance(
        prompt,
        str,
    )

    assert len(prompt.strip()) > 0

    assert TEST_QUERY in prompt
    assert context["context_text"] in prompt

    print(
        f"[PASS] Final Prompt generated "
        f"({len(prompt)} characters)"
    )

    # ========================================================
    # RAG-7.4 LLM Invocation
    # ========================================================

    print()
    print("[3] Running RAG-7.4 LLM Invocation...")

    llm_invoker = LLMInvoker()

    llm_response = llm_invoker.invoke(
        prompt
    )

    assert isinstance(
        llm_response,
        str,
    )

    assert len(llm_response.strip()) > 0

    print(
        "[PASS] LLM Response received"
    )

    print()
    print("-" * 70)
    print("LLM Response")
    print("-" * 70)
    print(llm_response)

    # ========================================================
    # RAG-7.5 Answer Generation
    # ========================================================

    print()
    print("[4] Running RAG-7.5 Answer Generation...")

    answer_generator = AnswerGenerator()

    result = answer_generator.generate(
        llm_response=llm_response,
        context=context,
    )

    # ========================================================
    # Validate Result
    # ========================================================

    assert isinstance(
        result,
        dict,
    )

    assert "answer_text" in result
    assert "source_references" in result

    answer_text = result[
        "answer_text"
    ]

    source_references = result[
        "source_references"
    ]

    assert isinstance(
        answer_text,
        str,
    )

    assert len(
        answer_text.strip()
    ) > 0

    assert isinstance(
        source_references,
        list,
    )

    print(
        "[PASS] Answer Text generated"
    )

    print(
        f"[PASS] Source References: "
        f"{len(source_references)}"
    )

    # ========================================================
    # Display Answer
    # ========================================================

    print()
    print("=" * 70)
    print("RAG-7.5 Answer")
    print("=" * 70)

    print(
        answer_text
    )

    # ========================================================
    # Display Source References
    # ========================================================

    print()
    print("=" * 70)
    print("RAG-7.5 Source References")
    print("=" * 70)

    if not source_references:

        print(
            "[INFO] LLM Response did not explicitly "
            "reference any [Source N]."
        )

    else:

        for source in source_references:

            print()
            print(
                f"[Source "
                f"{source['source_index']}]"
            )

            print(
                f"Document ID : "
                f"{source['document_id']}"
            )

            print(
                f"Chunk Index : "
                f"{source['chunk_index']}"
            )

            print(
                f"Title       : "
                f"{source['title']}"
            )

            print(
                f"URL         : "
                f"{source['url']}"
            )

    # ========================================================
    # Source Reference Validation
    # ========================================================

    context_source_indexes = {
        entry["source_index"]
        for entry in context["entries"]
    }

    for source in source_references:

        assert (
            source["source_index"]
            in context_source_indexes
        )

    print()
    print(
        "[PASS] All source references "
        "map to RAG-6 Context"
    )

    # ========================================================
    # Final
    # ========================================================

    print()
    print("=" * 70)
    print(
        "RAG-7.5 REAL INTEGRATION TEST PASSED"
    )
    print("=" * 70)


# ============================================================
# Main
# ============================================================

def main():

    test_rag_7_5_real_integration()


if __name__ == "__main__":
    main()