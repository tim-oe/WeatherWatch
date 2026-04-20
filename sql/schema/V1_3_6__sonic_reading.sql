-- Migration: sonic_reading.read_time  remove server default
--
-- V1_2_0 created sonic_reading with:
--   `read_time` DATETIME NOT NULL DEFAULT current_timestamp()
--
-- current_timestamp() returns the MariaDB server's local time
-- (America/Chicago on this host), so all existing rows store local time
-- rather than UTC.  The SonicModBus application will be updated to set
-- read_time explicitly from the application layer via the LocalToUTCDateTime
-- TypeDecorator, consistent with the WeatherWatch UTC storage convention.
--
-- This is test/development data only — the table is safe to truncate.
-- ---------------------------------------------------------------------------

TRUNCATE TABLE `sonic_reading`;

ALTER TABLE `sonic_reading`
    MODIFY COLUMN `read_time` DATETIME NOT NULL;
