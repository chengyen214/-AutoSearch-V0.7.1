"""
extractor.py

AutoSearch V2.2 P1

Main Content Cleaner


功能:

1. 移除技術垃圾
2. 移除 URL
3. 移除 Email
4. 移除重複內容
5. 移除作者資訊
6. 清理空白
7. 保留正文完整性


注意:

P1 不負責廣告判斷

廣告 / 推薦內容
由 P2 Parser 處理

"""


import re






# =====================================
# 技術垃圾
# =====================================


REMOVE_PATTERNS=[


    r"https?://\S+",


    r"\S+@\S+\.\S+",


    r"javascript:\S+"

]








# =====================================
# STOP FOOTER
# =====================================


STOP_KEYWORDS=[


    "作者：",

    "作者:",

    "Author:",


    "Copyright",

    "All rights reserved",

    "©",


    "Privacy Policy",

    "隱私權政策",

    "Terms of Service",

    "使用條款"


]








# =====================================
# Line Filter
# =====================================


def clean_line(line):


    line=line.strip()



    if not line:

        return False



    if len(line)<5:

        return False



    return True









# =====================================
# Remove Duplicate
# =====================================


def remove_duplicate(lines):


    result=[]


    seen=set()



    for line in lines:


        if line in seen:

            continue



        seen.add(line)


        result.append(line)



    return result







# =====================================
# Remove Author
# =====================================


def remove_author(text):


    return re.sub(

        r"[\(（]作者.*?[\)）]",

        "",

        text

    )









# =====================================
# Remove Pattern
# =====================================


def remove_patterns(text):


    for pattern in REMOVE_PATTERNS:


        text=re.sub(

            pattern,

            "",

            text

        )



    return text







# =====================================
# Extract
# =====================================


def extract(content):


    if not content:


        return ""







    # remove pattern

    content=remove_patterns(

        content

    )






    # 空白

    content=re.sub(

        r"[ \t]+",

        " ",

        content

    )







    lines=[]





    for line in content.split("\n"):


        line=line.strip()



        if not line:


            continue





        # footer stop


        stop=False


        for key in STOP_KEYWORDS:


            if key in line:


                stop=True

                break




        if stop:

            break






        if clean_line(line):


            lines.append(line)








    lines=remove_duplicate(

        lines

    )







    result="\n".join(

        lines

    )







    result=remove_author(

        result

    )








    result=re.sub(

        r"\n{2,}",

        "\n",

        result

    )








    # quality check


    if len(result)<100:


        return ""






    return result.strip()