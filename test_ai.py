from models.article import Article
from ai.analyzer import AIAnalyzer


article = Article(
    keyword="IC",
    title="測試文章",
    content="""
台積電宣布2nm製程進入量產。
NVIDIA持續推出新一代AI GPU。
CoWoS先進封裝需求快速成長。
"""
)


analyzer = AIAnalyzer()


result = analyzer.analyze(article)


print(result)