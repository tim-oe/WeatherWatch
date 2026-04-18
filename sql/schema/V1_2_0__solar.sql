-- -----------------------------------------------------
-- Solar charge controller readings (Renogy Rover/Wanderer)
-- Source: SolarReading (extends SensorReading)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS solar_readings (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  -- SensorReading base fields
  type            VARCHAR(32)     NOT NULL DEFAULT 'solar',
  name            VARCHAR(64)     NOT NULL,
  read_time       DATETIME(3)     NOT NULL,
  read_duration_ms DECIMAL(10,2)  NULL,

  -- Device info
  model           VARCHAR(64)     NULL,
  device_id       SMALLINT UNSIGNED NULL,

  -- Battery status
  battery_percentage           TINYINT UNSIGNED NULL COMMENT 'SOC %',
  battery_voltage              DECIMAL(6,1)     NULL COMMENT 'Volts',
  battery_current              DECIMAL(7,2)     NULL COMMENT 'Amps',
  battery_temperature          TINYINT          NULL COMMENT 'Celsius (signed)',
  battery_type                 VARCHAR(16)      NULL COMMENT 'open, sealed, gel, lithium, custom',

  -- Controller status
  controller_temperature       TINYINT          NULL COMMENT 'Celsius (signed)',
  charging_status              VARCHAR(24)      NULL COMMENT 'deactivated, activated, mppt, equalizing, boost, floating, current_limiting',

  -- Load output
  load_status                  VARCHAR(8)       NULL COMMENT 'on, off',
  load_voltage                 DECIMAL(6,1)     NULL COMMENT 'Volts',
  load_current                 DECIMAL(7,2)     NULL COMMENT 'Amps',
  load_power                   SMALLINT UNSIGNED NULL COMMENT 'Watts',

  -- PV (solar panel) input
  pv_voltage                   DECIMAL(6,1)     NULL COMMENT 'Volts',
  pv_current                   DECIMAL(7,2)     NULL COMMENT 'Amps',
  pv_power                     SMALLINT UNSIGNED NULL COMMENT 'Watts',

  -- Daily statistics
  battery_min_voltage_today    DECIMAL(6,1)     NULL COMMENT 'Volts',
  battery_max_voltage_today    DECIMAL(6,1)     NULL COMMENT 'Volts',
  max_charging_current_today   DECIMAL(7,2)     NULL COMMENT 'Amps',
  max_discharging_current_today DECIMAL(7,2)    NULL COMMENT 'Amps',
  max_charging_power_today     SMALLINT UNSIGNED NULL COMMENT 'Watts',
  max_discharging_power_today  SMALLINT UNSIGNED NULL COMMENT 'Watts',
  charging_amp_hours_today     SMALLINT UNSIGNED NULL COMMENT 'Ah',
  discharging_amp_hours_today  SMALLINT UNSIGNED NULL COMMENT 'Ah',
  power_generation_today       DECIMAL(10,1)    NULL COMMENT 'Wh',
  power_consumption_today      DECIMAL(10,1)    NULL COMMENT 'Wh',

  -- Lifetime statistics
  power_generation_total       INT UNSIGNED     NULL COMMENT 'Wh cumulative',

PRIMARY KEY (`id`, `read_time`),
UNIQUE KEY solar_unique_sensor (read_time),
INDEX idx_solar_name_time (name, read_time),
INDEX idx_solar_read_time (read_time)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4
  PARTITION BY RANGE( UNIX_TIMESTAMP(read_time) ) (
    PARTITION p2026 VALUES LESS THAN (UNIX_TIMESTAMP('2027-01-01')),
    PARTITION p2027 VALUES LESS THAN (UNIX_TIMESTAMP('2028-01-01')),
    PARTITION p2028 VALUES LESS THAN (UNIX_TIMESTAMP('2029-01-01')),
    PARTITION p2029 VALUES LESS THAN (UNIX_TIMESTAMP('2030-01-01')),
    PARTITION p2030 VALUES LESS THAN (UNIX_TIMESTAMP('2031-01-01')),
    PARTITION p2031 VALUES LESS THAN (UNIX_TIMESTAMP('2032-01-01')),
    PARTITION p2032 VALUES LESS THAN (UNIX_TIMESTAMP('2033-01-01')),
    PARTITION p2033 VALUES LESS THAN (UNIX_TIMESTAMP('2034-01-01')),
    PARTITION p2034 VALUES LESS THAN (UNIX_TIMESTAMP('2035-01-01')),
    PARTITION p2035 VALUES LESS THAN (UNIX_TIMESTAMP('2036-01-01')),
    PARTITION p2036 VALUES LESS THAN (UNIX_TIMESTAMP('2037-01-01')),
    PARTITION future VALUES LESS THAN MAXVALUE
  );

-- -----------------------------------------------------
-- Temperature sensor readings (DS18B20 1-Wire)
-- Source: TemperatureReading (extends SensorReading)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS temperature_readings (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  -- SensorReading base fields
  type            VARCHAR(32)     NOT NULL DEFAULT 'temperature',
  name            VARCHAR(64)     NOT NULL,
  read_time       DATETIME(3)     NOT NULL,
  read_duration_ms DECIMAL(10,2)  NULL,

  -- Temperature data
  value           DECIMAL(6,3)    NOT NULL COMMENT 'Temperature value',
  unit            VARCHAR(4)      NOT NULL DEFAULT 'C' COMMENT 'Celsius, Fahrenheit, etc.',

  PRIMARY KEY (`id`, `read_time`),
  UNIQUE KEY temperature_unique_sensor (read_time),
  INDEX idx_temp_name_time (name, read_time),
  INDEX idx_temp_read_time (read_time)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4
  PARTITION BY RANGE( UNIX_TIMESTAMP(read_time) ) (
    PARTITION p2026 VALUES LESS THAN (UNIX_TIMESTAMP('2027-01-01')),
    PARTITION p2027 VALUES LESS THAN (UNIX_TIMESTAMP('2028-01-01')),
    PARTITION p2028 VALUES LESS THAN (UNIX_TIMESTAMP('2029-01-01')),
    PARTITION p2029 VALUES LESS THAN (UNIX_TIMESTAMP('2030-01-01')),
    PARTITION p2030 VALUES LESS THAN (UNIX_TIMESTAMP('2031-01-01')),
    PARTITION p2031 VALUES LESS THAN (UNIX_TIMESTAMP('2032-01-01')),
    PARTITION p2032 VALUES LESS THAN (UNIX_TIMESTAMP('2033-01-01')),
    PARTITION p2033 VALUES LESS THAN (UNIX_TIMESTAMP('2034-01-01')),
    PARTITION p2034 VALUES LESS THAN (UNIX_TIMESTAMP('2035-01-01')),
    PARTITION p2035 VALUES LESS THAN (UNIX_TIMESTAMP('2036-01-01')),
    PARTITION p2036 VALUES LESS THAN (UNIX_TIMESTAMP('2037-01-01')),
    PARTITION future VALUES LESS THAN MAXVALUE
  );
