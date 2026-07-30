"""
AutoSearch 系統設定
"""

# 搜尋設定
MAX_RESULTS = 5

# 網頁下載
TIMEOUT = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}

# Excel
OUTPUT_FILE = "output/result.xlsx"

# Log
LOG_FOLDER = "logs"

# Duplicate Checker
CHECK_DUPLICATE = True

# Cleaner
MIN_CONTENT_LENGTH = 200

# Source
PARSE_SOURCE = True

# Crawl
CRAWL_DELAY = 1