"""
services/gemini_url_source_discovery_service.py

AutoSearch V6.4

Gemini URL Source Discovery Service

功能：

1. 取得 URLSourceGroupingService 的 source_groups
2. 將同一來源的 URL 群組交給 Gemini
3. 請 Gemini 判斷：
   - name
   - url
   - description
4. 由 source host 自動產生 crawler_url
5. 如果 Gemini 找不到適合的內容入口，
   使用該網站主頁作為 url fallback
6. 回傳 Gemini 結果
7. 將 Gemini 結果寫入 targets
8. 提供完整流程 Function，
   可被其他程式直接呼叫

完整流程：

    articles
        ↓
    URL Source Grouping
        ↓
    Target Crawler URL Exclusion
        ↓
    Source Groups
        ↓
    Gemini Source Discovery
        ↓
    Gemini Result
        ↓
    Target INSERT / UPDATE
        ↓
    targets

注意：

本 Service 負責：

- URL Source Grouping
- Gemini Source Discovery
- Target INSERT / UPDATE

目前不負責：

- AIAnalyzer
- AI Worker
- AI Analysis Pipeline
- Crawl
- Parser
"""

import json
from datetime import datetime

from google import genai

from config.ai_config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

from database.connection import get_connection

from services.url_source_grouping_service import (
    URLSourceGroupingService,
)


