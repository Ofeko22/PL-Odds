-- Home/Away wins and draws as (%)
SELECT season,
       ROUND(100.0*SUM(FTR='H')/COUNT(*)) AS home_wins,
       ROUND(100.0*SUM(FTR='A')/COUNT(*)) AS away_wins,
       ROUND(100.0*SUM(FTR='D')/COUNT(*)) AS draws
FROM matches
GROUP BY season;