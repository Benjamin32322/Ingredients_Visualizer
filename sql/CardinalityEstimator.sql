-- CardinalityEstimator.sql

SELECT ps_sum_card_pc, ps_max_card_pc, ps_sum_card_build, 
ps_max_card_build, ps_sum_card_probe, ps_max_card_probe

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

  GROUP BY ps_sum_card_pc, ps_max_card_pc, ps_sum_card_build, ps_max_card_build, ps_sum_card_probe, ps_max_card_probe;
  
