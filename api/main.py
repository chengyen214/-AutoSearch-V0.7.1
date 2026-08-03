from fastapi import FastAPI


from services.article_service import ArticleService


# uvicorn api.main:app

app = FastAPI(

    title="AutoSearch V2.5 API",

    version="1.0"

)



service = ArticleService()



@app.get("/")
def root():

    return {

        "project":"AutoSearch V2.5",

        "status":"running"

    }



# ==========================
# 全部文章
# ==========================

@app.get("/articles")
def get_articles():

    return service.get_all_articles()



# ==========================
# 單篇文章
# ==========================

@app.get("/articles/{article_id}")
def get_article(article_id:int):

    return service.get_article_by_id(
        article_id
    )



# ==========================
# Keyword Search
# ==========================

@app.get("/search")
def search_article(keyword:str):

    return service.search_by_keyword(
        keyword
    )



# ==========================
# Source Search
# ==========================

@app.get("/source/{source}")
def search_source(source:str):

    return service.search_by_source(
        source
    )