from models.article import Article
from models.ai_analysis import AIAnalysis



def main():


    # 建立 AI Analysis

    analysis = AIAnalysis(

        summary="台積電2nm製程進入量產",

        category="Semiconductor",

        keywords=[
            "2nm",
            "CoWoS",
            "HBM3E"
        ],

        importance=9
    )



    # 建立 Article

    article = Article(

        keyword="IC semiconductor",

        title="台積電2nm量產",

        url="https://example.com",

        source="TechNews",

        content="測試文章內容"

    )



    # 綁定 AI

    article.ai_analysis = analysis



    # 輸出

    print("===== Article =====")

    print(article)



    print()


    print("===== Dictionary =====")

    print(
        article.to_dict()
    )



if __name__ == "__main__":

    main()