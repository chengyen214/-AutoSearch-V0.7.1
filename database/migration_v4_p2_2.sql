-- ======================================
-- AutoSearch V4
--
-- Migration P2.2
--
-- Search Index Optimization
--
-- Database: MySQL
-- ======================================


CREATE TABLE IF NOT EXISTS search_index
(

    id INT AUTO_INCREMENT PRIMARY KEY,


    knowledge_id INT NOT NULL,


    search_text TEXT,


    keywords TEXT,


    entities TEXT,


    topic VARCHAR(255),


    embedding_reference INT,


    index_version VARCHAR(20)
        DEFAULT '1.0',


    created_time TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_search_index_knowledge

        FOREIGN KEY (knowledge_id)

        REFERENCES knowledge_archive(id)

        ON DELETE CASCADE

);





CREATE INDEX idx_search_index_knowledge_id

ON search_index(knowledge_id);





CREATE INDEX idx_search_index_topic

ON search_index(topic);





CREATE INDEX idx_search_index_version

ON search_index(index_version);