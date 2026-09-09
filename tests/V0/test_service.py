from services.article_service import ArticleService



service = ArticleService()



articles = service.get_all_articles()


print(
    "文章數量:",
    len(articles)
)


for article in articles[:3]:

    print(
        article["title"]
    )


service.close()