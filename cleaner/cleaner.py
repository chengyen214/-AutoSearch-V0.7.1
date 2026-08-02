"""
cleaner.py

文章內容清理模組

功能：
1. 去除多餘空白
2. 清除換行
3. 基本文字整理
"""


import re



def clean_text(text):

    """
    清理文章文字

    input:
        原始文字

    output:
        清理後文字
    """


    if text is None:

        return ""



    # 多個空白、換行變成一個空白
    text = re.sub(

        r"[ \t]+",
        " ",
        text

    )


    # 移除前後空白
    text = text.strip()
    # print("Cleaner 執行")

    return text