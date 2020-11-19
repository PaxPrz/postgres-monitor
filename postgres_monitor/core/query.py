datname_query = 'SELECT datname FROM pg_database WHERE oid = {oid}'

stat_query = '''SELECT 'session_stats' AS chart_name, row_to_json(t) AS chart_data  
  FROM (SELECT 
    (SELECT count(*) FROM pg_stat_activity WHERE datname = '{datname}') AS "Total",
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND datname = '{datname}')  AS "Active", 
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle' AND datname = '{datname}')  AS "Idle"
  ) t
  UNION ALL
  SELECT 'tps_stats' AS chart_name, row_to_json(t) AS chart_data 
  FROM (SELECT 
    (SELECT sum(xact_commit) + sum(xact_rollback) FROM pg_stat_database WHERE datname = '{datname}') AS "Transactions",
    (SELECT sum(xact_commit) FROM pg_stat_database WHERE datname = '{datname}') AS "Commits",
    (SELECT sum(xact_rollback) FROM pg_stat_database WHERE datname = '{datname}') AS "Rollbacks"
 ) t;
 '''

all_stat_query  = '''SELECT 'session_stats' AS chart_name, row_to_json(t) AS chart_data  
  FROM (SELECT 
    (SELECT count(*) FROM pg_stat_activity) AS "Total",
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active')  AS "Active", 
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle')  AS "Idle"
  ) t
  UNION ALL
  SELECT 'tps_stats' AS chart_name, row_to_json(t) AS chart_data 
  FROM (SELECT 
    (SELECT sum(xact_commit) + sum(xact_rollback) FROM pg_stat_database) AS "Transactions",
    (SELECT sum(xact_commit) FROM pg_stat_database) AS "Commits",
    (SELECT sum(xact_rollback) FROM pg_stat_database) AS "Rollbacks"
 ) t;
 '''

db_list_query = 'SELECT DISTINCT datname from pg_stat_activity'

tuple_write_operation = '''SELECT 'ti_stats' AS chart_name, row_to_json(t) AS chart_data
FROM (SELECT
   (SELECT sum(tup_inserted) FROM pg_stat_database WHERE datname = '{datname}' AS "Inserts",
   (SELECT sum(tup_updated) FROM pg_stat_database WHERE datname = '{datname}' AS "Updates",
   (SELECT sum(tup_deleted) FROM pg_stat_database WHERE datname = '{datname}' AS "Deletes"
) t;
'''

tuple_read_operation = '''SELECT 'ti_stats' AS chart_name, row_to_json(t) AS chart_data
FROM (SELECT
   (SELECT sum(tup_fetched) FROM pg_stat_database WHERE datname = '{datname}' AS "Fetches",
   (SELECT sum(tup_returned) FROM pg_stat_database WHERE datname = '{datname}' AS "Returns"
) t;
'''

blocks_reads = '''SELECT 'bio_stats' AS chart_name, row_to_json(t) AS chart_data
FROM (SELECT
   (SELECT sum(blks_read) FROM pg_stat_database WHERE datname = '{datname}' AS "Reads",
   (SELECT sum(blks_hit) FROM pg_stat_database WHERE datname = '{datname}' AS "Hits"
) t;
'''