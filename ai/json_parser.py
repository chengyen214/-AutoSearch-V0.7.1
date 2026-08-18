"""
json_parser.py

AutoSearch V4

P2.4 Async AI Scaling

LLM JSON Output Parser

功能:

    將 LLM 回傳文字
    轉換成 Python Dict

處理:

    - Markdown JSON
    - 純 JSON
    - JSON Object Extraction
    - JSON 格式驗證
    - AI Response Validation
    - AI Response Auto Repair
    - AI Response Type Normalization

P2.4 AI Schema:

    summary
    category
    keywords
    entities
    relations
    importance

Pipeline:

    LLM Response
        |
        v
    JSONParser.parse()
        |
        +--> Extract JSON
        |
        +--> JSON Decode
        |
        +--> Repair / Normalize
        |
        +--> Validate
        |
        v
    Validated AI Dict
        |
        v
    AIAnalysisService
        |
        v
    AIWorker
        |
        v
    Knowledge Archive
"""


import json
import re

from utils.logger import logger


class JSONParser:

    """
    AI JSON 結果解析器。

    負責:

        1. 擷取 LLM JSON
        2. JSON Decode
        3. 基礎格式修復
        4. Schema Validation
        5. 型別正規化

    不負責:

        - AI Analysis
        - LLM API
        - Knowledge Processing
        - Database
        - Retry
        - AI Task Queue
    """

    # ==================================================
    # Required Fields
    # ==================================================

    REQUIRED_FIELDS = [

        "summary",

        "category",

        "keywords",

        "entities",

        "relations",

        "importance"

    ]

    # ==================================================
    # Allowed Category
    # ==================================================

    ALLOWED_CATEGORY = [

        "Semiconductor",

        "AI Chip",

        "Advanced Process",

        "Packaging",

        "Memory",

        "Equipment"

    ]

    # ==================================================
    # Importance Range
    # ==================================================

    MIN_IMPORTANCE = 0

    MAX_IMPORTANCE = 10

    # ==================================================
    # Parse
    # ==================================================

    def parse(
        self,
        response: str
    ) -> dict:
        """
        解析 LLM Response。

        Input
        -----

        response:
            LLM 回傳文字。

        Output
        ------

        dict:
            已通過 Schema Validation 的 AI 結果。

        Raises
        ------

        ValueError:
            JSON 不存在、JSON 格式錯誤或 Schema 錯誤。

        TypeError:
            Response 或 JSON Root 型別錯誤。
        """

        # ==================================================
        # Input Validation
        # ==================================================

        if response is None:

            raise ValueError(
                "LLM response is empty."
            )

        if not isinstance(
            response,
            str
        ):

            raise TypeError(
                "LLM response must be string."
            )

        response = response.strip()

        if not response:

            raise ValueError(
                "LLM response is empty."
            )

        logger.info(
            "AI JSON parsing started"
        )

        # ==================================================
        # Extract JSON
        # ==================================================

        json_text = self._extract_json(
            response
        )

        # ==================================================
        # JSON Decode
        # ==================================================

        data = self._decode_json(
            json_text
        )

        # ==================================================
        # Repair / Normalize
        # ==================================================

        data = self._repair(
            data
        )

        # ==================================================
        # Validation
        # ==================================================

        self._validate(
            data
        )

        logger.info(
            "AI Response Validation PASS"
        )

        return data

    # ==================================================
    # Decode JSON
    # ==================================================

    def _decode_json(
        self,
        json_text: str
    ) -> dict:
        """
        將 JSON String Decode 成 Python Dict。
        """

        if not isinstance(
            json_text,
            str
        ):

            raise TypeError(
                "JSON text must be string."
            )

        try:

            data = json.loads(
                json_text
            )

        except json.JSONDecodeError as e:

            logger.error(
                "JSON decode failed: "
                f"line={e.lineno}, "
                f"column={e.colno}, "
                f"message={e.msg}"
            )

            raise ValueError(
                "Invalid JSON response."
            ) from e

        # ==================================================
        # Root Type Validation
        # ==================================================

        if not isinstance(
            data,
            dict
        ):

            raise TypeError(
                "AI response must be JSON object."
            )

        return data

    # ==================================================
    # Extract JSON
    # ==================================================

    def _extract_json(
        self,
        text: str
    ) -> str:
        """
        從 LLM Response 擷取 JSON Object。

        支援:

            1. 純 JSON

                {
                    ...
                }

            2. Markdown JSON

                ```json
                {
                    ...
                }
                ```

            3. JSON 前後存在說明文字

                Here is the result:

                {
                    ...
                }

        不使用:

            r"\\{.*\\}"

        這種 greedy regex，
        避免多個 JSON Object
        被一次抓取。
        """

        if not isinstance(
            text,
            str
        ):

            raise TypeError(
                "LLM response must be string."
            )

        text = text.strip()

        if not text:

            raise ValueError(
                "LLM response is empty."
            )

        # ==================================================
        # First:
        # 嘗試整個 Response 直接 JSON Decode
        # ==================================================

        try:

            parsed = json.loads(
                text
            )

            if isinstance(
                parsed,
                dict
            ):

                return text

        except (
            json.JSONDecodeError,
            TypeError
        ):

            pass

        # ==================================================
        # Markdown Code Block
        # ==================================================

        code_block_pattern = re.compile(
            r"```(?:json|JSON)?\s*(.*?)\s*```",
            re.DOTALL
        )

        matches = code_block_pattern.findall(
            text
        )

        for block in matches:

            block = block.strip()

            if not block:

                continue

            try:

                parsed = json.loads(
                    block
                )

                if isinstance(
                    parsed,
                    dict
                ):

                    return block

            except (
                json.JSONDecodeError,
                TypeError
            ):

                continue

        # ==================================================
        # General JSON Object Extraction
        # ==================================================

        start_positions = [

            index

            for index, char in enumerate(text)

            if char == "{"

        ]

        if not start_positions:

            raise ValueError(
                "No JSON object found."
            )

        # ==================================================
        # Balanced Brace Scan
        # ==================================================

        for start in start_positions:

            candidate = (
                self._extract_balanced_object(
                    text,
                    start
                )
            )

            if candidate is None:

                continue

            try:

                parsed = json.loads(
                    candidate
                )

                if isinstance(
                    parsed,
                    dict
                ):

                    return candidate

            except (
                json.JSONDecodeError,
                TypeError
            ):

                continue

        # ==================================================
        # Extraction Failed
        # ==================================================

        logger.error(
            "Unable to extract valid JSON object "
            "from LLM response."
        )

        raise ValueError(
            "No valid JSON object found."
        )

    # ==================================================
    # Balanced JSON Object Extraction
    # ==================================================

    def _extract_balanced_object(
        self,
        text: str,
        start: int
    ):
        """
        使用大括號深度擷取 JSON Object。

        注意:

        JSON String 裡面的:

            {
            }

        不應被當成 JSON 結構。

        因此需要處理:

            String
            Escape Character
            Brace Depth
        """

        if start < 0 or start >= len(text):

            return None

        if text[start] != "{":

            return None

        depth = 0

        in_string = False

        escaped = False

        for index in range(
            start,
            len(text)
        ):

            char = text[index]

            # ------------------------------------------
            # Escape Character
            # ------------------------------------------

            if escaped:

                escaped = False

                continue

            if char == "\\":

                if in_string:

                    escaped = True

                continue

            # ------------------------------------------
            # String
            # ------------------------------------------

            if char == '"':

                in_string = not in_string

                continue

            # ------------------------------------------
            # Ignore Braces Inside String
            # ------------------------------------------

            if in_string:

                continue

            # ------------------------------------------
            # Object Start
            # ------------------------------------------

            if char == "{":

                depth += 1

                continue

            # ------------------------------------------
            # Object End
            # ------------------------------------------

            if char == "}":

                depth -= 1

                if depth == 0:

                    return text[
                        start:index + 1
                    ]

        return None

    # ==================================================
    # Repair
    # ==================================================

    def _repair(
        self,
        data: dict
    ) -> dict:
        """
        修復 / 正規化 LLM Response。

        Repair 只處理:

            - 缺少可安全預設的欄位
            - String -> List
            - Numeric String -> Integer
            - Float -> Integer

        不處理:

            - 業務語意猜測
            - Unknown Category 強制修改
            - 任意錯誤資料自動轉換

        原則:

            Parser 可以修復格式，
            不應替 AI 猜答案。
        """

        logger.info(
            "AI Response Repair Start"
        )

        # ==================================================
        # Dict Validation
        # ==================================================

        if not isinstance(
            data,
            dict
        ):

            raise TypeError(
                "AI response must be JSON object."
            )

        # ==================================================
        # Summary
        # ==================================================

        if "summary" not in data:

            data["summary"] = ""

        elif not isinstance(
            data["summary"],
            str
        ):

            data["summary"] = str(
                data["summary"]
            )

        # ==================================================
        # Category
        # ==================================================

        if "category" not in data:

            data["category"] = ""

        elif not isinstance(
            data["category"],
            str
        ):

            data["category"] = str(
                data["category"]
            )

        data["category"] = (
            data["category"].strip()
        )

        # ==================================================
        # Keywords
        # ==================================================

        data["keywords"] = (
            self._normalize_string_list(
                data.get(
                    "keywords",
                    []
                )
            )
        )

        # ==================================================
        # Entities
        # ==================================================

        data["entities"] = (
            self._normalize_string_list(
                data.get(
                    "entities",
                    []
                )
            )
        )

        # ==================================================
        # Relations
        # ==================================================

        data["relations"] = (
            self._normalize_string_list(
                data.get(
                    "relations",
                    []
                )
            )
        )

        # ==================================================
        # Importance
        # ==================================================

        data["importance"] = (
            self._normalize_importance(
                data.get(
                    "importance",
                    0
                )
            )
        )

        logger.info(
            "AI Response Repair Complete"
        )

        return data

    # ==================================================
    # Normalize String List
    # ==================================================

    def _normalize_string_list(
        self,
        value
    ) -> list:
        """
        將 AI List 欄位正規化。

        支援:

            None
                -> []

            "A,B,C"
                -> ["A", "B", "C"]

            "A"
                -> ["A"]

            ["A", "B"]
                -> ["A", "B"]

        不符合格式:

            number
            dict
            tuple

        -> []

        注意:

        此方法只處理格式，
        不進行語意轉換。
        """

        if value is None:

            return []

        # --------------------------------------------------
        # String
        # --------------------------------------------------

        if isinstance(
            value,
            str
        ):

            value = value.strip()

            if not value:

                return []

            # ----------------------------------------------
            # 支援逗號分隔
            # ----------------------------------------------

            items = value.split(",")

            return [

                item.strip()

                for item in items

                if item.strip()

            ]

        # --------------------------------------------------
        # List
        # --------------------------------------------------

        if isinstance(
            value,
            list
        ):

            normalized = []

            for item in value:

                if isinstance(
                    item,
                    str
                ):

                    item = item.strip()

                    if item:

                        normalized.append(
                            item
                        )

            return normalized

        # --------------------------------------------------
        # Unsupported Type
        # --------------------------------------------------

        return []

    # ==================================================
    # Normalize Importance
    # ==================================================

    def _normalize_importance(
        self,
        value
    ) -> int:
        """
        正規化 Importance。

        支援:

            5
                -> 5

            5.0
                -> 5

            "5"
                -> 5

        不合法值:

            "abc"
            None
            dict

        -> 0

        最後限制:

            0 <= importance <= 10
        """

        # ==================================================
        # Boolean
        # ==================================================

        if isinstance(
            value,
            bool
        ):

            return 0

        # ==================================================
        # Integer
        # ==================================================

        if isinstance(
            value,
            int
        ):

            importance = value

        # ==================================================
        # Float
        # ==================================================

        elif isinstance(
            value,
            float
        ):

            importance = int(
                value
            )

        # ==================================================
        # String
        # ==================================================

        elif isinstance(
            value,
            str
        ):

            value = value.strip()

            if not value:

                return 0

            try:

                importance = int(
                    float(value)
                )

            except (
                ValueError,
                TypeError
            ):

                logger.warning(
                    "Invalid AI importance value: "
                    f"{value!r}; using 0"
                )

                return 0

        # ==================================================
        # Unsupported Type
        # ==================================================

        else:

            logger.warning(
                "Unsupported AI importance type: "
                f"{type(value).__name__}; using 0"
            )

            return 0

        # ==================================================
        # Clamp
        # ==================================================

        importance = max(
            self.MIN_IMPORTANCE,
            min(
                self.MAX_IMPORTANCE,
                importance
            )
        )

        return importance

    # ==================================================
    # Validation
    # ==================================================

    def _validate(
        self,
        data: dict
    ):
        """
        驗證 AI 結果。

        驗證:

            - Root Object
            - Required Fields
            - Summary
            - Category
            - Keywords
            - Entities
            - Relations
            - Importance
            - List Item Types
        """

        # ==================================================
        # Root Validation
        # ==================================================

        if not isinstance(
            data,
            dict
        ):

            raise TypeError(
                "AI response must be JSON object."
            )

        # ==================================================
        # Required Fields
        # ==================================================

        for field in self.REQUIRED_FIELDS:

            if field not in data:

                raise ValueError(
                    f"Missing field: {field}"
                )

        # ==================================================
        # Summary
        # ==================================================

        if not isinstance(
            data["summary"],
            str
        ):

            raise TypeError(
                "summary must be string."
            )

        # ==================================================
        # Category
        # ==================================================

        if not isinstance(
            data["category"],
            str
        ):

            raise TypeError(
                "category must be string."
            )

        if not data["category"]:

            raise ValueError(
                "category cannot be empty."
            )

        # --------------------------------------------------
        # Unknown Category
        #
        # 保持目前 V4 行為:
        #
        # warning
        #
        # 不直接 FAILED
        # --------------------------------------------------

        if (
            data["category"]
            not in self.ALLOWED_CATEGORY
        ):

            logger.warning(
                "Unknown AI category: "
                f"{data['category']}"
            )

        # ==================================================
        # Keywords
        # ==================================================

        if not isinstance(
            data["keywords"],
            list
        ):

            raise TypeError(
                "keywords must be list."
            )

        # ==================================================
        # Entities
        # ==================================================

        if not isinstance(
            data["entities"],
            list
        ):

            raise TypeError(
                "entities must be list."
            )

        # ==================================================
        # Relations
        # ==================================================

        if not isinstance(
            data["relations"],
            list
        ):

            raise TypeError(
                "relations must be list."
            )

        # ==================================================
        # Importance
        # ==================================================

        if not isinstance(
            data["importance"],
            int
        ):

            raise TypeError(
                "importance must be int."
            )

        if not (
            self.MIN_IMPORTANCE
            <= data["importance"]
            <= self.MAX_IMPORTANCE
        ):

            raise ValueError(
                "importance must be between "
                f"{self.MIN_IMPORTANCE} and "
                f"{self.MAX_IMPORTANCE}."
            )

        # ==================================================
        # List Item Validation
        # ==================================================

        self._validate_string_list(
            data["keywords"],
            "keywords"
        )

        self._validate_string_list(
            data["entities"],
            "entities"
        )

        self._validate_string_list(
            data["relations"],
            "relations"
        )

    # ==================================================
    # Validate String List
    # ==================================================

    def _validate_string_list(
        self,
        values: list,
        field_name: str
    ):
        """
        驗證 List 內所有元素
        必須為 String。
        """

        if not isinstance(
            values,
            list
        ):

            raise TypeError(
                f"{field_name} must be list."
            )

        for item in values:

            if not isinstance(
                item,
                str
            ):

                raise TypeError(
                    f"{field_name} items "
                    "must be string."
                )

    # ==================================================
    # Repr
    # ==================================================

    def __repr__(
        self
    ):

        return (
            "JSONParser("
            f"required_fields="
            f"{len(self.REQUIRED_FIELDS)}, "
            f"allowed_categories="
            f"{len(self.ALLOWED_CATEGORY)}"
            ")"
        )