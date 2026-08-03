CREATE TABLE IF NOT EXISTS articles
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    document_id VARCHAR(64) UNIQUE,


    keyword VARCHAR(255),


    title TEXT,


    url TEXT,


    source VARCHAR(255),


    published DATETIME NULL,


    content LONGTEXT,


    crawl_time DATETIME NULL,


    status VARCHAR(50),



    -- =========================
    -- AI Analysis (V3)
    -- =========================


    ai_summary TEXT,


    ai_category VARCHAR(100),


    ai_keywords TEXT,


    ai_importance INT DEFAULT 0,



    -- =========================
    -- AI Metadata (P4.4.3)
    -- =========================


    ai_model VARCHAR(100),


    ai_version VARCHAR(50),


    ai_analyze_time DATETIME NULL,


    ai_confidence FLOAT DEFAULT 0.0



);