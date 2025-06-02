SELECT
    DATE(TIMESTAMP_MILLIS(properties.time)) AS event_date,
    TIME(TIMESTAMP_MILLIS(properties.time)) AS event_time,
    properties.mag AS magnitude,
    properties.place AS location_desc,
    geometry.coordinates[0] AS longitude,
    geometry.coordinates[1] AS latitude,
    geometry.coordinates[2] AS depth,
    ST_GEOGPOINT(geometry.coordinates[0], geometry.coordinates[1]) AS geo,
    properties.type as type,
    properties.url as url
FROM
    `starlingcontacts-data-dev.staging_temp.earthquake_{{ ds_nodash }}`
;