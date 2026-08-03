CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,

    document_id VARCHAR(64) UNIQUE,

    keyword VARCHAR(255),

    title TEXT,

    url TEXT,

    source VARCHAR(255),

    published DATETIME NULL,

    content LONGTEXT,

    crawl_time DATETIME,

    status VARCHAR(50)
);