"""
utils/target_validator.py

AutoSearch V5

V5.3 P3.2

Target Validation
"""

from urllib.parse import urlparse, urlunparse

from models.target import Target


class TargetValidator:
    """
    V5 Target Validator。

    負責 Target 建立前的基本資料驗證
    與標準化。
    """

    # ==================================
    # Allowed Values
    # ==================================

    ALLOWED_TYPES = {
        Target.TYPE_URL,
        Target.TYPE_SEARCH,
    }

    ALLOWED_PROVIDERS = {
        Target.PROVIDER_GOOGLE_SEARCH,
        Target.PROVIDER_GOOGLE_NEWS,
    }

    ALLOWED_STATUS = {
        "active",
        "inactive",
    }

    # ==================================
    # Validate Target
    # ==================================

    @classmethod
    def validate(cls, target):

        if not isinstance(
            target,
            Target,
        ):
            raise TypeError(
                "target must be an instance of Target"
            )

        cls.validate_target_type(
            target.target_type
        )

        cls.validate_status(
            target.status
        )

        if target.is_url_target:

            cls.validate_url(
                target.url
            )

        elif target.is_search_target:

            cls.validate_keyword(
                target.keyword
            )

            cls.validate_search_provider(
                target.search_provider
            )

        return True

    # ==================================
    # Target Type
    # ==================================

    @classmethod
    def validate_target_type(
        cls,
        target_type,
    ):

        if target_type not in cls.ALLOWED_TYPES:

            raise ValueError(
                f"Invalid target_type: "
                f"{target_type}"
            )

        return True

    # ==================================
    # URL
    # ==================================

    @classmethod
    def validate_url(
        cls,
        url,
    ):

        if url is None:

            raise ValueError(
                "url cannot be empty"
            )

        url = str(
            url
        ).strip()

        if not url:

            raise ValueError(
                "url cannot be empty"
            )

        parsed = urlparse(
            url
        )

        if parsed.scheme not in {
            "http",
            "https",
        }:

            raise ValueError(
                "url must use http or https"
            )

        if not parsed.netloc:

            raise ValueError(
                "url must contain a valid host"
            )

        return True

    # ==================================
    # URL Normalization
    # ==================================

    @classmethod
    def normalize_url(
        cls,
        url,
    ):
        """
        URL Canonicalization。

        例如：

            https://example.com/
                ↓
            https://example.com

        保留：

            path
            query
            fragment
        """

        cls.validate_url(
            url
        )

        url = str(
            url
        ).strip()

        parsed = urlparse(
            url
        )

        path = parsed.path

        # Root path "/" 不需要保存。
        if path == "/":
            path = ""

        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )

    # ==================================
    # Keyword
    # ==================================

    @classmethod
    def validate_keyword(
        cls,
        keyword,
    ):

        if keyword is None:

            raise ValueError(
                "keyword cannot be None"
            )

        keyword = str(
            keyword
        ).strip()

        if not keyword:

            raise ValueError(
                "keyword cannot be empty"
            )

        return True

    # ==================================
    # Search Provider
    # ==================================

    @classmethod
    def validate_search_provider(
        cls,
        provider,
    ):

        if provider not in cls.ALLOWED_PROVIDERS:

            raise ValueError(
                f"Invalid search_provider: "
                f"{provider}"
            )

        return True

    # ==================================
    # Status
    # ==================================

    @classmethod
    def validate_status(
        cls,
        status,
    ):

        if status not in cls.ALLOWED_STATUS:

            raise ValueError(
                f"Invalid status: "
                f"{status}"
            )

        return True

    # ==================================
    # Normalize Target
    # ==================================

    @classmethod
    def normalize(
        cls,
        target,
    ):

        if not isinstance(
            target,
            Target,
        ):
            raise TypeError(
                "target must be an instance of Target"
            )

        # ----------------------------------
        # Basic String Normalization
        # ----------------------------------

        target.name = (
            str(target.name).strip()
            if target.name is not None
            else ""
        )

        target.description = (
            str(target.description).strip()
            if target.description is not None
            else ""
        )

        target.target_type = (
            str(target.target_type).strip()
            if target.target_type is not None
            else ""
        )

        # ----------------------------------
        # URL
        # ----------------------------------

        if target.target_type == Target.TYPE_URL:

            target.url = cls.normalize_url(
                target.url
            )

        else:

            target.url = (
                str(target.url).strip()
                if target.url is not None
                else ""
            )

        # ----------------------------------
        # Keyword
        # ----------------------------------

        target.keyword = (
            str(target.keyword).strip()
            if target.keyword is not None
            else None
        )

        # ----------------------------------
        # Search Provider
        # ----------------------------------

        target.search_provider = (
            str(target.search_provider).strip()
            if target.search_provider is not None
            else ""
        )

        # ----------------------------------
        # Status
        # ----------------------------------

        target.status = (
            str(target.status).strip()
            if target.status is not None
            else ""
        )

        # ----------------------------------
        # Validate
        # ----------------------------------

        cls.validate(
            target
        )

        return target


# ==================================
# Public API
# ==================================

__all__ = [
    "TargetValidator",
]
