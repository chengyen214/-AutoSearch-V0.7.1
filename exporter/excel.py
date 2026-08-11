"""
excel.py

AutoSearch V4

功能：

將 Article 資料新增到 Excel。

支援：

1. Article Object
2. dict Article
3. Excel 欄位固定
4. 歷史資料保留
5. document_id 去重
6. 新舊資料合併
7. V4 Pipeline 相容

輸出：

    output/result.xlsx
"""

import os

import pandas as pd

from config.settings import OUTPUT_FILE


# ==================================================
# Article -> Dict
# ==================================================

def _article_to_dict(
    article
):
    """
    將 Article 統一轉換成 dict。

    支援：

        Article Object
        dict

    Returns
    -------

    dict
    """

    # ----------------------------------------------
    # None
    # ----------------------------------------------

    if article is None:

        return None

    # ----------------------------------------------
    # dict
    # ----------------------------------------------

    if isinstance(
        article,
        dict
    ):

        return dict(
            article
        )

    # ----------------------------------------------
    # Article Object
    # ----------------------------------------------

    if hasattr(
        article,
        "to_dict"
    ):

        return article.to_dict()

    # ----------------------------------------------
    # Unsupported
    # ----------------------------------------------

    raise TypeError(
        "Unsupported Article type: "
        f"{type(article).__name__}"
    )


# ==================================================
# Export
# ==================================================

def export(
    articles
):
    """
    Article 列表輸出 Excel。

    新資料追加，
    不覆蓋舊資料。

    支援：

        list[Article]

        list[dict]

    Parameters
    ----------

    articles:
        Article object 或 dict 的列表。

    Returns
    -------

    bool

        True:
            Excel 更新成功

        False:
            沒有資料或輸出失敗
    """

    # ==================================================
    # Empty
    # ==================================================

    if not articles:

        print(
            "沒有資料可以輸出"
        )

        return False

    # ==================================================
    # Article -> dict
    # ==================================================

    data = []

    for article in articles:

        try:

            row = _article_to_dict(
                article
            )

            if row is not None:

                data.append(
                    row
                )

        except Exception as e:

            print(
                "Article 轉換失敗：",
                e
            )

    # ==================================================
    # No valid data
    # ==================================================

    if not data:

        print(
            "沒有有效資料可以輸出"
        )

        return False

    # ==================================================
    # New DataFrame
    # ==================================================

    new_df = pd.DataFrame(
        data
    )

    # ==================================================
    # Create Folder
    # ==================================================

    folder = os.path.dirname(
        OUTPUT_FILE
    )

    if folder:

        os.makedirs(
            folder,
            exist_ok=True
        )

    # ==================================================
    # Existing Excel
    # ==================================================

    if os.path.exists(
        OUTPUT_FILE
    ):

        try:

            old_df = pd.read_excel(
                OUTPUT_FILE
            )

        except Exception as e:

            print(
                "讀取既有 Excel 失敗：",
                e
            )

            old_df = pd.DataFrame()

        # ----------------------------------------------
        # New + Old
        # ----------------------------------------------

        df = pd.concat(

            [
                old_df,
                new_df
            ],

            ignore_index=True

        )

        # ----------------------------------------------
        # document_id Duplicate
        # ----------------------------------------------

        if (
            "document_id" in df.columns
        ):

            df.drop_duplicates(

                subset=[
                    "document_id"
                ],

                keep="first",

                inplace=True

            )

    else:

        df = new_df

    # ==================================================
    # Output
    # ==================================================

    df.to_excel(

        OUTPUT_FILE,

        index=False

    )

    print(
        "Excel更新完成：",
        OUTPUT_FILE
    )

    return True
