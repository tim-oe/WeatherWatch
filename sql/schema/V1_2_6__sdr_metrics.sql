-- Migration: sdr_metrics.start_time and end_time  TIMESTAMP -> DATETIME(6)
--
-- Background:
--   Mirrors V1_2_1__outdoor_sensor.sql — same TIMESTAMP -> DATETIME(6) conversion
--   for consistency with solar_reading and the migrated sensor tables.
--   Both start_time and end_time are TIMESTAMP columns and are both converted.
--
-- Partitioning change:
--   RANGE( UNIX_TIMESTAMP(start_time) ) requires a TIMESTAMP column.  Switching to
--   RANGE COLUMNS(start_time) for DATETIME(6).
--
-- DST fall-back:
--   The unique key is (start_time, end_time) — two columns — so a collision
--   requires both to map to the same Chicago local time simultaneously.
--   INSERT IGNORE discards the later duplicate (higher id), keeping the earlier
--   UTC reading.
--
-- Prerequisites:
--   MariaDB named-timezone tables must be loaded before running this migration.
--   Check:  SELECT COUNT(*) FROM mysql.time_zone_name WHERE name = 'America/Chicago';
--   Load:   mariadb-tzinfo-to-sql /usr/share/zoneinfo | sudo mariadb -u root mysql
--   Flush:  FLUSH TABLES;
-- ---------------------------------------------------------------------------


-- Step 1: set session timezone
SET TIME_ZONE = 'America/Chicago';


-- ---------------------------------------------------------------------------
-- Step 2: create new table with DATETIME(6) and RANGE COLUMNS partitioning
-- ---------------------------------------------------------------------------
CREATE TABLE `sdr_metrics_new` (
    `id`           BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    `start_time`   DATETIME(6)       NOT NULL,
    `end_time`     DATETIME(6)       NOT NULL,
    `duration_sec` SMALLINT UNSIGNED NOT NULL,
    `sensor_cnt`   SMALLINT UNSIGNED NOT NULL,
    PRIMARY KEY (`id`, `start_time`),
    UNIQUE KEY `sdr_unique_sensor` (`start_time`, `end_time`),
    KEY `start_time_idx` (`start_time`),
    KEY `end_time_idx` (`end_time`)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4
  PARTITION BY RANGE COLUMNS(`start_time`) (
    PARTITION p2024 VALUES LESS THAN ('2025-01-01 00:00:00'),
    PARTITION p2025 VALUES LESS THAN ('2026-01-01 00:00:00'),
    PARTITION p2026 VALUES LESS THAN ('2027-01-01 00:00:00'),
    PARTITION p2027 VALUES LESS THAN ('2028-01-01 00:00:00'),
    PARTITION p2028 VALUES LESS THAN ('2029-01-01 00:00:00'),
    PARTITION p2029 VALUES LESS THAN ('2030-01-01 00:00:00'),
    PARTITION p2030 VALUES LESS THAN ('2031-01-01 00:00:00'),
    PARTITION p2031 VALUES LESS THAN ('2032-01-01 00:00:00'),
    PARTITION p2032 VALUES LESS THAN ('2033-01-01 00:00:00'),
    PARTITION p2033 VALUES LESS THAN ('2034-01-01 00:00:00'),
    PARTITION p2034 VALUES LESS THAN ('2035-01-01 00:00:00'),
    PARTITION future VALUES LESS THAN MAXVALUE
  );


-- ---------------------------------------------------------------------------
-- Step 3: populate
--   Both start_time and end_time are converted from UTC to America/Chicago.
--   INSERT IGNORE silently drops DST fall-back duplicates; ORDER BY id ensures
--   the earlier UTC reading (lower id) is always kept.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO `sdr_metrics_new`
    (id, start_time, end_time, duration_sec, sensor_cnt)
SELECT
    id,
    CAST(CONVERT_TZ(start_time, '+00:00', 'America/Chicago') AS DATETIME(6)),
    CAST(CONVERT_TZ(end_time,   '+00:00', 'America/Chicago') AS DATETIME(6)),
    duration_sec, sensor_cnt
FROM `sdr_metrics`
ORDER BY `id`;


-- ---------------------------------------------------------------------------
-- Step 4: atomic rename — swap new table in, keep original as sdr_metrics_old
--   sdr_metrics_old is intentionally retained as a safety backup.
--   Once the application has been running cleanly, drop it manually:
--     DROP TABLE `sdr_metrics_old`;
-- ---------------------------------------------------------------------------
RENAME TABLE
    `sdr_metrics`     TO `sdr_metrics_old`,
    `sdr_metrics_new` TO `sdr_metrics`;
