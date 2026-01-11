-- View_p-error.sql

CREATE OR REPLACE VIEW plan_summary_with_perror AS
SELECT
  ps.*,
  CASE
    WHEN ps.ps_cost_pg < ps.ps_cost_tru
      THEN -(ps.ps_cost_tru / NULLIF(ps.ps_cost_pg, 0)) - 1
    ELSE (ps.ps_cost_pg / NULLIF(ps.ps_cost_tru, 0)) - 1
  END AS ps_p_error
FROM plan_summary AS ps;

