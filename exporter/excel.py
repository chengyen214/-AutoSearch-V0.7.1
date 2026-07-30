"""
excel.py

功能：
    將搜尋結果輸出成 Excel。

輸入：
    Article資料列表

輸出：
    output/result.xlsx

版本：
    V2.0
"""


import pandas as pd

from config.settings import OUTPUT_FILE
import os


def export(articles):
    """
    輸出Excel檔案

    Parameters
    ----------
    articles:
        Article物件列表

    Returns
    -------
    None
    """


    # ----------------------------
    # 檢查是否有資料
    # ----------------------------

    if not articles:

        print("沒有資料可以輸出")

        return



    # ----------------------------
    # 建立Excel資料列表
    # ----------------------------

    data = []


    # ----------------------------
    # Article物件轉成dictionary
    # ----------------------------

    for article in articles:

        data.append(
            article.to_dict()
        )



    # ----------------------------
    # 建立Pandas表格
    # ----------------------------

    df = pd.DataFrame(data)
# 自動建立輸出資料夾
    folder = os.path.dirname(OUTPUT_FILE)

    if folder:
        os.makedirs(
            folder,
            exist_ok=True
        )


    # ----------------------------
    # 輸出Excel
    # ----------------------------

    df.to_excel(
        
        OUTPUT_FILE,

        index=False

    )



    print(
        "Excel輸出完成：",
        OUTPUT_FILE
    )