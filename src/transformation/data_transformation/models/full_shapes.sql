{{ config(materialized='table') }}

WITH ordered AS (
	SELECT
		*,
		COUNT(date) OVER (PARTITION BY "9_shape", ex_shape) AS instances,
		ROW_NUMBER() OVER (PARTITION BY "9_shape", ex_shape ORDER BY date ASC) AS instance_count
	FROM {{ source('raw_linescores', 'raw_linescores') }}
)
SELECT
	o."9_shape",
	o.ex_shape,
	o.instances,
	o.date AS first_date,
	o.away_team AS first_away_team,
	o.home_team AS first_home_team,
	o."9_score" AS first_9_score,
	o.ex_score AS first_ex_score,
	o.rhe AS first_rhe,
	latest.date AS latest_date,
	latest.away_team AS latest_away_team,
	latest.home_team AS latest_home_team,
	latest."9_score" AS latest_9_score,
	latest.ex_score AS latest_ex_score,
	latest.rhe AS latest_rhe
FROM ordered o
LEFT JOIN (
	SELECT
		*
	FROM ordered
	WHERE instances = instance_count AND instances > 1
) AS latest
ON o."9_shape" = latest."9_shape" AND o.ex_shape = latest.ex_shape
WHERE o.instance_count = 1
ORDER BY instances DESC, "9_shape" ASC
