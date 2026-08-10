"""
models/archive_diff.py

AutoSearch V4

P2.3.4 Version Comparison / Diff

用途:

    表示兩個 Archive Version 之間的差異。

負責:

    1. 儲存版本比較資訊
    2. 儲存新增內容
    3. 儲存刪除內容
    4. 儲存修改內容
    5. 提供 Diff Summary

注意:

    本 Model 不負責實際 Diff 計算。

    Diff 計算由:

        archive/version_diff.py

    負責。
"""


class ArchiveDiff:

    """
    Archive Version Diff Model
    """

    def __init__(
        self,
        article_id=None,
        from_version=None,
        to_version=None,
        added=None,
        removed=None,
        changed=None
    ):

        # ==================================
        # Article
        # ==================================

        self.article_id = article_id

        # ==================================
        # Compared Versions
        # ==================================

        self.from_version = from_version

        self.to_version = to_version

        # ==================================
        # Diff Content
        # ==================================

        self.added = (
            added
            if added is not None
            else []
        )

        self.removed = (
            removed
            if removed is not None
            else []
        )

        self.changed = (
            changed
            if changed is not None
            else []
        )

    # ==================================
    # Added Count
    # ==================================

    @property
    def added_count(self):

        return len(self.added)

    # ==================================
    # Removed Count
    # ==================================

    @property
    def removed_count(self):

        return len(self.removed)

    # ==================================
    # Changed Count
    # ==================================

    @property
    def changed_count(self):

        return len(self.changed)

    # ==================================
    # Total Changes
    # ==================================

    @property
    def total_changes(self):

        return (
            self.added_count
            + self.removed_count
            + self.changed_count
        )

    # ==================================
    # Has Changes
    # ==================================

    @property
    def has_changes(self):

        return self.total_changes > 0

    # ==================================
    # Summary
    # ==================================

    def summary(self):

        return {
            "article_id": self.article_id,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "added_count": self.added_count,
            "removed_count": self.removed_count,
            "changed_count": self.changed_count,
            "total_changes": self.total_changes
        }

    # ==================================
    # To Dictionary
    # ==================================

    def to_dict(self):

        return {
            "article_id": self.article_id,
            "from_version": self.from_version,
            "to_version": self.to_version,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "added_count": self.added_count,
            "removed_count": self.removed_count,
            "changed_count": self.changed_count,
            "total_changes": self.total_changes
        }

    # ==================================
    # String
    # ==================================

    def __repr__(self):

        return (
            "ArchiveDiff("
            f"article_id={self.article_id}, "
            f"from_version={self.from_version}, "
            f"to_version={self.to_version}, "
            f"added={self.added_count}, "
            f"removed={self.removed_count}, "
            f"changed={self.changed_count}"
            ")"
        )