"""
tests/V7_6/test_rag_7_5_answer_only.py

RAG-7.5 Answer-Only Integration Test

目的：
    只驗證使用者輸入問題後，RAG Pipeline 最後產生的回答。

不顯示：
    - Retriever 找到的 Context
    - Chunk
    - Prompt
    - LLM Request
    - 中間 Pipeline 資訊

顯示：
    - User Query
    - 最終 Answer
    - Source References
"""

from rag.retrieval_context import RetrievalContext
from rag.generation.prompt_builder import PromptBuilder
from rag.generation.llm_invoker import LLMInvoker
from rag.generation.answer_generator import AnswerGenerator



TEST_QUERY = "請整理 2026 年 9 月半導體產業的重要發展，列出主要事件，並說明這些事件對台灣半導體產業可能造成的影響。"
def main():
    print("=" * 70)
    print("RAG ANSWER-ONLY TEST")
    print("=" * 70)

    print("\nUser Query:")
    print(TEST_QUERY)

    # ------------------------------------------------------------
    # RAG-5 → RAG-6
    # ------------------------------------------------------------
    retrieval_context = RetrievalContext()
    context = retrieval_context.build(TEST_QUERY)

    assert isinstance(context, dict)
    assert context.get("context_text")
    assert context.get("entries")

    # ------------------------------------------------------------
    # RAG-7.2
    # ------------------------------------------------------------
    prompt_builder = PromptBuilder()

    prompt = prompt_builder.build(
        query=TEST_QUERY,
        context=context,
    )

    assert isinstance(prompt, str)
    assert prompt.strip()

    # ------------------------------------------------------------
    # RAG-7.4
    # ------------------------------------------------------------
    llm_invoker = LLMInvoker()

    llm_response = llm_invoker.invoke(prompt)

    assert isinstance(llm_response, str)
    assert llm_response.strip()

    # ------------------------------------------------------------
    # RAG-7.5
    # ------------------------------------------------------------
    answer_generator = AnswerGenerator()

    result = answer_generator.generate(
        llm_response=llm_response,
        context=context,
    )

    assert isinstance(result, dict)

    answer_text = result.get("answer_text")
    source_references = result.get("source_references")

    assert isinstance(answer_text, str)
    assert answer_text.strip()

    assert isinstance(source_references, list)

    # ------------------------------------------------------------
    # ONLY SHOW FINAL RESULT
    # ------------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)

    print(answer_text)

    print("\n")
    print("=" * 70)
    print("SOURCE REFERENCES")
    print("=" * 70)

    if source_references:
        for source in source_references:
            print(
                f"[Source {source['source_index']}] "
                f"{source['title']}"
            )
            print(f"URL: {source['url']}")
            print()

    else:
        print("No source references.")

    print("=" * 70)
    print("RAG ANSWER-ONLY TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()