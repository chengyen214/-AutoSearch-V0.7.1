-- ======================================================================
-- AutoSearch V5
--
-- V5.4 P4.2
--
-- Job Repository Database Migration
--
-- 用途：
--
--     建立 Target → Job 的工作任務資料層。
--
-- 架構：
--
--     User
--       ↓
--     Target
--       ↓
--     Job
--       ↓
--     Batch Runner
--       ↓
--     Existing V4 Crawl Pipeline
--
-- ======================================================================


-- ======================================================================
-- 1. Extend targets Table
--
-- V5.3 Target Model / TargetRepository 已支援：
--
--     keyword
--     search_provider
--
-- V5.1 原始 targets schema 尚未包含這兩個欄位。
--
-- ======================================================================

ALTER TABLE `targets`

    ADD COLUMN `keyword`
        varchar(500)
        DEFAULT NULL
        AFTER `url`;


ALTER TABLE `targets`

    ADD COLUMN `search_provider`
        varchar(100)
        DEFAULT NULL
        AFTER `keyword`;


-- ======================================================================
-- 2. Target Search Indexes
-- ======================================================================

ALTER TABLE `targets`

    ADD KEY `idx_targets_keyword`
        (`keyword`);


ALTER TABLE `targets`

    ADD KEY `idx_targets_search_provider`
        (`search_provider`);


-- ======================================================================
-- 3. Create jobs Table
--
-- 一個 Target 可以建立多個 Job。
--
-- 例如：
--
--     Target #1
--         ↓
--     Job #1 → DONE
--     Job #2 → DONE
--     Job #3 → FAILED
--     Job #4 → WAITING
--
-- Job 是一次執行工作的紀錄。
--
-- ======================================================================

CREATE TABLE IF NOT EXISTS `jobs` (

    `id`
        int NOT NULL AUTO_INCREMENT,

    `target_id`
        int NOT NULL,

    `status`
        varchar(30)
        NOT NULL
        DEFAULT 'WAITING',

    `retry_count`
        int NOT NULL
        DEFAULT 0,

    `created_time`
        datetime
        DEFAULT CURRENT_TIMESTAMP,

    `started_time`
        datetime
        DEFAULT NULL,

    `finished_time`
        datetime
        DEFAULT NULL,

    `error_message`
        text
        DEFAULT NULL,

    PRIMARY KEY (`id`),

    KEY `idx_jobs_target_id`
        (`target_id`),

    KEY `idx_jobs_status`
        (`status`),

    KEY `idx_jobs_created_time`
        (`created_time`),

    KEY `idx_jobs_target_status`
        (`target_id`, `status`)

)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;


-- ======================================================================
-- 4. Job Status Policy
--
-- Application Layer 使用以下狀態：
--
--     WAITING
--     RUNNING
--     DONE
--     FAILED
--
-- 狀態轉換：
--
--     WAITING
--        ↓
--     RUNNING
--        ↓
--     DONE
--
--     RUNNING
--        ↓
--     FAILED
--        ↓
--     WAITING
--        ↓
--     RUNNING
--
-- Retry 是否允許由 Job Model / Job Service 控制。
--
-- Database 不負責 Job Business Logic。
--
-- ======================================================================


-- ======================================================================
-- 5. Migration Note
--
-- 本 Migration 不建立：
--
--     - Job Service
--     - Job API
--     - Batch Runner
--     - Scheduler
--     - Crawl Pipeline
--
-- 後續架構：
--
--     Job Model
--          ↓
--     Job Repository
--          ↓
--     Job Service
--          ↓
--     Job API
--          ↓
--     Batch Runner
--          ↓
--     V4 Crawl Pipeline
--
-- ======================================================================
