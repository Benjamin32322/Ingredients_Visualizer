-- Plangüte.sql

-- cf_est
SELECT 
  pg_name,
  'cf_est' AS cf,
  cp_name,
  ROUND(AVG(ps_loss_factor), 2) AS avg_lf,
  ROUND(MEDIAN(ps.ps_loss_factor), 2) AS median_lf,
  ROUND(MAX(ps_loss_factor), 2) AS max_lf,
  COUNT(*) AS cnt

FROM v_ps_base

WHERE bpc_name = 'BpTrad'
  AND bpi_cf_join_bundle = 0
  AND bpi_cf_mat = 0
  AND bpi_cf_concat = 0
  AND wp_cf_host_id = 2
  AND LOWER(pg_name) IN ('dpccp','dpccpcout','goocost','goocard','simplisquared')
  AND LOWER(cp_name) IN ('cp_true','cp_ia_m','cp_ia_s','cp_ia_l','cp_crude_base','cp_crude_sel','cp_join_base','cp_join_sel')

GROUP BY pg_name, cp_name

UNION ALL

-- cf_tru
SELECT 
  pg_name,
  'cf_tru' AS cf,
  cp_name,
  ROUND(AVG(ps_loss_factor), 2) AS avg_lf,
  ROUND(MEDIAN(ps.ps_loss_factor), 2) AS median_lf,
  ROUND(MAX(ps_loss_factor), 2) AS max_lf,
  COUNT(*) AS cnt
FROM v_ps_base
WHERE bpc_name = 'BpTrad'
  AND bpi_cf_join_bundle = 3
  AND bpi_cf_mat = 3
  AND bpi_cf_concat = 3
  AND wp_cf_host_id = 2
  AND LOWER(pg_name) IN ('dpccp','dpccpcout','goocost','goocard','simplisquared')
  AND LOWER(cp_name) IN ('cp_true','cp_ia_m','cp_ia_s','cp_ia_l','cp_crude_base','cp_crude_sel','cp_join_base','cp_join_sel')
GROUP BY pg_name, cp_name
ORDER BY pg_name ASC, cf DESC, cp_name ASC;
