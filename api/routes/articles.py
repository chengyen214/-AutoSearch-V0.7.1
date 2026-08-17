"""
api/routes/articles.py

AutoSearch V4

P3.2.2

Article API Router


功能:

    FastAPI Article API


支援:

    Article Query

    Article Search

    Article Management

    AI Retrieval

    Article Health Check


API:

    GET     /articles/
    GET     /articles/{id}

    GET     /articles/search/keyword/{keyword}
    GET     /articles/search/source/{source}

    GET     /articles/ai/importance/{level}
    GET     /articles/ai/category/{category}
    GET     /articles/ai/keyword/{keyword}
    GET     /articles/ai/top

    PUT     /articles/{id}

    DELETE  /articles/{id}

    GET     /articles/health/check


P3.2.2 Article Management API Enhancement:

    Update Article Metadata

    JSON Request Body

    Request Validation

    Delete Article

    Archive Protection


注意:

    Article Management API 不直接修改:

        document_id
        content
        AI Analysis
        Archive Data

    Delete 會受到 Knowledge Archive
    / Archive Pipeline 關聯保護。
"""


from fastapi import (
    APIRouter,
    HTTPException
)


from services.article_service import (
    ArticleService
)


from models.article_update import (
    ArticleUpdateRequest
)


from utils.logger import (
    logger
)


# ==================================================
# Router
# ==================================================

router = APIRouter(

    prefix="/articles",

    tags=[
        "Article API"
    ]

)


# ==================================================
# Service
# ==================================================

service = ArticleService()


# ==================================================
# GET ALL
# ==================================================

@router.get("/")
def get_articles(
    limit: int = 20
):
    """
    取得文章列表。

    Example:

        GET /articles/?limit=10
    """

    # ==============================================
    # Validate Limit
    # ==============================================

    if limit <= 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "limit must be greater than 0"
            )

        )

    # ==============================================
    # Query
    # ==============================================

    try:

        return service.get_all(
            limit
        )

    except Exception as e:

        logger.exception(
            f"Get articles API failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to retrieve articles"

        )


# ==================================================
# SEARCH KEYWORD
#
# 注意:
#
# 必須位於 /{article_id} 前面。
#
# ==================================================

@router.get(
    "/search/keyword/{keyword}"
)
def search_keyword(
    keyword: str
):
    """
    搜尋文章 Keyword。

    Example:

        GET /articles/search/keyword/TSMC
    """

    if not keyword.strip():

        raise HTTPException(

            status_code=400,

            detail="keyword cannot be empty"

        )

    try:

        return service.get_by_keyword(
            keyword
        )

    except Exception as e:

        logger.exception(
            f"Keyword search failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Keyword search failed"

        )


# ==================================================
# SEARCH SOURCE
# ==================================================

@router.get(
    "/search/source/{source}"
)
def search_source(
    source: str
):
    """
    依 Article Source 查詢。

    Example:

        GET /articles/search/source/CNA
    """

    if not source.strip():

        raise HTTPException(

            status_code=400,

            detail="source cannot be empty"

        )

    try:

        return service.get_by_source(
            source
        )

    except Exception as e:

        logger.exception(
            f"Source search failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Source search failed"

        )


# ==================================================
# AI IMPORTANCE
# ==================================================

@router.get(
    "/ai/importance/{level}"
)
def ai_importance(
    level: int
):
    """
    AI 重要度查詢。

    回傳:

        ai_importance >= level

    Example:

        GET /articles/ai/importance/8
    """

    if level < 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "level must be greater than "
                "or equal to 0"
            )

        )

    try:

        return service.get_by_importance(
            level
        )

    except Exception as e:

        logger.exception(
            f"AI importance search failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="AI importance search failed"

        )


# ==================================================
# AI CATEGORY
# ==================================================

@router.get(
    "/ai/category/{category}"
)
def ai_category(
    category: str
):
    """
    AI 分類查詢。

    Example:

        GET /articles/ai/category/Semiconductor
    """

    if not category.strip():

        raise HTTPException(

            status_code=400,

            detail="category cannot be empty"

        )

    try:

        return service.get_by_category(
            category
        )

    except Exception as e:

        logger.exception(
            f"AI category search failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="AI category search failed"

        )


# ==================================================
# AI KEYWORD
# ==================================================

@router.get(
    "/ai/keyword/{keyword}"
)
def ai_keyword(
    keyword: str
):
    """
    AI Keyword Retrieval。

    Example:

        GET /articles/ai/keyword/CoWoS
    """

    if not keyword.strip():

        raise HTTPException(

            status_code=400,

            detail="keyword cannot be empty"

        )

    try:

        return service.get_by_ai_keyword(
            keyword
        )

    except Exception as e:

        logger.exception(
            f"AI keyword search failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="AI keyword search failed"

        )


# ==================================================
# AI TOP
# ==================================================

@router.get(
    "/ai/top"
)
def ai_top(
    limit: int = 10
):
    """
    AI Importance Ranking。

    Example:

        GET /articles/ai/top?limit=5
    """

    if limit <= 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "limit must be greater than 0"
            )

        )

    try:

        return service.get_ai_top(
            limit
        )

    except Exception as e:

        logger.exception(
            f"AI top query failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="AI top query failed"

        )


# ==================================================
# HEALTH CHECK
#
# 必須位於 /{article_id} 前面。
#
# ==================================================

@router.get(
    "/health/check"
)
def health_check():
    """
    Article API Health Check。
    """

    return {

        "status": "ok",

        "service":
            "AutoSearch V4 Article API",

        "version":
            "P3.2.2"

    }


