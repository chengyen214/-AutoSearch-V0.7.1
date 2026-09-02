"""
utils/keyword_processor.py

AutoSearch V5

Keyword Processor

用途：

    將使用者輸入的 Keyword
    拆分成具有意義的詞彙，
    並將拆分後的詞彙翻譯成指定目標語言。

Pipeline:

    User Keyword
        ↓
    KeywordProcessor
        ↓
    Keyword Tokenization
        ↓
    Meaningful Terms
        ↓
    Translation
        ↓
    Processed Keyword Result


例如：

    Input:

        keyword = "IC semiconductor"
        target_language = "Chinese"


    Output:

        {
            "original_keyword": "IC semiconductor",
            "target_language": "Chinese",
            "terms": [
                {
                    "original": "IC",
                    "translated": "IC"
                },
                {
                    "original": "semiconductor",
                    "translated": "半導體"
                }
            ],
            "original_terms": [
                "IC",
                "semiconductor"
            ],
            "translated_terms": [
                "IC",
                "半導體"
            ]
        }


Failure Policy:

    如果 Split / Translation
    發生任何未預期錯誤：

        不使用部分結果
        不使用部分 Split
        不使用部分 Translation

        直接回傳原始 Keyword。


    例如：

        IC semiconductor
              ↓
            Split
              ↓
        IC
        semiconductor
              ↓
        semiconductor Translation Error
              ↓
        放棄全部處理
              ↓
        IC semiconductor


責任：

    - Keyword Normalize
    - Keyword Split
    - Meaningful Term Extraction
    - Term Translation
    - Result Formatting
    - Safe Fallback


不負責：

    - Search
    - Search Provider
    - SearchAdapter
    - SearchExecutionBridge
    - Crawler
    - Parser
    - Article
    - Archive
    - AI Analysis
    - Database
    - Job
"""


# ==================================================
#
# Imports
#
# ==================================================

import re


# ==================================================
#
# Keyword Processor
#
# ==================================================

