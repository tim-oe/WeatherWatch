-- Migration: pi_metrics.read_time  re-derive UTC from original TIMESTAMP backup
-- See V1_3_0__outdoor_sensor.sql for full rationale.
-- pi_metrics_old is intentionally left intact as the authoritative backup.
-- ---------------------------------------------------------------------------

SET TIME_ZONE = '+00:00';

TRUNCATE TABLE `pi_metrics`;

INSERT IGNORE INTO `pi_metrics`
    (id, read_time, mem_available, mem_used, mem_percent,
     disk_available, disk_used, disk_percent, cpu_temp_c)
SELECT
    id,
    CAST(read_time AS DATETIME(6)),
    mem_available, mem_used, mem_percent,
    disk_available, disk_used, disk_percent, cpu_temp_c
FROM `pi_metrics_old`
ORDER BY `id`;
