-- Migration: outdoor_sensor.read_time  re-derive UTC from original TIMESTAMP backup
--
-- V1_2_1 populated outdoor_sensor from outdoor_sensor_old (TIMESTAMP) by
-- converting UTC -> America/Chicago, storing local time in DATETIME(6).
-- The goal is to store UTC, so this migration truncates the incorrectly-valued
-- outdoor_sensor and re-populates it from outdoor_sensor_old using UTC directly.
--
-- TIMESTAMP columns store UTC internally.  With the session timezone set to
-- '+00:00', reading a TIMESTAMP returns the raw UTC value, so a plain CAST to
-- DATETIME(6) gives the correct UTC datetime with no CONVERT_TZ needed.
--
-- outdoor_sensor_old is intentionally left intact as the authoritative backup.
-- ---------------------------------------------------------------------------

SET TIME_ZONE = '+00:00';

TRUNCATE TABLE `outdoor_sensor`;

INSERT IGNORE INTO `outdoor_sensor`
    (id, read_time, battery_ok, sensor_id, temperature_f, humidity, pressure,
     rain_cum_mm, rain_delta_mm, wind_avg_m_s, wind_max_m_s, wind_dir_deg,
     light_lux, uv, raw)
SELECT
    id,
    CAST(read_time AS DATETIME(6)),
    battery_ok, sensor_id, temperature_f, humidity, pressure,
    rain_cum_mm, rain_delta_mm, wind_avg_m_s, wind_max_m_s, wind_dir_deg,
    light_lux, uv, raw
FROM `outdoor_sensor_old`
ORDER BY `id`;
