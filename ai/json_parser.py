"""
json_parser.py

AutoSearch V3

LLM JSON Output Parser

P3.2.4

功能：

    將 LLM 回傳文字
    轉換成 Python Dict


處理：

    - Markdown JSON
    - 純 JSON
    - JSON格式驗證
    - AI Response Validation
    - AI Response Auto Repair

"""


import json

import re


from utils.logger import logger





class JSONParser:
    """
    AI JSON 結果解析器
    """



    REQUIRED_FIELDS = [

        "summary",

        "category",

        "keywords",

        "importance"

    ]



    ALLOWED_CATEGORY = [

        "Semiconductor",

        "AI Chip",

        "Advanced Process",

        "Packaging",

        "Memory",

        "Equipment"

    ]






    def parse(
        self,
        response: str
    ) -> dict:
        """
        解析 LLM Response
        """



        if not response:


            raise ValueError(
                "LLM response is empty."
            )





        # =====================
        # Extract JSON
        # =====================

        json_text = self._extract_json(

            response

        )





        # =====================
        # JSON Decode
        # =====================

        try:


            data = json.loads(

                json_text

            )


        except json.JSONDecodeError as e:


            logger.error(

                f"JSON decode failed: {e}"

            )


            raise ValueError(

                "Invalid JSON response."

            )






        # =====================
        # Auto Repair
        # =====================

        data = self._repair(

            data

        )






        # =====================
        # Validation
        # =====================

        self._validate(

            data

        )





        logger.info(

            "AI Response Validation PASS"

        )



        return data







    def _extract_json(
        self,
        text: str
    ) -> str:
        """
        擷取 JSON 區段
        """



        # 移除 Markdown

        text = text.replace(

            "```json",

            ""

        )


        text = text.replace(

            "```",

            ""

        )



        text = text.strip()





        match = re.search(

            r"\{.*\}",

            text,

            re.DOTALL

        )



        if not match:


            raise ValueError(

                "No JSON object found."

            )



        return match.group(0)









    def _repair(
        self,
        data: dict
    ) -> dict:
        """
        修復 AI 不完整輸出
        """



        logger.info(

            "AI Response Repair Start"

        )




        # =====================
        # 確認 dict
        # =====================


        if not isinstance(

            data,

            dict

        ):


            raise TypeError(

                "AI response must be JSON object."

            )






        # =====================
        # summary
        # =====================


        if "summary" not in data:


            data["summary"] = ""



        elif not isinstance(

            data["summary"],

            str

        ):


            data["summary"] = str(

                data["summary"]

            )








        # =====================
        # category
        # =====================


        if "category" not in data:


            data["category"] = "Semiconductor"







        # =====================
        # keywords
        # =====================


        if "keywords" not in data:


            data["keywords"] = []



        elif isinstance(

            data["keywords"],

            str

        ):


            data["keywords"] = [

                item.strip()

                for item in data["keywords"].split(",")

                if item.strip()

            ]







        # =====================
        # importance
        # =====================


        if "importance" not in data:


            data["importance"] = 0



        elif isinstance(

            data["importance"],

            str

        ):


            try:


                data["importance"] = int(

                    data["importance"]

                )


            except:


                data["importance"] = 0





        logger.info(

            "AI Response Repair Complete"

        )



        return data










    def _validate(
        self,
        data: dict
    ):
        """
        AI Response Validation
        """



        # =====================
        # 必須欄位
        # =====================


        for field in self.REQUIRED_FIELDS:


            if field not in data:


                raise ValueError(

                    f"Missing field: {field}"

                )







        # =====================
        # summary
        # =====================


        if not isinstance(

            data["summary"],

            str

        ):


            raise TypeError(

                "summary must be string."

            )







        # =====================
        # category
        # =====================


        if data["category"] not in self.ALLOWED_CATEGORY:


            logger.warning(

                f"Unknown category: {data['category']}"

            )







        # =====================
        # keywords
        # =====================


        if not isinstance(

            data["keywords"],

            list

        ):


            raise TypeError(

                "keywords must be list."

            )








        # =====================
        # importance
        # =====================


        if not isinstance(

            data["importance"],

            int

        ):


            raise TypeError(

                "importance must be int."

            )



        if not 0 <= data["importance"] <= 10:


            raise ValueError(

                "importance must be between 0 and 10."

            )