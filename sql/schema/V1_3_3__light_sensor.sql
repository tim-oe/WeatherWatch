-- Migration: light_sensor.read_time  re-derive UTC from original TIMESTAMP backup
-- See V1_3_0__outdoor_sensor.sql for full rationale.
-- light_sensor_old is intentionally left intact as the authoritative backup.
-- ---------------------------------------------------------------------------

SET TIME_ZONE = '+00:00';

TRUNCATE TABLE `light_sensor`;

INSERT IGNORE INTO `light_sensor`
    (id, read_time, lux, visible, infrared, full_spectrum, ir_visible_luminosity, ir_only)
SELECT
    id,
    CAST(read_time AS DATETIME(6)),
    lux, visible, infrared, full_spectrum, ir_visible_luminosity, ir_only
FROM `light_sensor_old`
ORDER BY `id`;
