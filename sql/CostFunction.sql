-- CostFunction.sql

SELECT ps_qerr_cost_pg, ps_qerr_opt_cost_pg,

  ROUND(AVG(ps_qerr_cost_pg), 4) AS avg_qerr,
  ROUND(MEDIAN(ps_qerr_cost_pg), 4) AS median_qerr,
  ROUND(MAX(ps_qerr_cost_pg), 4) AS max_qerr,
  COUNT(*) AS cnt

FROM plan_summary ps

JOIN work_package        wp  ON wp.wp_id   = ps.ps_wp
JOIN plan_generator      pg  ON pg.pg_id   = wp.wp_pg
JOIN card_provider       cp  ON cp.cp_id   = wp.wp_cp
JOIN build_plan_instance bpi ON bpi.bpi_id = wp.wp_bp
JOIN build_plan_class    bpc ON bpc.bpc_id = bpi.bpi_bpc

WHERE 1=1
  {BPC_NAME_FILTER}
  {CF_JOIN_BUNDLE_FILTER}
  {CF_MAT_FILTER}
  {CF_CONCAT_FILTER}
  {CF_HOST_ID_FILTER}
  {PG_NAME_FILTER}
  {CP_NAME_FILTER}

GROUP BY ps_qerr_cost_pg, ps_qerr_opt_cost_pg
ORDER BY ps_qerr_cost_pg DESC;