CREATE TABLE `sonic_reading` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `read_time` datetime NOT NULL DEFAULT current_timestamp(),
  `wind_speed_ms` double unsigned NOT NULL,
  `wind_direction` tinyint(3) unsigned NOT NULL,
  `wind_angle_deg` smallint(5) unsigned NOT NULL,
  `humidity_pct` double unsigned NOT NULL,
  `temperature_c` double NOT NULL,
  `noise_db` double unsigned NOT NULL,
  `pm25_ugm3` int(10) unsigned NOT NULL,
  `pm10_ugm3` int(10) unsigned NOT NULL,
  `atm_pressure_kpa` double unsigned NOT NULL,
  `light_lux` int(10) unsigned NOT NULL,
  `rainfall_mm` double unsigned NOT NULL,
  PRIMARY KEY (`id`,`read_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci
 PARTITION BY RANGE  COLUMNS(`read_time`)
(PARTITION `p2026` VALUES LESS THAN ('2027-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2027` VALUES LESS THAN ('2028-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2028` VALUES LESS THAN ('2029-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2029` VALUES LESS THAN ('2030-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2030` VALUES LESS THAN ('2031-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2031` VALUES LESS THAN ('2032-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2032` VALUES LESS THAN ('2033-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2033` VALUES LESS THAN ('2034-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2034` VALUES LESS THAN ('2035-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2035` VALUES LESS THAN ('2036-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2036` VALUES LESS THAN ('2037-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `future` VALUES LESS THAN (MAXVALUE) ENGINE = InnoDB);

CREATE TABLE IF NOT EXISTS solar_reading (
    id                            INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    sensor_name                   VARCHAR(100)    NOT NULL,
    read_time                     DATETIME(6)     NOT NULL,

    -- Device info
    model                         VARCHAR(64),
    device_id                     TINYINT UNSIGNED,

    -- Battery status
    battery_percentage            TINYINT UNSIGNED,
    battery_voltage               FLOAT UNSIGNED,
    battery_current               FLOAT UNSIGNED,
    battery_temperature           TINYINT,
    battery_type                  VARCHAR(32),

    -- Controller status
    controller_temperature        TINYINT,
    charging_status               VARCHAR(32),

    -- Load output (street light)
    load_status                   VARCHAR(8),
    load_voltage                  FLOAT UNSIGNED,
    load_current                  FLOAT UNSIGNED,
    load_power                    SMALLINT UNSIGNED,

    -- PV (solar panel) input
    pv_voltage                    FLOAT UNSIGNED,
    pv_current                    FLOAT UNSIGNED,
    pv_power                      SMALLINT UNSIGNED,

    -- Daily statistics
    battery_min_voltage_today     FLOAT UNSIGNED,
    battery_max_voltage_today     FLOAT UNSIGNED,
    max_charging_current_today    FLOAT UNSIGNED,
    max_discharging_current_today FLOAT UNSIGNED,
    max_charging_power_today      SMALLINT UNSIGNED,
    max_discharging_power_today   SMALLINT UNSIGNED,
    charging_amp_hours_today      SMALLINT UNSIGNED,
    discharging_amp_hours_today   SMALLINT UNSIGNED,
    power_generation_today        FLOAT UNSIGNED,
    power_consumption_today       FLOAT UNSIGNED,

    -- Lifetime statistics
    power_generation_total        INT UNSIGNED,

    PRIMARY KEY (id, read_time),
    INDEX idx_solar_sensor_name (sensor_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci
 PARTITION BY RANGE  COLUMNS(`read_time`)
(PARTITION `p2026` VALUES LESS THAN ('2027-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2027` VALUES LESS THAN ('2028-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2028` VALUES LESS THAN ('2029-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2029` VALUES LESS THAN ('2030-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2030` VALUES LESS THAN ('2031-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2031` VALUES LESS THAN ('2032-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2032` VALUES LESS THAN ('2033-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2033` VALUES LESS THAN ('2034-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2034` VALUES LESS THAN ('2035-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2035` VALUES LESS THAN ('2036-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2036` VALUES LESS THAN ('2037-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `future` VALUES LESS THAN (MAXVALUE) ENGINE = InnoDB);

CREATE TABLE IF NOT EXISTS solar_temperature_sensor (
    id    TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name  VARCHAR(100)     NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_temp_sensor_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4  COLLATE=utf8mb4_uca1400_ai_ci;

insert into solar_temperature_sensor (id, name) values (1, 'temp 1');
insert into solar_temperature_sensor (id, name) values (2, 'temp 2');
insert into solar_temperature_sensor (id, name) values (3, 'temp 3');
insert into solar_temperature_sensor (id, name) values (4, 'temp 4');

CREATE TABLE IF NOT EXISTS solar_temperature_reading (
    id               INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    sensor_id        TINYINT UNSIGNED NOT NULL,
    read_time        DATETIME         NOT NULL,
    value            FLOAT            NOT NULL,
    PRIMARY KEY (id, read_time),
    INDEX idx_temp_sensor_id  (sensor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci
 PARTITION BY RANGE  COLUMNS(`read_time`)
(PARTITION `p2026` VALUES LESS THAN ('2027-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2027` VALUES LESS THAN ('2028-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2028` VALUES LESS THAN ('2029-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2029` VALUES LESS THAN ('2030-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2030` VALUES LESS THAN ('2031-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2031` VALUES LESS THAN ('2032-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2032` VALUES LESS THAN ('2033-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2033` VALUES LESS THAN ('2034-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2034` VALUES LESS THAN ('2035-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2035` VALUES LESS THAN ('2036-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `p2036` VALUES LESS THAN ('2037-01-01 00:00:00') ENGINE = InnoDB,
 PARTITION `future` VALUES LESS THAN (MAXVALUE) ENGINE = InnoDB);