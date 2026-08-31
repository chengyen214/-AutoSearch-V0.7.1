"""
tests/V6_2/test_crawl_service.py

AutoSearch V5

V6.2

CrawlService -> RawHTMLRepository Integration Test

測試目標：

    ③ services/crawl_service.py
            |
            v
        CrawlResult
            |
            v
    ④ database/raw_html_repository.py
            |
            v
        MongoDB
            |
            v
        raw_html

本測試確認：

    1. CrawlService 可以成功 Crawl
    2. CrawlResult 正確建立
    3. resources 結構存在
    4. resources.css[] 有 Resource
    5. resources.images[] 有 Resource
    6. CrawlService 將 CrawlResult
       傳給 RawHTMLRepository
    7. RawHTMLRepository 將資料保存至 MongoDB
    8. MongoDB raw_html.resources
       正確保存 css[]
    9. MongoDB raw_html.resources
       正確保存 images[]
    10. HTML / Hash / URL
        與 CrawlResult 一致
    11. Resource Metadata
        與 CrawlResult 一致
    12. Image Binary Data
        確實保存至 MongoDB

本階段不測：

    - ParserService
    - ArticleService
    - Article
    - MySQL
    - ArchiveService
    - AI
    - AI Task


Pipeline：

    URL
     |
     v
    CrawlService
     |
     v
    crawler.py
     |
     +--> HTML
     |
     +--> CSS Download
     |
     +--> Image Download
     |
     v
    CrawlResult
     |
     v
    RawHTMLRepository.save_crawl_result()
     |
     v
    MongoDB
     |
     v
    raw_html
        |
        +-- url
        +-- resolved_url
        +-- html
        +-- content_hash
        +-- resources
             |
             +-- css[]
             |
             +-- images[]
"""


# ==================================================
#
# Standard Library
#
# ==================================================

import hashlib

from datetime import (
    datetime,
    timezone,
)


# ==================================================
#
# Project
#
# ==================================================

from services.crawl_service import (
    CrawlResult,
    CrawlService,
)

from database.raw_html_repository import (
    RawHTMLRepository,
)


# ==================================================
#
# Test Configuration
#
# ==================================================

TEST_URL = (
    "https://www.nuk.edu.tw/"
)


# ==================================================
#
# Main Integration Test
#
# ==================================================

