"""
utils/show_project_tree.py

AutoSearch V4

用途：
    顯示目前專案的相對檔案路徑，
    方便在進入下一個開發階段前確認完整專案結構。

排除：
    test/
    tests/
    __pycache__/
    .git/
    .venv/
    venv/
    archive/html/

執行：
    python -m utils.show_project_tree
"""

from pathlib import Path


# ---------------------------------------------------------
# Project Root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------
# Excluded Directories
# ---------------------------------------------------------

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    "test",
    "tests",
}


# ---------------------------------------------------------
# Excluded Directory Paths
# ---------------------------------------------------------

EXCLUDED_PATHS = {
    Path("archive/html"),
}


# ---------------------------------------------------------
# Excluded Files
# ---------------------------------------------------------

EXCLUDED_FILES = {
    ".gitignore",
}


# ---------------------------------------------------------
# Included File Extensions
# ---------------------------------------------------------

INCLUDED_EXTENSIONS = {
    ".py",
    ".sql",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
}


# ---------------------------------------------------------
# Should Exclude
# ---------------------------------------------------------

def should_exclude(path: Path) -> bool:
    """
    判斷檔案或資料夾是否需要排除。
    """

    # 一般排除資料夾
    for part in path.parts:
        if part in EXCLUDED_DIRS:
            return True

    # 特定路徑排除，例如 archive/html
    for excluded_path in EXCLUDED_PATHS:
        if (
            path == excluded_path
            or excluded_path in path.parents
        ):
            return True

    return False


# ---------------------------------------------------------
# Should Include File
# ---------------------------------------------------------

def should_include_file(path: Path) -> bool:
    """
    判斷檔案是否屬於需要顯示的專案檔案。
    """

    if path.name in EXCLUDED_FILES:
        return False

    # Dockerfile
    if path.name.lower() == "dockerfile":
        return True

    # .env / .env.example
    if path.name.startswith(".env"):
        return True

    # 副檔名
    if path.suffix.lower() in INCLUDED_EXTENSIONS:
        return True

    return False


# ---------------------------------------------------------
# Print Project Tree
# ---------------------------------------------------------

def print_project_tree():
    """
    顯示 AutoSearch V4 專案結構。
    """

    print("=" * 70)
    print("AutoSearch V4 Project Structure")
    print("=" * 70)

    print(f"Project Root: {PROJECT_ROOT}")
    print()

    files = []

    for path in PROJECT_ROOT.rglob("*"):

        relative_path = path.relative_to(PROJECT_ROOT)

        if should_exclude(relative_path):
            continue

        if path.is_file() and should_include_file(path):
            files.append(relative_path)

    for relative_path in sorted(files):
        print(relative_path)

    print()
    print("=" * 70)
    print(f"Total Files: {len(files)}")
    print("=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    print_project_tree()