-- Query_Analysis.sql
SELECT 
  pg_name,
  cp_name,
  bpc_name,
  bpi_cf_join_bundle,
  bpi_cf_mat,
  bpi_cf_concat,
  wp_cf_host_id,
  ps_loss_factor,
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

GROUP BY pg_name, cp_name, bpc_name, bpi_cf_join_bundle, bpi_cf_mat, bpi_cf_concat, wp_cf_host_id, ps_loss_factor
ORDER BY pg_name ASC, cp_name ASC, ps_loss_factor DESC;