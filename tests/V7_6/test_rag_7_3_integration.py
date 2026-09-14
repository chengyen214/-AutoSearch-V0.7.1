"""
tests/V7_6/test_rag_7_3_integration.py

AutoSearch V7

RAG-7.3

Context + Query → Prompt Integration Test

測試流程：

RAG-5 Retriever
    ↓
RAG-6 ContextBuilder
    ↓
User Query + Context
    ↓
RAG-7.2 PromptBuilder
    ↓
Final Prompt
"""

from rag.retrieval_context import RetrievalContext
from rag.generation.prompt_builder import PromptBuilder


def main():
    print("=" * 70)
    print("RAG-7.3 CONTEXT + QUERY → PROMPT INTEGRATION TEST")
    print("=" * 70)

    # ==================================================
    # 1. Initialize RAG-5 → RAG-6
    # ==================================================

    print("\n[1] Initialize RAG Retrieval Context")

    retrieval_context = RetrievalContext()

    print("[PASS] RetrievalContext initialized")

    # ==================================================
    # 2. Real RAG-6 Context
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
    # 3. Initialize PromptBuilder
    # ==================================================

    print("\n[3] Initialize RAG-7.2 PromptBuilder")

    prompt_builder = PromptBuilder()

    print("[PASS] PromptBuilder initialized")

    # ==================================================
    # 4. Context + Query → Prompt
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
    # 5. Validate Query Integration
    # ==================================================

    print("\n[5] Validate Query Integration")

    if query not in final_prompt:
        raise AssertionError(
            "User Query was not included in Final Prompt"
        )

    print("[PASS] User Query integrated")

    # ==================================================
    # 6. Validate Context Integration
    # ==================================================

    print("\n[6] Validate Context Integration")

    if context_text not in final_prompt:
        raise AssertionError(
            "Retrieved Context was not included in Final Prompt"
        )

    print("[PASS] Retrieved Context integrated")

    # ==================================================
    # 7. Validate Prompt Sections
    # ==================================================

    print("\n[7] Validate Prompt Sections")

    required_sections = [
        "User Query",
        "Retrieved Context",
        "Answer Instructions",
    ]

    for section in required_sections:
        if section not in final_prompt:
            raise AssertionError(
                f"Missing prompt section: {section}"
            )

        print(f"[PASS] {section}")

    # ==================================================
    # 8. Validate Context Size
    # ==================================================

    print("\n[8] Validate Context Preservation")

    if len(context_text) > 20000:
        raise AssertionError(
            "Context exceeds RAG-6 maximum context size"
        )

    print("[PASS] Context size preserved")

    # ==================================================
    # 9. Display Result Summary
    # ==================================================

    print("\n[9] Integration Result")

    print(f"Query Length        : {len(query)}")
    print(f"Context Length      : {len(context_text)}")
    print(f"Final Prompt Length : {len(final_prompt)}")

    # ==================================================
    # 10. Final Validation
    # ==================================================

    print("\n[10] RAG-7.3 Functional Validation")

    print("[PASS] RAG-5 Retrieval")
    print("[PASS] RAG-6 Context Building")
    print("[PASS] User Query")
    print("[PASS] Query + Context Integration")
    print("[PASS] PromptBuilder")
    print("[PASS] Final Prompt")

    print("\n" + "=" * 70)
    print("RAG-7.3 CONTEXT + QUERY → PROMPT INTEGRATION TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()