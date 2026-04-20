-- Migration: indoor_sensor.read_time  re-derive UTC from original TIMESTAMP backup
-- See V1_3_0__outdoor_sensor.sql for full rationale.
-- indoor_sensor_old is intentionally left intact as the authoritative backup.
-- ---------------------------------------------------------------------------

SET TIME_ZONE = '+00:00';

TRUNCATE TABLE `indoor_sensor`;

INSERT IGNORE INTO `indoor_sensor`
    (id, read_time, battery_ok, sensor_id, channel, temperature_f, humidity, raw)
SELECT
    id,
    CAST(read_time AS DATETIME(6)),
    battery_ok, sensor_id, channel, temperature_f, humidity, raw
FROM `indoor_sensor_old`
ORDER BY `id`;
