"""
tests/V5/test_job_executor_google_news.py

AutoSearch V5

Test:

    JobExecutorBridge
        ↓
    Google News Search
        ↓
    SearchResult[]
        ↓
    Crawl
        ↓
    Parser
        ↓
    ArticleService
"""


from services.job_executor_bridge import (
    JobExecutorBridge,
)


from models.target import (
    Target,
)


class MockJob:

    id = 1



def create_test_target():
    
    target = Target()


    target.target_type = "search"


    target.keyword = "TSMC"


    target.search_provider = (
        "google_news"
    )


    return target



def test_job_executor_google_news():


    job = (
        MockJob()
    )


    target = (
        create_test_target()
    )


    bridge = (
        JobExecutorBridge()
    )


    result = (
        bridge.execute(
            job,
            target,
        )
    )


    assert result is not None


    assert (
        "search_results"
        in result
    )


    search_results = (
        result["search_results"]
    )


    assert isinstance(
        search_results,
        list,
    )


    print(
        "=============================="
    )

    print(
        "Search Result Count:",
        len(search_results),
    )


    for item in search_results:

        print(
            item.url
        )


    print(
        "=============================="
    )



if __name__ == "__main__":

    test_job_executor_google_news()

    print(
        "JobExecutorBridge Google News test passed"
    )