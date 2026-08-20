/*
AutoSearch V4

P2.4.1
AI Ready Article Schema

目的：
--------------------------------------------------
1. Article 必須可以在尚未 AI 分析時先存入 SQL
2. AI 欄位允許 NULL
3. AI 分析狀態由 ai_status 管理
4. Article Storage 與 AI Analysis 解耦
5. 不因 AI 尚未完成而阻止 Article 建立
6. 為 P2.4 Async AI Scaling 建立穩定資料基礎


Pipeline：

Search
    ↓
Download
    ↓
Parser
    ↓
Article
    ↓
articles
    │
    ├── AI fields = NULL
    │
    └── ai_status = 'pending'
            ↓
        ai_tasks
            ↓
        WAITING
            ↓
        AI Worker
            ↓
        AI Analysis
            ↓
        更新 AI fields
            ↓
        ai_status = 'completed'


AI 欄位：

ai_summary
ai_category
ai_keywords
ai_importance
ai_model
ai_version
ai_analyze_time
ai_confidence

尚未分析時：

NULL


AI 狀態：

pending
    ↓
running
    ↓
completed

失敗：

failed


注意：

ai_status 與 ai_tasks.status 是不同概念。

ai_status：
    Article 的 AI Analysis 狀態

ai_tasks.status：
    AI Task Queue 的執行狀態
*/


-- =====================================================
-- Database
-- =====================================================

USE autosearch;


-- =====================================================
-- 1. AI Summary
--
-- 尚未分析：
--     NULL
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_summary TEXT NULL;


-- =====================================================
-- 2. AI Category
--
-- 尚未分析：
--     NULL
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_category VARCHAR(100) NULL;


-- =====================================================
-- 3. AI Keywords
--
-- 尚未分析：
--     NULL
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_keywords TEXT NULL;


-- =====================================================
-- 4. AI Importance
--
-- 尚未分析：
--     NULL
--
-- 不再使用：
--     0 = 未分析
--
-- 因為 0 可能本身就是合法 Importance。
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_importance INT NULL;


-- =====================================================
-- 5. AI Model
--
-- 尚未分析：
--     NULL
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_model VARCHAR(100) NULL;


-- =====================================================
-- 6. AI Version
--
-- 尚未分析：
--     NULL
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_version VARCHAR(50) NULL;


-- =====================================================
-- 7. AI Analyze Time
--
-- 尚未分析：
--     NULL
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_analyze_time DATETIME NULL;


-- =====================================================
-- 8. AI Confidence
--
-- 尚未分析：
--     NULL
--
-- 不再使用：
--     0.0 = 未分析
--
-- 因為 0.0 可能本身就是合法 Confidence。
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_confidence FLOAT NULL;


-- =====================================================
-- 9. AI Status
--
-- P2.2.5 已建立 ai_status。
--
-- 確保：
--
--     NULL       = 未設定
--     pending    = 等待 AI 分析
--     running    = AI 分析中
--     completed  = AI 分析完成
--     failed     = AI 分析失敗
--
-- Article 建立時：
--
--     ai_status = pending
-- =====================================================

ALTER TABLE articles

MODIFY COLUMN ai_status VARCHAR(20)

NULL

DEFAULT 'pending';


-- =====================================================
-- 10. AI Status Index
--
-- 用途：
--
-- 查詢：
--
--     尚未分析 Article
--
--     ai_status = 'pending'
--
-- 或：
--
--     AI 分析失敗 Article
--
--     ai_status = 'failed'
-- =====================================================

CREATE INDEX idx_articles_ai_status

ON articles(ai_status);


-- =====================================================
-- 11. AI Analyze Time Index
--
-- 方便後續查詢：
--
--     最近 AI 分析
--     長時間未分析
--     AI Analysis History
-- =====================================================

CREATE INDEX idx_articles_ai_analyze_time

ON articles(ai_analyze_time);


-- =====================================================
-- Migration Complete
-- =====================================================

/*
完成後：

Article 可以：

    articles
        ↓
    AI fields = NULL
        ↓
    ai_status = pending
        ↓
    ai_tasks
        ↓
    WAITING
        ↓
    AI Worker
        ↓
    AI Analysis
        ↓
    更新 AI fields
        ↓
    ai_status = completed


核心原則：

Crawler 不等待 AI。

Crawler 只負責：

    Search
    Download
    Parse
    Save Article
    Save Archive
    Create AI Task


AI Worker 負責：

    AI Analysis
    Update AI fields
    Update ai_status
*/
