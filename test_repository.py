from database.article_repository import ArticleRepository
from models.article import Article

repo = ArticleRepository()

article = Article(
    keyword="AI",
    title="Repository Test",
    url="https://example.com",
    published=None,
    source="Example",
    content="This is a repository test.",
    crawl_time=None,
    status="Success",
    document_id="TEST001"
)
rows = repo.find_all()

repo.save(article)

print("Save Success!")

db_article = repo.find_by_document_id("TEST001")

print(db_article)

print(repo.count())

repo.close()