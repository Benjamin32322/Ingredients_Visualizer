-- DetailQuery.sql
-- Query for detailed filtering based on metric comparison
-- Parameters:
--   {DETAIL_METRIC_FILTER} - Dynamic HAVING conditions for selected metrics
--     Examples: 
--       "avg_lf > 10.0"
--       "median_lf BETWEEN 5.0 AND 15.0"
--       "avg_lf > 10.0 AND median_qerr < 20.0"
--   {BPC_NAME_FILTER}, {CF_*_FILTER}, {PG_FILTER}, {CP_FILTER} - Standard filters from main query

SELECT 
  pg_name,
  cp_name,
  bpc_name,
  bpi_cf_join_bundle,
  bpi_cf_mat,
  bpi_cf_concat,
  wp_cf_host_id,
  COUNT(*) AS cnt

FROM v_ps_base 

WHERE 1=1
  {BPC_NAME_FILTER}
  {CF_JOIN_BUNDLE_FILTER}
  {CF_MAT_FILTER}
  {CF_CONCAT_FILTER}
  {CF_HOST_ID_FILTER}
  {PG_FILTER}
  {CP_FILTER}

GROUP BY pg_name, cp_name, bpc_name, bpi_cf_join_bundle, bpi_cf_mat, bpi_cf_concat, wp_cf_host_id

HAVING {DETAIL_METRIC_FILTER}

ORDER BY pg_name ASC, cp_name ASC;

