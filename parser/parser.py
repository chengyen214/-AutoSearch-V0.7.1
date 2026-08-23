"""
parser/parser.py

AutoSearch V5

V5 Parser

用途：

1. HTML 解析
2. 移除 HTML 結構垃圾
3. 移除廣告 / 推薦區塊
4. Content Density Score
5. Keyword Ranking
6. 找真正文章正文
7. 支援中文 / 英文新聞
8. 傳給 Cleaner / Extractor 清理
9. 建立 Article Object
10. 建立完整文章內容 SHA-256 Hash 作為 document_id

Pipeline：

    Crawler
        ↓
    HTML
        ↓
    Parser
        ↓
    Clean / Extract
        ↓
    Article
        ↓
    ArticleRepository
        ↓
    SQL
        ↓
    AI Task / Archive

document_id 設計：

    document_id = SHA-256(
        完整清理後文章正文
    )

用途：

    - Article Duplicate Detection
    - Content Identity
    - Article Version Detection
    - 不同文章內容版本產生不同 document_id

本模組負責：

    - HTML Parsing
    - HTML Noise Removal
    - Main Content Detection
    - Content Cleaning
    - Article Object 建立
    - document_id Hash 建立

本模組不負責：

    - Search
    - Search Provider
    - Search Adapter
    - Crawler
    - MongoDB
    - MySQL
    - Archive
    - AI
    - Job
    - Scheduler
"""


from hashlib import sha256


from bs4 import BeautifulSoup


from cleaner.cleaner import (
    clean_text,
)


from extractor.extractor import (
    extract,
)


from models.article import (
    Article,
)


# ==================================================
#
# HTML Noise Keywords
#
# ==================================================

BAD_WORDS = [

    # ----------------------------------------------
    # Advertisement
    # ----------------------------------------------

    "advert",
    "advertisement",
    "ad-banner",
    "ad-container",
    "ads-container",
    "sponsor",

    # ----------------------------------------------
    # Recommendation
    # ----------------------------------------------

    "related-news",
    "related-article",
    "recommended",
    "recommendation",
    "more-news",
    "latest-news",

    # ----------------------------------------------
    # Social
    # ----------------------------------------------

    "social-share",
    "social-links",
    "share-buttons",
    "share-tools",

    # ----------------------------------------------
    # Membership
    # ----------------------------------------------

    "subscribe",
    "newsletter",
    "login",
    "register",

]


# ==================================================
#
# Generate Document ID
#
# ==================================================

def generate_document_id(
    content,
):
    """
    根據完整文章正文建立 document_id。

    規則：

        document_id =
            SHA-256(
                完整清理後文章正文
            )

    注意：

        Hash 的來源必須是最終文章正文，
        而不是：

            - URL
            - Title
            - Keyword
            - Source
            - Crawl Time
            - HTML 原始內容

    這樣可以讓：

        相同文章內容
            ↓
        相同 document_id

        文章內容改變
            ↓
        不同 document_id

    用途：

        - Duplicate Detection
        - Content Identity
        - Article Version Detection

    Parameters
    ----------
    content :
        最終清理完成的文章正文。

    Returns
    -------
    str

        SHA-256 hexadecimal hash。

    Raises
    ------
    ValueError
        content 為空。
    """

    if content is None:

        raise ValueError(
            "generate_document_id() "
            "requires content"
        )

    if not isinstance(
        content,
        str,
    ):

        content = str(
            content
        )

    content = content.strip()

    if not content:

        raise ValueError(
            "generate_document_id() "
            "requires non-empty content"
        )

    return sha256(
        content.encode(
            "utf-8"
        )
    ).hexdigest()


# ==================================================
#
# Remove HTML Noise
#
# ==================================================

