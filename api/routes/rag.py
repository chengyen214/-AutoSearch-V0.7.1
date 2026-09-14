"""
api/routes/rag.py

AutoSearch V7

RAG-8 FastAPI Web Integration

功能：

    GET  /rag
        顯示 RAG 問答 Web Page

    POST /rag/query
        執行 RAG Query

架構：

    Browser
        ↓
    FastAPI
        ↓
    RAGQuery
        ↓
    RAG-5 Retriever
        ↓
    RAG-6 Context Builder
        ↓
    RAG-7 LLM Generation
        ↓
    Response
"""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from rag.rag_query import RAGQuery


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


# ============================================================
# Templates
# ============================================================

templates = Jinja2Templates(
    directory="templates"
)


# ============================================================
# RAG Query
#
# 注意：
# 不在 FastAPI import 時立即初始化。
#
# Embedding Model / Chroma / RAG components
# 等到真正執行 /rag/query 時才初始化。
# ============================================================

_rag_query = None


def get_rag_query():
    global _rag_query

    if _rag_query is None:
        _rag_query = RAGQuery()

    return _rag_query


# ============================================================
# Request Model
# ============================================================

class RAGQueryRequest(BaseModel):
    query: str


# ============================================================
# RAG Web Page
# ============================================================

@router.get(
    "",
    include_in_schema=False,
)
def rag_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="rag/index.html",
        context={
            "project": "AutoSearch V7",
            "page": "RAG 問答",
        },
    )


# ============================================================
# RAG Query API
# ============================================================

@router.post(
    "/query",
)
def rag_query_api(
    request: RAGQueryRequest,
):

    query = request.query.strip()

    if not query:
        return {
            "answer": "",
            "sources": [],
            "error": "Query cannot be empty.",
        }

    rag = get_rag_query()

    result = rag.run(
        query
    )

    print("\n========== RAG API RESULT ==========")
    print("RESULT TYPE:", type(result))
    print("RESULT:", result)

    if isinstance(result, dict):
        print("ANSWER:", result.get("answer"))
        print("SOURCES:", result.get("sources"))
        print("SOURCE REFERENCES:", result.get("source_references"))

    print("====================================\n")

    return result