def test_crawl_service_nuk():
    """
    測試完整：

        CrawlService
            |
            v
        CrawlResult
            |
            v
        RawHTMLRepository
            |
            v
        MongoDB

    核心確認：

        resources
        ├── css[]
        └── images[]

    不只是確認 CrawlResult 有 resources，

    而是確認：

        CrawlResult.resources
                |
                v
        RawHTMLRepository
                |
                v
        MongoDB
                |
                v
        raw_html.resources

    完整保存成功。
    """

    # ==================================================
    #
    # 建立 Repository
    #
    # ==================================================

    repository = RawHTMLRepository()

    # ==================================================
    #
    # 建立 CrawlService
    #
    # IMPORTANT：
    #
    # save_raw_html=True
    #
    # 才會測試：
    #
    # CrawlService
    #     ->
    # RawHTMLRepository
    #     ->
    # MongoDB
    #
    # ==================================================

    service = CrawlService(

        raw_html_repository=repository,

        save_raw_html=True,

    )

    # ==================================================
    #
    # Crawl
    #
    # ==================================================

    crawl_started_at = datetime.now(
        timezone.utc
    )

    result = service.crawl(
        TEST_URL
    )

    crawl_finished_at = datetime.now(
        timezone.utc
    )

    # ==================================================
    #
    # Basic Result
    #
    # ==================================================

    assert isinstance(
        result,
        CrawlResult,
    )

    assert result.url == TEST_URL

    assert result.success is True

    assert result.error is None

    # ==================================================
    #
    # HTML
    #
    # ==================================================

    assert result.html is not None

    assert isinstance(
        result.html,
        str,
    )

    assert result.html.strip() != ""

    # ==================================================
    #
    # Resolved URL
    #
    # ==================================================

    assert result.resolved_url is not None

    assert isinstance(
        result.resolved_url,
        str,
    )

    assert result.resolved_url.strip() != ""

    # ==================================================
    #
    # Content Hash
    #
    # ==================================================

    assert result.content_hash is not None

    assert isinstance(
        result.content_hash,
        str,
    )

    assert len(
        result.content_hash
    ) == 64

    expected_hash = hashlib.sha256(
        result.html.encode(
            "utf-8"
        )
    ).hexdigest()

    assert (
        result.content_hash
        == expected_hash
    )

    # ==================================================
    #
    # Resources
    #
    # ==================================================

    assert result.resources is not None

    assert isinstance(
        result.resources,
        dict,
    )

    assert "css" in result.resources

    assert "images" in result.resources

    assert isinstance(
        result.resources["css"],
        list,
    )

    assert isinstance(
        result.resources["images"],
        list,
    )

    # ==================================================
    #
    # Resource Download Confirmation
    #
    # ==================================================

    print()
    print("=" * 70)
    print(
        "CrawlService -> RawHTMLRepository "
        "Integration Test"
    )
    print("=" * 70)

    print(
        f"Original URL : {result.url}"
    )

    print(
        f"Resolved URL : {result.resolved_url}"
    )

    print(
        f"CSS count    : "
        f"{len(result.resources['css'])}"
    )

    print(
        f"Image count  : "
        f"{len(result.resources['images'])}"
    )

    # --------------------------------------------------
    # 至少要確認 Resource Processing
    # --------------------------------------------------

    assert (
        len(result.resources["css"])
        +
        len(result.resources["images"])
        > 0
    )

    # ==================================================
    #
    # CSS Resource Validation
    #
    # ==================================================

    for index, resource in enumerate(
        result.resources["css"],
        start=1,
    ):

        assert isinstance(
            resource,
            dict,
        )

        assert resource.get(
            "url"
        )

        assert resource.get(
            "content"
        )

        assert resource.get(
            "content_hash"
        )

        assert resource.get(
            "mime_type"
        )

        assert resource.get(
            "file_size"
        ) is not None

        # Verify CSS Hash

        expected_resource_hash = (
            hashlib.sha256(
                resource["content"].encode(
                    "utf-8"
                )
            ).hexdigest()
        )

        assert (
            resource["content_hash"]
            ==
            expected_resource_hash
        )

        # Verify CSS Size

        expected_size = len(
            resource["content"].encode(
                "utf-8"
            )
        )

        assert (
            resource["file_size"]
            ==
            expected_size
        )

        print(
            f"[CSS {index}] "
            f"{resource['url']}"
        )

        print(
            f"         MIME : "
            f"{resource['mime_type']}"
        )

        print(
            f"         Size : "
            f"{resource['file_size']}"
        )

    # ==================================================
    #
    # Image Resource Validation
    #
    # ==================================================

    for index, resource in enumerate(
        result.resources["images"],
        start=1,
    ):

        assert isinstance(
            resource,
            dict,
        )

        assert resource.get(
            "url"
        )

        assert resource.get(
            "data"
        )

        assert resource.get(
            "content_hash"
        )

        assert resource.get(
            "mime_type"
        )

        assert resource.get(
            "file_size"
        ) is not None

        # --------------------------------------------------
        # MIME
        # --------------------------------------------------

        assert resource[
            "mime_type"
        ].startswith(
            "image/"
        )

        # --------------------------------------------------
        # Binary Data
        # --------------------------------------------------

        assert isinstance(
            resource["data"],
            bytes,
        )

        # --------------------------------------------------
        # Hash
        # --------------------------------------------------

        expected_resource_hash = (
            hashlib.sha256(
                resource["data"]
            ).hexdigest()
        )

        assert (
            resource["content_hash"]
            ==
            expected_resource_hash
        )

        # --------------------------------------------------
        # Size
        # --------------------------------------------------

        assert (
            resource["file_size"]
            ==
            len(resource["data"])
        )

        print(
            f"[IMAGE {index}] "
            f"{resource['url']}"
        )

        print(
            f"           MIME : "
            f"{resource['mime_type']}"
        )

        print(
            f"           Size : "
            f"{resource['file_size']}"
        )

    # ==================================================
    #
    # MongoDB Lookup
    #
    # ==================================================

    # --------------------------------------------------
    # 使用 URL + Content Hash
    #
    # 確認 CrawlService 建立的
    # Snapshot 已進 MongoDB。
    # --------------------------------------------------

    stored_document = (
        repository.find_by_url_and_content_hash(

            result.url,

            result.content_hash,

        )
    )

    assert stored_document is not None

    # ==================================================
    #
    # MongoDB Basic Fields
    #
    # ==================================================

    assert stored_document.get(
        "url"
    ) == result.url

    assert stored_document.get(
        "resolved_url"
    ) == result.resolved_url

    assert stored_document.get(
        "html"
    ) == result.html

    assert stored_document.get(
        "content_hash"
    ) == result.content_hash

    # ==================================================
    #
    # MongoDB Document Identity
    #
    # ==================================================

    assert stored_document.get(
        "_id"
    ) is not None

    # Crawl 階段尚未建立 Article / Document

    assert stored_document.get(
        "document_id"
    ) is None

    # ==================================================
    #
    # MongoDB Datetime
    #
    # ==================================================

    created_at = stored_document.get(
        "created_at"
    )

    updated_at = stored_document.get(
        "updated_at"
    )

    assert isinstance(
        created_at,
        datetime,
    )

    assert isinstance(
        updated_at,
        datetime,
    )

    # MongoDB / PyMongo 通常會回傳
    # timezone-aware UTC 或可轉換 datetime。

    if created_at.tzinfo is None:

        created_at = created_at.replace(
            tzinfo=timezone.utc
        )

    else:

        created_at = created_at.astimezone(
            timezone.utc
        )

    if updated_at.tzinfo is None:

        updated_at = updated_at.replace(
            tzinfo=timezone.utc
        )

    else:

        updated_at = updated_at.astimezone(
            timezone.utc
        )

    assert (
        crawl_started_at
        <= created_at
        <= crawl_finished_at
    )

    assert (
        crawl_started_at
        <= updated_at
        <= crawl_finished_at
    )

    # ==================================================
    #
    # MongoDB Resources
    #
    # ==================================================

    stored_resources = (
        stored_document.get(
            "resources"
        )
    )

    assert stored_resources is not None

    assert isinstance(
        stored_resources,
        dict,
    )

    assert "css" in stored_resources

    assert "images" in stored_resources

    assert isinstance(
        stored_resources["css"],
        list,
    )

    assert isinstance(
        stored_resources["images"],
        list,
    )

    # ==================================================
    #
    # Resource Count
    #
    # ==================================================

    assert (
        len(stored_resources["css"])
        ==
        len(result.resources["css"])
    )

    assert (
        len(stored_resources["images"])
        ==
        len(result.resources["images"])
    )

    # ==================================================
    #
    # CSS MongoDB Persistence
    #
    # ==================================================

    for expected, stored in zip(
        result.resources["css"],
        stored_resources["css"],
    ):

        assert stored.get(
            "url"
        ) == expected.get(
            "url"
        )

        assert stored.get(
            "content"
        ) == expected.get(
            "content"
        )

        assert stored.get(
            "content_hash"
        ) == expected.get(
            "content_hash"
        )

        assert stored.get(
            "mime_type"
        ) == expected.get(
            "mime_type"
        )

        assert stored.get(
            "file_size"
        ) == expected.get(
            "file_size"
        )

    # ==================================================
    #
    # Image MongoDB Persistence
    #
    # ==================================================

    for expected, stored in zip(
        result.resources["images"],
        stored_resources["images"],
    ):

        assert stored.get(
            "url"
        ) == expected.get(
            "url"
        )

        assert stored.get(
            "data"
        ) == expected.get(
            "data"
        )

        assert stored.get(
            "content_hash"
        ) == expected.get(
            "content_hash"
        )

        assert stored.get(
            "mime_type"
        ) == expected.get(
            "mime_type"
        )

        assert stored.get(
            "file_size"
        ) == expected.get(
            "file_size"
        )

    # ==================================================
    #
    # Explicit Resource Confirmation
    #
    # ==================================================

    print()
    print("-" * 70)

    print(
        "MongoDB raw_html.resources verification"
    )

    print("-" * 70)

    print(
        f"MongoDB CSS count    : "
        f"{len(stored_resources['css'])}"
    )

    print(
        f"MongoDB Image count  : "
        f"{len(stored_resources['images'])}"
    )

    print(
        "CrawlResult.resources"
        " == MongoDB.resources"
    )

    print(
        "CSS resources       : PASSED"
    )

    print(
        "Image resources     : PASSED"
    )

    print(
        "HTML persistence    : PASSED"
    )

    print(
        "Hash persistence    : PASSED"
    )

    print(
        "MongoDB persistence : PASSED"
    )

    print("-" * 70)

    print(
        "CRAWL SERVICE -> "
        "RAW HTML REPOSITORY "
        "TEST PASSED"
    )

    print("=" * 70)

    # ==================================================
    #
    # Cleanup
    #
    # ==================================================

    mongo_id = stored_document.get(
        "_id"
    )

    if mongo_id is not None:

        deleted = (
            repository.delete_by_id(
                str(
                    mongo_id
                )
            )
        )

        assert deleted is True