"""
tests/V7_6/test_rag_7_4_groq.py

AutoSearch V7

RAG-7.4

Real Groq Functional Test

測試完整 RAG Generation Flow：

RAG-5 Retriever
    ↓
RAG-6 ContextBuilder
    ↓
RAG-7.2 PromptBuilder
    ↓
RAG-7.3 Final Prompt
    ↓
RAG-7.4 LLMInvoker
    ↓
LLMClient
    ↓
Groq
    ↓
Real LLM Response
"""

from rag.retrieval_context import RetrievalContext
from rag.generation.prompt_builder import PromptBuilder
from rag.generation.llm_invoker import LLMInvoker


def main():
    print("=" * 70)
    print("RAG-7.4 REAL GROQ FUNCTIONAL TEST")
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
    # 3. RAG-7.2 Prompt Construction
    # ==================================================

    print("\n[3] Build RAG-7.2 Final Prompt")

    prompt_builder = PromptBuilder()

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
    print(f"Prompt Length : {len(final_prompt)}")

    # ==================================================
    # 4. RAG-7.4 LLMInvoker
    # ==================================================

    print("\n[4] Initialize RAG-7.4 LLMInvoker")

    llm_invoker = LLMInvoker()

    print("[PASS] LLMInvoker initialized")

    # ==================================================
    # 5. Real Groq Invocation
    # ==================================================

    print("\n[5] Send real request to Groq")

    response = llm_invoker.invoke(final_prompt)

    if not isinstance(response, str):
        raise AssertionError(
            "LLM Response must be a string"
        )

    if not response.strip():
        raise AssertionError(
            "LLM Response cannot be empty"
        )

    print("[PASS] Groq invocation succeeded")

    # ==================================================
    # 6. Display LLM Response
    # ==================================================

    print("\n[6] LLM Response")
    print("-" * 70)
    print(response)
    print("-" * 70)

    # ==================================================
    # 7. Functional Validation
    # ==================================================

    print("\n[7] RAG-7.4 Functional Validation")

    print("[PASS] RAG-5 Retrieval")
    print("[PASS] RAG-6 Context Building")
    print("[PASS] RAG-7.2 Prompt Construction")
    print("[PASS] RAG-7.3 Context + Query → Prompt")
    print("[PASS] RAG-7.4 LLMInvoker")
    print("[PASS] LLMClient")
    print("[PASS] Groq API Request")
    print("[PASS] Non-empty LLM Response")

    print("\n" + "=" * 70)
    print("RAG-7.4 REAL GROQ FUNCTIONAL TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()