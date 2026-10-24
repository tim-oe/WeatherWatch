-- Migration: outdoor_sensor daily rainfall index
--
-- get_days_rainfall sums rain_delta_mm for one UTC day of read_time.
-- CAST(read_time AS DATE) cannot use read_time_idx and scans every partition.
-- outdoor_rain_day_idx covers the half-open read_time range and the summed column.
--
-- The 7-day history reads do not need a new index. Each one is
-- read_time > :cutoff ORDER BY read_time DESC, and the live plans already
-- range-scan about 2,000 rows:
--   outdoor_sensor  out_unique_sensor (read_time, sensor_id)
--   light_sensor    light_unique_sensor (read_time)
--   aqi_sensor      aqi_unique_sensor (read_time)
--   indoor_sensor   in_unique_sensor (read_time, sensor_id, channel)
--     channel is applied after the read_time range; both channels are ~2,000 rows
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS outdoor_rain_day_idx
    ON outdoor_sensor (read_time, rain_delta_mm);
