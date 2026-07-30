"""
excel.py

功能：
    將 Article 資料新增到 Excel。

P5:
    1. Excel欄位固定
    2. 歷史資料保留
    3. document_id去重

輸出：
    output/result.xlsx
"""


import os
import pandas as pd

from config.settings import OUTPUT_FILE



def export(articles):
    """
    Article列表輸出Excel

    新資料追加，
    不覆蓋舊資料。
    """


    if not articles:

        print("沒有資料可以輸出")

        return



    # ----------------------------
    # Article -> dict
    # ----------------------------

    data = []


    for article in articles:

        data.append(
            article.to_dict()
        )


    new_df = pd.DataFrame(data)



    # ----------------------------
    # 建立資料夾
    # ----------------------------

    folder = os.path.dirname(
        OUTPUT_FILE
    )


    if folder:

        os.makedirs(
            folder,
            exist_ok=True
        )



    # ----------------------------
    # Excel已存在
    # ----------------------------

    if os.path.exists(
        OUTPUT_FILE
    ):


        old_df = pd.read_excel(
            OUTPUT_FILE
        )


        # 新舊資料合併

        df = pd.concat(

            [
                old_df,
                new_df
            ],

            ignore_index=True

        )


        # ------------------------
        # P5 Duplicate
        # document_id去重
        # ------------------------

        if "document_id" in df.columns:


            df.drop_duplicates(

                subset=[
                    "document_id"
                ],

                keep="first",

                inplace=True

            )


    else:


        df = new_df



    # ----------------------------
    # 輸出
    # ----------------------------

    df.to_excel(

        OUTPUT_FILE,

        index=False

    )


    print(
        "Excel更新完成：",
        OUTPUT_FILE
    )