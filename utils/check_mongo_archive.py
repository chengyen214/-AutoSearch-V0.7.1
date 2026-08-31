"""
utils/check_mongo_archive.py

AutoSearch V4

MongoDB Archive Structure Inspector

用途：
    檢查 MongoDB 目前實際儲存的 Archive Snapshot 結構。

重點：

    Snapshot
    ├── article_id
    ├── document_id
    ├── url
    ├── resolved_url
    ├── html
    ├── content_hash
    ├── created_at
    │
    └── resources
         ├── css[]
         │    ├── url
         │    ├── content
         │    ├── content_hash
         │    ├── mime_type
         │    └── file_size
         │
         └── images[]
              ├── url
              ├── data
              ├── content_hash
              ├── mime_type
              └── file_size

注意：

    本工具只讀取 MongoDB。
    不會新增、修改或刪除任何資料。

執行：

    python -m utils.check_mongo_archive
"""


from pprint import pprint


# ============================================================
# MongoDB
# ============================================================

try:

    from database.raw_html_repository import (
        RawHTMLRepository
    )

except ImportError as e:

    print(
        "無法載入 RawHTMLRepository："
        f"{e}"
    )

    raise


# ============================================================
# Helpers
# ============================================================


def print_line():

    print(
        "-" * 80
    )


def print_value(
    name,
    value,
    indent=0
):

    prefix = " " * indent

    print(
        f"{prefix}{name}: {value!r}"
    )


def print_resource_summary(
    resources
):

    print()
    print(
        "resources:"
    )

    if not resources:

        print(
            "  None"
        )

        return

    if not isinstance(
        resources,
        dict
    ):

        print(
            "  [Invalid resources type]"
        )

        print(
            f"  type={type(resources).__name__}"
        )

        return

    # --------------------------------------------------------
    # CSS
    # --------------------------------------------------------

    css_list = resources.get(
        "css",
        []
    )

    print()

    print(
        f"  css: "
        f"{len(css_list) if isinstance(css_list, list) else 'INVALID'}"
    )

    if isinstance(
        css_list,
        list
    ):

        for index, css in enumerate(
            css_list,
            start=1
        ):

            print()

            print(
                f"    css[{index}]"
            )

            if not isinstance(
                css,
                dict
            ):

                print(
                    f"      type="
                    f"{type(css).__name__}"
                )

                continue

            print_value(
                "url",
                css.get("url"),
                6
            )

            print_value(
                "content_hash",
                css.get("content_hash"),
                6
            )

            print_value(
                "mime_type",
                css.get("mime_type"),
                6
            )

            print_value(
                "file_size",
                css.get("file_size"),
                6
            )

            content = css.get(
                "content"
            )

            if content is None:

                print_value(
                    "content",
                    None,
                    6
                )

            else:

                content_length = len(
                    content
                )

                print(
                    "      content_length: "
                    f"{content_length}"
                )

                preview = str(
                    content
                )[:300]

                print(
                    "      content_preview:"
                )

                print(
                    f"        {preview}"
                )

    # --------------------------------------------------------
    # Images
    # --------------------------------------------------------

    images_list = resources.get(
        "images",
        []
    )

    print()

    print(
        f"  images: "
        f"{len(images_list) if isinstance(images_list, list) else 'INVALID'}"
    )

    if isinstance(
        images_list,
        list
    ):

        for index, image in enumerate(
            images_list,
            start=1
        ):

            print()

            print(
                f"    images[{index}]"
            )

            if not isinstance(
                image,
                dict
            ):

                print(
                    f"      type="
                    f"{type(image).__name__}"
                )

                continue

            print_value(
                "url",
                image.get("url"),
                6
            )

            print_value(
                "content_hash",
                image.get("content_hash"),
                6
            )

            print_value(
                "mime_type",
                image.get("mime_type"),
                6
            )

            print_value(
                "file_size",
                image.get("file_size"),
                6
            )

            data = image.get(
                "data"
            )

            if data is None:

                print_value(
                    "data",
                    None,
                    6
                )

            else:

                # ------------------------------------------------
                # Binary Data
                # ------------------------------------------------

                if isinstance(
                    data,
                    bytes
                ):

                    print(
                        "      data_type: bytes"
                    )

                    print(
                        "      data_size: "
                        f"{len(data)}"
                    )

                else:

                    print(
                        "      data_type: "
                        f"{type(data).__name__}"
                    )

                    try:

                        print(
                            "      data_size: "
                            f"{len(data)}"
                        )

                    except TypeError:

                        pass


# ============================================================
# Snapshot
# ============================================================


