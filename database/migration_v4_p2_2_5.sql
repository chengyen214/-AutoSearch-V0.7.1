-- ======================================
-- AutoSearch V4
-- P2.2.5
--
-- Async AI Analysis Pipeline
--
-- Add AI Analysis Status
-- ======================================


ALTER TABLE articles

ADD COLUMN ai_status VARCHAR(20)

DEFAULT 'pending'

AFTER ai_confidence;