class GeminiURLSourceDiscoveryService:
    """
    使用 Gemini 分析 URL Source Grouping 結果。

    目的：

        找出同一來源相關內容的：

        1. 最新消息／專業資訊入口 URL
        2. Source name
        3. Description

    crawler_url 不由 Gemini 判斷。

    crawler_url 直接由 source host 產生：

        https://{host}/

    例如：

        www.digitimes.com.tw
            ↓
        https://www.digitimes.com.tw/

    如果 Gemini 找不到適合的內容入口：

        url
            ↓
        https://www.digitimes.com.tw/

    注意：

        url 與 crawler_url 在 fallback 情況下
        可能相同。

        但兩者用途不同：

        crawler_url：
            代表來源網站本身的入口。

        url：
            代表 AutoSearch 應該優先尋找相關
            新聞／專業知識／技術資訊的入口。
            如果找不到，才 fallback 到網站主頁。
    """

    KEYWORD = "IC semiconductor"

    TARGET_TYPE = "url"

    SEARCH_PROVIDER = "google_search"

    TARGET_STATUS = "active"

    def __init__(
        self,
        grouping_service=None,
        api_key=None,
        model=None,
    ):
        """
        初始化 Gemini URL Source Discovery Service。

        Args:
            grouping_service:
                URLSourceGroupingService instance

            api_key:
                Gemini API Key。
                預設使用 config.ai_config.GEMINI_API_KEY

            model:
                Gemini Model。
                預設使用 config.ai_config.GEMINI_MODEL
        """

        self.grouping_service = (
            grouping_service
            if grouping_service is not None
            else URLSourceGroupingService()
        )

        self.api_key = (
            api_key
            if api_key is not None
            else GEMINI_API_KEY
        )

        self.model = (
            model
            if model is not None
            else GEMINI_MODEL
        )

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        if not self.model:
            raise ValueError(
                "GEMINI_MODEL is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    # ==========================================================
    # Crawler URL
    # ==========================================================

    @staticmethod
    def build_crawler_url(
        host,
    ):
        """
        根據 source host 建立 crawler_url。

        crawler_url 完全由程式產生，
        不由 Gemini 判斷。

        crawler_url 代表：

            來源網站本身的入口／主頁

        例如：

            www.digitimes.com.tw
                ↓
            https://www.digitimes.com.tw/

        Args:
            host:
                Source host

        Returns:
            str
        """

        if not host:
            raise ValueError(
                "Host cannot be empty."
            )

        normalized_host = str(
            host
        ).strip().lower()

        if not normalized_host:
            raise ValueError(
                "Host cannot be empty."
            )

        return (
            f"https://{normalized_host}/"
        )

    # ==========================================================
    # Prompt
    # ==========================================================

    def build_prompt(
        self,
        host,
        urls,
    ):
        """
        建立 Gemini Source Discovery Prompt。

        Gemini 負責找：

            name
            url
            description

        crawler_url 不交給 Gemini。

        如果 Gemini 找不到適合的 url，
        必須回傳空字串：

            "url": ""

        程式收到空字串後，
        再 fallback 到網站主頁。
        """

        if not host:
            raise ValueError(
                "Host cannot be empty."
            )

        if not urls:
            raise ValueError(
                "URL list cannot be empty."
            )

        url_lines = "\n".join(
            f"{index}. {url}"
            for index, url in enumerate(
                urls,
                start=1,
            )
        )

        source_url = (
            self.build_crawler_url(
                host
            )
        )

        prompt = f"""
You are an expert web source discovery system for AutoSearch.

AutoSearch has collected several URLs from the same website.

SOURCE HOST:
{host}

SOURCE WEBSITE:
{source_url}

COLLECTED URLS:
{url_lines}

KEYWORD:
{self.KEYWORD}

Your task is to identify the most appropriate REAL and CURRENT
web location on this website where AutoSearch should look for
the latest information related to the topic represented by
the collected URLs.

The purpose is to discover NEW and useful information that can
be crawled again in the future.

PRIORITY:

Prefer web locations related to the following types of content,
in approximately this priority order:

1. News
2. Industry news
3. Semiconductor news
4. Technology news
5. Professional technical knowledge
6. Technical articles
7. Industry analysis
8. Specialized technology content
9. Topic or category pages
10. Other continuously updated related information

The selected URL should preferably be a listing, category,
topic, search, archive, news, or other continuously updated
page rather than a single article or single event page.

IMPORTANT RULES:

1. The URL MUST be a real existing URL on the source website.

2. The URL MUST belong to this source website:

   {source_url}

3. The URL should be useful for finding CURRENT or FUTURE
   related content.

4. The URL should preferably expose multiple related pieces of
   content or provide access to continuously updated content.

5. Prefer NEWS, INDUSTRY INFORMATION, SEMICONDUCTOR,
   TECHNOLOGY, TECHNICAL ARTICLES, PROFESSIONAL KNOWLEDGE,
   or INDUSTRY ANALYSIS.

6. If a news or professional-information section exists,
   prefer it over a general company homepage.

7. If a category or topic page exists for the relevant subject,
   prefer that page over a generic homepage.

8. If a search page is the most appropriate continuously
   updated source, it may be selected.

9. Do NOT simply return the common path of the provided URLs.

10. Do NOT assume that the original URL directory is the
    correct discovery location.

11. If the provided URLs are seminar, event, product,
    company, or other specific pages, do NOT automatically
    return their directory.

    Instead, determine whether the website has a better
    continuously updated source for:

    - news
    - semiconductor information
    - technology information
    - technical knowledge
    - professional information
    - industry information
    - industry analysis

12. Do NOT invent a URL.

13. Do NOT return a URL that is only inferred from a URL pattern
    without confirming that it is a real website location.

14. The provided URLs are evidence for understanding the topic
    and content context.

15. The provided URLs are NOT necessarily the final URL.

16. The keyword is:

    {self.KEYWORD}

17. The selected URL should be useful for AutoSearch to discover
    future relevant information.

18. Prefer a specific professional-information or news section
    over the website homepage whenever possible.

19. The selected URL should be related to the subject represented
    by the provided URLs and the keyword.

20. The result should focus on information discovery, not
    corporate introduction, company profile, careers, investor
    relations, or other general corporate information unless
    that is clearly the relevant content source.

21. Do NOT return crawler_url as a separate field.

    crawler_url is handled by the AutoSearch program.

22. If you cannot identify a suitable REAL and CURRENT
    news, technology, semiconductor, professional knowledge,
    technical article, industry analysis, category, topic,
    search, or other continuously updated URL, return:

    "url": ""

    Do NOT invent a fallback URL yourself.

    AutoSearch will automatically use the source website
    homepage as the fallback URL.

23. The homepage fallback is:

    {source_url}

24. The "url" field has two possible meanings:

    A. Preferred result:
       A real news / professional knowledge /
       technology / semiconductor / industry information
       entry point found by you.

    B. No suitable result:
       Return an empty string and let AutoSearch use
       the source website homepage as fallback.

Return the following:

1. name

The name of the website, source, or relevant content section.

2. url

The REAL website location where AutoSearch should look for
the latest related NEWS, INDUSTRY INFORMATION, SEMICONDUCTOR
INFORMATION, TECHNOLOGY INFORMATION, TECHNICAL ARTICLES,
PROFESSIONAL KNOWLEDGE, INDUSTRY ANALYSIS, or other relevant
continuously updated content.

If no suitable URL can be identified, return:

"url": ""

3. description

A short description explaining what type of useful latest
information can be found at this URL.

Return ONLY valid JSON.

Do not use Markdown.
Do not include ```json.
Do not include explanations outside the JSON.

Required JSON format:

{{
    "name": "...",
    "url": "...",
    "description": "..."
}}
"""

        return prompt.strip()

    # ==========================================================
    # Gemini
    # ==========================================================

    def analyze_source(
        self,
        host,
        urls,
    ):
        """
        將單一 source group 交給 Gemini 分析。

        Gemini 負責：

            name
            url
            description

        crawler_url 由程式產生。

        如果 Gemini 找不到合適 URL：

            url = crawler_url

        Returns:
            dict
        """

        if not urls:
            raise ValueError(
                "URL list cannot be empty."
            )

        crawler_url = (
            self.build_crawler_url(
                host
            )
        )

        prompt = self.build_prompt(
            host=host,
            urls=urls,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        text = getattr(
            response,
            "text",
            None,
        )

        if not text:
            raise ValueError(
                f"Gemini returned empty response "
                f"for source: {host}"
            )

        gemini_result = (
            self.parse_response(
                text=text,
                host=host,
            )
        )

        discovered_url = (
            gemini_result["url"]
        )

        if not discovered_url:
            discovered_url = crawler_url

        return {
            "name": gemini_result[
                "name"
            ],
            "url": discovered_url,
            "crawler_url": crawler_url,
            "description": gemini_result[
                "description"
            ],
        }

    # ==========================================================
    # Response Parser
    # ==========================================================

    @staticmethod
    def parse_response(
        text,
        host,
    ):
        """
        解析 Gemini JSON Response。

        url 可以為空。

        空 URL 不視為 Response 格式錯誤。

        analyze_source() 會將空 URL
        fallback 到 crawler_url。
        """

        cleaned = text.strip()

        # ------------------------------------------------------
        # 防止 Gemini 偶爾回傳 Markdown JSON
        # ------------------------------------------------------

        if cleaned.startswith(
            "```json"
        ):
            cleaned = cleaned[
                len("```json"):
            ].strip()

        elif cleaned.startswith(
            "```"
        ):
            cleaned = cleaned[
                len("```"):
            ].strip()

        if cleaned.endswith(
            "```"
        ):
            cleaned = cleaned[
                :-3
            ].strip()

        try:
            result = json.loads(
                cleaned
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini response is not valid JSON "
                f"for source: {host}\n"
                f"Response:\n{text}"
            ) from exc

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "Gemini response must be a JSON object "
                f"for source: {host}"
            )

        required_fields = (
            "name",
            "url",
            "description",
        )

        for field in required_fields:
            if field not in result:
                raise ValueError(
                    f"Gemini response missing required field "
                    f"'{field}' for source: {host}"
                )

        name = str(
            result["name"]
        ).strip()

        url = str(
            result["url"]
        ).strip()

        description = str(
            result["description"]
        ).strip()

        if not name:
            raise ValueError(
                f"Gemini returned empty name "
                f"for source: {host}"
            )

        if not description:
            raise ValueError(
                f"Gemini returned empty description "
                f"for source: {host}"
            )

        return {
            "name": name,
            "url": url,
            "description": description,
        }

    # ==========================================================
    # Save Result To Target
    # ==========================================================

    def save_result_to_target(
        self,
        result,
    ):
        """
        將單一 Gemini Source Discovery Result
        寫入 targets。

        Duplicate Rule：

            target_type
            +
            crawler_url
            +
            keyword

        判斷是否為同一個 Target。

        如果已存在：

            UPDATE

        如果不存在：

            INSERT

        url 不作為 duplicate key。

        因為 Gemini 未來可能重新找到更適合的：

            新聞
            專業資訊
            技術資訊
            產業資訊

        入口。

        Args:
            result:
                Gemini Source Discovery result。

        Returns:
            dict
        """

        if not isinstance(
            result,
            dict,
        ):
            raise ValueError(
                "result must be a dictionary."
            )

        name = str(
            result.get(
                "name",
                "",
            )
        ).strip()

        url = str(
            result.get(
                "url",
                "",
            )
        ).strip()

        crawler_url = str(
            result.get(
                "crawler_url",
                "",
            )
        ).strip()

        keyword = str(
            result.get(
                "keyword",
                self.KEYWORD,
            )
        ).strip()

        description = str(
            result.get(
                "description",
                "",
            )
        ).strip()

        # ------------------------------------------------------
        # 如果 result 沒有 crawler_url，
        # 使用 host 自動產生。
        # ------------------------------------------------------

        if not crawler_url:

            host = str(
                result.get(
                    "host",
                    "",
                )
            ).strip()

            if not host:
                raise ValueError(
                    "crawler_url or host is required."
                )

            crawler_url = (
                self.build_crawler_url(
                    host
                )
            )

        if not name:
            raise ValueError(
                "Target name cannot be empty."
            )

        if not url:
            url = crawler_url

        if not keyword:
            keyword = self.KEYWORD

        conn = get_connection()

        cursor = conn.cursor()

        try:
            # --------------------------------------------------
            # Check Existing Target
            #
            # 同一來源 + 同一 Keyword
            # 視為同一個 URL Target。
            # --------------------------------------------------

            select_sql = """
            SELECT id
            FROM targets
            WHERE target_type = %s
              AND crawler_url = %s
              AND keyword = %s
            ORDER BY id DESC
            LIMIT 1
            """

            cursor.execute(
                select_sql,
                (
                    self.TARGET_TYPE,
                    crawler_url,
                    keyword,
                ),
            )

            row = cursor.fetchone()

            now = datetime.now()

            # --------------------------------------------------
            # Existing Target → UPDATE
            # --------------------------------------------------

            if row:

                if isinstance(
                    row,
                    dict,
                ):
                    target_id = row.get(
                        "id"
                    )

                else:
                    target_id = row[0]

                update_sql = """
                UPDATE targets
                SET
                    name = %s,
                    target_type = %s,
                    url = %s,
                    crawler_url = %s,
                    keyword = %s,
                    search_provider = %s,
                    description = %s,
                    status = %s,
                    updated_time = %s
                WHERE id = %s
                """

                cursor.execute(
                    update_sql,
                    (
                        name,
                        self.TARGET_TYPE,
                        url,
                        crawler_url,
                        keyword,
                        self.SEARCH_PROVIDER,
                        description,
                        self.TARGET_STATUS,
                        now,
                        target_id,
                    ),
                )

                conn.commit()

                return {
                    "action": "updated",
                    "id": target_id,
                    "name": name,
                    "target_type": self.TARGET_TYPE,
                    "url": url,
                    "crawler_url": crawler_url,
                    "keyword": keyword,
                    "search_provider": (
                        self.SEARCH_PROVIDER
                    ),
                    "description": description,
                    "status": self.TARGET_STATUS,
                }

            # --------------------------------------------------
            # Target 不存在 → INSERT
            # --------------------------------------------------

            insert_sql = """
            INSERT INTO targets (
                name,
                target_type,
                url,
                crawler_url,
                keyword,
                search_provider,
                description,
                status,
                created_time,
                updated_time
            )
            VALUES (
                %s,
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
                insert_sql,
                (
                    name,
                    self.TARGET_TYPE,
                    url,
                    crawler_url,
                    keyword,
                    self.SEARCH_PROVIDER,
                    description,
                    self.TARGET_STATUS,
                    now,
                    now,
                ),
            )

            conn.commit()

            target_id = cursor.lastrowid

            return {
                "action": "inserted",
                "id": target_id,
                "name": name,
                "target_type": self.TARGET_TYPE,
                "url": url,
                "crawler_url": crawler_url,
                "keyword": keyword,
                "search_provider": (
                    self.SEARCH_PROVIDER
                ),
                "description": description,
                "status": self.TARGET_STATUS,
            }

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # ==========================================================
    # Save Results To Targets
    # ==========================================================

    def save_results_to_targets(
        self,
        results,
    ):
        """
        將 Gemini Source Discovery Results
        全部寫入 targets。

        Gemini API 發生錯誤的 source：

            不寫入 targets。

        正常 Gemini Result：

            INSERT
            或
            UPDATE

        Returns:
            list[dict]
        """

        if results is None:
            return []

        if not isinstance(
            results,
            list,
        ):
            raise ValueError(
                "results must be a list."
            )

        saved_results = []

        for result in results:

            if not isinstance(
                result,
                dict,
            ):
                saved_results.append(
                    {
                        "action": "skipped",
                        "reason": "invalid_result",
                    }
                )

                continue

            # --------------------------------------------------
            # Gemini API Error
            #
            # 不寫入 targets。
            # --------------------------------------------------

            if "error" in result:

                saved_results.append(
                    {
                        "action": "skipped",
                        "reason": "gemini_error",
                        "host": result.get(
                            "host",
                            "",
                        ),
                        "error": result.get(
                            "error",
                            "",
                        ),
                    }
                )

                continue

            saved_result = (
                self.save_result_to_target(
                    result
                )
            )

            saved_results.append(
                saved_result
            )

        return saved_results

    # ==========================================================
    # Execute Gemini Discovery
    # ==========================================================

    def execute(
        self,
        source_groups=None,
    ):
        """
        執行 Gemini Source Discovery。

        流程：

            articles
                ↓
            URL Source Grouping
                ↓
            source_groups
                ↓
            Gemini
                ↓
            Gemini Results

        注意：

            execute() 本身只負責取得 Gemini Results。

            如果需要同時寫入 targets，
            使用：

                execute_and_save()

        Args:
            source_groups:
                可選。

                如果沒有提供，
                自動執行 URLSourceGroupingService。

        Returns:
            list[dict]
        """

        if source_groups is None:

            grouping_result = (
                self.grouping_service.execute()
            )

            source_groups = (
                grouping_result.get(
                    "source_groups",
                    {},
                )
            )

        if not isinstance(
            source_groups,
            dict,
        ):
            raise ValueError(
                "source_groups must be a dictionary."
            )

        results = []

        for host, urls in sorted(
            source_groups.items()
        ):

            if not urls:
                continue

            try:

                gemini_result = (
                    self.analyze_source(
                        host=host,
                        urls=urls,
                    )
                )

                result = {
                    "host": host,
                    "keyword": self.KEYWORD,
                    "source_url_count": len(
                        urls
                    ),
                    "source_urls": list(
                        urls
                    ),
                    "name": gemini_result[
                        "name"
                    ],
                    "url": gemini_result[
                        "url"
                    ],
                    "crawler_url": gemini_result[
                        "crawler_url"
                    ],
                    "description": gemini_result[
                        "description"
                    ],
                }

                results.append(
                    result
                )

            except Exception as exc:

                # --------------------------------------------------
                # Gemini API 發生錯誤：
                #
                # 保留 source result，
                # 但標記 error。
                #
                # save_results_to_targets()
                # 會跳過這筆。
                # --------------------------------------------------

                crawler_url = (
                    self.build_crawler_url(
                        host
                    )
                )

                results.append(
                    {
                        "host": host,
                        "keyword": self.KEYWORD,
                        "source_url_count": len(
                            urls
                        ),
                        "source_urls": list(
                            urls
                        ),
                        "url": crawler_url,
                        "crawler_url": crawler_url,
                        "error": str(exc),
                    }
                )

        return results

    # ==========================================================
    # Execute And Save
    # ==========================================================

    def execute_and_save(
        self,
        source_groups=None,
    ):
        """
        執行完整 Gemini URL Source Discovery 流程。

        完整流程：

            URL Source Grouping
                ↓
            Target Crawler URL Exclusion
                ↓
            Source Groups
                ↓
            Gemini Source Discovery
                ↓
            Gemini Result
                ↓
            Target INSERT / UPDATE
                ↓
            targets

        這是提供給其他程式使用的完整 Service Function。

        Args:
            source_groups:
                可選。

                如果沒有提供，
                自動從 URLSourceGroupingService
                取得 source_groups。

        Returns:
            dict

        回傳：

            {
                "gemini_results": [...],
                "saved_results": [...],
                "gemini_source_count": 2,
                "inserted_count": 1,
                "updated_count": 1,
                "skipped_count": 0
            }
        """

        # ------------------------------------------------------
        # Step 1
        #
        # URL Source Grouping
        #
        # 如果沒有傳 source_groups，
        # execute() 內部會自動執行：
        #
        # articles
        #     ↓
        # targets crawler_url exclusion
        #     ↓
        # source grouping
        # ------------------------------------------------------

        gemini_results = (
            self.execute(
                source_groups=source_groups
            )
        )

        # ------------------------------------------------------
        # Step 2
        #
        # Gemini Results
        #     ↓
        # targets
        # ------------------------------------------------------

        saved_results = (
            self.save_results_to_targets(
                gemini_results
            )
        )

        # ------------------------------------------------------
        # Step 3
        #
        # Persistence Statistics
        # ------------------------------------------------------

        inserted_count = 0

        updated_count = 0

        skipped_count = 0

        for saved_result in saved_results:

            action = saved_result.get(
                "action"
            )

            if action == "inserted":
                inserted_count += 1

            elif action == "updated":
                updated_count += 1

            elif action == "skipped":
                skipped_count += 1

        return {
            "gemini_results": gemini_results,
            "saved_results": saved_results,
            "gemini_source_count": len(
                gemini_results
            ),
            "inserted_count": inserted_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
        }


# ==============================================================
# Public Complete Flow Function
# ==============================================================

def run_gemini_url_source_discovery(
    source_groups=None,
    grouping_service=None,
    api_key=None,
    model=None,
):
    """
    AutoSearch V6.4

    Gemini URL Source Discovery 完整流程入口。

    此 Function 可以被其他程式直接呼叫。

    完整流程：

        articles
            ↓
        URL Source Grouping
            ↓
        Target Crawler URL Exclusion
            ↓
        Source Groups
            ↓
        Gemini
            ↓
        name / url / description
            ↓
        crawler_url
            ↓
        targets INSERT / UPDATE

    使用方式：

        from services.gemini_url_source_discovery_service import (
            run_gemini_url_source_discovery,
        )

        result = (
            run_gemini_url_source_discovery()
        )

    如果需要指定：

        grouping_service
        api_key
        model

    也可以傳入。

    Returns:
        dict

    Example:

        {
            "gemini_results": [...],
            "saved_results": [...],
            "gemini_source_count": 2,
            "inserted_count": 1,
            "updated_count": 1,
            "skipped_count": 0
        }
    """

    service = (
        GeminiURLSourceDiscoveryService(
            grouping_service=grouping_service,
            api_key=api_key,
            model=model,
        )
    )

    return (
        service.execute_and_save(
            source_groups=source_groups
        )
    )


# ==============================================================
# Manual Test / Complete Flow
# ==============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "AutoSearch V6.4 "
        "Gemini URL Source Discovery"
    )

    print(
        "=" * 60
    )

    # ----------------------------------------------------------
    # 執行完整流程
    #
    # articles
    #     ↓
    # URL Source Grouping
    #     ↓
    # Gemini
    #     ↓
    # targets INSERT / UPDATE
    # ----------------------------------------------------------

    result = (
        run_gemini_url_source_discovery()
    )

    gemini_results = (
        result[
            "gemini_results"
        ]
    )

    saved_results = (
        result[
            "saved_results"
        ]
    )

    # ----------------------------------------------------------
    # Gemini Results
    # ----------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "GEMINI SOURCE DISCOVERY RESULTS"
    )

    print(
        "=" * 60
    )

    for item in gemini_results:

        print(
            f"\n[{item.get('host', '')}]"
        )

        if "error" in item:

            print(
                f"ERROR: "
                f"{item.get('error', '')}"
            )

            continue

        print(
            f"name: "
            f"{item.get('name', '')}"
        )

        print(
            f"url: "
            f"{item.get('url', '')}"
        )

        print(
            f"crawler_url: "
            f"{item.get('crawler_url', '')}"
        )

        print(
            f"keyword: "
            f"{item.get('keyword', '')}"
        )

        print(
            f"description: "
            f"{item.get('description', '')}"
        )

    # ----------------------------------------------------------
    # Target Persistence Results
    # ----------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "TARGET PERSISTENCE"
    )

    print(
        "=" * 60
    )

    for item in saved_results:

        action = item.get(
            "action",
            "",
        )

        if action == "inserted":

            print(
                f"INSERTED "
                f"target_id={item.get('id')}, "
                f"name={item.get('name', '')}, "
                f"url={item.get('url', '')}"
            )

        elif action == "updated":

            print(
                f"UPDATED "
                f"target_id={item.get('id')}, "
                f"name={item.get('name', '')}, "
                f"url={item.get('url', '')}"
            )

        elif action == "skipped":

            print(
                f"SKIPPED "
                f"host={item.get('host', '')}, "
                f"reason={item.get('reason', '')}"
            )

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------

    print(
        "\n"
        + "=" * 60
    )

    print(
        "COMPLETE FLOW SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"Gemini source count: "
        f"{result['gemini_source_count']}"
    )

    print(
        f"Inserted targets: "
        f"{result['inserted_count']}"
    )

    print(
        f"Updated targets: "
        f"{result['updated_count']}"
    )

    print(
        f"Skipped targets: "
        f"{result['skipped_count']}"
    )

    print(
        "=" * 60
    )