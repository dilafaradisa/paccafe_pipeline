SELECT MAX(etl_date)
FROM etl_log
WHERE 
    step = :step AND
    component = :component AND
    status = :status AND
    table_name ilike :table_name