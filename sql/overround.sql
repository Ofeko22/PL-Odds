SELECT season,
       ROUND((AVG((1.0/B365H)+(1.0/B365D)+(1.0/B365A))-1)*100,2) AS b365_overround,
       ROUND((AVG((1.0/PSH)+(1.0/PSD)+(1.0/PSA))-1)*100,2) AS pinnacle_oveeround
FROM matches
GROUP BY season;