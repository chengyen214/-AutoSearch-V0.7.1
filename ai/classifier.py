"""
classifier.py

AutoSearch V3

文章分類模組

功能：

    1. 接收文章內容
    2. 根據關鍵字判斷文章類型


目前：

    Rule-Based 分類


未來：

    - LLM Classification
    - LangChain Chain
    - Machine Learning Model
"""


class Classifier:
    """
    文章分類器
    """


    def __init__(self):

        # 分類規則

        self.rules = {


            "Process": [

                "2nm",
                "3nm",
                "5nm",
                "製程",
                "EUV",
                "晶圓"
            ],



            "Memory": [

                "HBM",
                "DRAM",
                "NAND",
                "Flash",
                "記憶體"
            ],



            "Packaging": [

                "CoWoS",
                "Chiplet",
                "封裝",
                "先進封裝"
            ],



            "AI Chip": [

                "GPU",
                "NPU",
                "AI晶片",
                "AI GPU",
                "Accelerator"
            ],



            "EDA": [

                "EDA",
                "Cadence",
                "Synopsys",
                "Design"
            ]

        }



    def classify(
        self,
        text: str
    ) -> str:
        """
        分類文章


        Parameters
        ----------
        text : str
            文章內容


        Returns
        -------
        str
            分類結果
        """


        if not text:

            return "Unknown"



        text = text.lower()



        scores = {}



        for category, keywords in self.rules.items():

            score = 0


            for keyword in keywords:

                if keyword.lower() in text:

                    score += 1


            scores[category] = score



        # 沒有符合

        if max(scores.values()) == 0:

            return "Unknown"



        # 回傳最高分分類

        return max(
            scores,
            key=scores.get
        )