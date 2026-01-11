-- Combined View: v_ps_base with P-Error calculation
-- This replaces both View_ps_base.sql and View_p-error.sql

CREATE OR REPLACE VIEW v_ps_base AS

SELECT
  ps.ps_qg,
  ps.ps_loss_factor,
  pg.pg_name,
  cp.cp_name,
  bpc.bpc_name,
  bpi.bpi_cf_join_bundle,
  bpi.bpi_cf_mat,
  bpi.bpi_cf_concat,
  wp.wp_cf_host_id,
  ps.ps_qerr_cost_pg,
  ps.ps_sum_card_build,
  ps.ps_sum_card_probe,
  ps.ps_sum_card_pc,
  ps.ps_max_card_build,
  ps.ps_max_card_probe,
  ps.ps_max_card_pc,
  ps.ps_cost_pg,
  ps.ps_cost_tru,
  -- P-Error calculation
  CASE
    WHEN ps.ps_cost_pg < ps.ps_cost_tru
      THEN -(ps.ps_cost_tru / NULLIF(ps.ps_cost_pg, 0)) - 1
    ELSE (ps.ps_cost_pg / NULLIF(ps.ps_cost_tru, 0)) - 1
  END AS ps_p_error

FROM plan_summary ps

JOIN work_package        wp  ON wp.wp_id   = ps.ps_wp
JOIN plan_generator      pg  ON pg.pg_id   = wp.wp_pg
JOIN card_provider       cp  ON cp.cp_id   = wp.wp_cp
JOIN build_plan_instance bpi ON bpi.bpi_id = wp.wp_bp
JOIN build_plan_class    bpc ON bpc.bpc_id = bpi.bpi_bpc;
