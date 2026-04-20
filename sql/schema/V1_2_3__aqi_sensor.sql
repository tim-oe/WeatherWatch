-- Migration: aqi_sensor.read_time  TIMESTAMP -> DATETIME(6)
--
-- Background:
--   Mirrors V1_2_1__outdoor_sensor.sql — same TIMESTAMP -> DATETIME(6) conversion
--   for consistency with solar_reading and the migrated sensor tables.
--
-- Partitioning change:
--   RANGE( UNIX_TIMESTAMP(col) ) requires a TIMESTAMP column.  Switching to
--   RANGE COLUMNS(read_time) for DATETIME(6).
--
-- DST fall-back:
--   On the first Sunday of November, two distinct UTC readings can share the same
--   Chicago local clock time.  The aqi_sensor unique key is (read_time) only —
--   a single column — so any two readings during the fall-back hour will collide.
--   INSERT IGNORE discards the later duplicate (higher id), keeping the earlier
--   UTC reading.  Acceptable data loss for air quality sensor readings.
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
CREATE TABLE `aqi_sensor_new` (
    `id`                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `read_time`             DATETIME(6)     NOT NULL,
    `pm_1_0_conctrt_std`    INT UNSIGNED    NOT NULL,
    `pm_2_5_conctrt_std`    INT UNSIGNED    NOT NULL,
    `pm_10_conctrt_std`     INT UNSIGNED    NOT NULL,
    `pm_1_0_conctrt_atmosph` INT UNSIGNED   NOT NULL,
    `pm_2_5_conctrt_atmosph` INT UNSIGNED   NOT NULL,
    `pm_10_conctrt_atmosph`  INT UNSIGNED   NOT NULL,
    PRIMARY KEY (`id`, `read_time`),
    UNIQUE KEY `aqi_unique_sensor` (`read_time`)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4
  PARTITION BY RANGE COLUMNS(`read_time`) (
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
--   CONVERT_TZ converts each TIMESTAMP from UTC to America/Chicago local time,
--   applying the correct -5 (CDT) or -6 (CST) offset per row based on date.
--   INSERT IGNORE silently drops DST fall-back duplicates; ORDER BY id ensures
--   the earlier UTC reading (lower id) is always kept.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO `aqi_sensor_new`
    (id, read_time, pm_1_0_conctrt_std, pm_2_5_conctrt_std, pm_10_conctrt_std,
     pm_1_0_conctrt_atmosph, pm_2_5_conctrt_atmosph, pm_10_conctrt_atmosph)
SELECT
    id,
    CAST(CONVERT_TZ(read_time, '+00:00', 'America/Chicago') AS DATETIME(6)),
    pm_1_0_conctrt_std, pm_2_5_conctrt_std, pm_10_conctrt_std,
    pm_1_0_conctrt_atmosph, pm_2_5_conctrt_atmosph, pm_10_conctrt_atmosph
FROM `aqi_sensor`
ORDER BY `id`;


-- ---------------------------------------------------------------------------
-- Step 4: atomic rename — swap new table in, keep original as aqi_sensor_old
--   aqi_sensor_old is intentionally retained as a safety backup.
--   Once the application has been running cleanly, drop it manually:
--     DROP TABLE `aqi_sensor_old`;
-- ---------------------------------------------------------------------------
RENAME TABLE
    `aqi_sensor`     TO `aqi_sensor_old`,
    `aqi_sensor_new` TO `aqi_sensor`;
