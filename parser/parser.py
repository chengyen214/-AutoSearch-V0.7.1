"""
parser.py

HTML解析
"""


from bs4 import BeautifulSoup

from cleaner.cleaner import clean_text

from models.article import Article



def parse(html, keyword):


    soup = BeautifulSoup(

        html,

        "html.parser"

    )



    # 取得網頁文字
    content = soup.get_text(

        separator=" "

    )



    # Part4 新增
    content = clean_text(

        content
        

    )



    article = Article()



    article.title = soup.title.text if soup.title else ""
    article.url = ""
    article.published = ""
    article.keyword = keyword
    article.content = content



    return article