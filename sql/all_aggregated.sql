-- all_aggregated.sql
-- Unified query that computes ALL metrics but displays only relevant ones based on analysis type
-- Parameters:
--   {ANALYSIS_TYPE} - 'LF', 'QERR', or 'PERR' to control which columns are displayed
--   {DETAIL_METRIC_FILTER} - HAVING clause conditions (can filter on ANY metric)
--   {BPC_NAME_FILTER}, {CF_*_FILTER}, {PG_NAME_FILTER}, {CP_NAME_FILTER} - Standard filters

WITH all_metrics AS (
  SELECT 
    pg_name,
    cp_name,
    bpc_name,
    bpi_cf_join_bundle,
    bpi_cf_mat,
    bpi_cf_concat,
    wp_cf_host_id,
    
    -- Loss Factor metrics
    ROUND(AVG(ps_loss_factor), 2) AS avg_lf,
    ROUND(MEDIAN(ps_loss_factor), 2) AS median_lf,
    ROUND(MAX(ps_loss_factor), 2) AS max_lf,
    ROUND(MIN(ps_loss_factor), 2) AS min_lf,

    -- Q-Error metrics
    ROUND(AVG(ps_qerr_cost_pg), 2) AS avg_qerr,  
    ROUND(MEDIAN(ps_qerr_cost_pg), 2) AS median_qerr,
    ROUND(MAX(ps_qerr_cost_pg), 2) AS max_qerr,
    ROUND(MIN(ps_qerr_cost_pg), 2) AS min_qerr,

    -- P-Error metrics
    ROUND(AVG(ps_p_error), 2) AS avg_perr,
    ROUND(MEDIAN(ps_p_error), 2) AS median_perr,
    ROUND(MAX(ps_p_error), 2) AS max_perr,
    ROUND(MIN(ps_p_error), 2) AS min_perr,

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

  GROUP BY pg_name, cp_name, bpc_name, bpi_cf_join_bundle, bpi_cf_mat, bpi_cf_concat, wp_cf_host_id

  HAVING {DETAIL_METRIC_FILTER}
)

-- Select only the relevant columns based on analysis type
SELECT 
  pg_name,
  cp_name,
  bpc_name,
  bpi_cf_join_bundle,
  bpi_cf_mat,
  bpi_cf_concat,
  wp_cf_host_id,
  {METRIC_COLUMNS}
  cnt

FROM all_metrics

ORDER BY pg_name ASC, cp_name ASC;

