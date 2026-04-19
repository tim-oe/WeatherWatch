-- Migration: light_sensor.read_time  TIMESTAMP -> DATETIME(6)
--
-- Background:
--   Mirrors V1_2_1__outdoor_sensor.sql — same TIMESTAMP -> DATETIME(6) conversion
--   for consistency with solar_reading and the migrated sensor tables.
--
-- Partitioning change:
--   RANGE( UNIX_TIMESTAMP(col) ) requires a TIMESTAMP column.  Switching to
--   RANGE COLUMNS(read_time) for DATETIME(6).
--   Partition history starts at p2026 matching the original table.
--
-- DST fall-back:
--   The unique key is (read_time) only — any two readings during the fall-back
--   hour will collide.  INSERT IGNORE discards the later duplicate (higher id),
--   keeping the earlier UTC reading.
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
CREATE TABLE `light_sensor_new` (
    `id`                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `read_time`             DATETIME(6)     NOT NULL,
    `lux`                   DECIMAL(8,2)    NOT NULL,
    `visible`               INT UNSIGNED    NOT NULL,
    `infrared`              INT UNSIGNED    NOT NULL,
    `full_spectrum`         INT UNSIGNED    NOT NULL,
    `ir_visible_luminosity` INT UNSIGNED    NOT NULL,
    `ir_only`               INT UNSIGNED    NOT NULL,
    PRIMARY KEY (`id`, `read_time`),
    UNIQUE KEY `light_unique_sensor` (`read_time`)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4
  PARTITION BY RANGE COLUMNS(`read_time`) (
    PARTITION p2026 VALUES LESS THAN ('2027-01-01 00:00:00'),
    PARTITION p2027 VALUES LESS THAN ('2028-01-01 00:00:00'),
    PARTITION p2028 VALUES LESS THAN ('2029-01-01 00:00:00'),
    PARTITION p2029 VALUES LESS THAN ('2030-01-01 00:00:00'),
    PARTITION p2030 VALUES LESS THAN ('2031-01-01 00:00:00'),
    PARTITION p2031 VALUES LESS THAN ('2032-01-01 00:00:00'),
    PARTITION p2032 VALUES LESS THAN ('2033-01-01 00:00:00'),
    PARTITION p2033 VALUES LESS THAN ('2034-01-01 00:00:00'),
    PARTITION p2034 VALUES LESS THAN ('2035-01-01 00:00:00'),
    PARTITION p2035 VALUES LESS THAN ('2036-01-01 00:00:00'),
    PARTITION p2036 VALUES LESS THAN ('2037-01-01 00:00:00'),
    PARTITION future VALUES LESS THAN MAXVALUE
  );


-- ---------------------------------------------------------------------------
-- Step 3: populate
--   CONVERT_TZ converts each TIMESTAMP from UTC to America/Chicago local time,
--   applying the correct -5 (CDT) or -6 (CST) offset per row based on date.
--   INSERT IGNORE silently drops DST fall-back duplicates; ORDER BY id ensures
--   the earlier UTC reading (lower id) is always kept.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO `light_sensor_new`
    (id, read_time, lux, visible, infrared, full_spectrum, ir_visible_luminosity, ir_only)
SELECT
    id,
    CAST(CONVERT_TZ(read_time, '+00:00', 'America/Chicago') AS DATETIME(6)),
    lux, visible, infrared, full_spectrum, ir_visible_luminosity, ir_only
FROM `light_sensor`
ORDER BY `id`;


-- ---------------------------------------------------------------------------
-- Step 4: atomic rename — swap new table in, keep original as light_sensor_old
--   light_sensor_old is intentionally retained as a safety backup.
--   Once the application has been running cleanly, drop it manually:
--     DROP TABLE `light_sensor_old`;
-- ---------------------------------------------------------------------------
RENAME TABLE
    `light_sensor`     TO `light_sensor_old`,
    `light_sensor_new` TO `light_sensor`;
