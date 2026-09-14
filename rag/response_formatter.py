"""
rag/response_formatter.py

AutoSearch V7

RAG-8

Response Formatting

將 RAG-7 的生成結果整理成
使用者端可直接使用的 Response。
"""


class ResponseFormatter:

    def format(self, result: dict) -> dict:

        if not isinstance(result, dict):
            raise TypeError(
                "RAG result must be a dict."
            )

        if "answer_text" not in result:
            raise ValueError(
                "RAG result missing 'answer_text'."
            )

        if "source_references" not in result:
            raise ValueError(
                "RAG result missing 'source_references'."
            )

        answer = result["answer_text"]
        source_references = result["source_references"]

        if not isinstance(answer, str):
            raise TypeError(
                "'answer_text' must be a string."
            )

        if not answer.strip():
            raise ValueError(
                "'answer_text' cannot be empty."
            )

        if not isinstance(source_references, list):
            raise TypeError(
                "'source_references' must be a list."
            )

        sources = []

        for source in source_references:

            sources.append(
                {
                    "source_index": source["source_index"],
                    "title": source["title"],
                    "url": source["url"],
                }
            )

        return {
            "answer": answer,
            "sources": sources,
        }