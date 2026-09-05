-- 4.1: EXPERIMENT SUMMARY - Group Statistics
SELECT 
    group,
    COUNT(DISTINCT user_id) AS users,
    SUM(converted) AS conversions,
    ROUND(SUM(converted)::FLOAT / COUNT(*)::FLOAT, 6) AS conversion_rate
FROM 'data/processed/clean_ab_data.parquet'
GROUP BY group
ORDER BY group;
 
 -- 4.2: DAILY SUMMARY - Time Series by Group
SELECT 
    experiment_date,
    group,
    COUNT(DISTINCT user_id) AS users,
    SUM(converted) AS conversions,
    ROUND(SUM(converted)::FLOAT / COUNT(*)::FLOAT, 6) AS conversion_rate
FROM 'data/processed/clean_ab_data.parquet'
GROUP BY experiment_date, group
ORDER BY experiment_date, group;
 
 
-- 4.3: DATA VERIFICATION - Quality Assurance
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT user_id) AS distinct_user_ids,
    MIN(experiment_date) AS min_experiment_date,
    MAX(experiment_date) AS max_experiment_date
FROM 'data/processed/clean_ab_data.parquet';
 