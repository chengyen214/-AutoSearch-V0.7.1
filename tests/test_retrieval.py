from database.article_repository import ArticleRepository


repo = ArticleRepository()


print("=== Importance >=8 ===")

for a in repo.find_by_importance(8):

    print(
        a["title"],
        a["ai_importance"]
    )



print("\n=== Category ===")

for a in repo.find_by_category(
    "Semiconductor"
):

    print(
        a["title"],
        a["ai_category"]
    )



print("\n=== AI Keyword ===")

for a in repo.search_ai_keyword(
    "AI"
):

    print(
        a["title"]
    )


repo.close()