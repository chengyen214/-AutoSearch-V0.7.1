"""
tests/V5-6/test_job_executor_bridge.py

AutoSearch V5

V5.6.1

Job Executor Bridge Test

測試範圍：

    Job
      ↓
    Target
      ↓
    JobExecutorBridge
      ↓
    TargetSourceService
      ↓
    Source Definition

本測試不負責：

    - Google Search API
    - Google News API
    - SearchAdapter
    - Crawler
    - Parser
    - ArticleService
    - Archive
    - AI
    - Database
"""


import pytest

from models.job import Job
from models.target import Target

from services.job_executor_bridge import (
    JobExecutorBridge,
)


# ==================================================
#
# Helpers
#
# ==================================================


def create_job(
    job_id=1,
):
    """
    建立最小可用 Job。
    """

    job = Job()

    job.id = job_id

    return job


def create_search_target(
    provider,
    keyword="semiconductor",
):
    """
    建立 Search Target。
    """

    target = Target()

    target.target_type = "search"
    target.keyword = keyword
    target.search_provider = provider

    return target


def create_url_target(
    url="https://example.com",
):
    """
    建立 URL Target。
    """

    target = Target()

    target.target_type = "url"
    target.url = url

    return target


# ==================================================
#
# P5.6.1
#
# Search Target - Google Search
#
# ==================================================


def test_google_search_target_resolution():
    """
    P5.6.1

    Search Target
        ↓
    JobExecutorBridge
        ↓
    TargetSourceService
        ↓
    Google Search Source Definition
    """

    bridge = JobExecutorBridge()

    job = create_job()

    target = create_search_target(
        provider="google_search",
    )

    context = bridge.execute(
        job,
        target,
    )

    assert context is not None

    assert context["job"] is job

    assert context["target"] is target

    source = context["source"]

    assert source["source_type"] == "search"

    assert source["keyword"] == "semiconductor"

    assert source["provider"] == "google_search"


# ==================================================
#
# P5.6.1
#
# Search Target - Google News
#
# ==================================================


def test_google_news_target_resolution():
    """
    P5.6.1

    Search Target
        ↓
    JobExecutorBridge
        ↓
    TargetSourceService
        ↓
    Google News Source Definition
    """

    bridge = JobExecutorBridge()

    job = create_job(
        job_id=2,
    )

    target = create_search_target(
        provider="google_news",
    )

    context = bridge.execute(
        job,
        target,
    )

    assert context is not None

    assert context["job"] is job

    assert context["target"] is target

    source = context["source"]

    assert source["source_type"] == "search"

    assert source["keyword"] == "semiconductor"

    assert source["provider"] == "google_news"


# ==================================================
#
# P5.6.1
#
# Direct URL Target
#
# ==================================================


def test_direct_url_target_resolution():
    """
    P5.6.1

    URL Target
        ↓
    JobExecutorBridge
        ↓
    TargetSourceService
        ↓
    Direct URL Source Definition
    """

    bridge = JobExecutorBridge()

    job = create_job(
        job_id=3,
    )

    target = create_url_target()

    context = bridge.execute(
        job,
        target,
    )

    assert context is not None

    assert context["job"] is job

    assert context["target"] is target

    source = context["source"]

    assert source["source_type"] == "direct_url"

    assert source["url"] == "https://example.com"


# ==================================================
#
# P5.6.1
#
# Job Validation
#
# ==================================================


def test_none_job_raises_error():
    """
    Job 不存在時應拒絕執行。
    """

    bridge = JobExecutorBridge()

    target = create_search_target(
        provider="google_search",
    )

    with pytest.raises(
        ValueError,
        match="job cannot be None",
    ):

        bridge.execute(
            None,
            target,
        )


# ==================================================
#
# P5.6.1
#
# Target Validation
#
# ==================================================


def test_none_target_raises_error():
    """
    Target 不存在時應拒絕執行。
    """

    bridge = JobExecutorBridge()

    job = create_job()

    with pytest.raises(
        ValueError,
        match="target cannot be None",
    ):

        bridge.execute(
            job,
            None,
        )


