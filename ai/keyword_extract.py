"""
keyword_extract.py

AutoSearch V3

文章關鍵字抽取模組

功能：

    1. 接收文章內容
    2. 找出重要技術關鍵字


目前：

    Rule-Based


未來：

    - TF-IDF
    - KeyBERT
    - LLM Keyword Extraction
    - LangChain
"""


class KeywordExtractor:
    """
    關鍵字抽取器
    """


    def __init__(self):

        # IC 領域關鍵字庫

        self.keywords = [

            # Foundry / Process
            "TSMC",
            "台積電",
            "2nm",
            "3nm",
            "5nm",
            "EUV",
            "製程",


            # Packaging

            "CoWoS",
            "Chiplet",
            "先進封裝",


            # Memory

            "HBM",
            "HBM3E",
            "DRAM",
            "NAND",


            # AI Chip

            "NVIDIA",
            "GPU",
            "AI GPU",
            "NPU",
            "AI晶片",


            # EDA

            "EDA",
            "Cadence",
            "Synopsys"

        ]



    def extract(
        self,
        text: str
    ) -> list:
        """
        抽取文章關鍵字


        Parameters
        ----------
        text : str
            文章內容


        Returns
        -------
        list
            關鍵字列表
        """


        if not text:

            return []



        result = []



        for keyword in self.keywords:

            if keyword.lower() in text.lower():

                result.append(keyword)



        return result