/*
    AutoSearch V4

    Database Schema

    Version:

        V4 Phase 1.5


    Features:

        - Article Database (V2.5)
        - AI Analysis (V3)
        - Raw Document Archive (V4 P1.1)
        - Async AI Task Queue (V4 P1.2)
        - Knowledge Archive Foundation (V4 P1.3)
        - Knowledge Retrieval Layer (V4 P1.4)
        - Knowledge Intelligence Layer (V4 P1.5)

*/


CREATE DATABASE IF NOT EXISTS autosearch;


USE autosearch;



-- =====================================================
-- Article Table
--
-- V2.5 + V3 AI Extension
--
-- =====================================================


CREATE TABLE IF NOT EXISTS articles
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    document_id VARCHAR(64)
        UNIQUE NOT NULL,


    keyword VARCHAR(255),


    title TEXT,


    url TEXT,


    source VARCHAR(255),


    published DATETIME NULL,


    content LONGTEXT,


    crawl_time DATETIME NULL,


    status VARCHAR(50),



    -- =========================
    -- AI Analysis
    -- =========================


    ai_summary TEXT,


    ai_category VARCHAR(100),


    ai_keywords TEXT,


    ai_importance INT DEFAULT 0,


    ai_model VARCHAR(100),


    ai_version VARCHAR(50),


    ai_analyze_time DATETIME NULL,


    ai_confidence FLOAT DEFAULT 0.0


);









-- =====================================================
-- Raw Document Archive
--
-- V4 P1.1
--
-- =====================================================


CREATE TABLE IF NOT EXISTS raw_documents
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    article_id INT NOT NULL,


    original_url TEXT,


    storage_path VARCHAR(255),


    file_hash VARCHAR(64)
        UNIQUE,


    file_size BIGINT DEFAULT 0,


    mime_type VARCHAR(50)
        DEFAULT 'text/html',


    created_time DATETIME
        DEFAULT CURRENT_TIMESTAMP,



    CONSTRAINT fk_raw_documents_article


    FOREIGN KEY(article_id)


    REFERENCES articles(id)


    ON DELETE CASCADE


);









-- =====================================================
-- Article Metadata
--
-- V4 P1.3
--
-- =====================================================


CREATE TABLE IF NOT EXISTS article_metadata
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    article_id INT NOT NULL,


    author VARCHAR(100),


    category VARCHAR(100),


    language VARCHAR(20),


    source_type VARCHAR(50),


    tags TEXT,


    created_time DATETIME
        DEFAULT CURRENT_TIMESTAMP,



    CONSTRAINT fk_article_metadata_article


    FOREIGN KEY(article_id)


    REFERENCES articles(id)


    ON DELETE CASCADE


);









-- =====================================================
-- Knowledge Archive
--
-- V4 P1.3
--
-- Knowledge Layer
--
-- =====================================================


CREATE TABLE IF NOT EXISTS knowledge_archive
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    article_id INT NOT NULL,


    topic VARCHAR(255),


    entities TEXT,


    relations TEXT,


    knowledge_version VARCHAR(50)
        DEFAULT '1.0',


    created_time DATETIME
        DEFAULT CURRENT_TIMESTAMP,



    CONSTRAINT fk_knowledge_archive_article


    FOREIGN KEY(article_id)


    REFERENCES articles(id)


    ON DELETE CASCADE


);









-- =====================================================
-- Knowledge Scores
--
-- V4 P1.5
--
-- Knowledge Intelligence Layer
--
-- 功能:
--
-- Importance
-- Confidence
-- Quality
-- Freshness
-- Ranking
--
-- =====================================================


CREATE TABLE IF NOT EXISTS knowledge_scores
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    knowledge_id INT NOT NULL,



    -- =========================
    -- Intelligence Score
    -- =========================


    importance INT DEFAULT 0,


    confidence FLOAT DEFAULT 0.0,


    quality_score FLOAT DEFAULT 0.0,


    freshness_score FLOAT DEFAULT 0.0,


    ranking_score FLOAT DEFAULT 0.0,



    created_time DATETIME
        DEFAULT CURRENT_TIMESTAMP,



    CONSTRAINT fk_knowledge_scores_archive


    FOREIGN KEY(knowledge_id)


    REFERENCES knowledge_archive(id)


    ON DELETE CASCADE


);





-- =====================================================
-- Knowledge Ranking Index
--
-- P1.5 Retrieval Optimization
--
-- =====================================================


CREATE INDEX idx_knowledge_ranking


ON knowledge_scores
(
    ranking_score DESC
);









-- =====================================================
-- Async AI Task Queue
--
-- V4 P1.2
--
--
-- Article
--    |
-- ai_tasks
--    |
-- AI Worker
--    |
-- AI Analysis
--    |
-- Knowledge Archive
--
-- =====================================================


CREATE TABLE IF NOT EXISTS ai_tasks
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    article_id INT NOT NULL,


    task_type VARCHAR(50)
        DEFAULT 'analysis',



    -- WAITING
    -- RUNNING
    -- SUCCESS
    -- FAILED


    status VARCHAR(30)
        DEFAULT 'WAITING',



    priority INT
        DEFAULT 5,



    retry_count INT
        DEFAULT 0,



    error_message TEXT NULL,



    created_time DATETIME
        DEFAULT CURRENT_TIMESTAMP,


    started_time DATETIME NULL,


    finished_time DATETIME NULL,



    CONSTRAINT fk_ai_tasks_article


    FOREIGN KEY(article_id)


    REFERENCES articles(id)


    ON DELETE CASCADE


);







-- =====================================================
-- AI Worker Query Index
--
-- 找待處理任務
--
-- =====================================================


CREATE INDEX idx_ai_tasks_status_priority


ON ai_tasks
(
    status,
    priority
);





-- =====================================================
-- Knowledge Search Index
--
-- V4 P1.4
--
-- Retrieval Optimization
--
-- =====================================================


CREATE INDEX idx_knowledge_topic


ON knowledge_archive
(
    topic
);