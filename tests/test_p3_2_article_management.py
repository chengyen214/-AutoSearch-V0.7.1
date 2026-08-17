"""
tests/test_p3_2_article_management.py

AutoSearch V4

P3.2

Article Management Final Integration Test

測試範圍：

    P3.2.1
        Article Repository

    P3.2.2
        Article Management API

    P3.2.3
        Article Update Validation

    P3.2
        Article Query
        Article Search
        AI Retrieval
        Article Update
        Article Delete
        Archive Protection

執行：

    python -m pytest tests/test_p3_2_article_management.py -v
"""


from fastapi.testclient import TestClient


from api.main import app


# ==================================================
# Test Client
# ==================================================

client = TestClient(
    app
)


# ==================================================
# Constants
# ==================================================

NON_EXISTENT_ARTICLE_ID = 999999999


# ==================================================
# Helper
# ==================================================

def assert_json_list(
    response
):
    """
    確認 API 回傳 JSON List。
    """

    assert response.status_code == 200

    data = response.json()

    assert isinstance(
        data,
        list
    )

    return data


# ==================================================
# P3.2.2
# Article API Health Check
# ==================================================

def test_article_health_check():
    """
    GET /articles/health/check

    驗證 Article API 是否正常。
    """

    response = client.get(
        "/articles/health/check"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    assert (
        data["service"]
        == "AutoSearch V4 Article API"
    )

    assert (
        data["version"]
        == "P3.2.2"
    )


# ==================================================
# GET ALL
# ==================================================

def test_get_articles():
    """
    GET /articles/
    """

    response = client.get(
        "/articles/?limit=5"
    )

    assert_json_list(
        response
    )


# ==================================================
# GET ALL
# Invalid Limit
# ==================================================

def test_get_articles_invalid_limit():
    """
    limit <= 0 必須拒絕。
    """

    response = client.get(
        "/articles/?limit=0"
    )

    assert response.status_code == 400


# ==================================================
# GET ALL
# Negative Limit
# ==================================================

def test_get_articles_negative_limit():
    """
    負數 limit 必須拒絕。
    """

    response = client.get(
        "/articles/?limit=-1"
    )

    assert response.status_code == 400


# ==================================================
# GET BY ID
# ==================================================

def test_get_article_by_id_not_found():
    """
    GET /articles/{id}

    不存在 Article 必須回傳 404。
    """

    response = client.get(
        f"/articles/{NON_EXISTENT_ARTICLE_ID}"
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        data["detail"]
        == "Article not found"
    )


# ==================================================
# GET BY ID
# Invalid ID
# ==================================================

def test_get_article_by_id_invalid():
    """
    Article ID <= 0 必須回傳 400。
    """

    response = client.get(
        "/articles/0"
    )

    assert response.status_code == 400


# ==================================================
# GET BY ID
# Negative ID
# ==================================================

def test_get_article_by_id_negative():
    """
    負數 Article ID 必須回傳 400。
    """

    response = client.get(
        "/articles/-1"
    )

    assert response.status_code == 400


# ==================================================
# KEYWORD SEARCH
# ==================================================

def test_search_keyword():
    """
    GET /articles/search/keyword/{keyword}
    """

    response = client.get(
        "/articles/search/keyword/test"
    )

    assert_json_list(
        response
    )


# ==================================================
# KEYWORD SEARCH
# ==================================================

def test_search_keyword_empty():
    """
    空 Keyword 必須拒絕。
    """

    response = client.get(
        "/articles/search/keyword/%20"
    )

    assert response.status_code == 400


# ==================================================
# SOURCE SEARCH
# ==================================================

def test_search_source():
    """
    GET /articles/search/source/{source}
    """

    response = client.get(
        "/articles/search/source/test"
    )

    assert_json_list(
        response
    )


# ==================================================
# SOURCE SEARCH
# ==================================================

def test_search_source_empty():
    """
    空 Source 必須拒絕。
    """

    response = client.get(
        "/articles/search/source/%20"
    )

    assert response.status_code == 400


# ==================================================
# AI IMPORTANCE
# ==================================================

def test_ai_importance():
    """
    GET /articles/ai/importance/{level}
    """

    response = client.get(
        "/articles/ai/importance/5"
    )

    assert_json_list(
        response
    )


# ==================================================
# AI IMPORTANCE
# Invalid Level
# ==================================================

def test_ai_importance_invalid():
    """
    level < 0 必須拒絕。
    """

    response = client.get(
        "/articles/ai/importance/-1"
    )

    assert response.status_code == 400


# ==================================================
# AI CATEGORY
# ==================================================

def test_ai_category():
    """
    GET /articles/ai/category/{category}
    """

    response = client.get(
        "/articles/ai/category/Semiconductor"
    )

    assert_json_list(
        response
    )


# ==================================================
# AI CATEGORY
# Empty
# ==================================================

def test_ai_category_empty():
    """
    空 Category 必須拒絕。
    """

    response = client.get(
        "/articles/ai/category/%20"
    )

    assert response.status_code == 400


# ==================================================
# AI KEYWORD
# ==================================================

def test_ai_keyword():
    """
    GET /articles/ai/keyword/{keyword}
    """

    response = client.get(
        "/articles/ai/keyword/AI"
    )

    assert_json_list(
        response
    )


# ==================================================
# AI KEYWORD
# Empty
# ==================================================

def test_ai_keyword_empty():
    """
    空 AI Keyword 必須拒絕。
    """

    response = client.get(
        "/articles/ai/keyword/%20"
    )

    assert response.status_code == 400


# ==================================================
# AI TOP
# ==================================================

def test_ai_top():
    """
    GET /articles/ai/top
    """

    response = client.get(
        "/articles/ai/top?limit=5"
    )

    assert_json_list(
        response
    )


# ==================================================
# AI TOP
# Invalid Limit
# ==================================================

def test_ai_top_invalid_limit():
    """
    limit <= 0 必須拒絕。
    """

    response = client.get(
        "/articles/ai/top?limit=0"
    )

    assert response.status_code == 400


# ==================================================
# UPDATE
# Protected Field
# ==================================================

def test_update_protected_ai_importance():
    """
    ai_importance 不允許透過
    Article Management API 修改。

    Pydantic extra="forbid"
    必須回傳 422。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "ai_importance": 10

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Protected AI Summary
# ==================================================

def test_update_protected_ai_summary():
    """
    ai_summary 不允許修改。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "ai_summary":
                "modified"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Protected AI Category
# ==================================================

def test_update_protected_ai_category():
    """
    ai_category 不允許修改。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "ai_category":
                "modified"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Protected AI Status
# ==================================================

def test_update_protected_ai_status():
    """
    ai_status 不允許修改。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "ai_status":
                "completed"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Protected Content
# ==================================================

def test_update_protected_content():
    """
    content 不允許修改。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "content":
                "modified"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Protected Document ID
# ==================================================

def test_update_protected_document_id():
    """
    document_id 不允許修改。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "document_id":
                "modified"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Protected ID
# ==================================================

def test_update_protected_id():
    """
    id 不允許修改。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "id":
                123

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Protected Archive Field
# ==================================================

def test_update_protected_archive_field():
    """
    Archive 欄位不允許修改。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "version_number":
                999

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Empty Body
# ==================================================

def test_update_empty_body():
    """
    PUT {}

    API 必須要求至少一個欄位。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={}

    )

    assert response.status_code == 400


# ==================================================
# UPDATE
# Empty Title
# ==================================================

def test_update_empty_title():
    """
    title 不允許空字串。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "title":
                "   "

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Empty Keyword
# ==================================================

def test_update_empty_keyword():
    """
    keyword 不允許空字串。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "keyword":
                ""

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Empty Source
# ==================================================

def test_update_empty_source():
    """
    source 不允許空字串。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "source":
                "   "

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Empty URL
# ==================================================

def test_update_empty_url():
    """
    URL 不允許空字串。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "url":
                ""

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Empty Published
# ==================================================

def test_update_empty_published():
    """
    published 不允許空字串。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "published":
                ""

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Invalid Published
# ==================================================

def test_update_invalid_published():
    """
    published 必須是合法 datetime。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "published":
                "invalid-date"

        }

    )

    assert response.status_code == 422


# ==================================================
# UPDATE
# Valid Published
# ==================================================

def test_update_valid_published():
    """
    合法 published 格式應通過
    Pydantic Validation。

    因為 Article ID 不存在，
    所以 Validation 通過後會得到 404。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "published":
                "2026-08-15 12:30:00"

        }

    )

    assert response.status_code == 404


