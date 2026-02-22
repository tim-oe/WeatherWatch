-- CREATE TABLE aqi_sensor_tmp AS
-- SELECT *
-- FROM aqi_sensor

--   SELECT * FROM aqi_sensor
--     WHERE pm_1_0_conctrt_std > 100
--        OR pm_2_5_conctrt_std > 100
--        OR pm_10_conctrt_std > 100
--        OR pm_1_0_conctrt_atmosph > 100
--        OR pm_2_5_conctrt_atmosph > 100
--        OR pm_10_conctrt_atmosph > 100
--     ORDER BY id ASC;

-- call aqi_clean(100);

-- drop table aqi_sensor_tmp;

-- the aqi sensor get errant readings so we need to clean them
-- we do this by replacing the outlying readings with the average of the nearest valid neighbors
-- we do this by using a cursor to iterate through the records and replace the outlying readings
-- we do this by using a cursor to iterate through the records and replace the outlying readings

DELIMITER //

DROP PROCEDURE IF EXISTS aqi_clean //

CREATE PROCEDURE aqi_clean(IN p_ceiling INT)
BEGIN
    DECLARE v_id BIGINT UNSIGNED;
    DECLARE v_done INT DEFAULT FALSE;

    DECLARE v_prev_pm_1_0_std INT;
    DECLARE v_prev_pm_2_5_std INT;
    DECLARE v_prev_pm_10_std INT;
    DECLARE v_prev_pm_1_0_atm INT;
    DECLARE v_prev_pm_2_5_atm INT;
    DECLARE v_prev_pm_10_atm INT;

    DECLARE v_next_pm_1_0_std INT;
    DECLARE v_next_pm_2_5_std INT;
    DECLARE v_next_pm_10_std INT;
    DECLARE v_next_pm_1_0_atm INT;
    DECLARE v_next_pm_2_5_atm INT;
    DECLARE v_next_pm_10_atm INT;

    DECLARE v_has_prev BOOLEAN;
    DECLARE v_has_next BOOLEAN;

    DECLARE cur CURSOR FOR
        SELECT id FROM aqi_sensor
        WHERE pm_1_0_conctrt_std > p_ceiling
           OR pm_2_5_conctrt_std > p_ceiling
           OR pm_10_conctrt_std > p_ceiling
           OR pm_1_0_conctrt_atmosph > p_ceiling
           OR pm_2_5_conctrt_atmosph > p_ceiling
           OR pm_10_conctrt_atmosph > p_ceiling
        ORDER BY id ASC;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_id;
        IF v_done THEN
            LEAVE read_loop;
        END IF;

        SET v_has_prev = FALSE;
        SET v_has_next = FALSE;

        SELECT pm_1_0_conctrt_std, pm_2_5_conctrt_std, pm_10_conctrt_std,
               pm_1_0_conctrt_atmosph, pm_2_5_conctrt_atmosph, pm_10_conctrt_atmosph
          INTO v_prev_pm_1_0_std, v_prev_pm_2_5_std, v_prev_pm_10_std,
               v_prev_pm_1_0_atm, v_prev_pm_2_5_atm, v_prev_pm_10_atm
          FROM aqi_sensor
         WHERE id < v_id
           AND pm_1_0_conctrt_std <= p_ceiling
           AND pm_2_5_conctrt_std <= p_ceiling
           AND pm_10_conctrt_std <= p_ceiling
           AND pm_1_0_conctrt_atmosph <= p_ceiling
           AND pm_2_5_conctrt_atmosph <= p_ceiling
           AND pm_10_conctrt_atmosph <= p_ceiling
         ORDER BY id DESC
         LIMIT 1;

        IF FOUND_ROWS() > 0 THEN
            SET v_has_prev = TRUE;
        END IF;

        SELECT pm_1_0_conctrt_std, pm_2_5_conctrt_std, pm_10_conctrt_std,
               pm_1_0_conctrt_atmosph, pm_2_5_conctrt_atmosph, pm_10_conctrt_atmosph
          INTO v_next_pm_1_0_std, v_next_pm_2_5_std, v_next_pm_10_std,
               v_next_pm_1_0_atm, v_next_pm_2_5_atm, v_next_pm_10_atm
          FROM aqi_sensor
         WHERE id > v_id
           AND pm_1_0_conctrt_std <= p_ceiling
           AND pm_2_5_conctrt_std <= p_ceiling
           AND pm_10_conctrt_std <= p_ceiling
           AND pm_1_0_conctrt_atmosph <= p_ceiling
           AND pm_2_5_conctrt_atmosph <= p_ceiling
           AND pm_10_conctrt_atmosph <= p_ceiling
         ORDER BY id ASC
         LIMIT 1;

        IF FOUND_ROWS() > 0 THEN
            SET v_has_next = TRUE;
        END IF;

        UPDATE aqi_sensor
           SET pm_1_0_conctrt_std = CASE
                   WHEN pm_1_0_conctrt_std <= p_ceiling THEN pm_1_0_conctrt_std
                   WHEN v_has_prev AND v_has_next THEN (v_prev_pm_1_0_std + v_next_pm_1_0_std) DIV 2
                   WHEN v_has_prev THEN v_prev_pm_1_0_std
                   WHEN v_has_next THEN v_next_pm_1_0_std
                   ELSE pm_1_0_conctrt_std
               END,
               pm_2_5_conctrt_std = CASE
                   WHEN pm_2_5_conctrt_std <= p_ceiling THEN pm_2_5_conctrt_std
                   WHEN v_has_prev AND v_has_next THEN (v_prev_pm_2_5_std + v_next_pm_2_5_std) DIV 2
                   WHEN v_has_prev THEN v_prev_pm_2_5_std
                   WHEN v_has_next THEN v_next_pm_2_5_std
                   ELSE pm_2_5_conctrt_std
               END,
               pm_10_conctrt_std = CASE
                   WHEN pm_10_conctrt_std <= p_ceiling THEN pm_10_conctrt_std
                   WHEN v_has_prev AND v_has_next THEN (v_prev_pm_10_std + v_next_pm_10_std) DIV 2
                   WHEN v_has_prev THEN v_prev_pm_10_std
                   WHEN v_has_next THEN v_next_pm_10_std
                   ELSE pm_10_conctrt_std
               END,
               pm_1_0_conctrt_atmosph = CASE
                   WHEN pm_1_0_conctrt_atmosph <= p_ceiling THEN pm_1_0_conctrt_atmosph
                   WHEN v_has_prev AND v_has_next THEN (v_prev_pm_1_0_atm + v_next_pm_1_0_atm) DIV 2
                   WHEN v_has_prev THEN v_prev_pm_1_0_atm
                   WHEN v_has_next THEN v_next_pm_1_0_atm
                   ELSE pm_1_0_conctrt_atmosph
               END,
               pm_2_5_conctrt_atmosph = CASE
                   WHEN pm_2_5_conctrt_atmosph <= p_ceiling THEN pm_2_5_conctrt_atmosph
                   WHEN v_has_prev AND v_has_next THEN (v_prev_pm_2_5_atm + v_next_pm_2_5_atm) DIV 2
                   WHEN v_has_prev THEN v_prev_pm_2_5_atm
                   WHEN v_has_next THEN v_next_pm_2_5_atm
                   ELSE pm_2_5_conctrt_atmosph
               END,
               pm_10_conctrt_atmosph = CASE
                   WHEN pm_10_conctrt_atmosph <= p_ceiling THEN pm_10_conctrt_atmosph
                   WHEN v_has_prev AND v_has_next THEN (v_prev_pm_10_atm + v_next_pm_10_atm) DIV 2
                   WHEN v_has_prev THEN v_prev_pm_10_atm
                   WHEN v_has_next THEN v_next_pm_10_atm
                   ELSE pm_10_conctrt_atmosph
               END
         WHERE id = v_id;

    END LOOP;

    CLOSE cur;
END //

DELIMITER ;
