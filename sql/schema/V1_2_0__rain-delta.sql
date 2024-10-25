ALTER TABLE outdoor_sensor 
CHANGE `rain_mm` `rain_cum_mm` DECIMAL(7,2) NOT NULL comment 'cumulative rain in mm since last reset',
add column `rain_delta_mm` DECIMAL(7,2) NOT NULL comment 'rain in mm since the last sensor read' AFTER `rain_cum_mm`;

-- seed existing data
update outdoor_sensor curr
inner join outdoor_sensor prev on (curr.id-1) = prev.id
set curr.rain_delta_mm = if (curr.rain_cum_mm - prev.rain_cum_mm >= 0, curr.rain_cum_mm - prev.rain_cum_mm,  curr.rain_cum_mm)  