# ==================================================
# UPDATE
# Valid ISO Published
# ==================================================

def test_update_valid_iso_published():
    """
    ISO datetime 應通過 Validation。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "published":
                "2026-08-15T12:30:00"

        }

    )

    assert response.status_code == 404


# ==================================================
# UPDATE
# Invalid Article ID
# ==================================================

def test_update_invalid_article_id():
    """
    Article ID <= 0 必須回傳 400。
    """

    response = client.put(

        "/articles/0",

        json={

            "title":
                "Test"

        }

    )

    assert response.status_code == 400


# ==================================================
# UPDATE
# Non-existent Article
# ==================================================

def test_update_not_found():
    """
    合法 Update Request，
    但 Article 不存在。

    必須回傳 404。
    """

    response = client.put(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}",

        json={

            "title":
                "Test Article"

        }

    )

    assert response.status_code == 404


# ==================================================
# DELETE
# Invalid ID
# ==================================================

def test_delete_invalid_article_id():
    """
    Article ID <= 0 必須回傳 400。
    """

    response = client.delete(
        "/articles/0"
    )

    assert response.status_code == 400


# ==================================================
# DELETE
# Non-existent Article
# ==================================================

def test_delete_not_found():
    """
    不存在 Article 必須回傳 404。
    """

    response = client.delete(

        f"/articles/{NON_EXISTENT_ARTICLE_ID}"

    )

    assert response.status_code == 404