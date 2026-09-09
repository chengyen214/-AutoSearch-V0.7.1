"""
test_ai_pipeline.py

AutoSearch V3

P1.6 AI Pipeline Integration Test

測試：

Article
    |
    v
AIAnalyzer
    |
    v
Summary
Category
Keywords
"""


from models.article import Article

from ai.analyzer import AIAnalyzer



def main():


    # 建立 V2.5 Article 物件

    article = Article(

        keyword="IC",

        title="台積電2nm與AI晶片發展",

        url="https://example.com",

        published="2026-08-03",

        source="Test",

        content="""
        台積電宣布2nm製程進入量產。
        NVIDIA推出新一代AI GPU。
        CoWoS先進封裝需求持續增加。
        HBM3E記憶體需求快速成長。
        """,

        crawl_time="2026-08-03"

    )



    # 建立 AI Analyzer

    analyzer = AIAnalyzer()



    # 執行分析

    result = analyzer.analyze(article)



    # 顯示結果

    print("\n===== AI Analysis Result =====")

    print(
        result.to_dict()
    )



if __name__ == "__main__":

    main()