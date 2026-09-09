"""
tests/test_archive_diff.py

AutoSearch V4

P2.3.4 Version Comparison / Diff

測試:

    models/archive_diff.py

測試範圍:

    1. 建立 ArchiveDiff
    2. 預設值
    3. Added Count
    4. Removed Count
    5. Changed Count
    6. Total Changes
    7. Has Changes
    8. Summary
    9. To Dictionary
    10. Representation
"""


from models.archive_diff import ArchiveDiff


# ==================================
# Create
# ==================================

def test_create_archive_diff():

    diff = ArchiveDiff(
        article_id=1,
        from_version=1,
        to_version=2,
        added=[
            "新增內容"
        ],
        removed=[
            "刪除內容"
        ],
        changed=[
            "修改內容"
        ]
    )

    assert diff.article_id == 1

    assert diff.from_version == 1

    assert diff.to_version == 2

    assert diff.added == [
        "新增內容"
    ]

    assert diff.removed == [
        "刪除內容"
    ]

    assert diff.changed == [
        "修改內容"
    ]


# ==================================
# Default Values
# ==================================

def test_default_values():

    diff = ArchiveDiff()

    assert diff.article_id is None

    assert diff.from_version is None

    assert diff.to_version is None

    assert diff.added == []

    assert diff.removed == []

    assert diff.changed == []


# ==================================
# Added Count
# ==================================

def test_added_count():

    diff = ArchiveDiff(
        added=[
            "A",
            "B",
            "C"
        ]
    )

    assert diff.added_count == 3


# ==================================
# Removed Count
# ==================================

def test_removed_count():

    diff = ArchiveDiff(
        removed=[
            "A",
            "B"
        ]
    )

    assert diff.removed_count == 2


# ==================================
# Changed Count
# ==================================

def test_changed_count():

    diff = ArchiveDiff(
        changed=[
            "A",
            "B",
            "C",
            "D"
        ]
    )

    assert diff.changed_count == 4


# ==================================
# Total Changes
# ==================================

def test_total_changes():

    diff = ArchiveDiff(
        added=[
            "A",
            "B"
        ],
        removed=[
            "C"
        ],
        changed=[
            "D",
            "E"
        ]
    )

    assert diff.total_changes == 5


# ==================================
# Has Changes
# ==================================

def test_has_changes():

    diff = ArchiveDiff(
        added=[
            "新增內容"
        ]
    )

    assert diff.has_changes is True


# ==================================
# No Changes
# ==================================

def test_no_changes():

    diff = ArchiveDiff()

    assert diff.has_changes is False

    assert diff.total_changes == 0


# ==================================
# Summary
# ==================================

def test_summary():

    diff = ArchiveDiff(
        article_id=10,
        from_version=2,
        to_version=3,
        added=[
            "A",
            "B"
        ],
        removed=[
            "C"
        ],
        changed=[
            "D"
        ]
    )

    summary = diff.summary()

    assert summary["article_id"] == 10

    assert summary["from_version"] == 2

    assert summary["to_version"] == 3

    assert summary["added_count"] == 2

    assert summary["removed_count"] == 1

    assert summary["changed_count"] == 1

    assert summary["total_changes"] == 4


# ==================================
# To Dictionary
# ==================================

def test_to_dict():

    diff = ArchiveDiff(
        article_id=5,
        from_version=1,
        to_version=2,
        added=[
            "新增"
        ],
        removed=[
            "刪除"
        ],
        changed=[
            "修改"
        ]
    )

    data = diff.to_dict()

    assert data["article_id"] == 5

    assert data["from_version"] == 1

    assert data["to_version"] == 2

    assert data["added"] == [
        "新增"
    ]

    assert data["removed"] == [
        "刪除"
    ]

    assert data["changed"] == [
        "修改"
    ]

    assert data["added_count"] == 1

    assert data["removed_count"] == 1

    assert data["changed_count"] == 1

    assert data["total_changes"] == 3


# ==================================
# Empty Lists
# ==================================

def test_empty_lists():

    diff = ArchiveDiff(
        added=[],
        removed=[],
        changed=[]
    )

    assert diff.added_count == 0

    assert diff.removed_count == 0

    assert diff.changed_count == 0

    assert diff.total_changes == 0

    assert diff.has_changes is False


# ==================================
# Representation
# ==================================

def test_repr():

    diff = ArchiveDiff(
        article_id=1,
        from_version=1,
        to_version=2,
        added=[
            "A",
            "B"
        ],
        removed=[
            "C"
        ],
        changed=[
            "D",
            "E",
            "F"
        ]
    )

    result = repr(diff)

    assert "ArchiveDiff" in result

    assert "article_id=1" in result

    assert "from_version=1" in result

    assert "to_version=2" in result

    assert "added=2" in result

    assert "removed=1" in result

    assert "changed=3" in result