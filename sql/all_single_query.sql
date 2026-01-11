-- all_single_query.sql
-- Single query results (no aggregation) that computes ALL metrics but displays only relevant ones
-- Used when specific queries are selected in "Query Selection"
-- Parameters:
--   {ANALYSIS_TYPE} - 'LF', 'QERR', or 'PERR' to control which columns are displayed
--   {DETAIL_METRIC_FILTER} - WHERE clause conditions (can filter on ANY metric)
--   {BPC_NAME_FILTER}, {CF_*_FILTER}, {PG_NAME_FILTER}, {CP_NAME_FILTER}, {QUERY_NAME_FILTER} - Standard filters

WITH all_metrics AS (
  SELECT 
    ps_qg,
    pg_name,
    cp_name,
    bpc_name,
    bpi_cf_join_bundle,
    bpi_cf_mat,
    bpi_cf_concat,
    wp_cf_host_id,
    
    -- Loss Factor metric
    ROUND(ps_loss_factor, 2) AS lf,
    
    -- Q-Error metric
    ROUND(ps_qerr_cost_pg, 2) AS qerr,
    
    -- P-Error metric
    ROUND(ps_p_error, 2) AS perr,

    COUNT(*) AS cnt

  FROM v_ps_base 

  WHERE 1=1
    {BPC_NAME_FILTER}
    {CF_JOIN_BUNDLE_FILTER}
    {CF_MAT_FILTER}
    {CF_CONCAT_FILTER}
    {CF_HOST_ID_FILTER}
    {PG_NAME_FILTER}
    {CP_NAME_FILTER}
    {QUERY_NAME_FILTER}
    
  GROUP BY pg_name, cp_name, bpc_name, bpi_cf_join_bundle, bpi_cf_mat, bpi_cf_concat, wp_cf_host_id, ps_qg, ps_loss_factor, ps_qerr_cost_pg, ps_p_error

  HAVING {DETAIL_METRIC_FILTER}
)

-- Select only the relevant columns based on analysis type
SELECT 
  ps_qg,
  pg_name,
  cp_name,
  bpc_name,
  bpi_cf_join_bundle,
  bpi_cf_mat,
  bpi_cf_concat,
  wp_cf_host_id,
  {METRIC_COLUMNS},
  cnt

  

FROM all_metrics

ORDER BY ps_qg ASC, pg_name ASC, cp_name ASC;

