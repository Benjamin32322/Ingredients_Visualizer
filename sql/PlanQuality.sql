-- PlanQuality.sql

SELECT 
  pg_name,
  cp_name,
  bpc_name,
  bpi_cf_join_bundle,
  bpi_cf_mat,
  bpi_cf_concat,
  wp_cf_host_id,
  

  ROUND(AVG(ps_loss_factor), 2) AS avg_lf,
  ROUND(MEDIAN(ps_loss_factor), 2) AS median_lf,
  ROUND(MAX(ps_loss_factor), 2) AS max_lf,
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

GROUP BY pg_name, cp_name, bpc_name, bpi_cf_join_bundle, bpi_cf_mat, bpi_cf_concat, wp_cf_host_id
ORDER BY pg_name ASC, cp_name ASC;
