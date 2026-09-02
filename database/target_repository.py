"""
database/target_repository.py

AutoSearch V5

V5.3 P3.3

Target Repository Extension

用途：

    儲存與管理使用者指定的 Target。

架構：

    User Target
        ↓
    TargetRepository
        ↓
    MySQL targets

支援 Target：

    URL Target
        target_type = "url"
        url

    Search Target
        target_type = "search"
        keyword
        search_provider

負責：

    - Target Create
    - Target Query
    - Target Update
    - Target Delete
    - Target Status
    - Target Enable
    - Target Disable
    - Target URL Query
    - Target Search Query
    - Target Keyword Query
    - Database Row → Target Model

不負責：

    - Target Validation
    - Search Provider
    - SearchAdapter
    - SearchAdapterManager
    - Crawler
    - Parser
    - Article
    - Archive
    - Raw HTML
    - Duplicate Detection
    - AI Analysis
    - Crawl Scheduling

V5 設計：

    Target
        ↓
    TargetRepository
        ↓
    Target Service
        ↓
    Search Provider / Direct URL
        ↓
    Existing V4 Crawl Pipeline

Repository 原則：

    Repository 只負責 Database Persistence。

    Target Business Validation
        ↓
    TargetValidator

    Database Persistence
        ↓
    TargetRepository
"""


from datetime import datetime


from database.connection import get_connection

from models.target import Target


