INSERT INTO aqi_sensor (read_time,pm_1_0_conctrt_std,pm_2_5_conctrt_std,pm_10_conctrt_std,pm_1_0_conctrt_atmosph,pm_2_5_conctrt_atmosph,pm_10_conctrt_atmosph) VALUES
	 (TIMESTAMP(NOW()),3,4,4,3,4,4),
	 (TIMESTAMP(SUBTIME(NOW(), "0:10:00.0")),4,5,5,4,5,5),
	 (TIMESTAMP(SUBTIME(NOW(), "0:20:00.0")),3,4,4,3,4,4),
	 (TIMESTAMP(SUBTIME(NOW(), "0:30:00.0")),3,4,4,3,4,4),
	 (TIMESTAMP(SUBTIME(NOW(), "0:40:00.0")),4,5,5,4,5,5),
	 (TIMESTAMP(SUBTIME(NOW(), "0:50:00.0")),5,7,1007,5,7,7),
	 (TIMESTAMP(SUBTIME(NOW(), "1:00:00.0")),5000,7,7,5,7,7),
	 (TIMESTAMP(SUBTIME(NOW(), "1:10:00.0")),5,7,7,5,7,7),
	 (TIMESTAMP(SUBTIME(NOW(), "1:20:00.0")),4,5,5,4,5,5),
	 (TIMESTAMP(SUBTIME(NOW(), "1:30:00.0")),4,5,5,4,5,5);