def print_snapshot(
    snapshot,
    index
):

    print()
    print_line()

    print(
        f"SNAPSHOT #{index}"
    )

    print_line()

    if not isinstance(
        snapshot,
        dict
    ):

        print(
            f"type={type(snapshot).__name__}"
        )

        pprint(
            snapshot
        )

        return

    # --------------------------------------------------------
    # Mongo ID
    # --------------------------------------------------------

    print_value(
        "_id",
        snapshot.get("_id")
    )

    # --------------------------------------------------------
    # Article
    # --------------------------------------------------------

    print()
    print(
        "Article:"
    )

    print_value(
        "article_id",
        snapshot.get("article_id"),
        2
    )

    print_value(
        "document_id",
        snapshot.get("document_id"),
        2
    )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    print()
    print(
        "URL:"
    )

    print_value(
        "url",
        snapshot.get("url"),
        2
    )

    print_value(
        "resolved_url",
        snapshot.get("resolved_url"),
        2
    )

    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    html = snapshot.get(
        "html"
    )

    print()
    print(
        "HTML:"
    )

    if html is None:

        print(
            "  html: None"
        )

    else:

        print(
            "  html_length: "
            f"{len(html)}"
        )

        print(
            "  html_preview:"
        )

        preview = str(
            html
        )[:500]

        print(
            f"    {preview}"
        )

    # --------------------------------------------------------
    # Hash
    # --------------------------------------------------------

    print()
    print(
        "Hash:"
    )

    print_value(
        "content_hash",
        snapshot.get(
            "content_hash"
        ),
        2
    )

    # --------------------------------------------------------
    # Created
    # --------------------------------------------------------

    print()
    print(
        "Created:"
    )

    print_value(
        "created_at",
        snapshot.get(
            "created_at"
        ),
        2
    )

    # --------------------------------------------------------
    # Resources
    # --------------------------------------------------------

    print_resource_summary(
        snapshot.get(
            "resources"
        )
    )


# ============================================================
# Main
# ============================================================


def main():

    print()
    print("=" * 80)
    print(
        "AutoSearch V4 - MongoDB Archive Structure"
    )
    print("=" * 80)

    print()
    print(
        "模式：READ ONLY"
    )

    print()

    # ========================================================
    # Repository
    # ========================================================

    try:

        repository = RawHTMLRepository()

    except Exception as e:

        print()
        print(
            "MongoDB Repository 初始化失敗："
        )

        print(
            f"{e}"
        )

        return

    # ========================================================
    # Collection
    # ========================================================

    collection = getattr(
        repository,
        "collection",
        None
    )

    if collection is None:

        print()
        print(
            "找不到 repository.collection"
        )

        print(
            "請確認 RawHTMLRepository "
            "是否使用 self.collection。"
        )

        return

    print(
        "MongoDB Collection:"
    )

    try:

        print(
            f"  {collection.full_name}"
        )

    except Exception:

        print(
            f"  {collection}"
        )

    # ========================================================
    # Count
    # ========================================================

    print()

    try:

        total = collection.count_documents(
            {}
        )

        print(
            f"Snapshot Count: {total}"
        )

    except Exception as e:

        print(
            "無法取得 Snapshot Count："
        )

        print(
            f"{e}"
        )

        return

    # ========================================================
    # Latest Snapshots
    # ========================================================

    print()

    print_line()

    print(
        "LATEST SNAPSHOTS"
    )

    print_line()

    try:

        snapshots = list(
            collection.find(
                {}
            )
            .sort(
                "created_at",
                -1
            )
            .limit(
                10
            )
        )

    except Exception as e:

        print(
            "MongoDB 查詢失敗："
        )

        print(
            f"{e}"
        )

        return

    if not snapshots:

        print(
            "目前沒有 Snapshot。"
        )

        return

    # ========================================================
    # Print
    # ========================================================

    for index, snapshot in enumerate(
        snapshots,
        start=1
    ):

        print_snapshot(
            snapshot,
            index
        )

    # ========================================================
    # Structure Summary
    # ========================================================

    print()
    print("=" * 80)

    print(
        "EXPECTED ARCHIVE STRUCTURE"
    )

    print("=" * 80)

    print(
        """
Snapshot
│
├── _id
├── article_id
├── document_id
│
├── url
├── resolved_url
│
├── html
├── content_hash
├── created_at
│
└── resources
    │
    ├── css[]
    │   ├── url
    │   ├── content
    │   ├── content_hash
    │   ├── mime_type
    │   └── file_size
    │
    └── images[]
        ├── url
        ├── data
        ├── content_hash
        ├── mime_type
        └── file_size
"""
    )

    print(
        "=" * 80
    )

    print(
        "MongoDB Archive Structure Check Completed."
    )


# ============================================================
# Entry Point
# ============================================================


if __name__ == "__main__":

    main()