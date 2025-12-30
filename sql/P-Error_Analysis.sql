-- CardinalityEstimator.sql

SELECT ps_sum_card_pc, ps_max_card_pc, ps_sum_card_build, 
ps_max_card_build, ps_sum_card_probe, ps_max_card_probe

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

  GROUP BY ps_sum_card_pc, ps_max_card_pc, ps_sum_card_build, ps_max_card_build, ps_sum_card_probe, ps_max_card_probe;
  
