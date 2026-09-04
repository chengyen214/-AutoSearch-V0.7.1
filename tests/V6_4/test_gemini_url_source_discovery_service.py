"""
tests/V6_4/test_gemini_url_source_discovery_service.py

AutoSearch V6.4

Gemini URL Source Discovery Service Test
"""

from services.gemini_url_source_discovery_service import (
    GeminiURLSourceDiscoveryService,
)


def test_gemini_url_source_discovery():
    service = (
        GeminiURLSourceDiscoveryService()
    )

    results = service.execute()

    assert isinstance(results, list)

    print(
        "\n"
        + "=" * 60
    )
    print(
        "GEMINI URL SOURCE DISCOVERY"
    )
    print(
        "=" * 60
    )

    for result in results:
        print(
            f"\n[{result['host']}]"
        )

        if "error" in result:
            print(
                f"ERROR: {result['error']}"
            )
            continue

        print(
            f"name: {result['name']}"
        )

        print(
            f"url: {result['url']}"
        )

        print(
            f"crawler_url: "
            f"{result['crawler_url']}"
        )

        print(
            f"keyword: {result['keyword']}"
        )

        print(
            f"description: "
            f"{result['description']}"
        )

    print(
        "\n"
        + "=" * 60
    )
    print(
        f"Gemini source count: "
        f"{len(results)}"
    )
    print(
        "=" * 60
    )


if __name__ == "__main__":
    test_gemini_url_source_discovery()