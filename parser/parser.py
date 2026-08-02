"""
parser.py

AutoSearch V2.2 P2.2

HTML Parser


功能:

1. HTML解析
2. 移除HTML結構垃圾
3. 移除廣告/推薦區塊
4. Content Density Score
5. Keyword Ranking
6. 找真正文章正文
7. 支援中文 / 英文新聞
8. 傳給 Extractor 清理
9. 建立 Article Object


P2.2 不負責:

- AI分析
- 摘要
- 分類
- 語意理解

以上留給 V3

"""


from bs4 import BeautifulSoup


from cleaner.cleaner import clean_text


from extractor.extractor import extract


from models.article import Article







# =====================================
# P2.2 HTML垃圾關鍵字
# =====================================


BAD_WORDS = [


    # 廣告

    "ad",
    "ads",
    "advert",
    "banner",
    "sponsor",



    # 推薦

    "related",
    "recommend",
    "recommended",
    "more-news",
    "latest-news",



    # 社群

    "share",
    "social",



    # 會員

    "subscribe",
    "newsletter",
    "login",
    "register"

]








# =====================================
# 移除HTML垃圾
# =====================================


def remove_html_noise(soup):


    # -------------------------
    # Tag垃圾
    # -------------------------


    remove_tags=[


        "script",

        "style",

        "nav",

        "header",

        "footer",

        "aside",

        "form",

        "iframe",

        "button"

    ]




    for tag in soup(remove_tags):


        tag.decompose()






    # -------------------------
    # class / id垃圾
    # -------------------------


    for node in soup.find_all(True):


        # 防止 attrs 為 None

        if not node.attrs:

            continue




        classes=node.get(

            "class",

            []

        )



        if isinstance(classes,list):


            classes=" ".join(classes)




        ids=node.get(

            "id",

            ""

        )




        attrs=(

            str(classes)

            +

            " "

            +

            str(ids)

        ).lower()





        remove=False



        for word in BAD_WORDS:


            if word in attrs:


                remove=True

                break





        if remove:


            node.decompose()





    return soup











# =====================================
# Content Score
# =====================================


def content_score(node, keyword=""):


    text=node.get_text(


        separator="\n",

        strip=True

    )




    if len(text)<100:


        return 0






    # -------------------------
    # 文字量
    # -------------------------


    text_score=len(text)






    # -------------------------
    # Link penalty
    # -------------------------


    links=len(

        node.find_all("a")

    )


    link_penalty=links*50






    # -------------------------
    # HTML複雜度
    # -------------------------


    tags=len(

        node.find_all()

    )


    tag_penalty=tags*2






    # -------------------------
    # Content Density
    # -------------------------


    html_size=len(str(node))


    density=len(text)/(html_size+1)


    density_bonus=density*500






    # -------------------------
    # Keyword Bonus
    # -------------------------


    keyword_bonus=0



    if keyword:


        count=text.lower().count(

            keyword.lower()

        )


        keyword_bonus=count*100








    score=(


        text_score


        -


        link_penalty


        -


        tag_penalty


        +


        density_bonus


        +


        keyword_bonus

    )



    return score












# =====================================
# 找正文
# =====================================


def find_main_content(soup, keyword=""):


    candidates=[]






    # article

    for node in soup.find_all("article"):


        candidates.append(node)







    # main


    for node in soup.find_all("main"):


        candidates.append(node)








    # 常見新聞class


    selectors=[


        ".article-body",

        ".article-content",

        ".post-content",

        ".entry-content",

        ".story-body",

        ".news-content",

        ".content",

        ".post"


    ]





    for selector in selectors:


        node=soup.select_one(selector)



        if node:


            candidates.append(node)









    best_node=None


    best_score=0






    # 候選排名


    for node in candidates:


        score=content_score(

            node,

            keyword

        )


        if score>best_score:


            best_score=score


            best_node=node










    # div fallback


    if best_node is None:



        for div in soup.find_all("div"):



            score=content_score(

                div,

                keyword

            )



            if score>best_score:


                best_score=score


                best_node=div










    if best_node:


        return best_node.get_text(


            separator="\n",

            strip=True

        )





    return ""












# =====================================
# Parser
# =====================================


def parse(html, keyword, url=""):


    soup=BeautifulSoup(


        html,


        "html.parser"

    )







    # -------------------------
    # P2.2 HTML Cleaning
    # -------------------------


    soup=remove_html_noise(

        soup

    )








    # -------------------------
    # 找正文
    # -------------------------


    content=find_main_content(


        soup,

        keyword

    )








    # -------------------------
    # fallback
    # -------------------------


    if len(content)<200:


        content=soup.get_text(


            separator="\n",


            strip=True

        )









    # -------------------------
    # P1 Cleaner
    # -------------------------


    content=clean_text(

        content

    )



    content=extract(

        content

    )









    # -------------------------
    # Article Object
    # -------------------------


    article=Article()





    if soup.title:


        article.title=soup.title.text.strip()


    else:


        article.title=""






    article.url=url


    article.published=""


    article.keyword=keyword


    article.content=content






    return article