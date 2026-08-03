"""
repository.py

ArticleRepository

負責：
1. Article 資料新增
2. Article 重複檢查
3. Article 查詢
4. Keyword 搜尋
5. Status 更新

Pipeline 不直接操作 MySQL，
統一透過 Repository 存取資料庫。
"""


from database.connection import get_connection



class ArticleRepository:


    """
    Article Repository

    封裝 articles table 的 CRUD 操作
    """



    # ==================================
    # 新增文章
    # ==================================

    def insert(self, article):

        """
        將 Article Object 寫入 MySQL

        Args:
            article:
                models.article.Article 物件

        """

        # 建立資料庫連線
        conn = get_connection()


        # 建立 SQL cursor
        cursor = conn.cursor()



        # SQL Insert 語句
        sql = """
        INSERT INTO articles
        (
            document_id,
            keyword,
            title,
            url,
            source,
            published,
            content,
            crawl_time,
            status
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



        # 執行 SQL
        cursor.execute(
            sql,
            (
                article.document_id,
                article.keyword,
                article.title,
                article.url,
                article.source,
                article.published,
                article.content,
                article.crawl_time,
                article.status
            )
        )



        # 確認寫入資料庫
        conn.commit()



        # 關閉資源
        cursor.close()
        conn.close()




    # ==================================
    # 檢查文章是否存在
    # ==================================

    def exists(self, document_id):

        """
        利用 document_id 判斷文章是否重複

        Returns:
            True  : 已存在
            False : 不存在
        """


        conn = get_connection()

        cursor = conn.cursor()



        sql = """
        SELECT id
        FROM articles
        WHERE document_id=%s
        """



        cursor.execute(
            sql,
            (document_id,)
        )



        result = cursor.fetchone()



        cursor.close()
        conn.close()



        # 有查詢結果代表已存在
        return result is not None




    # ==================================
    # 查詢單篇文章
    # ==================================

    def get(self, document_id):

        """
        根據 document_id 取得文章完整資料

        回傳：
            Dictionary
        """



        conn = get_connection()



        # dictionary=True
        # 讓結果使用欄位名稱存取
        cursor = conn.cursor(
            dictionary=True
        )



        sql = """
        SELECT *
        FROM articles
        WHERE document_id=%s
        """



        cursor.execute(
            sql,
            (document_id,)
        )



        result = cursor.fetchone()



        cursor.close()
        conn.close()



        return result




    # ==================================
    # 關鍵字搜尋
    # ==================================

    def search(self, keyword):

        """
        搜尋文章

        搜尋欄位：
            keyword
            title


        用於：
            Retrieval API
            AI Retrieval
        """



        conn = get_connection()


        cursor = conn.cursor(
            dictionary=True
        )



        sql = """
        SELECT *
        FROM articles
        WHERE keyword LIKE %s
        OR title LIKE %s
        ORDER BY published DESC
        """



        search_value = f"%{keyword}%"



        cursor.execute(
            sql,
            (
                search_value,
                search_value
            )
        )



        results = cursor.fetchall()



        cursor.close()
        conn.close()



        return results




    # ==================================
    # 更新文章狀態
    # ==================================

    def update_status(
        self,
        document_id,
        status
    ):

        """
        更新文章處理狀態


        範例：

        new
          |
          v
        parsed
          |
          v
        analyzed


        """



        conn = get_connection()


        cursor = conn.cursor()



        sql = """
        UPDATE articles
        SET status=%s
        WHERE document_id=%s
        """



        cursor.execute(
            sql,
            (
                status,
                document_id
            )
        )



        conn.commit()



        cursor.close()
        conn.close()