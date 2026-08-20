"""
utils/hash.py

AutoSearch V4

Centralized Hash Utilities

Hash Policy:

1. Article.document_id
   → generate_hash(title, content)

2. Archive content hash
   → generate_content_hash(content)

3. Archive actual file hash
   → generate_file_hash(file_path)

所有 SHA256 Hash 都集中在此模組，
避免 ArticleService / ArchiveService
各自實作不同 Hash 邏輯。
"""

import hashlib


# ==================================================
#
# Article Document Hash
#
# ==================================================

def generate_hash(
    title,
    content,
):
    """
    產生 Article document_id。

    用途：

        Article.document_id

    Hash Input:

        title + content

    Algorithm:

        SHA256

    """

    if title is None:

        title = ""

    if content is None:

        content = ""

    if not isinstance(
        title,
        str,
    ):

        title = str(title)

    if not isinstance(
        content,
        str,
    ):

        content = str(content)

    text = (
        title +
        content
    )

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ==================================================
#
# Content Hash
#
# ==================================================

def generate_content_hash(
    content,
):
    """
    產生內容 SHA256。

    用途：

        Archive HTML Content Hash

    注意：

        Hash 直接針對 UTF-8 bytes 計算。

    這個 Hash 應與 ArchiveService
    實際寫入 HTML File 後的 File Hash 一致。
    """

    if content is None:

        return None

    if not isinstance(
        content,
        str,
    ):

        content = str(content)

    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()


# ==================================================
#
# File Hash
#
# ==================================================

def generate_file_hash(
    file_path,
):
    """
    計算實際檔案內容 SHA256。

    用途：

        Archive File Hash

    特點：

        直接讀取實際落盤檔案 bytes。

    因此可以用來驗證：

        Original HTML
            ↓
        UTF-8 File
            ↓
        Actual File Hash

    """

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb",
    ) as file:

        for chunk in iter(
            lambda: file.read(
                1024 * 1024
            ),
            b"",
        ):

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


__all__ = [
    "generate_hash",
    "generate_content_hash",
    "generate_file_hash",
]