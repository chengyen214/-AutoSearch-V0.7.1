"""
models/article_update.py

AutoSearch V4

P3.2.3

Article Management API Validation Model


功能:

    Article Update Request Validation


負責:

    1. Article Metadata Validation
    2. Protected Field Protection
    3. Empty String Protection
    4. Published Datetime Validation
    5. Request Body Validation


允許修改:

    keyword
    title
    url
    source
    published
    status


禁止修改:

    id
    document_id
    content

    ai_summary
    ai_category
    ai_keywords
    ai_importance
    ai_model
    ai_version
    ai_analyze_time
    ai_confidence
    ai_status

    archive fields
"""


from datetime import datetime
from typing import Optional


from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator
)


# ==================================================
# Article Update Request
# ==================================================

class ArticleUpdateRequest(
    BaseModel
):
    """
    Article Management Update Request。

    只允許修改 Article Metadata。

    Protected fields 使用
    extra="forbid" 保護。

    因此任何未定義欄位
    都會直接產生 HTTP 422。
    """

    # ==================================================
    # Pydantic Configuration
    # ==================================================

    model_config = ConfigDict(

        # ==============================================
        # 禁止未知欄位
        #
        # 例如:
        #
        # {
        #     "content": "xxx"
        # }
        #
        # 會直接得到 ValidationError
        # -> FastAPI HTTP 422
        # ==============================================

        extra="forbid"

    )

    # ==================================================
    # Editable Metadata
    # ==================================================

    keyword: Optional[str] = None

    title: Optional[str] = None

    url: Optional[str] = None

    source: Optional[str] = None

    published: Optional[str] = None

    status: Optional[str] = None

    # ==================================================
    # TITLE VALIDATION
    # ==================================================

    @field_validator(
        "title"
    )
    @classmethod
    def validate_title(
        cls,
        value: Optional[str]
    ) -> Optional[str]:
        """
        title 不允許空字串。

        None:

            允許

        "":

            拒絕

        "   ":

            拒絕
        """

        if value is None:

            return value

        if not value.strip():

            raise ValueError(
                "title cannot be empty"
            )

        return value

    # ==================================================
    # SOURCE VALIDATION
    # ==================================================

    @field_validator(
        "source"
    )
    @classmethod
    def validate_source(
        cls,
        value: Optional[str]
    ) -> Optional[str]:
        """
        source 不允許空字串。
        """

        if value is None:

            return value

        if not value.strip():

            raise ValueError(
                "source cannot be empty"
            )

        return value

    # ==================================================
    # KEYWORD VALIDATION
    # ==================================================

    @field_validator(
        "keyword"
    )
    @classmethod
    def validate_keyword(
        cls,
        value: Optional[str]
    ) -> Optional[str]:
        """
        keyword 不允許空字串。
        """

        if value is None:

            return value

        if not value.strip():

            raise ValueError(
                "keyword cannot be empty"
            )

        return value

    # ==================================================
    # URL VALIDATION
    # ==================================================

    @field_validator(
        "url"
    )
    @classmethod
    def validate_url(
        cls,
        value: Optional[str]
    ) -> Optional[str]:
        """
        URL 基本驗證。

        此階段只拒絕空字串。

        不在 API Model 中強制
        URL scheme / domain。

        更完整的 URL 驗證
        可於後續階段再處理。
        """

        if value is None:

            return value

        if not value.strip():

            raise ValueError(
                "url cannot be empty"
            )

        return value

    # ==================================================
    # PUBLISHED VALIDATION
    # ==================================================

    @field_validator(
        "published"
    )
    @classmethod
    def validate_published(
        cls,
        value: Optional[str]
    ) -> Optional[str]:
        """
        published 必須符合日期時間格式。

        例如:

            2026-08-15
            2026-08-15 12:30:00
            2026-08-15T12:30:00

        使用 datetime.fromisoformat()
        進行基本驗證。
        """

        if value is None:

            return value

        if not value.strip():

            raise ValueError(
                "published cannot be empty"
            )

        try:

            datetime.fromisoformat(
                value
            )

        except ValueError:

            raise ValueError(
                "published must be a valid "
                "datetime format"
            )

        return value