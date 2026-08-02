"""
quality_filter.py

AutoSearch V2.2 P2

Quality Filter

功能:

1. 移除推薦文章
2. 移除社群區塊
3. 移除贊助內容
4. 移除網站導流
5. 保留正文

"""

import re



# =================================
# 低品質段落
# =================================

REMOVE_BLOCKS = [

    # 推薦

    "延伸閱讀",
    "推薦閱讀",
    "熱門文章",
    "相關文章",
    "您可能感興趣",
    "感興趣的話題",


    # 社群

    "Facebook",
    "Instagram",
    "YouTube",
    "粉絲團",


    # 贊助

    "請我們喝杯咖啡",
    "支持我們",
    "訂閱電子報",
    "Newsletter",


    # 導流

    "加入Google來源",
    "Google新聞",
    "追蹤我們",


    # 會員

    "登入會員",
    "註冊會員",
    "VIP"

]





# =================================
# Footer停止
# =================================


STOP_BLOCKS = [

    "Copyright",

    "Privacy Policy",

    "Terms of Service",

    "版權所有",

    "隱私權政策",

    "使用條款"

]





# =================================
# 段落品質判斷
# =================================


def quality_line(line):


    line=line.strip()


    if not line:

        return False



    # 太短

    if len(line)<10:

        return False



    for word in REMOVE_BLOCKS:


        if word in line:

            return False



    return True






# =================================
# Main Filter
# =================================


def filter_quality(content):


    if not content:

        return ""



    lines=[]



    for line in content.split("\n"):


        line=line.strip()



        if not line:

            continue



        # -----------------------
        # footer停止
        # -----------------------

        for stop in STOP_BLOCKS:


            if stop in line:

                return "\n".join(lines)




        # -----------------------
        # 過濾
        # -----------------------

        if quality_line(line):

            lines.append(line)




    result="\n".join(lines)



    # 多餘空白

    result=re.sub(

        r"\n{2,}",

        "\n",

        result

    )



    return result.strip()