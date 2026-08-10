/*
AutoSearch V4

P2.2.2
Archive Version History

用途：
建立 Archive 歷史版本管理
*/

CREATE TABLE IF NOT EXISTS archive_versions (

    id INT NOT NULL AUTO_INCREMENT,

    article_id INT NOT NULL,

    raw_document_id INT NOT NULL,

    version_number INT NOT NULL,

    file_hash VARCHAR(64) DEFAULT NULL,

    storage_path VARCHAR(255) DEFAULT NULL,

    file_size BIGINT DEFAULT 0,

    mime_type VARCHAR(50) DEFAULT 'text/html',

    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    KEY idx_archive_versions_article (
        article_id
    ),

    KEY idx_archive_versions_raw_document (
        raw_document_id
    ),

    KEY idx_archive_versions_version (
        article_id,
        version_number
    ),

    CONSTRAINT fk_archive_versions_article

        FOREIGN KEY (article_id)

        REFERENCES articles(id)

        ON DELETE CASCADE,

    CONSTRAINT fk_archive_versions_raw_document

        FOREIGN KEY (raw_document_id)

        REFERENCES raw_documents(id)

        ON DELETE CASCADE

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;