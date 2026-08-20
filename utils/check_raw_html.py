"""
utils/check_raw_html.py

AutoSearch V4

Raw HTML MongoDB Index Checker

用途：

    檢查：

        autosearch.raw_html

    的 MongoDB Index。

確認：

    - article_id index
    - document_id index
    - document_id 是否仍為 unique
    - url index
    - content_hash index

注意：

    本工具只讀取 MongoDB Index。

    不建立 Index。
    不刪除 Index。
    不修改資料。
"""


from config.mongo_config import (
    MONGO_RAW_HTML_COLLECTION,
)


from database.mongo_connection import (
    get_mongo_collection,
)


from utils.logger import (
    logger,
)


def main():
    """
    檢查 Raw HTML MongoDB Index。
    """

    print("=" * 60)
    print("AutoSearch V4")
    print("Raw HTML MongoDB Index Check")
    print("=" * 60)

    print()
    print(
        "Collection:",
        MONGO_RAW_HTML_COLLECTION,
    )

    try:

        collection = get_mongo_collection(
            MONGO_RAW_HTML_COLLECTION
        )

        indexes = collection.list_indexes()

        print()
        print("Indexes:")
        print("-" * 60)

        found_indexes = []

        for index in indexes:

            index_name = index.get(
                "name"
            )

            key = index.get(
                "key"
            )

            unique = index.get(
                "unique",
                False,
            )

            found_indexes.append(
                index
            )

            print(
                f"name        : {index_name}"
            )

            print(
                f"key         : {dict(key)}"
            )

            print(
                f"unique      : {unique}"
            )

            print("-" * 60)

        # ==================================================
        #
        # Expected Index Check
        #
        # ==================================================

        print()
        print("Expected Index Check")
        print("=" * 60)

        index_map = {}

        for index in found_indexes:

            key = index.get(
                "key"
            )

            if key:

                key_dict = dict(
                    key
                )

                if len(key_dict) == 1:

                    field = next(
                        iter(
                            key_dict
                        )
                    )

                    index_map[
                        field
                    ] = index

        # ==================================================
        # article_id
        # ==================================================

        article_index = index_map.get(
            "article_id"
        )

        if article_index:

            print(
                "[OK] article_id index exists"
            )

        else:

            print(
                "[WARN] article_id index missing"
            )

        # ==================================================
        # document_id
        # ==================================================

        document_index = index_map.get(
            "document_id"
        )

        if document_index:

            print(
                "[OK] document_id index exists"
            )

            if document_index.get(
                "unique",
                False,
            ):

                print(
                    "[WARN] document_id index "
                    "is UNIQUE"
                )

                print(
                    "       This should be reviewed."
                )

            else:

                print(
                    "[OK] document_id index "
                    "is NOT UNIQUE"
                )

        else:

            print(
                "[WARN] document_id index missing"
            )

        # ==================================================
        # url
        # ==================================================

        url_index = index_map.get(
            "url"
        )

        if url_index:

            print(
                "[OK] url index exists"
            )

        else:

            print(
                "[WARN] url index missing"
            )

        # ==================================================
        # content_hash
        # ==================================================

        content_hash_index = index_map.get(
            "content_hash"
        )

        if content_hash_index:

            print(
                "[OK] content_hash index exists"
            )

        else:

            print(
                "[WARN] content_hash index missing"
            )

        # ==================================================
        #
        # Summary
        #
        # ==================================================

        print()
        print("=" * 60)
        print("Raw HTML Index Check Completed")
        print("=" * 60)

    except Exception as e:

        logger.exception(
            "Raw HTML MongoDB index check failed: "
            f"{e}"
        )

        print()
        print(
            "[ERROR] Raw HTML MongoDB index check failed:"
        )

        print(
            str(e)
        )


if __name__ == "__main__":

    main()