class KeywordProcessor:
    """
    Keyword Processor。

    將：

        Keyword

    轉換成：

        原始詞彙
            +
        翻譯詞彙


    Failure Policy:

        Split / Translation
        任一階段發生未預期錯誤：

            → 放棄全部處理結果
            → 回傳原始 Keyword
    """


    # ==================================================
    #
    # Constructor
    #
    # ==================================================

    def __init__(
        self,
        translator=None,
    ):
        """
        建立 KeywordProcessor。

        Parameters
        ----------
        translator :
            Optional translation callable。

            格式：

                translator(
                    text,
                    target_language
                )

            必須回傳：

                str

            如果沒有提供 translator，
            則使用內建 fallback。
        """

        self.translator = translator


    # ==================================================
    #
    # Public Process
    #
    # ==================================================

    def process(
        self,
        keyword,
        target_language,
    ):
        """
        處理 Keyword。

        Parameters
        ----------
        keyword :
            使用者輸入 Keyword。

        target_language :
            目標語言。

            例如：

                Chinese
                zh-TW
                English
                Japanese
                Korean


        Returns
        -------

        dict


        Failure Policy
        --------------

        如果：

            Split
                或
            Translation

        發生任何未預期錯誤：

            不使用部分結果。

            直接回傳：

                original keyword


        Example
        -------

        Input:

            keyword =
                "IC semiconductor"

            target_language =
                "zh-TW"


        Normal Output:

            {
                "original_keyword":
                    "IC semiconductor",

                "target_language":
                    "zh-TW",

                "terms":
                    [
                        {
                            "original": "IC",
                            "translated": "IC"
                        },
                        {
                            "original":
                                "semiconductor",
                            "translated":
                                "半導體"
                        }
                    ],

                "original_terms":
                    [
                        "IC",
                        "semiconductor"
                    ],

                "translated_terms":
                    [
                        "IC",
                        "半導體"
                    ]
            }


        Error Output:

            {
                "original_keyword":
                    "IC semiconductor",

                "target_language":
                    "zh-TW",

                "terms":
                    [
                        {
                            "original":
                                "IC semiconductor",

                            "translated":
                                "IC semiconductor"
                        }
                    ],

                "original_terms":
                    [
                        "IC semiconductor"
                    ],

                "translated_terms":
                    [
                        "IC semiconductor"
                    ]
            }
        """

        # ==================================================
        #
        # Preserve Original Keyword
        #
        # ==================================================

        if keyword is None:

            original_keyword = ""

        else:

            try:

                original_keyword = str(
                    keyword
                ).strip()

            except Exception:

                original_keyword = ""


        # ==================================================
        #
        # Normalize Target Language
        #
        # ==================================================

        try:

            normalized_language = (
                self.normalize_language(
                    target_language
                )
            )

        except Exception:

            normalized_language = (
                "" if target_language is None
                else str(
                    target_language
                ).strip()
            )


        # ==================================================
        #
        # Empty Keyword
        #
        # ==================================================

        if not original_keyword:

            return {
                "original_keyword": "",
                "target_language":
                    normalized_language,
                "terms": [],
                "original_terms": [],
                "translated_terms": [],
            }


        # ==================================================
        #
        # Processing
        #
        # ==================================================

        try:

            # ----------------------------------------------
            #
            # Normalize Keyword
            #
            # ----------------------------------------------

            normalized_keyword = (
                self.normalize_keyword(
                    keyword
                )
            )


            if not normalized_keyword:

                return {
                    "original_keyword": "",
                    "target_language":
                        normalized_language,
                    "terms": [],
                    "original_terms": [],
                    "translated_terms": [],
                }


            # ----------------------------------------------
            #
            # Split
            #
            # ----------------------------------------------

            terms = self.split(
                normalized_keyword
            )


            # ----------------------------------------------
            #
            # Split Validation
            #
            # ----------------------------------------------

            if not isinstance(
                terms,
                list,
            ):

                raise ValueError(
                    "Keyword split returned "
                    "an invalid result"
                )


            if not terms:

                raise ValueError(
                    "Keyword split returned "
                    "no terms"
                )


            # ----------------------------------------------
            #
            # Translation
            #
            # ----------------------------------------------

            processed_terms = []

            original_terms = []

            translated_terms = []


            for term in terms:

                if not term:

                    raise ValueError(
                        "Keyword split returned "
                        "an empty term"
                    )


                translated = self.translate(
                    term,
                    normalized_language,
                )


                # ------------------------------------------
                #
                # Translation Validation
                #
                # ------------------------------------------

                if translated is None:

                    raise ValueError(
                        "Keyword translation "
                        "returned None"
                    )


                translated = str(
                    translated
                ).strip()


                if not translated:

                    raise ValueError(
                        "Keyword translation "
                        "returned empty value"
                    )


                # ------------------------------------------
                #
                # Store
                #
                # ------------------------------------------

                processed_terms.append(
                    {
                        "original": term,
                        "translated": translated,
                    }
                )


                original_terms.append(
                    term
                )


                translated_terms.append(
                    translated
                )


            # ==================================================
            #
            # Success
            #
            # ==================================================

            return {
                "original_keyword":
                    normalized_keyword,

                "target_language":
                    normalized_language,

                "terms":
                    processed_terms,

                "original_terms":
                    original_terms,

                "translated_terms":
                    translated_terms,
            }


        except Exception:

            # ==================================================
            #
            # Complete Original Keyword Fallback
            #
            # ==================================================

            return self._fallback_result(
                original_keyword,
                normalized_language,
            )


    # ==================================================
    #
    # Normalize Keyword
    #
    # ==================================================

    @staticmethod
    def normalize_keyword(
        keyword,
    ):
        """
        正規化 Keyword。

        None：

            ""

        其他：

            strip()
            collapse whitespace
        """

        if keyword is None:

            return ""


        keyword = str(
            keyword
        ).strip()


        if not keyword:

            return ""


        keyword = re.sub(
            r"\s+",
            " ",
            keyword,
        )


        return keyword


    # ==================================================
    #
    # Normalize Language
    #
    # ==================================================

    @staticmethod
    def normalize_language(
        target_language,
    ):
        """
        正規化目標語言。

        None：

            ""

        Example:

            zh-TW
                ↓
            zh-TW

            Chinese
                ↓
            Chinese
        """

        if target_language is None:

            return ""


        return str(
            target_language
        ).strip()


    # ==================================================
    #
    # Split Keyword
    #
    # ==================================================

    @classmethod
    def split(
        cls,
        keyword,
    ):
        """
        將 Keyword 拆成具有意義的詞彙。

        例如：

            IC semiconductor

        →

            [
                "IC",
                "semiconductor"
            ]


        例如：

            AI semiconductor technology

        →

            [
                "AI",
                "semiconductor",
                "technology"
            ]


        注意：

            不會直接把單一字母
            或純標點當成詞彙。
        """

        keyword = cls.normalize_keyword(
            keyword
        )


        if not keyword:

            return []


        # ----------------------------------------------
        #
        # Protect common technical forms
        #
        # ----------------------------------------------

        keyword = re.sub(
            r"(?<=[A-Za-z])/(?=[A-Za-z])",
            " ",
            keyword,
        )


        # ----------------------------------------------
        #
        # Split whitespace
        #
        # ----------------------------------------------

        raw_terms = re.split(
            r"\s+",
            keyword,
        )


        terms = []


        for term in raw_terms:

            term = term.strip()


            if not term:

                continue


            # ------------------------------------------
            #
            # Remove surrounding punctuation
            #
            # ------------------------------------------

            term = term.strip(
                ".,;:!?()[]{}\"'`"
            )


            if not term:

                continue


            # ------------------------------------------
            #
            # Split comma / semicolon
            #
            # ------------------------------------------

            parts = re.split(
                r"[,;]+",
                term,
            )


            for part in parts:

                part = part.strip()


                if not part:

                    continue


                # --------------------------------------
                #
                # Remove duplicate
                #
                # --------------------------------------

                if part not in terms:

                    terms.append(
                        part
                    )


        return terms


    # ==================================================
    #
    # Translate
    #
    # ==================================================

    def translate(
        self,
        term,
        target_language,
    ):
        """
        將單一詞彙翻譯成目標語言。

        如果有提供 translator：

            translator(
                term,
                target_language
            )

        否則：

            使用內建 Technical Translation。


        注意：

            本 method 如果發生 Exception，
            會向 process() 傳遞。

            process() 會放棄全部處理結果，
            回傳原始 Keyword。
        """

        term = self.normalize_keyword(
            term
        )


        if not term:

            return ""


        target_language = (
            self.normalize_language(
                target_language
            )
        )


        if not target_language:

            return term


        # ----------------------------------------------
        #
        # External Translator
        #
        # ----------------------------------------------

        if self.translator is not None:

            translated = self.translator(
                term,
                target_language,
            )


            if translated is None:

                raise ValueError(
                    "Translator returned None"
                )


            translated = str(
                translated
            ).strip()


            if not translated:

                raise ValueError(
                    "Translator returned "
                    "an empty result"
                )


            return translated


        # ----------------------------------------------
        #
        # Built-in Translation
        #
        # ----------------------------------------------

        return self._fallback_translate(
            term,
            target_language,
        )


    # ==================================================
    #
    # Fallback Translation
    #
    # ==================================================

    @staticmethod
    def _fallback_translate(
        term,
        target_language,
    ):
        """
        Technical Keyword Fallback Translation。

        注意：

            這不是完整 Machine Translation。

            主要保留：

                技術縮寫
                專有名詞
                未知詞

            並提供常見技術詞彙翻譯。

        真正完整翻譯可以透過：

            translator

        注入。

        未知詞：

            回傳原詞。
        """

        language = (
            target_language
            .lower()
            .replace("_", "-")
        )


        # ==================================================
        #
        # Chinese
        #
        # ==================================================

        chinese_languages = {

            "chinese",
            "zh",
            "zh-tw",
            "zh-cn",
            "traditional chinese",
            "simplified chinese",

        }


        if language in chinese_languages:

            translations = {

                "semiconductor":
                    "半導體",

                "semiconductors":
                    "半導體",

                "integrated":
                    "積體",

                "circuit":
                    "電路",

                "integrated-circuit":
                    "積體電路",

                "technology":
                    "技術",

                "technologies":
                    "技術",

                "industry":
                    "產業",

                "market":
                    "市場",

                "memory":
                    "記憶體",

                "processor":
                    "處理器",

                "microprocessor":
                    "微處理器",

                "chip":
                    "晶片",

                "chips":
                    "晶片",

                "design":
                    "設計",

                "manufacturing":
                    "製造",

                "foundry":
                    "晶圓代工",

                "wafer":
                    "晶圓",

                "electronics":
                    "電子",

                "electronic":
                    "電子",

                "artificial":
                    "人工",

                "intelligence":
                    "智慧",

                "artificial-intelligence":
                    "人工智慧",

                "automotive":
                    "汽車",

                "communication":
                    "通訊",

                "communications":
                    "通訊",

                "network":
                    "網路",

                "networking":
                    "網路",

                "sensor":
                    "感測器",

                "sensors":
                    "感測器",

                "power":
                    "電源",

                "display":
                    "顯示器",

                "storage":
                    "儲存",

                "cloud":
                    "雲端",

                "data":
                    "資料",

                "center":
                    "中心",

                "server":
                    "伺服器",

                "servers":
                    "伺服器",

            }


            normalized = (
                term.lower()
            )


            if normalized in translations:

                return translations[
                    normalized
                ]


            # ------------------------------------------
            #
            # Acronym / Technical Name
            #
            # ------------------------------------------

            if (
                term.isupper()
                and len(term) <= 10
            ):

                return term


            # ------------------------------------------
            #
            # Unknown Technical Term
            #
            # ------------------------------------------

            return term


        # ==================================================
        #
        # English
        #
        # ==================================================

        english_languages = {

            "english",
            "en",
            "en-us",
            "en-gb",

        }


        if language in english_languages:

            return term


        # ==================================================
        #
        # Other Languages
        #
        # ==================================================

        # 未來可以接：

        # Google Translate
        # DeepL
        # LLM
        # Groq
        # Ollama

        return term


    # ==================================================
    #
    # Complete Fallback Result
    #
    # ==================================================

    @staticmethod
    def _fallback_result(
        original_keyword,
        target_language,
    ):
        """
        完整 Keyword Fallback。

        任何：

            Split Error
            Translation Error
            Unexpected Error

        都不使用部分結果。

        直接：

            original keyword
                ↓
            translated keyword
        """

        if original_keyword is None:

            original_keyword = ""


        original_keyword = str(
            original_keyword
        ).strip()


        if not original_keyword:

            return {
                "original_keyword": "",
                "target_language":
                    target_language,
                "terms": [],
                "original_terms": [],
                "translated_terms": [],
            }


        return {
            "original_keyword":
                original_keyword,

            "target_language":
                target_language,

            "terms": [
                {
                    "original":
                        original_keyword,

                    "translated":
                        original_keyword,
                }
            ],

            "original_terms": [
                original_keyword
            ],

            "translated_terms": [
                original_keyword
            ],
        }


    # ==================================================
    #
    # Convenience API
    #
    # ==================================================

    @classmethod
    def process_keyword(
        cls,
        keyword,
        target_language,
        translator=None,
    ):
        """
        Class-level Convenience API。

        可以直接：

            KeywordProcessor.process_keyword(
                "IC semiconductor",
                "Chinese"
            )
        """

        processor = cls(
            translator=translator
        )


        return processor.process(
            keyword,
            target_language,
        )


# ==================================================
#
# Public API
#
# ==================================================

__all__ = [
    "KeywordProcessor",
]