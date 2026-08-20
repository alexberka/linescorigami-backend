{{ config(materialized='table') }}

WITH winning_losing AS (
	SELECT
		*,
		CASE WHEN away_score > home_score THEN away_score ELSE home_score END AS winning_score,
		CASE WHEN home_score < away_score THEN home_score ELSE away_score END AS losing_score
	FROM {{ source('raw_linescores', 'raw_linescores') }}
),
ordered AS (
	SELECT
		*,
		COUNT(date) OVER (PARTITION BY winning_score, losing_score) AS instances,
		ROW_NUMBER() OVER (PARTITION BY winning_score, losing_score ORDER BY date ASC) AS instance_count
	FROM winning_losing
)
SELECT
	o.winning_score,
	o.losing_score,
	o.instances,
	o.date AS first_date,
	o.away_team AS first_away_team,
	o.home_team AS first_home_team,
	o."9_shape" AS first_9_shape,
	o."9_score" AS first_9_score,
	o.ex_shape AS first_ex_shape,
	o.ex_score AS first_ex_score,
	o.rhe AS first_rhe,
	latest.date AS latest_date,
	latest.away_team AS latest_away_team,
	latest.home_team AS latest_home_team,
	latest."9_shape" AS latest_9_shape,
	latest."9_score" AS latest_9_score,
	latest.ex_shape AS latest_ex_shape,
	latest.ex_score AS latest_ex_score,
	latest.rhe AS latest_rhe
FROM ordered o
LEFT JOIN (
	SELECT
		*
	FROM ordered
	WHERE instances = instance_count AND instances > 1
) AS latest
ON o.winning_score = latest.winning_score AND o.losing_score = latest.losing_score
WHERE o.instance_count = 1
ORDER BY o.winning_score DESC, o.losing_score DESC
