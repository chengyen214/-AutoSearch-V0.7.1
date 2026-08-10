"""
tests/test_prompt.py

AutoSearch V4

PromptBuilder Test
"""

from ai.prompt import PromptBuilder
from models.article import Article


# ==================================================
# Mock Article
# ==================================================

article = Article(
    keyword="半導體",
    title="台積電2nm與AI GPU發展",
    url="https://example.com/test",
    published="2026-08-09",
    source="TestSource",
    content="""
台積電宣布2nm製程進入量產。
NVIDIA推出新一代AI GPU。
CoWoS先進封裝需求增加。
"""
)


# ==================================================
# Build Prompt
# ==================================================

builder = PromptBuilder()

prompt = builder.build(article)


# ==================================================
# Assertions
# ==================================================

assert prompt is not None
assert isinstance(prompt, str)

assert article.title in prompt
assert article.source in prompt
assert article.content.strip() in prompt


print(prompt)
