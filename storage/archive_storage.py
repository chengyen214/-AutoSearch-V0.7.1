"""
archive_storage.py

AutoSearch V4

P1.1 Step 4.1


Raw HTML Archive Storage


功能:

1. 儲存原始 HTML
2. 計算 hash
3. 回傳 Archive metadata


設計:

HTML:
    Local Storage


SQL:
    儲存索引


"""


import os

import hashlib





# ======================================
# Archive Path
# ======================================


ARCHIVE_DIR = (

    "storage/archive/raw/html"

)






# ======================================
# Create Directory
# ======================================


def ensure_archive_dir():


    """
    建立 Archive 資料夾

    """


    os.makedirs(

        ARCHIVE_DIR,

        exist_ok=True

    )







# ======================================
# Calculate Hash
# ======================================


def calculate_hash(html):


    """
    計算 HTML SHA256

    """


    return hashlib.sha256(

        html.encode(

            "utf-8"

        )

    ).hexdigest()







# ======================================
# Normalize Path
# ======================================


def normalize_path(path):


    """
    統一 Storage Path 格式

    Windows:

        \


    Linux:

        /


    Database 儲存:

        /

    """


    return path.replace(

        "\\",

        "/"

    )








# ======================================
# Save HTML
# ======================================


def save_html(

    document_id,

    html

):


    """
    儲存 Raw HTML


    Args:

        document_id:

            Article document_id


        html:

            原始 HTML



    Returns:

        Archive metadata


    """



    ensure_archive_dir()






    # -----------------------------
    # Filename
    # -----------------------------


    filename = (

        document_id

        +

        ".html"

    )







    # -----------------------------
    # Real File Path
    #
    # Windows 使用
    #
    # -----------------------------


    filepath = os.path.join(

        ARCHIVE_DIR,

        filename

    )







    # -----------------------------
    # Write HTML
    # -----------------------------


    with open(

        filepath,

        "w",

        encoding="utf-8"

    ) as file:


        file.write(

            html

        )







    # -----------------------------
    # Metadata
    # -----------------------------


    storage_path = normalize_path(

        filepath

    )






    return {


        "storage_path":

            storage_path,



        "file_hash":

            calculate_hash(

                html

            ),



        "file_size":

            os.path.getsize(

                filepath

            ),



        "mime_type":

            "text/html"


    }