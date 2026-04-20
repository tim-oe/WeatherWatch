-- Migration: aqi_sensor.read_time  re-derive UTC from original TIMESTAMP backup
-- See V1_3_0__outdoor_sensor.sql for full rationale.
-- aqi_sensor_old is intentionally left intact as the authoritative backup.
-- ---------------------------------------------------------------------------

SET TIME_ZONE = '+00:00';

TRUNCATE TABLE `aqi_sensor`;

INSERT IGNORE INTO `aqi_sensor`
    (id, read_time, pm_1_0_conctrt_std, pm_2_5_conctrt_std, pm_10_conctrt_std,
     pm_1_0_conctrt_atmosph, pm_2_5_conctrt_atmosph, pm_10_conctrt_atmosph)
SELECT
    id,
    CAST(read_time AS DATETIME(6)),
    pm_1_0_conctrt_std, pm_2_5_conctrt_std, pm_10_conctrt_std,
    pm_1_0_conctrt_atmosph, pm_2_5_conctrt_atmosph, pm_10_conctrt_atmosph
FROM `aqi_sensor_old`
ORDER BY `id`;
