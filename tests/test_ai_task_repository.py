"""
tests/test_ai_task_repository.py

AutoSearch V4

P2.4.1

Test:

AITaskRepository

測試:

1. Insert Task
2. Get Waiting Tasks
3. Find Task By ID
4. Update Status
5. Claim Task
6. Claim Waiting Tasks
7. Mark Running
8. Mark Done
9. Mark Failed
"""

from unittest.mock import MagicMock, patch

from database.ai_task_repository import AITaskRepository

from models.ai_task import AITask


# ==================================
# Mock Task
# ==================================

def create_task():

    return AITask(

        article_id=100,

        task_type="AI_ANALYSIS",

        status="WAITING",

        priority=10,

        retry_count=0

    )


# ==================================
# Test Insert
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_insert_task(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    cursor.lastrowid = 1

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    task = create_task()

    result = repo.insert(
        task
    )

    assert result.id == 1

    cursor.execute.assert_called_once()

    conn.commit.assert_called_once()


# ==================================
# Test Get Waiting Tasks
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_get_waiting_tasks(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    cursor.fetchall.return_value = [

        {
            "id": 1,
            "article_id": 100,
            "task_type": "AI_ANALYSIS",
            "status": "WAITING",
            "priority": 10,
            "retry_count": 0,
            "created_time": None,
            "finished_time": None
        }

    ]

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    tasks = repo.get_waiting_tasks()

    assert len(tasks) == 1

    assert tasks[0].article_id == 100

    assert tasks[0].status == "WAITING"


# ==================================
# Test Find By ID
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_find_task_by_id(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    cursor.fetchone.return_value = {

        "id": 1,
        "article_id": 100,
        "task_type": "AI_ANALYSIS",
        "status": "RUNNING",
        "priority": 10,
        "retry_count": 0,
        "created_time": None,
        "finished_time": None

    }

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    task = repo.find_by_id(
        1
    )

    assert task is not None

    assert task.id == 1

    assert task.status == "RUNNING"


# ==================================
# Test Update Status
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_update_status(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    # MySQL UPDATE 成功時
    # rowcount 應為整數

    cursor.rowcount = 1

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    result = repo.update_status(

        1,

        "RUNNING"

    )

    assert result is True

    cursor.execute.assert_called_once()

    conn.commit.assert_called_once()


# ==================================
# Test Claim Task Success
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_claim_task_success(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    # UPDATE WAITING -> RUNNING 成功

    cursor.rowcount = 1

    # Claim 成功後重新查詢 Task

    cursor.fetchone.return_value = {

        "id": 1,
        "article_id": 100,
        "task_type": "AI_ANALYSIS",
        "status": "RUNNING",
        "priority": 10,
        "retry_count": 0,
        "created_time": None,
        "finished_time": None

    }

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    task = repo.claim_task(
        1
    )

    assert task is not None

    assert task.id == 1

    assert task.status == "RUNNING"

    cursor.execute.assert_called()

    conn.commit.assert_called_once()


# ==================================
# Test Claim Task Failed
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_claim_task_failed(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    # UPDATE 失敗
    #
    # 代表:
    #
    # Task 不存在
    # 或
    # Task 已經不是 WAITING

    cursor.rowcount = 0

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    task = repo.claim_task(
        1
    )

    assert task is None

    cursor.execute.assert_called_once()

    conn.commit.assert_called_once()


# ==================================
# Test Claim Waiting Tasks
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_claim_waiting_tasks(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    # ------------------------------------------------
    # 第一次:
    #
    # get_waiting_tasks()
    #
    # 回傳兩個 WAITING Tasks
    # ------------------------------------------------

    cursor.fetchall.return_value = [

        {
            "id": 1,
            "article_id": 100,
            "task_type": "AI_ANALYSIS",
            "status": "WAITING",
            "priority": 10,
            "retry_count": 0,
            "created_time": None,
            "finished_time": None
        },

        {
            "id": 2,
            "article_id": 101,
            "task_type": "AI_ANALYSIS",
            "status": "WAITING",
            "priority": 5,
            "retry_count": 0,
            "created_time": None,
            "finished_time": None
        }

    ]

    # ------------------------------------------------
    # claim_task()
    #
    # 每一次 UPDATE 都成功
    # ------------------------------------------------

    cursor.rowcount = 1

    # find_by_id()
    # 依序回傳兩個 RUNNING Tasks

    cursor.fetchone.side_effect = [

        {
            "id": 1,
            "article_id": 100,
            "task_type": "AI_ANALYSIS",
            "status": "RUNNING",
            "priority": 10,
            "retry_count": 0,
            "created_time": None,
            "finished_time": None
        },

        {
            "id": 2,
            "article_id": 101,
            "task_type": "AI_ANALYSIS",
            "status": "RUNNING",
            "priority": 5,
            "retry_count": 0,
            "created_time": None,
            "finished_time": None
        }

    ]

    tasks = repo.claim_waiting_tasks(
        limit=2
    )

    assert len(tasks) == 2

    assert tasks[0].id == 1

    assert tasks[0].status == "RUNNING"

    assert tasks[1].id == 2

    assert tasks[1].status == "RUNNING"


# ==================================
# Test Mark Running
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_mark_running(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    # Claim 成功

    cursor.rowcount = 1

    # claim 成功後 find_by_id()

    cursor.fetchone.return_value = {

        "id": 1,
        "article_id": 100,
        "task_type": "AI_ANALYSIS",
        "status": "RUNNING",
        "priority": 10,
        "retry_count": 0,
        "created_time": None,
        "finished_time": None

    }

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    result = repo.mark_running(
        1
    )

    assert result is True

    cursor.execute.assert_called_once()

    conn.commit.assert_called_once()


# ==================================
# Test Mark Done
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_mark_done(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    # MySQL UPDATE 成功

    cursor.rowcount = 1

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    result = repo.mark_done(
        1
    )

    assert result is True

    cursor.execute.assert_called_once()

    conn.commit.assert_called_once()


# ==================================
# Test Mark Running
# ==================================

@patch(
    "database.ai_task_repository.get_connection"
)
def test_mark_running(
    mock_connection
):

    conn = MagicMock()

    cursor = MagicMock()

    # ----------------------------------
    # Claim 成功
    # ----------------------------------

    cursor.rowcount = 1

    # ----------------------------------
    # claim_task() 成功後
    # find_by_id() 取得 RUNNING Task
    # ----------------------------------

    cursor.fetchone.return_value = {

        "id": 1,

        "article_id": 100,

        "task_type": "AI_ANALYSIS",

        "status": "RUNNING",

        "priority": 10,

        "retry_count": 0,

        "created_time": None,

        "finished_time": None

    }

    conn.cursor.return_value = cursor

    mock_connection.return_value = conn

    repo = AITaskRepository()

    # ----------------------------------
    # Execute
    # ----------------------------------

    result = repo.mark_running(
        1
    )

    # ----------------------------------
    # Assert
    # ----------------------------------

    assert result is True

    # mark_running()
    #
    # 1. UPDATE WAITING -> RUNNING
    # 2. SELECT latest Task
    #
    assert cursor.execute.call_count == 2

    conn.commit.assert_called_once()

    # ----------------------------------
    # 確認第一次 SQL 是 Claim
    # ----------------------------------

    first_call = (
        cursor.execute.call_args_list[0]
    )

    sql = first_call.args[0]

    assert "UPDATE ai_tasks" in sql

    assert "status='RUNNING'" in sql

    assert "status='WAITING'" in sql

    # ----------------------------------
    # 確認第二次 SQL 是 Find By ID
    # ----------------------------------

    second_call = (
        cursor.execute.call_args_list[1]
    )

    sql = second_call.args[0]

    assert "SELECT *" in sql

    assert "FROM ai_tasks" in sql

    assert "WHERE id=%s" in sql
