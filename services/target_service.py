"""
services/target_service.py

AutoSearch V5

V5.3 P3.4

Target Service

用途：

    整合：

        Target Model
        Target Validator
        Target Repository

架構：

    User
        ↓
    TargetService
        ↓
    TargetValidator
        ↓
    TargetRepository
        ↓
    MySQL


負責：

    - Create Target
    - Create URL Target
    - Create Search Target
    - Google Search Target
    - Google News Target
    - Get Target
    - Get Target By URL
    - Get Target By Keyword
    - Get Target By Search
    - Find All
    - Find Active
    - Find By Type
    - Find URL Targets
    - Find Search Targets
    - Update Target
    - Enable Target
    - Disable Target
    - Delete Target
    - Target Exists
    - Target Duplicate Check
    - Target Count


不負責：

    - Search Provider
    - Search API
    - SearchAdapter
    - Crawler
    - Parser
    - Article
    - Archive
    - AI
    - Job
    - Scheduler


V5 設計：

    Target
        ↓
    TargetService
        ↓
    Existing V4 Crawl Pipeline
"""


from urllib.parse import urlparse

from models.target import Target

from database.target_repository import (
    TargetRepository,
)

from utils.target_validator import (
    TargetValidator,
)


class TargetService:
    """
    V5 P3.4 Target Service。

    TargetService 是 Target 的 Business Logic Layer。

    Repository：
        負責 Database CRUD。

    Validator：
        負責 Target Normalize / Validate。

    Service：
        負責：

            Business Logic
            Duplicate Check
            Create / Update Flow
            Repository Coordination
    """

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        repository=None,
        validator=None,
    ):
        """
        建立 TargetService。

        若未注入 Validator：

            預設使用 TargetValidator。

        支援 Dependency Injection：

            TargetService(
                repository=fake_repository,
                validator=fake_validator,
            )
        """

        self.repository = (
            repository
            if repository is not None
            else TargetRepository()
        )

        self.validator = (
            validator
            if validator is not None
            else TargetValidator()
        )

    # ==================================================
    # Create
    # ==================================================

    def create(
        self,
        target,
    ):
        """
        建立 Target。

        Flow：

            Target
                ↓
            Type Check
                ↓
            Normalize
                ↓
            Validate
                ↓
            Duplicate Check
                ↓
            Repository.save()
                ↓
            Target
        """

        if not isinstance(
            target,
            Target,
        ):
            raise TypeError(
                "target must be an instance of Target"
            )

        target = self._normalize(
            target
        )

        self._validate(
            target
        )

        self._check_duplicate(
            target
        )

        return self.repository.save(
            target
        )

    # ==================================================
    # Create URL Target
    # ==================================================

    def create_url_target(
        self,
        url,
        name="",
        description="",
        status="active",
    ):
        """
        建立 URL Target。
        """

        target = Target(
            name=name,
            target_type="url",
            url=url,
            description=description,
            status=status,
        )

        return self.create(
            target
        )

    # ==================================================
    # Create Search Target
    # ==================================================

    def create_search_target(
        self,
        keyword,
        search_provider,
        name="",
        description="",
        status="active",
    ):
        """
        建立 Search Target。

        Example：

            service.create_search_target(
                keyword="semiconductor",
                search_provider="google_search",
            )

        注意：

            keyword=None 必須保留其語意，
            讓 Validator 能夠區分：

                None
                    → keyword cannot be None

                ""
                    → keyword cannot be empty
        """

        # ----------------------------------------------
        # Preserve None semantics
        # ----------------------------------------------

        if keyword is None:

            if self.validator is not None:

                self.validator.validate_keyword(
                    None
                )

            raise ValueError(
                "keyword cannot be None"
            )

        target = Target(
            name=name,
            target_type="search",
            url="",
            keyword=keyword,
            search_provider=search_provider,
            description=description,
            status=status,
        )

        return self.create(
            target
        )

    # ==================================================
    # Google Search
    # ==================================================

    def create_google_search_target(
        self,
        keyword,
        name="",
        description="",
        status="active",
    ):
        """
        建立 Google Search Target。
        """

        return self.create_search_target(
            keyword=keyword,
            search_provider="google_search",
            name=name,
            description=description,
            status=status,
        )

    # ==================================================
    # Google News
    # ==================================================

    def create_google_news_target(
        self,
        keyword,
        name="",
        description="",
        status="active",
    ):
        """
        建立 Google News Target。
        """

        return self.create_search_target(
            keyword=keyword,
            search_provider="google_news",
            name=name,
            description=description,
            status=status,
        )

    # ==================================================
    # Get By ID
    # ==================================================

    def get_by_id(
        self,
        target_id,
    ):
        """
        依 Target ID 取得 Target。
        """

        return self.repository.get_by_id(
            target_id
        )

    # ==================================================
    # Get By URL
    # ==================================================

    def get_by_url(
        self,
        url,
    ):
        """
        依 URL 取得 Target。

        查詢前先進行 URL Canonicalization，
        確保：

            https://example.com
            https://example.com/

        視為相同 URL。
        """

        normalized_url = self._normalize_url_lookup(
            url
        )

        return self.repository.get_by_url(
            normalized_url
        )

    # ==================================================
    # Get By Keyword
    # ==================================================

    def get_by_keyword(
        self,
        keyword,
    ):
        """
        依 Keyword 取得 Search Target。
        """

        return self.repository.get_by_keyword(
            keyword
        )

    # ==================================================
    # Get By Search
    # ==================================================

    def get_by_search(
        self,
        keyword,
        search_provider,
    ):
        """
        依 Keyword + Search Provider
        取得 Search Target。
        """

        return self.repository.get_by_search(
            keyword,
            search_provider,
        )

    # ==================================================
    # Find All
    # ==================================================

    def find_all(
        self,
    ):
        """
        取得所有 Target。
        """

        return self.repository.find_all()

    # ==================================================
    # Find Active
    # ==================================================

    def find_active(
        self,
    ):
        """
        取得所有 Active Target。
        """

        return self.repository.find_active()

    # ==================================================
    # Find By Type
    # ==================================================

    def find_by_type(
        self,
        target_type,
    ):
        """
        依 Target Type 查詢。
        """

        return self.repository.find_by_type(
            target_type
        )

    # ==================================================
    # Find URL Targets
    # ==================================================

    def find_url_targets(
        self,
    ):
        """
        取得所有 URL Targets。
        """

        return self.repository.find_url_targets()

    # ==================================================
    # Find Search Targets
    # ==================================================

    def find_search_targets(
        self,
    ):
        """
        取得所有 Search Targets。
        """

        return self.repository.find_search_targets()

    # ==================================================
    # Update
    # ==================================================

    def update(
        self,
        target,
    ):
        """
        更新 Target。

        Flow：

            Target
                ↓
            Type Check
                ↓
            Normalize
                ↓
            Validate
                ↓
            Duplicate Check
                ↓
            Repository.update()
        """

        if not isinstance(
            target,
            Target,
        ):
            raise TypeError(
                "target must be an instance of Target"
            )

        if target.id is None:
            raise ValueError(
                "target.id cannot be None"
            )

        target = self._normalize(
            target
        )

        self._validate(
            target
        )

        self._check_duplicate_for_update(
            target
        )

        return self.repository.update(
            target
        )

    # ==================================================
    # Enable
    # ==================================================

    def enable(
        self,
        target_id,
    ):
        """
        啟用 Target。
        """

        return self.repository.enable(
            target_id
        )

    # ==================================================
    # Disable
    # ==================================================

    def disable(
        self,
        target_id,
    ):
        """
        停用 Target。
        """

        return self.repository.disable(
            target_id
        )

    # ==================================================
    # Delete
    # ==================================================

    def delete(
        self,
        target_id,
    ):
        """
        刪除 Target。
        """

        return self.repository.delete_by_id(
            target_id
        )

    # ==================================================
    # Exists
    # ==================================================

    def exists(
        self,
        target_id,
    ):
        """
        判斷 Target 是否存在。
        """

        return self.repository.exists(
            target_id
        )

    # ==================================================
    # Exists By URL
    # ==================================================

    def exists_by_url(
        self,
        url,
    ):
        """
        判斷 URL Target 是否存在。

        查詢前進行 URL Canonicalization。
        """

        normalized_url = self._normalize_url_lookup(
            url
        )

        return self.repository.exists_by_url(
            normalized_url
        )

    # ==================================================
    # Exists By Search
    # ==================================================

    def exists_by_search(
        self,
        keyword,
        search_provider,
    ):
        """
        判斷 Search Target 是否存在。
        """

        return self.repository.exists_by_search(
            keyword,
            search_provider,
        )

    # ==================================================
    # Duplicate Check
    # ==================================================

    def _check_duplicate(
        self,
        target,
    ):
        """
        Create 時的 Duplicate Check。

        URL Target：
            URL

        Search Target：
            Keyword + Search Provider
        """

        if target.target_type == Target.TYPE_URL:

            if self.repository.exists_by_url(
                target.url
            ):

                raise ValueError(
                    "Target URL already exists"
                )

        elif target.target_type == Target.TYPE_SEARCH:

            if self.repository.exists_by_search(
                target.keyword,
                target.search_provider,
            ):

                raise ValueError(
                    "Search Target already exists"
                )

    # ==================================================
    # Duplicate Check For Update
    # ==================================================

    def _check_duplicate_for_update(
        self,
        target,
    ):
        """
        Update 時的 Duplicate Check。

        自己不能被判定為 duplicate。
        """

        if target.target_type == Target.TYPE_URL:

            existing = self.repository.get_by_url(
                target.url
            )

            if (
                existing is not None
                and existing.id != target.id
            ):

                raise ValueError(
                    "Target URL already exists"
                )

        elif target.target_type == Target.TYPE_SEARCH:

            existing = self.repository.get_by_search(
                target.keyword,
                target.search_provider,
            )

            if (
                existing is not None
                and existing.id != target.id
            ):

                raise ValueError(
                    "Search Target already exists"
                )

    # ==================================================
    # Normalize
    # ==================================================

    def _normalize(
        self,
        target,
    ):
        """
        呼叫 Validator Normalize。

        TargetValidator 預設會被注入，
        因此正式 Create / Update 一定會：

            Normalize
            Validate
        """

        if self.validator is None:
            return target

        result = self.validator.normalize(
            target
        )

        if result is None:
            return target

        return result

    # ==================================================
    # Validate
    # ==================================================

    def _validate(
        self,
        target,
    ):
        """
        呼叫 Validator Validate。
        """

        if self.validator is None:
            return True

        return self.validator.validate(
            target
        )

    # ==================================================
    # URL Lookup Normalization
    # ==================================================

    @staticmethod
    def _normalize_url_lookup(
        url,
    ):
        """
        URL Lookup Canonicalization。

        目的：

            https://example.com
            https://example.com/

        視為相同 URL。

        注意：

            不修改 query string。
            不修改 fragment。
            不修改 path 中間的 slash。

        僅移除 URL 最尾端的 slash。
        """

        if url is None:
            return ""

        url = str(
            url
        ).strip()

        if not url:
            return ""

        parsed = urlparse(
            url
        )

        # 只有合法 http / https URL 才做 canonicalization。
        # 非法 URL 交由 Validator 處理。
        if parsed.scheme not in {
            "http",
            "https",
        } or not parsed.netloc:

            return url

        # Root URL：
        #
        # https://example.com/
        #
        # ↓
        #
        # https://example.com
        if parsed.path in {
            "",
            "/",
        }:

            normalized = (
                f"{parsed.scheme}://"
                f"{parsed.netloc}"
            )

            if parsed.params:
                normalized += (
                    f";{parsed.params}"
                )

            if parsed.query:
                normalized += (
                    f"?{parsed.query}"
                )

            if parsed.fragment:
                normalized += (
                    f"#{parsed.fragment}"
                )

            return normalized

        return url

    # ==================================================
    # Count
    # ==================================================

    def count(
        self,
    ):
        """
        取得 Target 總數。
        """

        return self.repository.count()

    # ==================================================
    # Count Active
    # ==================================================

    def count_active(
        self,
    ):
        """
        取得 Active Target 數量。
        """

        return self.repository.count_active()

    # ==================================================
    # Count By Type
    # ==================================================

    def count_by_type(
        self,
        target_type,
    ):
        """
        取得指定 Target Type 數量。
        """

        return self.repository.count_by_type(
            target_type
        )


# ======================================================
# Public API
# ======================================================

__all__ = [
    "TargetService",
]