# ==================================================
#
# P5.6.1
#
# Invalid Target Type
#
# ==================================================


def test_invalid_target_type_raises_error():
    """
    非 Target instance
    應由 TargetSourceService 拒絕。
    """

    bridge = JobExecutorBridge()

    job = create_job()

    with pytest.raises(
        TypeError,
        match="target must be an instance of Target",
    ):

        bridge.execute(
            job,
            object(),
        )


# ==================================================
#
# P5.6.1
#
# Unsupported Provider
#
# ==================================================


def test_unsupported_provider_raises_error():
    """
    不支援的 Search Provider
    應由 TargetSourceService 拒絕。
    """

    bridge = JobExecutorBridge()

    job = create_job()

    target = create_search_target(
        provider="unsupported_provider",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported search provider",
    ):

        bridge.execute(
            job,
            target,
        )


# ==================================================
#
# P5.6.1
#
# Resolve Source Directly
#
# ==================================================


def test_resolve_source():
    """
    測試 Bridge 的 resolve_source()
    """

    bridge = JobExecutorBridge()

    target = create_search_target(
        provider="google_search",
        keyword="AI semiconductor",
    )

    source = bridge.resolve_source(
        target
    )

    assert source["source_type"] == "search"

    assert source["keyword"] == "AI semiconductor"

    assert source["provider"] == "google_search"


# ==================================================
#
# P5.6.1
#
# Target Type Helpers
#
# ==================================================


def test_is_search_target():
    """
    測試 Search Target 判斷。
    """

    bridge = JobExecutorBridge()

    target = create_search_target(
        provider="google_search",
    )

    assert bridge.is_search(
        target
    ) is True

    assert bridge.is_direct_url(
        target
    ) is False


def test_is_direct_url_target():
    """
    測試 Direct URL Target 判斷。
    """

    bridge = JobExecutorBridge()

    target = create_url_target()

    assert bridge.is_direct_url(
        target
    ) is True

    assert bridge.is_search(
        target
    ) is False


# ==================================================
#
# P5.6.1
#
# Provider Helper
#
# ==================================================


def test_get_provider():
    """
    測試取得 Search Provider。
    """

    bridge = JobExecutorBridge()

    target = create_search_target(
        provider="google_search",
    )

    provider = bridge.get_provider(
        target
    )

    assert provider == "google_search"


def test_get_provider_for_url_target():
    """
    URL Target 不應有 Provider。
    """

    bridge = JobExecutorBridge()

    target = create_url_target()

    provider = bridge.get_provider(
        target
    )

    assert provider is None


# ==================================================
#
# P5.6.1
#
# Keyword Preservation
#
# ==================================================


def test_keyword_is_preserved():
    """
    確認 Source Resolution
    不會在 Bridge 層修改 User Keyword。
    """

    bridge = JobExecutorBridge()

    job = create_job()

    target = create_search_target(
        provider="google_search",
        keyword="  AI semiconductor  ",
    )

    context = bridge.execute(
        job,
        target,
    )

    source = context["source"]

    assert source["keyword"] == (
        "  AI semiconductor  "
    )


# ==================================================
#
# Test Summary
#
# ==================================================

"""
P5.6.1 Expected:

    test_google_search_target_resolution
        PASS

    test_google_news_target_resolution
        PASS

    test_direct_url_target_resolution
        PASS

    test_none_job_raises_error
        PASS

    test_none_target_raises_error
        PASS

    test_invalid_target_type_raises_error
        PASS

    test_unsupported_provider_raises_error
        PASS

    test_resolve_source
        PASS

    test_is_search_target
        PASS

    test_is_direct_url_target
        PASS

    test_get_provider
        PASS

    test_get_provider_for_url_target
        PASS

    test_keyword_is_preserved
        PASS


P5.6.1 Test Boundary:

    Job
      ↓
    Target
      ↓
    JobExecutorBridge
      ↓
    TargetSourceService
      ↓
    Source Definition

    STOP

不應進入：

    Google Search API
    Google News API
    SearchResult
    SearchAdapter
    Crawler
    Parser
    ArticleService
    Archive
    AI
"""
