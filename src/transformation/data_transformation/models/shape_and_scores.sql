{{ config(materialized='table') }}

WITH ordered AS (
	SELECT
		*,
		COUNT(date) OVER (PARTITION BY "9_shape", "9_score", ex_shape, ex_score) AS instances,
		ROW_NUMBER() OVER (PARTITION BY "9_shape", "9_score", ex_shape, ex_score ORDER BY date ASC) AS instance_count
	FROM {{ source('raw_linescores', 'raw_linescores') }}
)
SELECT
	o."9_shape",
	o."9_score",
	o.ex_shape,
	o.ex_score,
	o.instances,
	o.date AS first_date,
	o.away_team AS first_away_team,
	o.home_team AS first_home_team,
	o.rhe AS first_rhe,
	latest.date AS latest_date,
	latest.away_team AS latest_away_team,
	latest.home_team AS latest_home_team,
	latest.rhe AS latest_rhe
FROM ordered o
LEFT JOIN (
	SELECT
		*
	FROM ordered
	WHERE instances = instance_count AND instances > 1
) AS latest
ON o."9_shape" = latest."9_shape" AND o."9_score" = latest."9_score" AND o.ex_shape = latest.ex_shape AND o.ex_score = latest.ex_score 
WHERE o.instance_count = 1
ORDER BY instances DESC, "9_shape" ASC, ex_shape ASC
