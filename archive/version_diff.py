"""
archive/version_diff.py

AutoSearch V4

P2.3.4 Version Comparison / Diff

用途:

    比較兩個 Archive Version 的內容差異。

功能:

    1. 比較兩個版本
    2. 找出新增內容
    3. 找出刪除內容
    4. 找出修改內容
    5. 產生 ArchiveDiff Model
    6. 產生 Diff Summary

設計:

    Version / Repository
            ↓
        VersionDiff
            ↓
        ArchiveDiff

注意:

    本模組不直接操作 Database。
"""

from difflib import SequenceMatcher

from models.archive_diff import ArchiveDiff


class VersionDiff:

    """
    Archive Version Diff Engine
    """

    # ==================================
    # Compare
    # ==================================

    @staticmethod
    def compare(
        old_content,
        new_content,
        article_id=None,
        from_version=None,
        to_version=None
    ):
        """
        比較兩個版本內容。

        Parameters
        ----------
        old_content : str
            舊版本內容

        new_content : str
            新版本內容

        article_id : int, optional
            Article ID

        from_version : int, optional
            舊版本號

        to_version : int, optional
            新版本號

        Returns
        -------
        ArchiveDiff
        """

        old_content = (
            old_content
            if old_content is not None
            else ""
        )

        new_content = (
            new_content
            if new_content is not None
            else ""
        )

        old_lines = old_content.splitlines()

        new_lines = new_content.splitlines()

        matcher = SequenceMatcher(
            None,
            old_lines,
            new_lines
        )

        added = []

        removed = []

        changed = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():

            # ==================================
            # Equal
            # ==================================

            if tag == "equal":

                continue

            # ==================================
            # Insert
            # ==================================

            if tag == "insert":

                added.extend(
                    new_lines[j1:j2]
                )

                continue

            # ==================================
            # Delete
            # ==================================

            if tag == "delete":

                removed.extend(
                    old_lines[i1:i2]
                )

                continue

            # ==================================
            # Replace
            # ==================================

            if tag == "replace":

                old_block = old_lines[i1:i2]

                new_block = new_lines[j1:j2]

                # ----------------------------------
                # Pair changed lines
                # ----------------------------------
                #
                # 例如:
                #
                # old:
                #   A
                #   B
                #
                # new:
                #   A'
                #   B'
                #
                # 會產生:
                #
                #   {"old": ["A"], "new": ["A'"]}
                #   {"old": ["B"], "new": ["B'"]}
                #
                # 而不是把整個 block
                # 視為一個 changed。
                #

                pair_count = min(
                    len(old_block),
                    len(new_block)
                )

                for index in range(pair_count):

                    changed.append(
                        {
                            "old": [
                                old_block[index]
                            ],
                            "new": [
                                new_block[index]
                            ]
                        }
                    )

                # ----------------------------------
                # Remaining Old Lines
                # ----------------------------------

                if len(old_block) > pair_count:

                    removed.extend(
                        old_block[pair_count:]
                    )

                # ----------------------------------
                # Remaining New Lines
                # ----------------------------------

                if len(new_block) > pair_count:

                    added.extend(
                        new_block[pair_count:]
                    )

        return ArchiveDiff(

            article_id=article_id,

            from_version=from_version,

            to_version=to_version,

            added=added,

            removed=removed,

            changed=changed
        )

    # ==================================
    # Compare Text
    # ==================================

    @staticmethod
    def compare_text(
        old_content,
        new_content
    ):
        """
        簡化版文字比較。

        只回傳 ArchiveDiff。
        """

        return VersionDiff.compare(
            old_content,
            new_content
        )

    # ==================================
    # Has Difference
    # ==================================

    @staticmethod
    def has_difference(
        old_content,
        new_content
    ):
        """
        判斷兩個版本是否有差異。
        """

        old_content = (
            old_content
            if old_content is not None
            else ""
        )

        new_content = (
            new_content
            if new_content is not None
            else ""
        )

        return old_content != new_content

    # ==================================
    # Get Added
    # ==================================

    @staticmethod
    def get_added(
        old_content,
        new_content
    ):
        """
        取得新增內容。
        """

        diff = VersionDiff.compare(
            old_content,
            new_content
        )

        return diff.added

    # ==================================
    # Get Removed
    # ==================================

    @staticmethod
    def get_removed(
        old_content,
        new_content
    ):
        """
        取得刪除內容。
        """

        diff = VersionDiff.compare(
            old_content,
            new_content
        )

        return diff.removed

    # ==================================
    # Get Changed
    # ==================================

    @staticmethod
    def get_changed(
        old_content,
        new_content
    ):
        """
        取得修改內容。
        """

        diff = VersionDiff.compare(
            old_content,
            new_content
        )

        return diff.changed

    # ==================================
    # Summary
    # ==================================

    @staticmethod
    def summary(
        old_content,
        new_content
    ):
        """
        直接取得 Diff Summary。
        """

        diff = VersionDiff.compare(
            old_content,
            new_content
        )

        return diff.summary()