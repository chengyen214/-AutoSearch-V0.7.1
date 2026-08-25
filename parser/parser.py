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

Fallback Strategy：

    正常 Main Content Detection
            ↓
    找不到可靠正文
            ↓
    Largest Text Block Fallback
            ↓
    找頁面中「文字最多」的合理區塊
            ↓
    Cleaner
            ↓
    Extractor
            ↓
    Article

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
    "advertising",

    # ----------------------------------------------
    # Sponsor
    # ----------------------------------------------

    "sponsor",
    "sponsored",

    # ----------------------------------------------
    # Recommendation
    # ----------------------------------------------

    "related-news",
    "related-article",
    "related-content",
    "recommended",
    "recommendation",
    "more-news",
    "latest-news",
    "you-may-like",

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

    # ----------------------------------------------
    # Navigation
    # ----------------------------------------------

    "breadcrumb",
    "navigation",
    "navbar",
    "menu",

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

    document_id =
        SHA-256(
            完整清理後文章正文
        )
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
        會員與導覽區塊。
    """

    if soup is None:

        return soup

    # ==================================================
    # Tag Noise
    # ==================================================

    remove_tags = [

        "script",
        "style",
        "noscript",
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

            try:

                tag.decompose()

            except Exception:

                pass

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

            except AttributeError:

                pass

    return soup


# ==================================================
#
# Extract Node Text
#
# ==================================================

def get_node_text(
    node,
):
    """
    取得候選節點的純文字。

    使用統一 separator，
    避免不同網站的 HTML 結構
    導致文字全部黏在一起。
    """

    if node is None:

        return ""

    try:

        text = node.get_text(
            separator="\n",
            strip=True,
        )

    except Exception:

        return ""

    if not isinstance(
        text,
        str,
    ):

        text = str(
            text
        )

    return text.strip()


# ==================================================
#
# Text Length
#
# ==================================================

def text_length(
    node,
):
    """
    計算候選節點的有效文字長度。
    """

    return len(
        get_node_text(
            node
        )
    )


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

    注意：

        這不是唯一判斷方法。

        如果沒有任何節點得到可靠分數，
        find_main_content() 會進入
        largest text block fallback。
    """

    if node is None:

        return 0

    text = get_node_text(
        node
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
    #
    # 對 link 很多的區塊扣分。
    #
    # 但不直接淘汰。
    #
    # 某些文章正文本身可能有超連結。
    # ==================================================

    links = len(
        node.find_all("a")
    )

    link_penalty = (
        links * 35
    )

    # ==================================================
    # HTML Complexity
    # ==================================================

    tags = len(
        node.find_all()
    )

    tag_penalty = (
        tags * 1.5
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
# Largest Text Block Fallback
#
# ==================================================

def find_largest_text_block(
    soup,
):
    """
    找出頁面中「文字最多」的合理區塊。

    這是 Parser 的重要 fallback。

    當網站：

        - 沒有 <article>
        - 沒有 <main>
        - 沒有標準 article class
        - Content Score 無法可靠判斷

    不直接放棄。

    而是：

        1. 搜尋 section / div / td / body
        2. 計算每個區塊的文字長度
        3. 避免大量 link / menu 類區塊
        4. 選擇文字最多的合理區塊

    目的：

        最大化不同網站的可爬取率。
    """

    if soup is None:

        return ""

    candidates = []

    # ==================================================
    # Candidate Tags
    # ==================================================

    for tag_name in [
        "article",
        "main",
        "section",
        "div",
        "td",
    ]:

        try:

            nodes = soup.find_all(
                tag_name
            )

        except Exception:

            nodes = []

        for node in nodes:

            candidates.append(
                node
            )

    # ==================================================
    # Body Fallback
    # ==================================================

    if soup.body is not None:

        candidates.append(
            soup.body
        )

    # ==================================================
    # Rank by Text Length
    # ==================================================

    best_node = None

    best_length = 0

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

        text = get_node_text(
            node
        )

        length = len(
            text
        )

        # ----------------------------------------------
        # Minimum meaningful content
        # ----------------------------------------------

        if length < 200:

            continue

        # ----------------------------------------------
        # Link Ratio
        #
        # 避免：
        #
        # 整個 menu
        # 整個 link list
        # 整個推薦區
        #
        # 被誤認為正文。
        # ----------------------------------------------

        links = len(
            node.find_all("a")
        )

        words = len(
            text.split()
        )

        if words <= 0:

            continue

        link_ratio = (
            links
            /
            max(
                words,
                1,
            )
        )

        # ----------------------------------------------
        # Link-heavy penalty
        # ----------------------------------------------

        if link_ratio > 0.8:

            continue

        # ----------------------------------------------
        # Text score
        #
        # 主要以文字量為核心。
        # ----------------------------------------------

        score = (
            length
            *
            (
                1
                -
                min(
                    link_ratio,
                    0.7,
                )
                * 0.5
            )
        )

        # ----------------------------------------------
        # 優先選擇文字最多
        # ----------------------------------------------

        if score > best_score:

            best_score = score

            best_length = length

            best_node = node

    # ==================================================
    # Return
    # ==================================================

    if best_node is not None:

        return get_node_text(
            best_node
        )

    # ==================================================
    # 最後 fallback：
    # 整個 Body
    # ==================================================

    if soup.body is not None:

        body_text = get_node_text(
            soup.body
        )

        if len(body_text) >= 200:

            return body_text

    return ""


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

    Strategy：

        第一層：
            Article / Main / 常見 Article Selector

        第二層：
            Content Score

        第三層：
            Largest Text Block

        第四層：
            Body Text

    因此：

        如果網站結構標準
            → 使用 Content Score

        如果網站結構特殊
            → 使用 Largest Text Block

        如果網站非常特殊
            → 使用 Body Text
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
        ".article-detail-content",

        ".post-content",
        ".post-body",
        ".entry-content",

        ".story-body",
        ".story-content",

        ".news-content",
        ".news-body",

        ".content-body",
        ".content-detail",
        ".content-article",

        ".article-main",
        ".article-container",

        "#article-content",
        "#article-body",
        "#article",

        "#content",
        "#main-content",

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
    # DIV / SECTION Content Score
    #
    # 如果 article/main 不存在，
    # 先嘗試一般內容容器。
    # ==================================================

    if best_node is None:

        fallback_candidates = []

        for tag_name in [
            "section",
            "div",
        ]:

            try:

                fallback_candidates.extend(
                    soup.find_all(
                        tag_name
                    )
                )

            except Exception:

                pass

        for node in fallback_candidates:

            score = content_score(
                node,
                keyword,
            )

            if score > best_score:

                best_score = score

                best_node = node

    # ==================================================
    # Return Main Content
    # ==================================================

    if best_node is not None:

        content = get_node_text(
            best_node
        )

        if len(content) >= 200:

            return content

    # ==================================================
    # IMPORTANT FALLBACK
    #
    # 找不到可靠正文時：
    #
    # 「不要放棄」
    #
    # 改找文字最多的合理區塊。
    # ==================================================

    largest_content = (
        find_largest_text_block(
            soup
        )
    )

    if len(largest_content) >= 200:

        return largest_content

    # ==================================================
    # Final Body Fallback
    # ==================================================

    if soup.body is not None:

        body_content = get_node_text(
            soup.body
        )

        if body_content:

            return body_content

    # ==================================================
    # Final Soup Fallback
    # ==================================================

    return get_node_text(
        soup
    )


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

    Parser Strategy：

        HTML
          ↓
        Remove Noise
          ↓
        Main Content Detection
          ↓
        Content Score
          ↓
        Largest Text Block Fallback
          ↓
        Body Fallback
          ↓
        Cleaner
          ↓
        Extractor
          ↓
        Article
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
    # Emergency Fallback
    #
    # 理論上 find_main_content()
    # 已經處理。
    #
    # 這裡再保護一次。
    # ==================================================

    if not content:

        content = get_node_text(
            soup.body
            if soup.body is not None
            else soup
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
    # Extractor Empty Fallback
    #
    # 如果 Extractor 對特殊網站過度嚴格，
    # 再回到原始選出的正文。
    #
    # 這是非常重要的第二層保護。
    # ==================================================

    if not content:

        fallback_content = find_main_content(
            BeautifulSoup(
                html,
                "html.parser",
            ),
            keyword,
        )

        fallback_content = clean_text(
            fallback_content
        )

        if fallback_content:

            content = fallback_content.strip()

    # ==================================================
    # Validate Final Content
    # ==================================================

    if not content:

        raise ValueError(
            "parse() produced empty article content"
        )

    # ==================================================
    # Generate Document ID
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

    "get_node_text",

    "text_length",

    "content_score",

    "find_largest_text_block",

    "find_main_content",

    "parse",

]