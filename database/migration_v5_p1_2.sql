-- ======================================================================
-- AutoSearch V5
--
-- V5.1 P1.2
--
-- Target Table Migration
--
-- 用途：
--
--     建立使用者指定的爬蟲 Target。
--
-- 架構：
--
--     User
--       ↓
--     Target
--       ↓
--     Existing V4 Crawl Pipeline
--
-- Target 不負責：
--
--     - Crawler
--     - Parser
--     - Article
--     - Archive
--     - Duplicate Detection
--     - AI Analysis
--
-- 注意：
--
--     Target URL 與 V4 Article / Archive URL
--     屬於不同層級。
--
--     V4 Archive Duplicate Detection：
--
--         URL + HTML Content Hash
--
--     不由本 Table 處理。
--
-- ======================================================================


-- ======================================================================
-- 1. Create targets Table
-- ======================================================================

CREATE TABLE IF NOT EXISTS `targets` (

    `id`
        int NOT NULL AUTO_INCREMENT,

    `name`
        varchar(255)
        DEFAULT NULL,

    `target_type`
        varchar(50)
        DEFAULT 'website',

    `url`
        text
        NOT NULL,

    `description`
        text,

    `status`
        varchar(30)
        DEFAULT 'active',

    `created_time`
        datetime
        DEFAULT CURRENT_TIMESTAMP,

    `updated_time`
        datetime
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (`id`),

    KEY `idx_targets_status`
        (`status`),

    KEY `idx_targets_type`
        (`target_type`)

)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;