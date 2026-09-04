DESCRIBE SELECT *

FROM read_parquet(

  'data/processed/practice_campaign.parquet'

);

 

SELECT *

FROM read_parquet(

  'data/processed/practice_campaign.parquet'

)

LIMIT 5;



CREATE OR REPLACE VIEW group_summary AS
SELECT
  version,
  COUNT(*) AS users,
  SUM(converted) AS conversions,
  AVG(converted) AS conversion_rate
FROM read_parquet(
  'data/processed/practice_campaign.parquet'
)
GROUP BY version
ORDER BY version;


CREATE OR REPLACE VIEW daily_conversion AS
SELECT
  CAST(event_date AS DATE) AS event_date,
  version,
  COUNT(*) AS users,
  SUM(converted) AS conversions,
  AVG(converted) AS conversion_rate
FROM read_parquet(
  'data/processed/practice_campaign.parquet'
)
GROUP BY event_date, version
ORDER BY event_date, version;


CREATE OR REPLACE VIEW data_verification AS
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT visitor_id) AS distinct_visitors,
  MIN(CAST(event_date AS DATE)) AS min_date,
  MAX(CAST(event_date AS DATE)) AS max_date
FROM read_parquet(
  'data/processed/practice_campaign.parquet'
);
 
 
CREATE OR REPLACE VIEW converted_only AS
SELECT visitor_id, version, event_date
FROM read_parquet(
  'data/processed/practice_campaign.parquet'
)
WHERE converted = 1;
 