"""
tests/V7_4/test_rag_chroma_client.py

AutoSearch V7

RAG-4.2

ChromaDB Client Test

驗證：

    1. ChromaDB Client initialization
    2. Persistent Client creation
    3. Persist Directory
    4. Client retrieval
    5. Custom Persist Directory
    6. Invalid Persist Directory validation
    7. ChromaDB Client API availability
    8. Persistent Storage Directory

本測試不負責：

    1. Collection
    2. Index
    3. MySQL
    4. Embedding
"""


import gc
import shutil
import tempfile
from pathlib import Path

import chromadb

from rag.chroma.client import (
    ChromaDBClient
)

from rag.chroma.config import (
    CHROMA_PERSIST_DIRECTORY
)


# ============================================================
# Shared Client
# ============================================================

_CLIENT = None


def create_client():
    """
    建立共用 ChromaDB Client。
    """

    global _CLIENT

    if _CLIENT is None:
        _CLIENT = ChromaDBClient()

    return _CLIENT


# ============================================================
# Cleanup Temporary Directory
# ============================================================

def cleanup_temp_directory(
    temp_dir
):
    """
    清除 Temporary ChromaDB Directory。

    Windows 可能因 SQLite / Chroma
    尚未立即釋放檔案而發生 WinError 32。

    因此：

        1. gc.collect()
        2. shutil.rmtree()
    """

    gc.collect()

    try:
        shutil.rmtree(
            temp_dir
        )

    except PermissionError:
        gc.collect()

        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )


# ============================================================
# Test 1
# ============================================================

def test_client_initialization():
    """
    驗證 ChromaDB Client 初始化。
    """

    client = create_client()

    assert isinstance(
        client,
        ChromaDBClient
    )

    print(
        "PASS: ChromaDB Client initialization"
    )


# ============================================================
# Test 2
# ============================================================

def test_persistent_client():
    """
    驗證底層 Client 已成功建立。

    ChromaDB PersistentClient
    在目前版本不是 isinstance type，
    因此驗證實際 Client API。
    """

    client = create_client()

    chroma_client = (
        client.get_client()
    )

    assert chroma_client is not None

    assert hasattr(
        chroma_client,
        "get_or_create_collection"
    )

    assert hasattr(
        chroma_client,
        "get_collection"
    )

    assert hasattr(
        chroma_client,
        "list_collections"
    )

    print(
        "PASS: Persistent ChromaDB Client"
    )

    print(
        f"      Client type: "
        f"{type(chroma_client).__name__}"
    )


# ============================================================
# Test 3
# ============================================================

def test_persist_directory():
    """
    驗證 Persist Directory。
    """

    client = create_client()

    persist_directory = (
        client.get_persist_directory()
    )

    assert isinstance(
        persist_directory,
        str
    )

    assert (
        persist_directory
        == CHROMA_PERSIST_DIRECTORY
    )

    assert persist_directory

    print(
        "PASS: Persist Directory"
    )

    print(
        f"      Directory: "
        f"{persist_directory}"
    )


# ============================================================
# Test 4
# ============================================================

def test_client_retrieval():
    """
    驗證 get_client() 可以取得
    ChromaDB Client。
    """

    client = create_client()

    chroma_client = (
        client.get_client()
    )

    assert (
        chroma_client
        is not None
    )

    assert hasattr(
        chroma_client,
        "get_or_create_collection"
    )

    print(
        "PASS: ChromaDB Client retrieval"
    )


# ============================================================
# Test 5
# ============================================================

def test_custom_persist_directory():
    """
    驗證可以注入自訂 Persist Directory。

    Windows 環境下不使用
    TemporaryDirectory() context manager，
    避免 SQLite 檔案尚未釋放時
    cleanup 發生 WinError 32。
    """

    temp_dir = tempfile.mkdtemp()

    client = None

    try:

        client = ChromaDBClient(
            persist_directory=temp_dir
        )

        assert (
            client.get_persist_directory()
            == str(Path(temp_dir))
        )

        chroma_client = (
            client.get_client()
        )

        assert (
            chroma_client
            is not None
        )

        assert hasattr(
            chroma_client,
            "get_or_create_collection"
        )

    finally:

        # ----------------------------------------------
        # Release Chroma Client
        # ----------------------------------------------

        client = None

        gc.collect()

        # ----------------------------------------------
        # Cleanup
        # ----------------------------------------------

        cleanup_temp_directory(
            temp_dir
        )

    print(
        "PASS: Custom Persist Directory"
    )


# ============================================================
# Test 6
# ============================================================

def test_none_persist_directory():
    """
    None 不應觸發錯誤。

    None 的意義是：

        使用 RAG-4.1 Configuration。
    """

    client = ChromaDBClient(
        persist_directory=None
    )

    assert (
        client.get_persist_directory()
        == CHROMA_PERSIST_DIRECTORY
    )

    assert (
        client.get_client()
        is not None
    )

    print(
        "PASS: None Persist Directory fallback"
    )


# ============================================================
# Test 7
# ============================================================

def test_empty_persist_directory():
    """
    空 Persist Directory 必須拒絕。
    """

    try:

        ChromaDBClient(
            persist_directory="   "
        )

    except ValueError:

        print(
            "PASS: Empty Persist Directory validation"
        )

        return

    raise AssertionError(
        "Empty Persist Directory "
        "should raise ValueError."
    )


# ============================================================
# Test 8
# ============================================================

def test_client_is_persistent():
    """
    驗證 Client 使用指定的
    Persistent Storage Directory。
    """

    temp_dir = tempfile.mkdtemp()

    client = None

    try:

        client = ChromaDBClient(
            persist_directory=temp_dir
        )

        chroma_client = (
            client.get_client()
        )

        assert (
            chroma_client
            is not None
        )

        assert (
            client.get_persist_directory()
            == temp_dir
        )

        assert hasattr(
            chroma_client,
            "get_or_create_collection"
        )

    finally:

        client = None

        gc.collect()

        cleanup_temp_directory(
            temp_dir
        )

    print(
        "PASS: Persistent client mode"
    )


# ============================================================
# Test 9
# ============================================================

def test_client_api():
    """
    驗證目前 RAG-4.2 Client
    已具備後續 RAG-4.3 所需的基本 API。
    """

    client = create_client()

    chroma_client = (
        client.get_client()
    )

    required_methods = [
        "get_or_create_collection",
        "get_collection",
        "list_collections",
        "delete_collection",
    ]

    for method_name in required_methods:

        assert hasattr(
            chroma_client,
            method_name
        ), (
            f"ChromaDB Client missing "
            f"required method: {method_name}"
        )

    print(
        "PASS: ChromaDB Client API"
    )


# ============================================================
# Main
# ============================================================

def main():
    """
    執行 RAG-4.2 ChromaDB Client Test。
    """

    print("=" * 60)

    print(
        "RAG-4.2 ChromaDB Client Test"
    )

    print("=" * 60)

    print()

    test_client_initialization()

    test_persistent_client()

    test_persist_directory()

    test_client_retrieval()

    test_custom_persist_directory()

    test_none_persist_directory()

    test_empty_persist_directory()

    test_client_is_persistent()

    test_client_api()

    print()

    print("=" * 60)

    print(
        "ALL RAG-4.2 CHROMADB CLIENT TESTS PASSED"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()