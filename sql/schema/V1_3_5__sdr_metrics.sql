-- Migration: sdr_metrics.start_time + end_time  re-derive UTC from original TIMESTAMP backup
-- See V1_3_0__outdoor_sensor.sql for full rationale.
-- Both time columns are re-derived from sdr_metrics_old in a single INSERT.
-- sdr_metrics_old is intentionally left intact as the authoritative backup.
-- ---------------------------------------------------------------------------

SET TIME_ZONE = '+00:00';

TRUNCATE TABLE `sdr_metrics`;

INSERT IGNORE INTO `sdr_metrics`
    (id, start_time, end_time, duration_sec, sensor_cnt)
SELECT
    id,
    CAST(start_time AS DATETIME(6)),
    CAST(end_time   AS DATETIME(6)),
    duration_sec, sensor_cnt
FROM `sdr_metrics_old`
ORDER BY `id`;
