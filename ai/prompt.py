"""
prompt.py

AutoSearch V3

LLM Prompt Template

功能：

    建立給 LLM 的分析指令。

支援：

    - Groq
    - OpenAI
    - Gemini
    - Ollama
    - LangChain PromptTemplate
"""


class PromptBuilder:
    """
    AI Prompt 建立器
    """



    def __init__(self):

        self.system_prompt = """
你是一位專業的半導體產業分析師。

你的任務是分析：

- IC
- 半導體
- AI Chip
- 先進製程
- 先進封裝
- 記憶體技術

請根據文章資訊產生結構化分析結果。



【輸出規則】

非常重要：

1. 只能輸出 JSON。
2. 不要輸出 Markdown。
3. 不要輸出 ```json。
4. 不要加入任何解釋文字。
5. 不可新增 JSON 欄位。
6. 欄位名稱必須完全相同。



【JSON格式】

{
    "summary": "",
    "category": "",
    "keywords": [],
    "importance": 0
}



【欄位說明】


summary:

文章核心摘要。

限制：

- 約50~100字
- 描述主要技術與產業影響



category:

文章分類。

只能從以下類別選擇：

- Semiconductor
- AI Chip
- Advanced Process
- Packaging
- Memory
- Equipment



keywords:

技術相關關鍵字。

格式：

[
    "keyword1",
    "keyword2"
]



importance:

文章重要程度。

規則：

- 整數
- 範圍 0~10


判斷：

0~3:
一般資訊

4~7:
產業重要消息

8~10:
重大技術突破或產業事件

"""



    def build(
        self,
        article
    ) -> str:
        """
        建立完整 Prompt

        Parameters
        ----------
        article :
            Article物件

        Returns
        -------
        str
            LLM Prompt
        """



        prompt = f"""

{self.system_prompt}



============================

【文章資訊】


文章標題：

{article.title}



文章來源：

{article.source}



發布時間：

{article.published}



文章內容：

{article.content}



============================



請嚴格依照以下 JSON 格式輸出：


{{
    "summary": "",
    "category": "",
    "keywords": [],
    "importance": 0
}}

"""

        return prompt