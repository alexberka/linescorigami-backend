{{ config(materialized='table') }}

WITH ordered AS (
	SELECT
		*,
		COUNT(date) OVER (PARTITION BY rhe) AS instances,
		ROW_NUMBER() OVER (PARTITION BY rhe ORDER BY date ASC) AS instance_count
	FROM {{ source('raw_linescores', 'raw_linescores') }}
)
SELECT
	o.rhe,
	o.instances,
	o.date AS first_date,
	o.away_team AS first_away_team,
	o.home_team AS first_home_team,
	o."9_shape" AS first_9_shape,
	o."9_score" AS first_9_score,
	o.ex_shape AS first_ex_shape,
	o.ex_score AS first_ex_score,
	latest.date AS latest_date,
	latest.away_team AS latest_away_team,
	latest.home_team AS latest_home_team,
	latest."9_shape" AS latest_9_shape,
	latest."9_score" AS latest_9_score,
	latest.ex_shape AS latest_ex_shape,
	latest.ex_score AS latest_ex_score
FROM ordered o
LEFT JOIN (
	SELECT
		*
	FROM ordered
	WHERE instances = instance_count AND instances > 1
) AS latest
ON o.rhe = latest.rhe
WHERE o.instance_count = 1
ORDER BY instances DESC, rhe ASC
