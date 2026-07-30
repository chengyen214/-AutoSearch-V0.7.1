"""
history.py

P5-3 Search History

功能:
1. 保存搜尋紀錄
2. 追蹤搜尋結果
3. 為 MySQL 做準備
"""


import json
import os
from datetime import datetime



DATABASE = "storage/history.json"





def load_history():

    """
    讀取歷史紀錄
    """

    if not os.path.exists(DATABASE):

        return []


    with open(
        DATABASE,
        "r",
        encoding="utf-8"
    ) as f:

        try:

            return json.load(f)

        except json.JSONDecodeError:

            return []





def save_history(
    keyword,
    total_results,
    new_documents,
    duplicate_documents,
    failed_documents
):

    """
    保存一次搜尋紀錄
    """

    history = load_history()



    record = {

        "keyword":
            keyword,

        "time":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "total_results":
            total_results,

        "new_documents":
            new_documents,

        "duplicate_documents":
            duplicate_documents,

        "failed_documents":
            failed_documents

    }



    history.append(
        record
    )



    with open(
        DATABASE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=4
        )