class TargetRepository:

    """
    Target Repository

    V5 P3.3

    封裝 targets table 操作。

    Repository 只負責：

        Database CRUD
        Database Query
        DB Row → Target Model

    不負責：

        Target Validation
        Target Business Logic
        Search Provider
        Search Adapter
        Crawler
        Parser
        Archive
        AI
    """

    # ==================================
    # Create
    # ==================================

    def save(
        self,
        target
    ):
        """
        儲存 Target。

        支援：

            URL Target

                target_type = "url"
                url

            Search Target

                target_type = "search"
                keyword
                search_provider

        Parameters
        ----------

        target :
            Target Model

        Returns
        -------

        Target
            儲存成功後的 Target。
        """

        # ----------------------------------
        # Basic Type Check
        # ----------------------------------

        if target is None:

            raise ValueError(
                "target cannot be None"
            )

        if not isinstance(
            target,
            Target
        ):

            raise TypeError(
                "target must be an instance of Target"
            )

        # ----------------------------------
        # Normalize Persistence Values
        # ----------------------------------

        if target.name is None:

            target.name = ""

        if target.description is None:

            target.description = ""

        if target.status is None:

            target.status = "active"

        if target.target_type is None:

            target.target_type = ""

        if target.url is None:

            target.url = ""

        if target.keyword is None:

            target.keyword = ""

        if target.search_provider is None:

            target.search_provider = ""

        # ----------------------------------
        # String Normalization
        # ----------------------------------

        target.target_type = str(
            target.target_type
        ).strip()

        target.url = str(
            target.url
        ).strip()

        target.keyword = str(
            target.keyword
        ).strip()

        target.search_provider = str(
            target.search_provider
        ).strip()

        # ----------------------------------
        # Database Connection
        # ----------------------------------

        conn = get_connection()

        cursor = conn.cursor()

        try:

            sql = """
            INSERT INTO targets
            (
                name,
                target_type,
                url,
                keyword,
                search_provider,
                description,
                status,
                created_time,
                updated_time
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """

            cursor.execute(
                sql,
                (
                    target.name,
                    target.target_type,
                    target.url,
                    target.keyword,
                    target.search_provider,
                    target.description,
                    target.status,
                    target.created_time,
                    target.updated_time
                )
            )

            conn.commit()

            target.id = (
                cursor.lastrowid
            )

            return target

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Alias
    # ==================================

    def insert(
        self,
        target
    ):
        """
        save() Alias。
        """

        return self.save(
            target
        )

    # ==================================
    # Query By ID
    # ==================================

    def get_by_id(
        self,
        target_id
    ):
        """
        依 Target ID 查詢 Target。
        """

        if target_id is None:

            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                WHERE id=%s
                LIMIT 1
                """,
                (
                    target_id,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )

    # ==================================
    # Query By URL
    # ==================================

    def get_by_url(
        self,
        url
    ):
        """
        依 Target URL 查詢 Target。

        主要用於：

            URL Target

        注意：

            這只是 Target Lookup。

            不代表 Article Duplicate Detection。

            Article / Raw HTML Duplicate Policy
            仍由 V4 Archive 架構處理。
        """

        if not url:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                WHERE url=%s
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    url,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )

    # ==================================
    # Query By Keyword
    # ==================================

    def get_by_keyword(
        self,
        keyword
    ):
        """
        依 Keyword 查詢 Search Target。

        注意：

            可能存在相同 keyword
            但使用不同 Provider。

        因此若需要精確 Provider Lookup，
        請使用 get_by_search().
        """

        if not keyword:

            return None

        keyword = str(
            keyword
        ).strip()

        if not keyword:

            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                WHERE target_type=%s
                  AND keyword=%s
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    "search",
                    keyword,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )

    # ==================================
    # Query Search Target
    # ==================================

    def get_by_search(
        self,
        keyword,
        search_provider
    ):
        """
        依 Keyword + Search Provider
        查詢 Search Target。

        例如：

            keyword =
                "semiconductor"

            search_provider =
                "google_news"

        """

        if not keyword:

            return None

        if not search_provider:

            return None

        keyword = str(
            keyword
        ).strip()

        search_provider = str(
            search_provider
        ).strip()

        if not keyword:

            return None

        if not search_provider:

            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                WHERE target_type=%s
                  AND keyword=%s
                  AND search_provider=%s
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    "search",
                    keyword,
                    search_provider,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return None

        return self._to_model(
            result
        )


    # ==================================
    # Query Crawler URL By URL + Keyword
    # ==================================

    def get_crawler_url_by_url_keyword(
        self,
        url,
        keyword
    ):
        """
        依 URL + Keyword
        取得 Target 對應的 crawler_url。

        用途：

            URL + Keyword Target
                ↓
            targets
                ↓
            crawler_url
                ↓
            TargetSourceService
                ↓
            Source Definition

        注意：

            本方法只負責 Database Query。

            不負責：

                Search Provider
                SearchAdapter
                Search
                Crawler
        """

        if not url:
            return None

        if not keyword:
            return None

        url = str(
            url
        ).strip()

        keyword = str(
            keyword
        ).strip()

        if not url:
            return None

        if not keyword:
            return None

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT crawler_url
                FROM targets
                WHERE target_type=%s
                AND url=%s
                AND keyword=%s
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    "url",
                    url,
                    keyword,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:
            return None

        crawler_url = result.get(
            "crawler_url"
        )

        if crawler_url is None:
            return None

        crawler_url = str(
            crawler_url
        ).strip()

        if not crawler_url:
            return None

        return crawler_url


    # ==================================
    # Exists By Search
    # ==================================

    def exists_by_search(
        self,
        keyword,
        search_provider
    ):
        """
        判斷 Search Target 是否存在。

        Unique Logical Target：

            target_type
            +
            keyword
            +
            search_provider
        """

        return (
            self.get_by_search(
                keyword,
                search_provider
            )
            is not None
        )

    # ==================================
    # Find All
    # ==================================

    def find_all(
        self
    ):
        """
        取得所有 Target。

        排序：

            最新建立 → 最舊
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                ORDER BY id DESC
                """
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]

    # ==================================
    # Find Active
    # ==================================

    def find_active(
        self
    ):
        """
        取得所有 Active Target。

        用途：

            Target
                ↓
            Active Target
                ↓
            V5 Job
                ↓
            V4 Crawl Pipeline
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                WHERE status=%s
                ORDER BY id ASC
                """,
                (
                    "active",
                )
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]
    # ==================================
    # Find By Status
    # ==================================

    def find_by_status(
        self,
        status
    ):
        """
        依 Target Status 查詢 Target。

        例如：

            active
            inactive
            completed

        Repository 只負責：

            Database Query

        不負責：

            Status Business Validation
        """

        if not status:

            return []

        status = str(
            status
        ).strip()

        if not status:

            return []

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                WHERE status=%s
                ORDER BY id DESC
                """,
                (
                    status,
                )
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]




    # ==================================
    # Find By Type
    # ==================================

    def find_by_type(
        self,
        target_type
    ):
        """
        依 Target Type 查詢。

        例如：

            url
            search
        """

        if not target_type:

            return []

        target_type = str(
            target_type
        ).strip()

        if not target_type:

            return []

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM targets
                WHERE target_type=%s
                ORDER BY id ASC
                """,
                (
                    target_type,
                )
            )

            results = cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

        return [
            self._to_model(row)
            for row in results
        ]

    # ==================================
    # Find Search Targets
    # ==================================

    def find_search_targets(
        self
    ):
        """
        取得所有 Search Target。
        """

        return self.find_by_type(
            "search"
        )

    # ==================================
    # Find URL Targets
    # ==================================

    def find_url_targets(
        self
    ):
        """
        取得所有 URL Target。
        """

        return self.find_by_type(
            "url"
        )

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        target_id
    ):
        """
        判斷 Target ID 是否存在。
        """

        if target_id is None:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM targets
                WHERE id=%s
                LIMIT 1
                """,
                (
                    target_id,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        return result is not None

    # ==================================
    # Exists By URL
    # ==================================

    def exists_by_url(
        self,
        url
    ):
        """
        判斷 URL Target 是否存在。
        """

        return (
            self.get_by_url(url)
            is not None
        )

    # ==================================
    # Update
    # ==================================

    def update(
        self,
        target
    ):
        """
        更新完整 Target。

        更新：

            name
            target_type
            url
            keyword
            search_provider
            description
            status
            updated_time
        """

        if target is None:

            raise ValueError(
                "target cannot be None"
            )

        if not isinstance(
            target,
            Target
        ):

            raise TypeError(
                "target must be an instance of Target"
            )

        if target.id is None:

            raise ValueError(
                "target.id cannot be None"
            )

        # ----------------------------------
        # Normalize
        # ----------------------------------

        if target.name is None:

            target.name = ""

        if target.description is None:

            target.description = ""

        if target.target_type is None:

            target.target_type = ""

        if target.url is None:

            target.url = ""

        if target.keyword is None:

            target.keyword = ""

        if target.search_provider is None:

            target.search_provider = ""

        if target.status is None:

            target.status = "active"

        target.target_type = str(
            target.target_type
        ).strip()

        target.url = str(
            target.url
        ).strip()

        target.keyword = str(
            target.keyword
        ).strip()

        target.search_provider = str(
            target.search_provider
        ).strip()

        # ----------------------------------
        # Update Time
        # ----------------------------------

        target.updated_time = (
            datetime.now()
        )

        # ----------------------------------
        # Database
        # ----------------------------------

        conn = get_connection()

        cursor = conn.cursor()

        try:

            sql = """
            UPDATE targets
            SET
                name=%s,
                target_type=%s,
                url=%s,
                keyword=%s,
                search_provider=%s,
                description=%s,
                status=%s,
                updated_time=%s
            WHERE id=%s
            """

            cursor.execute(
                sql,
                (
                    target.name,
                    target.target_type,
                    target.url,
                    target.keyword,
                    target.search_provider,
                    target.description,
                    target.status,
                    target.updated_time,
                    target.id
                )
            )

            conn.commit()

            if cursor.rowcount == 0:

                return False

            return True

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Update Status
    # ==================================

    def update_status(
        self,
        target_id,
        status
    ):
        """
        更新 Target Status。

        例如：

            active
            inactive
        """

        if target_id is None:

            return False

        if not status:

            return False

        status = str(
            status
        ).strip()

        if not status:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE targets
                SET
                    status=%s,
                    updated_time=%s
                WHERE id=%s
                """,
                (
                    status,
                    datetime.now(),
                    target_id
                )
            )

            conn.commit()

            return (
                cursor.rowcount > 0
            )

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Enable
    # ==================================

    def enable(
        self,
        target_id
    ):
        """
        啟用 Target。
        """

        return self.update_status(
            target_id=target_id,
            status="active"
        )

    # ==================================
    # Disable
    # ==================================

    def disable(
        self,
        target_id
    ):
        """
        停用 Target。

        不刪除 Target。

        只是：

            status = inactive
        """

        return self.update_status(
            target_id=target_id,
            status="inactive"
        )

    # ==================================
    # Delete By ID
    # ==================================

    def delete_by_id(
        self,
        target_id
    ):
        """
        依 ID 刪除 Target。
        """

        if target_id is None:

            return False

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM targets
                WHERE id=%s
                """,
                (
                    target_id,
                )
            )

            conn.commit()

            return (
                cursor.rowcount > 0
            )

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Count
    # ==================================

    def count(
        self
    ):
        """
        取得 Target 總數。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM targets
                """
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return 0

        return result[0]

    # ==================================
    # Count Active
    # ==================================

    def count_active(
        self
    ):
        """
        取得 Active Target 數量。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM targets
                WHERE status=%s
                """,
                (
                    "active",
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return 0

        return result[0]

    # ==================================
    # Count By Type
    # ==================================

    def count_by_type(
        self,
        target_type
    ):
        """
        取得指定 Target Type 數量。
        """

        if not target_type:

            return 0

        target_type = str(
            target_type
        ).strip()

        if not target_type:

            return 0

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM targets
                WHERE target_type=%s
                """,
                (
                    target_type,
                )
            )

            result = cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

        if result is None:

            return 0

        return result[0]

    # ==================================
    # Convert DB Row
    # ==================================

    def _to_model(
        self,
        result
    ):
        """
        Database Row
            ↓
        Target Model
        """

        if result is None:

            return None

        target = Target(

            name=result.get(
                "name",
                ""
            ),

            target_type=result.get(
                "target_type",
                ""
            ),

            url=result.get(
                "url",
                ""
            ),

            keyword=result.get(
                "keyword",
                ""
            ),

            search_provider=result.get(
                "search_provider",
                ""
            ),

            status=result.get(
                "status",
                "active"
            ),

            description=result.get(
                "description",
                ""
            ),

            created_time=result.get(
                "created_time"
            ),

            updated_time=result.get(
                "updated_time"
            )
        )

        target.id = result.get(
            "id"
        )

        return target


# ==================================
# Public API
# ==================================

__all__ = [
    "TargetRepository",
]