# ==================================================
# GET BY ID
#
# 必須位於所有固定 GET Route 之後。
#
# ==================================================

@router.get(
    "/{article_id}"
)
def get_article_by_id(
    article_id: int
):
    """
    使用 ID 查詢文章。

    Example:

        GET /articles/123
    """

    if article_id <= 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "article_id must be greater than 0"
            )

        )

    try:

        result = service.get_by_id(
            article_id
        )

    except Exception as e:

        logger.exception(
            f"Get article failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to retrieve article"

        )

    if result is None:

        raise HTTPException(

            status_code=404,

            detail="Article not found"

        )

    return result


# ==================================================
# UPDATE ARTICLE
#
# P3.2.2 Article Management API
#
# PUT /articles/{article_id}
#
# Request Body:
#
# {
#     "title": "Updated Article",
#     "source": "CNA"
# }
#
# 可修改:
#
#     keyword
#     title
#     url
#     source
#     published
#     status
#
# 不修改:
#
#     id
#     document_id
#     content
#     AI fields
#     archive data
#
# ==================================================

@router.put(
    "/{article_id}"
)
def update_article(
    article_id: int,
    request: ArticleUpdateRequest
):
    """
    更新 Article Metadata。

    Example:

        PUT /articles/123

    Request Body:

        {
            "title": "Updated Article",
            "source": "CNA"
        }

    注意:

        此 API 只允許修改
        Article Metadata。
    """

    # ==============================================
    # Validate ID
    # ==============================================

    if article_id <= 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "article_id must be greater than 0"
            )

        )

    # ==============================================
    # Validate Request
    #
    # 至少需要一個欄位
    #
    # exclude_unset=True:
    #
    # {} -> 空
    #
    # {"title": null}
    # -> title 被明確設定為 None
    #
    # ==============================================

    update_data = request.model_dump(
        exclude_unset=True
    )

    if not update_data:

        raise HTTPException(

            status_code=400,

            detail=(
                "At least one field must be provided"
            )

        )

    # ==============================================
    # Check Article
    # ==============================================

    try:

        article = service.get_by_id(
            article_id
        )

    except Exception as e:

        logger.exception(
            f"Get article before update failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to retrieve article"

        )

    if article is None:

        raise HTTPException(

            status_code=404,

            detail="Article not found"

        )

    # ==============================================
    # Update
    # ==============================================

    try:

        result = service.update_article(

            article_id=article_id,

            keyword=update_data.get(
                "keyword"
            ),

            title=update_data.get(
                "title"
            ),

            url=update_data.get(
                "url"
            ),

            source=update_data.get(
                "source"
            ),

            published=update_data.get(
                "published"
            ),

            status=update_data.get(
                "status"
            )

        )

    except AttributeError:

        logger.exception(
            "ArticleService.update_article() "
            "not implemented."
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Article update service unavailable"
            )

        )

    except Exception as e:

        logger.exception(
            f"Article update API failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Article update failed"

        )

    # ==============================================
    # Update Failed
    # ==============================================

    if result is None or result is False:

        raise HTTPException(

            status_code=400,

            detail="Article update failed"

        )

    # ==============================================
    # Success
    # ==============================================

    return {

        "status": "success",

        "message": "Article updated",

        "article_id": article_id,

        "article": result

    }


# ==================================================
# DELETE ARTICLE
#
# P3.2.2 Article Management API
#
# DELETE /articles/{article_id}
#
# Archive Protection:
#
#     archive_versions
#     raw_documents
#     ai_tasks
#     knowledge_archive
#
# 目前 Repository 已經提供
# Archive Protection。
#
# P3.2.2 此階段先維持既有
# Service / Repository 行為。
#
# 詳細 Protection Response
# 下一階段再獨立強化。
#
# ==================================================

@router.delete(
    "/{article_id}"
)
def delete_article(
    article_id: int
):
    """
    Delete Article。

    Example:

        DELETE /articles/123

    Archive Protection:

        如果 Article 已存在 Archive
        或 Pipeline 關聯資料，

        則拒絕刪除。
    """

    # ==============================================
    # Validate ID
    # ==============================================

    if article_id <= 0:

        raise HTTPException(

            status_code=400,

            detail=(
                "article_id must be greater than 0"
            )

        )

    # ==============================================
    # Check Article
    # ==============================================

    try:

        article = service.get_by_id(
            article_id
        )

    except Exception as e:

        logger.exception(
            f"Get article before delete failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Failed to retrieve article"

        )

    if article is None:

        raise HTTPException(

            status_code=404,

            detail="Article not found"

        )

    # ==============================================
    # Delete
    # ==============================================

    try:

        result = service.delete_article(
            article_id
        )

    except AttributeError:

        logger.exception(
            "ArticleService.delete_article() "
            "not implemented."
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Article delete service unavailable"
            )

        )

    except Exception as e:

        logger.exception(
            f"Article delete API failed: {e}"
        )

        raise HTTPException(

            status_code=500,

            detail="Article delete failed"

        )

    # ==============================================
    # Delete Failed
    #
    # 可能原因:
    #
    # Article 不存在
    # Archive Protection
    # Pipeline Protection
    # Database Error
    #
    # ==============================================

    if result is False:

        raise HTTPException(

            status_code=409,

            detail=(
                "Article cannot be deleted. "
                "Archive or pipeline related "
                "data exists."
            )

        )

    # ==============================================
    # Success
    # ==============================================

    return {

        "status": "success",

        "message": "Article deleted",

        "article_id": article_id

    }