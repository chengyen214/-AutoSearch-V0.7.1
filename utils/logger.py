"""
logger.py

AutoSearch V2.5

Logging System

用途：

    統一管理系統 Log

功能：

    - INFO 訊息
    - WARNING 警告
    - ERROR 錯誤
    - 自動輸出時間


使用：

    from utils.logger import logger


    logger.info("Start Search")

"""



import logging

import os

from datetime import datetime



# ==================================
# Log 資料夾
# ==================================

LOG_DIR = "logs"



if not os.path.exists(LOG_DIR):

    os.makedirs(LOG_DIR)



# ==================================
# Log File
# ==================================

log_file = os.path.join(

    LOG_DIR,

    datetime.now().strftime(
        "%Y-%m-%d"
    ) + ".log"

)



# ==================================
# Logger設定
# ==================================

logger = logging.getLogger(
    "AutoSearch"
)



logger.setLevel(
    logging.INFO
)



# 避免重複加入 Handler

if not logger.handlers:



    # ------------------------------
    # File Handler
    # ------------------------------

    file_handler = logging.FileHandler(

        log_file,

        encoding="utf-8"

    )



    # ------------------------------
    # Console Handler
    # ------------------------------

    console_handler = logging.StreamHandler()



    # ------------------------------
    # Format
    # ------------------------------

    formatter = logging.Formatter(

        "%(asctime)s | %(levelname)s | %(message)s"

    )



    file_handler.setFormatter(
        formatter
    )


    console_handler.setFormatter(
        formatter
    )



    logger.addHandler(
        file_handler
    )


    logger.addHandler(
        console_handler
    )