def remove_html_noise(
    soup,
):
    """
    移除常見 HTML 噪音。

    包含：

        - script
        - style
        - nav
        - header
        - footer
        - aside
        - form
        - iframe
        - button

    以及：

        class / id
        中常見的廣告、推薦、社群、
        會員區塊。

    Parameters
    ----------
    soup :
        BeautifulSoup instance

    Returns
    -------
    BeautifulSoup
    """

    if soup is None:

        return soup

    # ==================================================
    # Tag Noise
    # ==================================================

    remove_tags = [

        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        "form",
        "iframe",
        "button",

    ]

    for tag_name in remove_tags:

        for tag in soup.find_all(
            tag_name
        ):

            tag.decompose()

    # ==================================================
    # Class / ID Noise
    # ==================================================

    nodes = list(
        soup.find_all(True)
    )

    for node in nodes:

        if not getattr(
            node,
            "attrs",
            None,
        ):

            continue

        classes = node.get(
            "class",
            [],
        )

        if isinstance(
            classes,
            list,
        ):

            classes = " ".join(
                str(item)
                for item in classes
            )

        else:

            classes = str(
                classes
            )

        node_id = node.get(
            "id",
            "",
        )

        attributes = (
            f"{classes} "
            f"{node_id}"
        ).lower()

        should_remove = False

        for word in BAD_WORDS:

            if word in attributes:

                should_remove = True

                break

        if should_remove:

            try:

                node.decompose()

            except (
                AttributeError,
            ):

                pass

    return soup


# ==================================================
#
# Content Score
#
# ==================================================

def content_score(
    node,
    keyword="",
):
    """
    計算候選節點的正文分數。

    評估：

        - Text Length
        - Link Penalty
        - HTML Complexity
        - Content Density
        - Keyword Bonus

    分數越高：

        越可能是真正文章正文。
    """

    if node is None:

        return 0

    text = node.get_text(
        separator="\n",
        strip=True,
    )

    if len(text) < 100:

        return 0

    # ==================================================
    # Text Length
    # ==================================================

    text_score = len(
        text
    )

    # ==================================================
    # Link Penalty
    # ==================================================

    links = len(
        node.find_all("a")
    )

    link_penalty = (
        links * 50
    )

    # ==================================================
    # HTML Complexity
    # ==================================================

    tags = len(
        node.find_all()
    )

    tag_penalty = (
        tags * 2
    )

    # ==================================================
    # Content Density
    # ==================================================

    html_size = len(
        str(node)
    )

    density = (
        len(text)
        /
        (html_size + 1)
    )

    density_bonus = (
        density * 500
    )

    # ==================================================
    # Keyword Bonus
    # ==================================================

    keyword_bonus = 0

    if keyword:

        keyword_text = str(
            keyword
        ).strip()

        if keyword_text:

            keyword_count = (
                text.lower().count(
                    keyword_text.lower()
                )
            )

            keyword_bonus = (
                keyword_count * 100
            )

    # ==================================================
    # Final Score
    # ==================================================

    score = (

        text_score

        - link_penalty

        - tag_penalty

        + density_bonus

        + keyword_bonus

    )

    return score


# ==================================================
#
# Find Main Content
#
# ==================================================

def find_main_content(
    soup,
    keyword="",
):
    """
    找出最可能的文章正文。

    Candidate 優先順序：

        1. article
        2. main
        3. 常見新聞正文 class
        4. div fallback

    Returns
    -------

    str

        文章正文。
    """

    if soup is None:

        return ""

    candidates = []

    # ==================================================
    # <article>
    # ==================================================

    for node in soup.find_all(
        "article"
    ):

        candidates.append(
            node
        )

    # ==================================================
    # <main>
    # ==================================================

    for node in soup.find_all(
        "main"
    ):

        candidates.append(
            node
        )

    # ==================================================
    # Common Article Selectors
    # ==================================================

    selectors = [

        ".article-body",
        ".article-content",
        ".article-text",
        ".article-detail",
        ".post-content",
        ".entry-content",
        ".story-body",
        ".story-content",
        ".news-content",
        ".news-body",

    ]

    for selector in selectors:

        try:

            nodes = soup.select(
                selector
            )

        except Exception:

            nodes = []

        for node in nodes:

            candidates.append(
                node
            )

    # ==================================================
    # Candidate Ranking
    # ==================================================

    best_node = None

    best_score = 0

    seen_nodes = set()

    for node in candidates:

        node_id = id(
            node
        )

        if node_id in seen_nodes:

            continue

        seen_nodes.add(
            node_id
        )

        score = content_score(
            node,
            keyword,
        )

        if score > best_score:

            best_score = score

            best_node = node

    # ==================================================
    # DIV Fallback
    # ==================================================

    if best_node is None:

        for div in soup.find_all(
            "div"
        ):

            score = content_score(
                div,
                keyword,
            )

            if score > best_score:

                best_score = score

                best_node = div

    # ==================================================
    # Return Content
    # ==================================================

    if best_node is not None:

        return best_node.get_text(
            separator="\n",
            strip=True,
        )

    return ""


