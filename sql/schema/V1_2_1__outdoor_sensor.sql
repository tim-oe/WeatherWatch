-- Migration: outdoor_sensor.read_time  TIMESTAMP -> DATETIME(6)
--
-- Background:
--   TIMESTAMP stores UTC internally and converts to/from the session timezone on
--   read/write.  The records in outdoor_sensor were inserted as America/Chicago
--   naive local-time values.  DATETIME(6) stores the value exactly as-is with no
--   timezone conversion, which is the correct type for local-time values and is
--   consistent with the newer solar_reading table.
--
-- Partitioning change:
--   RANGE( UNIX_TIMESTAMP(col) ) requires a TIMESTAMP column.  For DATETIME we
--   switch to RANGE COLUMNS(read_time), which compares datetime values directly.
--
-- DST fall-back:
--   On the first Sunday of November, clocks roll back from 2 AM CDT to 1 AM CST.
--   Two distinct UTC readings can share the same Chicago local clock time.
--   INSERT IGNORE discards the later duplicate (higher id), keeping the earlier
--   UTC reading.  A handful of readings are lost once per year during the
--   1:00-1:59 AM window — acceptable for weather sensor data.
--
-- Prerequisites:
--   MariaDB named-timezone tables must be loaded before running this migration.
--   Check:  SELECT COUNT(*) FROM mysql.time_zone_name WHERE name = 'America/Chicago';
--   Load:   mariadb-tzinfo-to-sql /usr/share/zoneinfo | sudo mariadb -u root mysql
--   Flush:  FLUSH TABLES;
-- ---------------------------------------------------------------------------


-- Step 1: set session timezone for any implicit TIMESTAMP display
SET TIME_ZONE = 'America/Chicago';


-- ---------------------------------------------------------------------------
-- Step 2: create new table with DATETIME(6) and RANGE COLUMNS partitioning
-- ---------------------------------------------------------------------------
CREATE TABLE `outdoor_sensor_new` (
    `id`            BIGINT UNSIGNED   NOT NULL AUTO_INCREMENT,
    `read_time`     DATETIME(6)       NOT NULL,
    `battery_ok`    BIT(1)            NOT NULL,
    `sensor_id`     SMALLINT UNSIGNED NOT NULL,
    `temperature_f` DECIMAL(5,2)      NOT NULL,
    `humidity`      TINYINT UNSIGNED  NOT NULL,
    `pressure`      DECIMAL(6,2)      NOT NULL,
    `rain_cum_mm`   DECIMAL(7,2)      NOT NULL COMMENT 'cumulative rain in mm since last reset',
    `rain_delta_mm` DECIMAL(7,2)      NOT NULL COMMENT 'rain in mm since the last sensor read',
    `wind_avg_m_s`  DECIMAL(5,2)      NOT NULL,
    `wind_max_m_s`  DECIMAL(5,2)      NOT NULL,
    `wind_dir_deg`  SMALLINT UNSIGNED NOT NULL,
    `light_lux`     INT UNSIGNED      NOT NULL,
    `uv`            DECIMAL(5,2)      NOT NULL,
    `raw`           JSON              NOT NULL COMMENT 'the raw json record',
    PRIMARY KEY (`id`, `read_time`),
    UNIQUE KEY `out_unique_sensor` (`read_time`, `sensor_id`),
    KEY `read_time_idx` (`read_time`),
    KEY `sensor_id_idx` (`sensor_id`)
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
--   CAST to DATETIME(6) matches the destination column type.
--   INSERT IGNORE silently drops DST fall-back duplicates; ORDER BY id ensures
--   the earlier UTC reading (lower id) is always the one kept.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO `outdoor_sensor_new`
    (id, read_time, battery_ok, sensor_id, temperature_f, humidity, pressure,
     rain_cum_mm, rain_delta_mm, wind_avg_m_s, wind_max_m_s, wind_dir_deg,
     light_lux, uv, raw)
SELECT
    id,
    CAST(CONVERT_TZ(read_time, '+00:00', 'America/Chicago') AS DATETIME(6)),
    battery_ok, sensor_id, temperature_f, humidity, pressure,
    rain_cum_mm, rain_delta_mm, wind_avg_m_s, wind_max_m_s, wind_dir_deg,
    light_lux, uv, raw
FROM `outdoor_sensor`
ORDER BY `id`;


-- ---------------------------------------------------------------------------
-- Step 4: atomic rename — swap new table in, keep original as outdoor_sensor_old
--   outdoor_sensor_old is intentionally retained as a safety backup.
--   Once the application has been running cleanly, drop it manually:
--     DROP TABLE `outdoor_sensor_old`;
-- ---------------------------------------------------------------------------
RENAME TABLE
    `outdoor_sensor`     TO `outdoor_sensor_old`,
    `outdoor_sensor_new` TO `outdoor_sensor`;
