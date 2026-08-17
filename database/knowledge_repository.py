"""
database/knowledge_repository.py

AutoSearch V4

P2.3.1 Archive Repository

用途：

    Knowledge Archive Repository

負責：

    - knowledge_archive CRUD
    - Knowledge Archive Retrieval
    - Topic Search
    - Entity Search
    - Relation Search
    - Knowledge Version
    - Archive Statistics

Table:

    knowledge_archive
"""

from database.connection import get_connection


class KnowledgeRepository:
    """
    Knowledge Archive Repository

    負責操作：

        knowledge_archive

    主要用途：

        P2.3 Complete Knowledge Archive
        P2.3.1 Archive Repository
    """

    # ==================================
    # Insert
    # ==================================

    def insert(
        self,
        knowledge
    ):
        """
        新增 Knowledge Archive。

        Args:
            knowledge:
                KnowledgeArchive Model

        Returns:
            KnowledgeArchive
        """

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO knowledge_archive
                (
                    article_id,
                    topic,
                    entities,
                    relations,
                    knowledge_version
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    knowledge.article_id,
                    knowledge.topic,
                    knowledge.entities_text,
                    knowledge.relations_text,
                    knowledge.knowledge_version
                )
            )

            conn.commit()

            knowledge.id = cursor.lastrowid

            return knowledge

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get By ID
    # ==================================

    def get_by_id(
        self,
        knowledge_id
    ):
        """
        依 Knowledge ID 取得 Archive。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE id=%s
                """,
                (
                    knowledge_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get By Article ID
    # ==================================

    def get_by_article_id(
        self,
        article_id
    ):
        """
        依 Article ID 取得 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE article_id=%s
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Archive By Article
    # ==================================

    def get_archive_by_article(
        self,
        article_id
    ):
        """
        取得指定 Article 的完整 Archive。

        用於：

            P2.3 Complete Knowledge Archive
            Article History
            Knowledge History
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE article_id=%s
                ORDER BY created_time DESC, id DESC
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Latest
    # ==================================

    def get_latest(
        self,
        limit=20
    ):
        """
        取得最新 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                ORDER BY created_time DESC, id DESC
                LIMIT %s
                """,
                (
                    limit,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Find All
    # ==================================

    def find_all(
        self,
        limit=20
    ):
        """
        取得 Knowledge Archive 最新資料。

        用於：

            KnowledgeService.latest()
        """

        return self.get_latest(
            limit
        )



    # ==================================
    # Topic Search
    # ==================================

    def find_by_topic(
        self,
        topic
    ):
        """
        依 Topic 搜尋 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE topic LIKE %s
                ORDER BY created_time DESC, id DESC
                """,
                (
                    "%" + topic + "%",
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Entity Search
    # ==================================

    def find_by_entity(
        self,
        entity
    ):
        """
        依 Entity 搜尋 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE entities LIKE %s
                ORDER BY created_time DESC, id DESC
                """,
                (
                    "%" + entity + "%",
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Relation Search
    # ==================================

    def find_by_relation(
        self,
        relation
    ):
        """
        依 Relation 搜尋 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE relations LIKE %s
                ORDER BY created_time DESC, id DESC
                """,
                (
                    "%" + relation + "%",
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Full Search
    # ==================================

    def search(
        self,
        keyword
    ):
        """
        Knowledge Archive 全文欄位搜尋。

        搜尋：

            topic
            entities
            relations
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            key = "%" + keyword + "%"

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE
                    topic LIKE %s
                OR
                    entities LIKE %s
                OR
                    relations LIKE %s
                ORDER BY created_time DESC, id DESC
                """,
                (
                    key,
                    key,
                    key
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Search By Version
    # ==================================

    def find_by_version(
        self,
        version
    ):
        """
        依 Knowledge Version 搜尋 Archive。
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT *
                FROM knowledge_archive
                WHERE knowledge_version=%s
                ORDER BY created_time DESC, id DESC
                """,
                (
                    version,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        article_id
    ):
        """
        檢查 Article 是否已建立 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM knowledge_archive
                WHERE article_id=%s
                LIMIT 1
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchone() is not None

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Count
    # ==================================

    def count(self):
        """
        取得 Knowledge Archive 總數。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM knowledge_archive
                """
            )

            row = cursor.fetchone()

            return row[0]

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Count By Topic
    # ==================================

    def count_by_topic(
        self,
        topic
    ):
        """
        取得指定 Topic 的 Archive 數量。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM knowledge_archive
                WHERE topic LIKE %s
                """,
                (
                    "%" + topic + "%",
                )
            )

            row = cursor.fetchone()

            return row[0]

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Update
    # ==================================

    def update(
        self,
        article_id,
        knowledge
    ):
        """
        更新 Article 對應的 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE knowledge_archive
                SET
                    topic=%s,
                    entities=%s,
                    relations=%s,
                    knowledge_version=%s
                WHERE article_id=%s
                """,
                (
                    knowledge.topic,
                    knowledge.entities_text,
                    knowledge.relations_text,
                    knowledge.knowledge_version,
                    article_id
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Update Version
    # ==================================

    def update_version(
        self,
        knowledge_id,
        version
    ):
        """
        更新 Knowledge Archive Version。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE knowledge_archive
                SET knowledge_version=%s
                WHERE id=%s
                """,
                (
                    version,
                    knowledge_id
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Delete By ID
    # ==================================

    def delete(
        self,
        knowledge_id
    ):
        """
        依 Knowledge ID 刪除 Archive。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM knowledge_archive
                WHERE id=%s
                """,
                (
                    knowledge_id,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Delete By Article ID
    # ==================================

    def delete_by_article_id(
        self,
        article_id
    ):
        """
        依 Article ID 刪除 Knowledge Archive。
        """

        conn = get_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM knowledge_archive
                WHERE article_id=%s
                """,
                (
                    article_id,
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get With Article
    # ==================================

    def get_with_article(
        self,
        knowledge_id
    ):
        """
        取得 Knowledge Archive + Article。

        用於：

            Archive Viewer
            Knowledge History
            Historical Search
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    k.*,
                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status
                FROM knowledge_archive k
                INNER JOIN articles a
                    ON k.article_id = a.id
                WHERE k.id=%s
                """,
                (
                    knowledge_id,
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()

    # ==================================
    # Get Archive By Article With Article
    # ==================================

    def get_archive_with_article(
        self,
        article_id
    ):
        """
        取得指定 Article 的 Archive History。

        包含：

            Knowledge Archive
            Article Metadata
        """

        conn = get_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    k.*,
                    a.document_id,
                    a.keyword,
                    a.title,
                    a.url,
                    a.source,
                    a.published,
                    a.crawl_time,
                    a.status
                FROM knowledge_archive k
                INNER JOIN articles a
                    ON k.article_id = a.id
                WHERE k.article_id=%s
                ORDER BY k.created_time DESC, k.id DESC
                """,
                (
                    article_id,
                )
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()