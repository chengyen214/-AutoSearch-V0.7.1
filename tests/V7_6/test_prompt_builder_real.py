"""
tests/V7_6/test_prompt_builder_real.py

AutoSearch V7

RAG-7.2

Prompt Builder Real Functional Test

測試流程：

RAGRetriever
    ↓
ContextBuilder
    ↓
PromptBuilder
    ↓
Final Prompt
"""

from rag.retrieval_context import RetrievalContext
from rag.generation.prompt_builder import PromptBuilder


def main():
    print("=" * 70)
    print("RAG-7.2 PROMPT BUILDER REAL FUNCTIONAL TEST")
    print("=" * 70)

    # ==================================================
    # 1. 建立 RAG-5 → RAG-6 Pipeline
    # ==================================================

    print("\n[1] Initialize RAG Retrieval Context")

    retrieval_context = RetrievalContext()

    print("[PASS] RetrievalContext initialized")

    # ==================================================
    # 2. 實際 Retrieval + Context Building
    # ==================================================

    query = "半導體產業目前有哪些重要趨勢？"

    print("\n[2] Build real RAG-6 Context")
    print(f"Query : {query}")

    context = retrieval_context.build(query)

    if not isinstance(context, dict):
        raise AssertionError(
            "RAG-6 Context must be a dictionary"
        )

    context_text = context.get("context_text")

    if not isinstance(context_text, str):
        raise AssertionError(
            "RAG-6 context_text must be a string"
        )

    if not context_text.strip():
        raise AssertionError(
            "RAG-6 context_text cannot be empty"
        )

    print("[PASS] Real RAG-6 context generated")
    print(f"Context Length : {len(context_text)}")
    print(f"Context Chunks : {context.get('count')}")

    # ==================================================
    # 3. 建立 PromptBuilder
    # ==================================================

    print("\n[3] Initialize PromptBuilder")

    prompt_builder = PromptBuilder()

    print("[PASS] PromptBuilder initialized")

    # ==================================================
    # 4. 實際建立 Final Prompt
    # ==================================================

    print("\n[4] Build Final Prompt")

    final_prompt = prompt_builder.build(
        query=query,
        context=context,
    )

    if not isinstance(final_prompt, str):
        raise AssertionError(
            "Final Prompt must be a string"
        )

    if not final_prompt.strip():
        raise AssertionError(
            "Final Prompt cannot be empty"
        )

    print("[PASS] Final Prompt generated")

    # ==================================================
    # 5. 驗證 Prompt 結構
    # ==================================================

    print("\n[5] Validate Prompt Structure")

    required_sections = [
        "User Query",
        query,
        "Retrieved Context",
        context_text,
        "Answer Instructions",
    ]

    for section in required_sections:
        if section not in final_prompt:
            raise AssertionError(
                f"Missing prompt section: {section}"
            )

    print("[PASS] User Query included")
    print("[PASS] Retrieved Context included")
    print("[PASS] Answer Instructions included")

    # ==================================================
    # 6. 顯示實際 Prompt
    # ==================================================

    print("\n[6] Final Prompt")
    print("-" * 70)
    print(final_prompt)
    print("-" * 70)

    # ==================================================
    # 7. 最終驗證
    # ==================================================

    print("\n[7] RAG-7.2 Functional Validation")

    print("[PASS] RAG-5 Retrieval")
    print("[PASS] RAG-6 Context Building")
    print("[PASS] User Query")
    print("[PASS] Retrieved Context")
    print("[PASS] Answer Instructions")
    print("[PASS] Final Prompt")

    print("\n" + "=" * 70)
    print("RAG-7.2 PROMPT BUILDER REAL FUNCTIONAL TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()