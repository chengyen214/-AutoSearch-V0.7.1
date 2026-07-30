"""
duplicate.py

P5-2 歷史資料去重

功能:
1. 讀取歷史 document_id
2. 判斷是否重複
3. 保存新的 document_id
"""


import json
import os



DATABASE = "storage/documents.json"



def load_documents():

    """
    讀取歷史文件ID
    """

    if not os.path.exists(DATABASE):

        return set()


    with open(
        DATABASE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)


    return set(data)





def is_duplicate(document_id):

    """
    判斷是否已存在
    """

    documents = load_documents()


    return document_id in documents





def save_document(document_id):

    """
    保存新的文件ID
    """

    documents = load_documents()


    documents.add(
        document_id
    )


    with open(
        DATABASE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            list(documents),
            f,
            ensure_ascii=False,
            indent=4
        )