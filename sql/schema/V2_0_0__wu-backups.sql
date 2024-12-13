CREATE TABLE `backup_metrics` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `backup_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `to_date` date NOT NULL,
    `from_date` date NOT NULL,
    `table_name` VARCHAR(64) NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE KEY unique_backup (`table_name`, `to_date`, `from_date`),
    KEY `table_name_idx` (`table_name`),
    KEY `to_date_idx` (`to_date`),
    KEY `from_date_idx` (`from_date`)
) ENGINE=INNODB DEFAULT CHARSET=utf8mb4;
