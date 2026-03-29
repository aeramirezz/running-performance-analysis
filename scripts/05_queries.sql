-- 1. Top 5 longest runs
SELECT
    run_id,
    datetime,
    distance_km,
    duration_min,
    pace_min_km
FROM runs
ORDER BY distance_km DESC
LIMIT 5;


-- 2. Number of sessions per year
SELECT
    year,
    COUNT(*) AS total_sessions
FROM runs
GROUP BY year
ORDER BY year;


-- 3. Which month do I run the most?
SELECT
    month,
    COUNT(*) AS total_sessions
FROM runs
GROUP BY month
ORDER BY total_sessions DESC;


-- 4. Average pace: outdoor vs indoor
SELECT
    CASE WHEN indoor = 1 THEN 'indoor' ELSE 'outdoor' END AS session_type,
    COUNT(*)                        AS total_sessions,
    ROUND(AVG(pace_min_km), 2)      AS avg_pace_min_km,
    ROUND(AVG(distance_km), 2)      AS avg_distance_km
FROM runs
GROUP BY indoor;


-- 5. Which day of the week do I run fastest?
SELECT
    day_of_week,
    COUNT(*)                    AS total_sessions,
    ROUND(AVG(pace_min_km), 2)  AS avg_pace_min_km
FROM runs
GROUP BY day_of_week
ORDER BY avg_pace_min_km ASC;


-- 6. Top 5 fastest 4km runs
SELECT
    run_id,
    datetime,
    distance_km,
    duration_min,
    pace_min_km
FROM runs
WHERE distance_km BETWEEN 3.95 AND 4.05
ORDER BY pace_min_km ASC
LIMIT 5;


-- 7. Top 5 runs with highest elevation gain
SELECT
    r.run_id,
    r.datetime,
    r.distance_km,
    r.pace_min_km,
    ro.elevation_gain,
    ro.elevation_loss
FROM runs r
JOIN routes ro ON r.run_id = ro.run_id
ORDER BY ro.elevation_gain DESC
LIMIT 5;


-- 8. Does more elevation gain lead to slower pace?
SELECT
    CASE
        WHEN ro.elevation_gain < 20  THEN 'low (< 20m)'
        WHEN ro.elevation_gain < 50  THEN 'medium (20-50m)'
        ELSE                              'high (> 50m)'
    END                             AS elevation_category,
    COUNT(*)                        AS total_sessions,
    ROUND(AVG(r.pace_min_km), 2)    AS avg_pace_min_km,
    ROUND(AVG(r.distance_km), 2)    AS avg_distance_km
FROM runs r
JOIN routes ro ON r.run_id = ro.run_id
GROUP BY elevation_category
ORDER BY avg_pace_min_km ASC;


-- 9. In which climate conditions do I burn the most calories?
SELECT
    CASE
        WHEN c.temperature_c < 20 THEN 'cool (< 20°C)'
        ELSE                           'warm (>= 20°C)'
    END                                 AS temp_category,
    COUNT(*)                            AS total_sessions,
    ROUND(AVG(p.active_calories), 1)    AS avg_calories,
    ROUND(AVG(r.distance_km), 2)        AS avg_distance_km
FROM runs r
JOIN conditions  c ON r.run_id = c.run_id
JOIN performance p ON r.run_id = p.run_id
WHERE p.active_calories IS NOT NULL
  AND c.temperature_c   IS NOT NULL
GROUP BY temp_category
ORDER BY avg_calories DESC;


-- 10. Average performance by starting zone
--     Zones are defined by rounding coordinates to 2 decimal places
SELECT
    ROUND(ro.start_lat, 2)          AS zone_lat,
    ROUND(ro.start_lon, 2)          AS zone_lon,
    COUNT(*)                        AS total_sessions,
    ROUND(AVG(r.distance_km), 2)    AS avg_distance_km,
    ROUND(AVG(r.pace_min_km), 2)    AS avg_pace_min_km,
    ROUND(AVG(p.avg_heart_rate), 1) AS avg_heart_rate
FROM runs r
JOIN routes      ro ON r.run_id = ro.run_id
JOIN performance p  ON r.run_id = p.run_id
GROUP BY zone_lat, zone_lon
ORDER BY total_sessions DESC;
