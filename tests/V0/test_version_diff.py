"""
tests/test_version_diff.py

AutoSearch V4

P2.3.4 Version Comparison / Diff

測試:

    archive/version_diff.py

測試範圍:

    1. 完全相同內容
    2. 新增內容
    3. 刪除內容
    4. 修改內容
    5. 多種變更
    6. None Content
    7. Article / Version Metadata
    8. has_difference
    9. get_added
    10. get_removed
    11. get_changed
    12. summary
"""


from archive.version_diff import VersionDiff


# ==================================
# Same Content
# ==================================

def test_same_content():

    content = """\
台積電推出新製程
AI 晶片需求增加
"""

    diff = VersionDiff.compare(
        content,
        content
    )

    assert diff.added == []

    assert diff.removed == []

    assert diff.changed == []

    assert diff.total_changes == 0

    assert diff.has_changes is False


# ==================================
# Added Content
# ==================================

def test_added_content():

    old_content = """\
台積電推出新製程
"""

    new_content = """\
台積電推出新製程
AI 晶片需求增加
"""

    diff = VersionDiff.compare(
        old_content,
        new_content
    )

    assert "AI 晶片需求增加" in diff.added

    assert diff.removed == []

    assert diff.changed == []

    assert diff.has_changes is True


# ==================================
# Removed Content
# ==================================

def test_removed_content():

    old_content = """\
台積電推出新製程
AI 晶片需求增加
"""

    new_content = """\
台積電推出新製程
"""

    diff = VersionDiff.compare(
        old_content,
        new_content
    )

    assert "AI 晶片需求增加" in diff.removed

    assert diff.added == []

    assert diff.changed == []

    assert diff.has_changes is True


# ==================================
# Changed Content
# ==================================

def test_changed_content():

    old_content = """\
台積電推出新製程
AI 晶片需求增加
"""

    new_content = """\
台積電推出2nm新製程
AI 晶片需求大幅增加
"""

    diff = VersionDiff.compare(
        old_content,
        new_content
    )

    assert len(diff.changed) == 2

    assert diff.changed[0]["old"] == [
        "台積電推出新製程"
    ]

    assert diff.changed[0]["new"] == [
        "台積電推出2nm新製程"
    ]

    assert diff.changed[1]["old"] == [
        "AI 晶片需求增加"
    ]

    assert diff.changed[1]["new"] == [
        "AI 晶片需求大幅增加"
    ]


# ==================================
# Multiple Changes
# ==================================

def test_multiple_changes():

    old_content = """\
第一行
第二行
第三行
第四行
"""

    new_content = """\
第一行
第二行修改
第三行
新增第五行
"""

    diff = VersionDiff.compare(
        old_content,
        new_content
    )

    assert diff.has_changes is True

    assert diff.total_changes > 0


# ==================================
# None Content
# ==================================

def test_none_content():

    diff = VersionDiff.compare(
        None,
        None
    )

    assert diff.added == []

    assert diff.removed == []

    assert diff.changed == []

    assert diff.has_changes is False


# ==================================
# Empty To Content
# ==================================

def test_empty_to_content():

    old_content = """\
第一行
第二行
"""

    new_content = ""

    diff = VersionDiff.compare(
        old_content,
        new_content
    )

    assert diff.added == []

    assert diff.removed == [
        "第一行",
        "第二行"
    ]

    assert diff.has_changes is True


# ==================================
# Empty From Content
# ==================================

def test_empty_from_content():

    old_content = ""

    new_content = """\
第一行
第二行
"""

    diff = VersionDiff.compare(
        old_content,
        new_content
    )

    assert diff.added == [
        "第一行",
        "第二行"
    ]

    assert diff.removed == []

    assert diff.has_changes is True


# ==================================
# Metadata
# ==================================

def test_version_metadata():

    old_content = """\
Version 1
"""

    new_content = """\
Version 2
"""

    diff = VersionDiff.compare(
        old_content,
        new_content,
        article_id=100,
        from_version=1,
        to_version=2
    )

    assert diff.article_id == 100

    assert diff.from_version == 1

    assert diff.to_version == 2


# ==================================
# Has Difference
# ==================================

def test_has_difference():

    old_content = "原始內容"

    new_content = "修改後內容"

    assert VersionDiff.has_difference(
        old_content,
        new_content
    ) is True


# ==================================
# No Difference
# ==================================

def test_no_difference():

    content = "相同內容"

    assert VersionDiff.has_difference(
        content,
        content
    ) is False


# ==================================
# Get Added
# ==================================

def test_get_added():

    old_content = """\
第一行
"""

    new_content = """\
第一行
新增第二行
"""

    added = VersionDiff.get_added(
        old_content,
        new_content
    )

    assert added == [
        "新增第二行"
    ]


# ==================================
# Get Removed
# ==================================

def test_get_removed():

    old_content = """\
第一行
刪除第二行
"""

    new_content = """\
第一行
"""

    removed = VersionDiff.get_removed(
        old_content,
        new_content
    )

    assert removed == [
        "刪除第二行"
    ]


# ==================================
# Get Changed
# ==================================

def test_get_changed():

    old_content = """\
舊版本內容
"""

    new_content = """\
新版本內容
"""

    changed = VersionDiff.get_changed(
        old_content,
        new_content
    )

    assert len(changed) == 1

    assert changed[0]["old"] == [
        "舊版本內容"
    ]

    assert changed[0]["new"] == [
        "新版本內容"
    ]


# ==================================
# Summary
# ==================================

def test_summary():

    old_content = """\
第一行
第二行
"""

    new_content = """\
第一行修改
第二行
第三行
"""

    summary = VersionDiff.summary(
        old_content,
        new_content
    )

    assert "added_count" in summary

    assert "removed_count" in summary

    assert "changed_count" in summary

    assert "total_changes" in summary

    assert summary["total_changes"] >= 1