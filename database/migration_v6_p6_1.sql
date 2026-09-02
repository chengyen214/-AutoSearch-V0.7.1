/*
database/migration_v6_p6_1.sql

AutoSearch V5

V6 P6.1

Target Crawler URL

用途：

    targets 新增 crawler_url 欄位。

設計：

    url
        ↓
    Target 原始 / 目標 URL

    crawler_url
        ↓
    實際提供給 Crawler 使用的 URL

注意：

    本 Migration 只修改 targets。

    jobs 不修改。
    其他資料表不修改。
*/


ALTER TABLE targets
ADD COLUMN crawler_url TEXT NULL
AFTER url;