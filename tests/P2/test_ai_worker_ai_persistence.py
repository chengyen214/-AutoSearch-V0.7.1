"""
tests/P2/test_ai_worker_ai_persistence.py

AutoSearch V4

P2

驗證：

    AIWorker
        |
        v
    AIAnalysisService
        |
        v
    AIAnalysis
        |
        v
    ArticleRepository.update_ai_analysis()
        |
        v
    Article AI 欄位持久化流程

本測試不呼叫真正 Groq。

目的：

1. WAITING AI Task 可以進入 Worker
2. Worker 可以取得 Article
3. AIAnalysisService 可以產生 AIAnalysis
4. Worker 將 AIAnalysis 放入 Article
5. Worker 呼叫 update_ai_analysis()
6. Article AI status 最終為 completed
7. AI Task 最終為 DONE

注意：

    test_ai_analysis_persistence.py

已負責驗證：

    AIAnalysis
        ->
    ArticleRepository
        ->
    Database

本測試負責驗證：

    AIWorker
        ->
    AIAnalysisService
        ->
    ArticleRepository.update_ai_analysis()

因此兩支測試合起來即可確認：

    AI Worker
        ->
    AI Analysis
        ->
    Article AI 欄位
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

from ai.worker import AIWorker
from models.ai_analysis import AIAnalysis


def test_ai_worker_ai_persistence(monkeypatch):
    """
    驗證 AIWorker 完成 AI Analysis 後：

        1. Article 收到 AIAnalysis
        2. update_ai_analysis() 被呼叫
        3. AI status = completed
        4. AI Task = DONE

    不呼叫真正 LLM。
    """

    # ==================================================
    # Mock Article
    # ==================================================

    article = SimpleNamespace(
        id=1001,
        document_id="TEST-WORKER-AI-1001",
        title="Test Semiconductor Article",
        source="Test Source",
        content=(
            "This is a test article about "
            "semiconductor technology."
        ),
        ai_analysis=None,
        ai_status="pending",
    )

    # ==================================================
    # Mock AI Task
    # ==================================================

    task = SimpleNamespace(
        id=2001,
        article_id=article.id,
        task_type="AI_ANALYSIS",
        status="WAITING",
        priority=0,
        retry_count=0,
    )

    # ==================================================
    # Fake AI Analysis
    # ==================================================

    analysis = AIAnalysis(
        article_id=article.id,
        summary="測試文章摘要",
        category="半導體",
        keywords=[
            "semiconductor",
            "AI",
            "chip"
        ],
        entities=[
            "Test Semiconductor"
        ],
        relations=[
            "AI -> Semiconductor"
        ],
        importance=8,
        ai_model="test-model",
        ai_version="4.0",
        confidence=0.95,
        status="completed",
    )

    # ==================================================
    # Mock ArticleRepository
    # ==================================================

    article_repository = MagicMock()

    article_repository.find_model_by_id.return_value = (
        article
    )

    def update_ai_status(
        article_id,
        status
    ):
        """
        模擬 Article AI Status 更新。
        """

        article.ai_status = status

        return True

    article_repository.update_ai_status.side_effect = (
        update_ai_status
    )

    def update_ai_analysis(
        updated_article
    ):
        """
        模擬 AI Analysis persistence。

        Worker 必須先：

            article.ai_analysis = analysis

        然後：

            update_ai_analysis(article)
        """

        assert updated_article is article

        assert updated_article.ai_analysis is analysis

        assert (
            updated_article.ai_analysis.article_id
            == article.id
        )

        assert (
            updated_article.ai_analysis.summary
            == "測試文章摘要"
        )

        assert (
            updated_article.ai_analysis.category
            == "半導體"
        )

        assert (
            updated_article.ai_analysis.importance
            == 8
        )

        assert (
            updated_article.ai_analysis.status
            == "completed"
        )

        return True

    article_repository.update_ai_analysis.side_effect = (
        update_ai_analysis
    )

    # ==================================================
    # Mock AITaskRepository
    # ==================================================

    task_repository = MagicMock()

    def mark_running(
        task_id
    ):
        """
        WAITING -> RUNNING
        """

        assert task_id == task.id

        task.status = "RUNNING"

        return True

    task_repository.mark_running.side_effect = (
        mark_running
    )

    def mark_done(
        task_id
    ):
        """
        RUNNING -> DONE
        """

        assert task_id == task.id

        task.status = "DONE"

        return True

    task_repository.mark_done.side_effect = (
        mark_done
    )

    # ==================================================
    # Mock AIAnalysisService
    # ==================================================

    ai_service = MagicMock()

    ai_service.analyze.return_value = (
        analysis
    )

    # ==================================================
    # Mock KnowledgeService
    #
    # 本測試不測 Knowledge Pipeline。
    # 只讓 Worker 可以正常完成。
    # ==================================================

    knowledge = SimpleNamespace(
        id=3001,
        article_id=article.id,
        topic="半導體",
        entities=analysis.entities,
        relations=analysis.relations,
    )

    knowledge_service = MagicMock()

    knowledge_service.create_with_index.return_value = (
        knowledge
    )

    # ==================================================
    # Mock KnowledgeIntelligenceService
    # ==================================================

    knowledge_intelligence = MagicMock()

    # ==================================================
    # 建立 Worker
    #
    # Worker __init__ 會自行建立 Repository / Service，
    # 因此直接替換 instance dependencies。
    # ==================================================

    worker = AIWorker()

    worker.article_repository = (
        article_repository
    )

    worker.task_repository = (
        task_repository
    )

    worker.ai_service = (
        ai_service
    )

    worker.knowledge_service = (
        knowledge_service
    )

    worker.knowledge_intelligence = (
        knowledge_intelligence
    )

    # ==================================================
    # Execute
    # ==================================================

    result = worker.process_task(
        task
    )

    # ==================================================
    # Worker Result
    # ==================================================

    assert result is True

    # ==================================================
    # Task State
    # ==================================================

    assert task.status == "DONE"

    task_repository.mark_running.assert_called_once_with(
        task.id
    )

    task_repository.mark_done.assert_called_once_with(
        task.id
    )

    # ==================================================
    # AI Service
    # ==================================================

    ai_service.analyze.assert_called_once_with(
        article
    )

    # ==================================================
    # Article AI Result
    # ==================================================

    assert article.ai_analysis is analysis

    assert (
        article.ai_analysis.article_id
        == article.id
    )

    assert (
        article.ai_analysis.summary
        == "測試文章摘要"
    )

    assert (
        article.ai_analysis.category
        == "半導體"
    )

    assert (
        article.ai_analysis.keywords
        == [
            "semiconductor",
            "AI",
            "chip"
        ]
    )

    assert (
        article.ai_analysis.entities
        == [
            "Test Semiconductor"
        ]
    )

    assert (
        article.ai_analysis.relations
        == [
            "AI -> Semiconductor"
        ]
    )

    assert (
        article.ai_analysis.importance
        == 8
    )

    assert (
        article.ai_analysis.confidence
        == 0.95
    )

    assert (
        article.ai_analysis.status
        == "completed"
    )

    # ==================================================
    # Persistence
    # ==================================================

    article_repository.update_ai_analysis.assert_called_once_with(
        article
    )

    # ==================================================
    # Article Status
    # ==================================================

    assert article.ai_status == "completed"

    article_repository.update_ai_status.assert_any_call(
        article.id,
        "processing"
    )

    article_repository.update_ai_status.assert_any_call(
        article.id,
        "completed"
    )

    # ==================================================
    # Knowledge Pipeline was reached
    # ==================================================

    knowledge_service.create_with_index.assert_called_once()

    knowledge_intelligence.analyze_knowledge.assert_called_once_with(
        knowledge,
        analysis
    )