# ==================================================
#
# Parse
#
# ==================================================

def parse(
    html,
    keyword,
    url="",
):
    """
    解析 HTML 並建立 Article。

    Parameters
    ----------
    html :
        Crawler 下載的 HTML。

    keyword :
        本次搜尋 Keyword。

        必須提供。

    url :
        原始 / 最終 URL。

    Returns
    -------

    Article

    Raises
    ------

    ValueError
        HTML 或 Keyword 無效。

    document_id：

        最終文章正文經過 SHA-256
        所產生的內容 Hash。

    """

    # ==================================================
    # Validate HTML
    # ==================================================

    if html is None:

        raise ValueError(
            "parse() requires html"
        )

    if isinstance(
        html,
        bytes,
    ):

        try:

            html = html.decode(
                "utf-8",
                errors="replace",
            )

        except Exception as e:

            raise ValueError(
                f"Failed to decode html: {e}"
            ) from e

    elif not isinstance(
        html,
        str,
    ):

        html = str(
            html
        )

    html = html.strip()

    if not html:

        raise ValueError(
            "parse() requires non-empty html"
        )

    # ==================================================
    # Validate Keyword
    # ==================================================

    if keyword is None:

        raise ValueError(
            "parse() requires keyword"
        )

    keyword = str(
        keyword
    ).strip()

    if not keyword:

        raise ValueError(
            "parse() requires non-empty keyword"
        )

    # ==================================================
    # Normalize URL
    # ==================================================

    if url is None:

        url = ""

    url = str(
        url
    ).strip()

    # ==================================================
    # BeautifulSoup
    # ==================================================

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # ==================================================
    # Remove HTML Noise
    # ==================================================

    soup = remove_html_noise(
        soup
    )

    # ==================================================
    # Find Main Content
    # ==================================================

    content = find_main_content(
        soup,
        keyword,
    )

    # ==================================================
    # Fallback
    # ==================================================

    if len(content) < 200:

        content = soup.get_text(
            separator="\n",
            strip=True,
        )

    # ==================================================
    # Cleaner
    # ==================================================

    content = clean_text(
        content
    )

    # ==================================================
    # Extractor
    # ==================================================

    content = extract(
        content
    )

    # ==================================================
    # Normalize Final Content
    #
    # Hash 前最後一次 normalize。
    #
    # 確保：
    #
    # 相同正文
    #     ↓
    # 相同 document_id
    #
    # ==================================================

    if content is None:

        content = ""

    if not isinstance(
        content,
        str,
    ):

        content = str(
            content
        )

    content = content.strip()

    # ==================================================
    # Validate Final Content
    # ==================================================

    if not content:

        raise ValueError(
            "parse() produced empty article content"
        )

    # ==================================================
    # Generate Document ID
    #
    # 完整文章正文 SHA-256
    #
    # ==================================================

    document_id = generate_document_id(
        content
    )

    # ==================================================
    # Article
    # ==================================================

    article = Article()

    # ==================================================
    # Title
    # ==================================================

    if soup.title:

        article.title = (
            soup.title.get_text(
                strip=True
            )
        )

    else:

        article.title = ""

    # ==================================================
    # Article Fields
    # ==================================================

    article.url = url

    article.published = None

    article.keyword = keyword

    article.content = content

    # ==================================================
    # Document ID
    #
    # 注意：
    #
    # 名稱維持 document_id。
    #
    # 實際內容：
    #
    #     SHA-256(article.content)
    #
    # ==================================================

    article.document_id = (
        document_id
    )

    # ==================================================
    # Return
    # ==================================================

    return article


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [

    "generate_document_id",

    "remove_html_noise",

    "content_score",

    "find_main_content",

    "parse",

]