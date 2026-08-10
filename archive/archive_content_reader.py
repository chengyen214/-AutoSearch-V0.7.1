"""
archive/archive_content_reader.py

AutoSearch V4

P2.3.5 Historical Search

Archive Content Reader

功能:

1. 讀取 Archive HTML
2. 依 storage_path 取得 Archive File
3. 讀取 HTML Content
4. 檢查 Archive File 是否存在
5. 取得 Archive File Size
6. 計算 Archive File Hash
7. 驗證 Archive File Hash

Architecture:

HistoricalSearchService
        ↓
ArchiveContentReader
        ↓
archive_versions.storage_path
        ↓
Archive HTML
        ↓
Historical Search
"""

import os
import hashlib

from utils.logger import logger


class ArchiveContentReader:
    """
    Archive Content Reader

    負責讀取 Knowledge Archive
    實際儲存的 HTML 檔案。

    注意:

        本 class 不直接操作 Database。

    storage_path 可以是：

        archive/html/2026/08/08/hash.html

    """

    # ==================================
    # Initialize
    # ==================================

    def __init__(
        self,
        archive_root="."
    ):
        """
        初始化 Archive Content Reader。

        Parameters
        ----------
        archive_root :

            Archive 根目錄。

            預設：

                .

            因此：

                archive/html/...
        """

        if archive_root is None:

            archive_root = "."

        self.archive_root = os.path.abspath(
            archive_root
        )

    # ==================================
    # Normalize Path
    # ==================================

    def _normalize_path(
        self,
        storage_path
    ):
        """
        將 Database storage_path
        轉換成實際檔案路徑。

        Database:

            archive/html/2026/08/08/a.html

        實際：

            ./archive/html/2026/08/08/a.html
        """

        if not storage_path:

            return None

        # ==================================
        # Normalize Separator
        # ==================================

        storage_path = str(
            storage_path
        ).replace(
            "/",
            os.sep
        )

        # ==================================
        # Absolute Path
        # ==================================

        if os.path.isabs(
            storage_path
        ):

            return os.path.abspath(
                storage_path
            )

        # ==================================
        # Relative Path
        # ==================================

        return os.path.abspath(
            os.path.join(
                self.archive_root,
                storage_path
            )
        )

    # ==================================
    # Get Path
    # ==================================

    def get_path(
        self,
        storage_path
    ):
        """
        取得 Archive 實際檔案路徑。
        """

        return self._normalize_path(
            storage_path
        )

    # ==================================
    # Exists
    # ==================================

    def exists(
        self,
        storage_path
    ):
        """
        檢查 Archive File 是否存在。
        """

        file_path = self._normalize_path(
            storage_path
        )

        if file_path is None:

            return False

        return os.path.isfile(
            file_path
        )

    # ==================================
    # Read HTML
    # ==================================

    def read(
        self,
        storage_path
    ):
        """
        讀取 Archive HTML。

        Returns
        -------

        str / None
        """

        file_path = self._normalize_path(
            storage_path
        )

        if file_path is None:

            logger.warning(
                "Archive storage path is empty"
            )

            return None

        if not os.path.isfile(
            file_path
        ):

            logger.warning(
                "Archive file not found: "
                f"{file_path}"
            )

            return None

        try:

            with open(

                file_path,

                "r",

                encoding="utf-8"

            ) as f:

                return f.read()

        except UnicodeDecodeError:

            logger.warning(
                "Archive file UTF-8 decode failed: "
                f"{file_path}"
            )

            return None

        except OSError as e:

            logger.exception(
                "Archive file read error: "
                f"{e}"
            )

            return None

    # ==================================
    # Read Bytes
    # ==================================

    def read_bytes(
        self,
        storage_path
    ):
        """
        以 bytes 方式讀取 Archive File。

        用於：

            Hash
            File Verification
        """

        file_path = self._normalize_path(
            storage_path
        )

        if file_path is None:

            return None

        if not os.path.isfile(
            file_path
        ):

            return None

        try:

            with open(
                file_path,
                "rb"
            ) as f:

                return f.read()

        except OSError as e:

            logger.exception(
                "Archive binary read error: "
                f"{e}"
            )

            return None

    # ==================================
    # File Size
    # ==================================

    def get_file_size(
        self,
        storage_path
    ):
        """
        取得 Archive File Size。
        """

        file_path = self._normalize_path(
            storage_path
        )

        if file_path is None:

            return None

        if not os.path.isfile(
            file_path
        ):

            return None

        try:

            return os.path.getsize(
                file_path
            )

        except OSError as e:

            logger.exception(
                "Archive file size error: "
                f"{e}"
            )

            return None

    # ==================================
    # Generate Hash
    # ==================================

    def generate_hash(
        self,
        storage_path
    ):
        """
        計算 Archive 實際檔案 SHA256。

        注意：

            Hash 來自實際落盤 bytes。
        """

        file_path = self._normalize_path(
            storage_path
        )

        if file_path is None:

            return None

        if not os.path.isfile(
            file_path
        ):

            return None

        sha256 = hashlib.sha256()

        try:

            with open(
                file_path,
                "rb"
            ) as f:

                for chunk in iter(
                    lambda:
                    f.read(1024 * 1024),
                    b""
                ):

                    sha256.update(
                        chunk
                    )

            return sha256.hexdigest()

        except OSError as e:

            logger.exception(
                "Archive hash error: "
                f"{e}"
            )

            return None

    # ==================================
    # Verify Hash
    # ==================================

    def verify_hash(
        self,
        storage_path,
        expected_hash
    ):
        """
        驗證 Archive File Hash。

        Returns
        -------

        bool
        """

        if not expected_hash:

            return False

        actual_hash = (
            self.generate_hash(
                storage_path
            )
        )

        if actual_hash is None:

            return False

        return (
            actual_hash
            == expected_hash
        )

    # ==================================
    # Read Version
    # ==================================

    def read_version(
        self,
        archive_version
    ):
        """
        直接讀取 ArchiveVersion Model。

        ArchiveVersion 必須包含：

            storage_path

        Returns
        -------

        str / None
        """

        if archive_version is None:

            return None

        storage_path = getattr(
            archive_version,
            "storage_path",
            None
        )

        # 支援 dict
        if isinstance(
            archive_version,
            dict
        ):

            storage_path = (
                archive_version.get(
                    "storage_path"
                )
            )

        return self.read(
            storage_path
        )

    # ==================================
    # Verify Version
    # ==================================

    def verify_version(
        self,
        archive_version
    ):
        """
        驗證 ArchiveVersion 實際檔案。

        驗證：

            1. File Exists
            2. File Hash
        """

        if archive_version is None:

            return False

        if isinstance(
            archive_version,
            dict
        ):

            storage_path = (
                archive_version.get(
                    "storage_path"
                )
            )

            expected_hash = (
                archive_version.get(
                    "file_hash"
                )
            )

        else:

            storage_path = getattr(
                archive_version,
                "storage_path",
                None
            )

            expected_hash = getattr(
                archive_version,
                "file_hash",
                None
            )

        return self.verify_hash(

            storage_path,

            expected_hash

        )

    # ==================================
    # Get Metadata
    # ==================================

    def get_metadata(
        self,
        storage_path
    ):
        """
        取得 Archive File Metadata。

        Returns
        -------

        dict
        """

        file_path = self._normalize_path(
            storage_path
        )

        if file_path is None:

            return None

        if not os.path.isfile(
            file_path
        ):

            return None

        try:

            return {

                "storage_path": storage_path,

                "file_path": file_path,

                "file_size": (
                    os.path.getsize(
                        file_path
                    )
                ),

                "file_hash": (
                    self.generate_hash(
                        storage_path
                    )
                )

            }

        except OSError as e:

            logger.exception(
                "Archive metadata error: "
                f"{e}"
            )

            return None

    # ==================================
    # Search Content
    # ==================================

    def contains(
        self,
        storage_path,
        keyword,
        case_sensitive=False
    ):
        """
        檢查 Archive HTML 是否包含指定文字。

        用於：

            Historical Search

        Returns
        -------

        bool
        """

        if not keyword:

            return False

        content = self.read(
            storage_path
        )

        if content is None:

            return False

        if case_sensitive:

            return keyword in content

        return (
            keyword.lower()
            in content.lower()
        )

    # ==================================
    # Repr
    # ==================================

    def __repr__(self):

        return (
            "ArchiveContentReader("
            f"archive_root="
            f"{self.archive_root!r}"
            ")"
        )