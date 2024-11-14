-- rain delta fix up.
update outdoor_sensor curr
inner join outdoor_sensor prev on (curr.id-1) = prev.id
set curr.rain_delta_mm = if (curr.rain_cum_mm - prev.rain_cum_mm >= 0, curr.rain_cum_mm - prev.rain_cum_mm,  curr.rain_cum_mm)  
