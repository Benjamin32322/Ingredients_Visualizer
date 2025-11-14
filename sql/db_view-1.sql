--- contains
--- 1) core views
--- 2) pex  views
--- 3) dpe  views
---

---
--- 1) core views
--- 

---
--- join host table with itself to add name of reference host
---

create or replace temporary view
v_host as (
  select h.*, hr.ho_name as ho_name_ref
  from host_table h, host_table hr
  where h.ho_id_ref = hr.ho_id
);

---
--- join all build_plan_instance and build_plan_class
---

create or replace temporary view
v_bp as (
  select bpi_id             as bp_bpi_id,
         bpc_id             as bp_bpc_id,
         bpc_name           as bp_name,
         bpi_cf_join_bundle as bp_cf_join,
         bpi_cf_mat         as bp_cf_mat,
         bpi_cf_concat      as bp_cf_conc
  from build_plan_instance, build_plan_class
  where bpi_bpc = bpc_id
);

--- 
--- most precise build-plan configuration
--- (BpTrad, CP_0, CF_0, CFmat0, CFconc0)
---

create or replace temporary view
v_bp_trad_0_00 as (
  select * 
  from v_bp
  where bp_name = 'BpTrad' and
        bp_cf_join = 0 and
        bp_cf_mat  = 0 and
        bp_cf_conc = 0
);


---
--- join of all work-package related relations
---

create or replace temporary view
v_wp as (
  select wp_id              as wp_id,
         wp_no              as wp_no,
         pg_id              as wp_pg_id,
         pg_char            as wp_pg_char,
         pg_kind_sub        as wp_pg_kind_sub,
         pg_name            as wp_pg_name,
         cp_id              as wp_cp_id,
         cp_name            as wp_cp_name,
         bpi_id             as wp_bpi_id,
         bpc_id             as wp_bpc_id,
         bpc_name           as wp_bp_name,
         bpi_cf_join_bundle as wp_cf_join,
         bpi_cf_mat         as wp_cf_mat,
         bpi_cf_concat      as wp_cf_conc,
         ho_id              as wp_cf_host_id,
         ho_name            as wp_cf_host_name,
         ho_id_ref          as wp_cf_host_id_ref,
         ho_name_ref        as wp_cf_host_name_ref,
         ho_cluster_gen     as wp_cf_host_cluster_gen
  from   work_package, plan_generator, card_provider,
         build_plan_instance, build_plan_class, v_host
  where  wp_pg = pg_id and
         wp_cp = cp_id and
         wp_bp = bpi_id and
         bpi_bpc = bpc_id and
         wp_cf_host_id = ho_id
);



---
--- best work package according to cost functions 
--- (DPccp, CP_0, CF_0, CFmat0, CFconc0)
--- (1 row)

create or replace temporary view
v_wp_cf_opt as (
  select *
  from v_wp
  where wp_pg_name  = 'DPccp' and
        wp_bp_name  = 'BpTrad' and
        wp_cp_name  = 'cp_true' and
        wp_cf_join  = 0 and
        wp_cf_mat   = 0 and
        wp_cf_conc  = 0
);

---
--- work package of pessimistic plans
--- (1 row)

create or replace temporary view
v_wp_cf_pessimistic as (
  select *
  from v_wp
  where wp_pg_name  = 'DPccp' and
        wp_cp_name  = 'cp_join_base' and
        wp_bp_name  = 'BpTrad' and
        wp_cf_join  = 0 and
        wp_cf_mat   = 0 and
        wp_cf_conc  = 0
);


---
--- best plans according to cost functions
--- (DPccp, CP_0, CF_0, CFmat0, CFconc0)
---

create or replace temporary view 
v_ps_cf_opt as (
  select *
  from   plan_summary ps
  where  exists(select * from v_wp_cf_opt where ps_wp = wp_id)
);

---
--- pessimistic plans according to cost function
--- ((DPccp, CP_jbase, CF_0, CFmat0, CFconc0)
---

create or replace temporary view 
v_ps_cf_pessimistic as (
  select *
  from   plan_summary ps
  where  exists(select * from v_wp_cf_pessimistic where ps_wp = wp_id)
);
  


---
--- add cardinalities of plan classes to ccps
---
  
create or replace temporary view
v_ccp_card_true as (
select ccp.*,
       pcc1.pcc_card_true as ccp_card_1,
       pcc2.pcc_card_true as ccp_card_2

from csg_cmp_pair ccp, pc_card pcc1, pc_card pcc2
where ccp_qg = pcc1.pcc_qg and ccp_pc_1 = pcc1.pcc_pc and
      ccp_qg = pcc2.pcc_qg and ccp_pc_2 = pcc2.pcc_pc
);
  


---
--- 2) pex views
---

---
--- simple join of pex-tables with v_host
--- to add information of host on which plan was executed
---

create or replace temporary view
v_pex_plan as (select x.*,
                      h.ho_name        as pe_host_name,
                      h.ho_id_ref      as pe_host_id_ref,
                      h.ho_name_ref    as pe_host_name_ref,
                      h.ho_cluster_gen as pe_host_cluster_gen,
                      round(pe_exec_cc_max / pe_exec_cc_min, 2) as pe_ratio_cc_max_min
               from plan_exec x, v_host h
               where x.pe_host_id = h.ho_id);

create or replace temporary view
v_pex_scan as (select x.*,
                      h.ho_name        as se_host_name,
                      h.ho_id_ref      as se_host_id_ref,
                      h.ho_name_ref    as se_host_name_ref,
                      h.ho_cluster_gen as se_host_cluster_gen,
                      round(se_cc_max / se_cc_min, 2) as se_ratio_cc_max_min
               from scan_exec x, v_host h
               where x.se_host_id = ho_id);

---
--- select minimum runtime of plans 
--- per (query, host, sp_opt, like, codegen, timestamp)
---

create or replace temporary view
v_pex_best as (
select   pe_qg               as pb_qg, 
         pe_host_id_ref      as pb_host_id_ref,
         pe_host_name_ref    as pb_host_name_ref,
         pe_host_cluster_gen as pb_host_cluster_gen,
         pe_sp_opt           as pb_byp,
         pe_old_like         as pb_like,
         pe_codgen_kind      as pb_codegen,
         pe_timestamp        as pb_timestamp,
         min(pe_exec_cc_min) as pb_min_cc_min,
         max(pe_exec_cc_min) as pb_max_cc_min,
         min(pe_exec_cc_max) as pb_min_cc_max,
         max(pe_exec_cc_max) as pb_max_cc_max,
         min(pe_exec_min_s)  as pb_exec_min_s,
         round(min(pe_exec_cc_max / pe_exec_cc_min), 2)    as pb_min_ratio_cc_max_min,
         round(max(pe_exec_cc_max / pe_exec_cc_min), 2)    as pb_max_ratio_cc_max_min,
         round(avg(pe_exec_cc_max / pe_exec_cc_min), 2)    as pb_avg_ratio_cc_max_min,
         round(median(pe_exec_cc_max / pe_exec_cc_min), 2) as pb_median_ratio_cc_max_min,
         round(max(pe_exec_cc_min) / min(pe_exec_cc_min), 2) as pb_max_lf_pex,
         count(*) as pb_cnt 
from     v_pex_plan
where pe_exec_cc_min > 0 -- some plans may have been pruned from execution due to long runtime
group by pe_qg, pe_host_id_ref, pb_host_name_ref, pb_host_cluster_gen, 
         pe_sp_opt, pe_old_like, pe_codgen_kind, pe_timestamp
);         
               
select *
from v_pex_best
order by pb_exec_min_s;

select pb_qg, pb_host_name_ref, count(*)
from v_pex_best
group by pb_qg, pb_host_name_ref
order by pb_qg, pb_host_name_ref;




---
--- 3) dpe views
--- 

---
--- simple join of dpe-tables with v_host
--- to add information of host on which plan was produced by DpCcpExec
---

create or replace temporary view
v_dpe_plan as (select x.*,
                      h.ho_name        as epl_host_name,
                      h.ho_id_ref      as epl_host_id_ref,
                      h.ho_name_ref    as epl_host_name_ref,
                      h.ho_cluster_gen as epl_host_cluster_gen
               from dpe_plan x, v_host h
               where x.epl_host_id = ho_id);

create or replace temporary view
v_dpe_pc as (select x.*,
                    h.ho_name        as epc_host_name,
                    h.ho_id_ref      as epc_host_id_ref,
                    h.ho_id_ref      as epc_host_name_ref,
                    h.ho_cluster_gen as epc_host_cluster_gen
             from dpe_pc x, v_host h
             where x.epc_host_id = ho_id);

create or replace temporary view
v_dpe_ccp as (select x.*,
                     h.ho_name        as eccp_host_name,
                     h.ho_id_ref      as eccp_host_id_ref,
                     h.ho_name_ref    as eccp_host_name_ref,
                     h.ho_cluster_gen as eccp_host_cluster_gen
              from dpe_ccp x, v_host h
              where x.eccp_host_id = ho_id);

create or replace temporary view
v_dpe_op as (select x.*,
                    h.ho_name        as eop_host_name,
                    h.ho_id_ref      as eop_host_id_ref,
                    h.ho_name_ref    as eop_host_name_ref,
                    h.ho_cluster_gen as eop_host_cluster_gen
             from dpe_op x, v_host h
             where x.eop_host_id = ho_id);

---
--- simple join between dpe_ccp and dpe_op
---

create or replace temporary view
v_dpe_ccp_op as (
select *
from dpe_ccp, dpe_op
where eccp_host_id = eop_host_id and
      eccp_qg      = eop_qg and
      eccp_byp     = eop_byp and
      eccp_like    = eop_like and 
      eccp_codegen_kind = eop_codegen_kind and
      eccp_timestamp    = eop_timestamp and
      eccp_ccp_left     = eop_ccp_left and
      eccp_ccp_right    = eop_ccp_right
);

--- view to select the best operator implementation (optimal subtree)
--- for every plan class
--- (misses of course plan classes with only one relation)
--- (thus requires union with scan_exec)

create or replace temporary view
v_dpe_pc_ccp_op_best as (
select *
from dpe_pc,
     dpe_ccp,
     dpe_op
where
      epc_host_id       = eccp_host_id and
      epc_qg            = eccp_qg and
      epc_byp           = eccp_byp and
      epc_like          = eccp_like and
      epc_codegen_kind  = eccp_codegen_kind and
      epc_cf_host_ref   = eccp_cf_host_ref and
      epc_timestamp     = eccp_timestamp and
      epc_pc            = eccp_pc and
      epc_idx_best_exec = eccp_ccp_idx and
      eccp_host_id      = eop_host_id and
      eccp_qg           = eop_qg and
      eccp_byp          = eop_byp and
      eccp_like         = eop_like and
      eccp_codegen_kind = eop_codegen_kind and
      eccp_cf_host_ref  = eop_cf_host_ref and
      eccp_timestamp    = eop_timestamp and
      eccp_pc           = eop_pc and
      eccp_ccp_left     = eop_ccp_left and
      eccp_ccp_right    = eop_ccp_right and
      eccp_swap_exec    = eop_swap and
      eccp_op_exec_impl = eop_op_impl
);


-- check:
-- select count(*) from dpe_pc;
-- select count(*) from v_dpe_pc_ccp_op_best;
-- select count(*) from dpe_pc where 1 = bit_count(epc_pc);
-- select   (select count(*) from v_dpe_pc_ccp_op_best) 
--        + (select count(*) from dpe_pc where 1 = bit_count(epc_pc));



---
--- CHENG
---

---
--- for every dpe plan class in eop_pc
--- add the best subtree and operator for it
--- thereby also add the information about scans
--- for singleton plan classes

create or replace temporary view
v_dpe_pc_best_op(eop_host_id, eop_qg, eop_byp, eop_like, eop_codegen_kind, eop_cf_host_ref, eop_timestamp,
                 eop_pc,
                 pc_m_no_run, pc_m_cc_min, pc_m_cc_max, pc_m_cc_avg, pc_m_cc_med) AS (
  SELECT eop_host_id,
         eop_qg,
         eop_byp,
         eop_like,
         eop_codegen_kind,
         eop_cf_host_ref,
         eop_timestamp,
         eop_pc,
         eop_m_no_run AS pc_m_no_run,
         eop_m_min    AS pc_m_cc_min,
         eop_m_max    AS pc_m_cc_max,
         eop_m_avg    AS pc_m_cc_avg,
         eop_m_med    AS pc_m_cc_med,
    FROM dpe_pc x,
         dpe_ccp y,
         dpe_op z
   WHERE x.epc_pc = y.eccp_pc
     AND x.epc_qg = y.eccp_qg
     AND x.epc_byp = y.eccp_byp
     AND x.epc_like = y.eccp_like
     AND x.epc_codegen_kind = y.eccp_codegen_kind
     AND x.epc_cf_host_ref = y.eccp_cf_host_ref
     AND x.epc_timestamp = y.eccp_timestamp
     AND y.eccp_pc = z.eop_pc
     AND y.eccp_qg = z.eop_qg
     AND y.eccp_byp = z.eop_byp
     AND y.eccp_like = z.eop_like
     AND y.eccp_codegen_kind = z.eop_codegen_kind
     AND y.eccp_cf_host_ref = z.eop_cf_host_ref
     AND y.eccp_timestamp = z.eop_timestamp
     AND x.epc_idx_best_exec = y.eccp_ccp_idx
     AND y.eccp_ccp_idx = z.eop_ccp_idx
     AND y.eccp_ccp_left = z.eop_ccp_left
     AND y.eccp_ccp_right = z.eop_ccp_right
     AND y.eccp_swap_exec = z.eop_swap
     AND y.eccp_op_exec_impl = z.eop_op_impl
-- );
   UNION ALL
  SELECT se_host_id   AS eop_host_id,
         se_qg        AS eop_qg,
         se_sp_opt    AS eop_byp,
         se_old_like  AS eop_like,
         1            AS eop_codegen_kind,
         2            AS eop_cf_host_ref,
         se_timestamp AS eop_timestamp,
         (CAST(1 as bigint) << se_rel_id) AS eop_pc,
         se_no_run    AS pc_m_no_run,
         se_cc_min    AS pc_m_cc_min,
         se_cc_max    AS pc_m_cc_max,
         se_cc_avg    AS pc_m_cc_avg,
         se_cc_med    AS pc_m_cc_med
    FROM scan_exec
);

select count(*) from scan_exec;
--> 12304
select count(*) from dpe_pc;
--> 49348
select count(*) from dpe_pc where bit_count(epc_pc) > 1;
--> 47181
select count(*) from v_dpe_pc_best_op;
--> 59485 (47181 ohne scans)
select count(*) from pc_desc;
--> 71406

-- second temp table to list down the execution cost of each join operator
CREATE OR REPLACE temporary VIEW view_s_op_dpe AS
   SELECT d.*,
          l.pc_m_cc_min AS left_min,
          l.pc_m_cc_max AS left_max,
          r.pc_m_cc_min AS right_min,
          r.pc_m_cc_max AS right_max,
          (d.eop_m_max - l.pc_m_cc_min - r.pc_m_cc_min) AS eop_exec_max_loc,
          (d.eop_m_min - l.pc_m_cc_max - r.pc_m_cc_max) AS eop_exec_min_loc,
          (d.eop_m_min - l.pc_m_cc_min - r.pc_m_cc_min) AS self_eop_exec_loc -- should be same as eop_exec_loc
     FROM dpe_op AS d
     JOIN v_dpe_pc_best_op AS l
       ON l.eop_pc = d.eop_ccp_left
      AND l.eop_qg = d.eop_qg
      AND l.eop_byp = d.eop_byp
      AND l.eop_like = d.eop_like
      AND l.eop_codegen_kind = d.eop_codegen_kind
      -- AND l.eop_cf_host_ref = d.eop_cf_host_ref
      AND l.eop_timestamp = d.eop_timestamp
     JOIN v_dpe_pc_best_op AS r
       ON r.eop_pc = d.eop_ccp_right
      AND r.eop_qg = d.eop_qg
      AND r.eop_byp = d.eop_byp
      AND r.eop_like = d.eop_like
      AND r.eop_codegen_kind = d.eop_codegen_kind
      -- AND r.eop_cf_host_ref = d.eop_cf_host_ref
      AND r.eop_timestamp = d.eop_timestamp;

select count(*) from dpe_op;
--> 23.187.744
select count(*) from view_s_op_dpe;
--> 11.538.576

select count(*), min(bit_count(eop_pc)), max(bit_count(eop_pc))
from dpe_op as x
where not exists(select *
                 from v_dpe_pc_best_op as y
                 where x.eop_host_id = y.eop_host_id and
                       x.eop_qg      = y.eop_qg and
                       x.eop_byp     = y.eop_byp and
                       x.eop_like    = y.eop_like and
                       x.eop_codegen_kind = y.eop_codegen_kind and
                       x.eop_cf_host_ref  = y.eop_cf_host_ref and
                       x.eop_timestamp    = y.eop_timestamp and
                       x.eop_ccp_left     = y.eop_pc);
--> 2.332.944

select x.eop_qg, count(*), min(bit_count(eop_pc)), max(bit_count(eop_pc))
from dpe_op as x
where not exists(select *
                 from v_dpe_pc_best_op as y
                 where x.eop_host_id = y.eop_host_id and
                       x.eop_qg      = y.eop_qg and
                       x.eop_byp     = y.eop_byp and
                       x.eop_like    = y.eop_like and
                       x.eop_codegen_kind = y.eop_codegen_kind and
                       x.eop_cf_host_ref  = y.eop_cf_host_ref and
                       x.eop_timestamp    = y.eop_timestamp and
                       x.eop_ccp_left     = y.eop_pc)
      and x.eop_host_id in (2,3,4,5)
group by x.eop_qg
order by x.eop_qg;

select count(*) from pc_desc;
--> 71406

select pcd_qg, count(*) as no_pruned
from pc_desc
where not exists(select *
                 from dpe_pc
                 where epc_host_id in (2, 3, 4, 5) and epc_qg = pcd_qg)
group by pcd_qg
order by pcd_qg;

select pcd_qg, count(*) as no_pruned
from pc_desc
where not exists(select *
                 from dpe_pc
                 where epc_host_id in (22, 23, 24, 25, 33, 34, 35, 36) and epc_qg = pcd_qg)
group by pcd_qg
order by pcd_qg;



-- third temp table to get extra statistic for each join operator
-- include: eop_max_min_ratio, eop_qerror_max_loc, eop_qerror_min_loc 
CREATE OR REPLACE VIEW view_s_op_st_dpe AS
   SELECT eop_host_id,
          eop_qg,
          eop_pc,
          eop_byp,
          eop_like,
          eop_codegen_kind,
          eop_cf_host_ref,
          eop_timestamp,
          eop_op_impl,
          eop_op_uniq_bld,
          eop_op_uniq_prb,
          eop_op_uniq,
          eop_swap,
          eop_m_max,
          eop_m_min,
          eop_exec_max_loc,
          eop_exec_min_loc,
          eop_cost_cf_loc,
          eop_qerror_loc,
          CASE
            WHEN eop_exec_max_loc > 0 AND eop_exec_min_loc > 0
            THEN (eop_exec_max_loc / eop_exec_min_loc)
            ELSE 0 END AS eop_max_min_ratio,
          CASE
            WHEN eop_exec_max_loc > 0 AND eop_cost_cf_loc > 0
            THEN GREATEST(eop_exec_max_loc / eop_cost_cf_loc, eop_cost_cf_loc / eop_exec_max_loc)
            ELSE 0 END AS eop_qerror_max_loc,
          CASE
            WHEN eop_exec_min_loc > 0 AND eop_cost_cf_loc > 0
            THEN GREATEST(eop_exec_min_loc / eop_cost_cf_loc, eop_cost_cf_loc / eop_exec_min_loc)
            ELSE 0 END AS eop_qerror_min_loc,
            ji_kind,
            ji_flag_left,
            ji_flag_right,
            ji_name
     FROM view_s_op_dpe
     JOIN join_impl
       ON view_s_op_dpe.eop_op_impl = join_impl.ji_id;

-- filtered dataset
   SELECT count(*),
          round(eop_qerror_min_loc, 1) AS q
     FROM view_s_op_st_dpe                       -- 4.52M
    WHERE eop_qerror_loc <> 0                    -- 4.44M
      AND eop_max_min_ratio > 0                  -- 4.36M               
      AND eop_max_min_ratio < 1.03               -- 1.58M
 GROUP BY q
 ORDER BY q;
  




--- OLD

--
--  select minimum runtime of 
-- plans per (query, host, sp_opt, like, codegen, timestamp)

create or replace temporary view
v_pex_best as (
select   pe_qg               as pb_qg, 
         pe_host_id_ref      as pb_host_id_ref,
         ho_name             as pb_host_name_ref,
         pe_host_cluster_gen as pb_host_cluster_gen,
         pe_qg               as pb_qg,
         pe_sp_opt           as pb_byp,
         pe_old_like         as pb_like, 
         pe_codgen_kind      as pb_codegen,
         pe_timestamp        as pb_timestamp,
         min(pe_exec_cc_min) as pb_min_cc_min,
         max(pe_exec_cc_min) as pb_max_cc_min,
         min(pe_exec_cc_max) as pb_min_cc_max,
         max(pe_exec_cc_max) as pb_max_cc_max,
         round(min(pe_exec_cc_max / pe_exec_cc_min), 2)    as pb_min_ratio_cc_max_min,
         round(max(pe_exec_cc_max / pe_exec_cc_min), 2)    as pb_max_ratio_cc_max_min,
         round(avg(pe_exec_cc_max / pe_exec_cc_min), 2)    as pb_avg_ratio_cc_max_min,
         round(median(pe_exec_cc_max / pe_exec_cc_min), 2) as pb_median_ratio_cc_max_min,
         round(max(pe_exec_cc_min) / min(pe_exec_cc_min), 2) as pb_max_lf_pex,
         count(*) as pb_cnt
from     v_pex_plan
where pe_exec_cc_min > 0 -- some plans may have been pruned from execution due to long runtime
group by pe_host_id_ref, ho_name, pe_host_cluster_gen, 
         pe_qg, pe_sp_opt, pe_old_like, pe_codgen_kind, pe_timestamp
);


create or replace temporary view
v_pex_stat as (
select pex_host_ref      as pest_host_ref,
       pex_host_ref_name as pest_host_ref_name,
       pex_wp            as pest_wp,
       max(pex_cc_min/pb_min_cc_min)   as pest_lf_pex_max,
       avg(pex_cc_min/pb_min_cc_min)   as pest_lf_pex_avg,
       median(pex_cc_min/pex_aggr_min) as pest_lf_pex_med,
       count(*)          as pest_wp
from  v_pex_plan, v_pex_best
where pe_host_ref = pex_aggr_host_id_ref
      pe_qg       = pex_aggr_qg and
group by pex_host_id_ref, pex_host_ref_name, pex_wp
);


--- dpe-views
--- bop

-- new bop taking minimum of swapped ccps into account using 

create or replace temporary view
v_bop as (
select distinct
       ho_id_ref          as bop_host_ref,
       ho_id              as bop_host_id,
       ho_cluster_gen     as bop_cluster_gen,
       eccp_qg            as bop_qg,
       eccp_byp           as bop_byp,
       eccp_like          as bop_like,
       eccp_codegen_kind  as bop_cgk,
       eccp_cf_host_ref   as bop_cf_host_ref,
       eccp_timestamp     as bop_timestamp,
       eccp_op_exec_impl  as bop_j_impl,
       ji_kind            as bop_j_kind,
       ji_name            as bop_j_name,
       ji_flag_left       as bop_j_flag_left,
       ji_flag_right      as bop_j_flag_right,
       (case when ji_kind = 1 or ji_kind = 2 then 0 else 1 end) as bop_j_hj, -- 0 = CH, 1 = 3D
       (case when ji_kind = 1 or ji_kind = 3 then 0 else 1 end) as bop_j_packed, -- 0 = upk, 1 = pkd
       (case when 0 == eccp_swap_exec then ji_flag_left  else ji_flag_right end) as bop_j_flag_1,
       (case when 0 == eccp_swap_exec then ji_flag_right else ji_flag_left  end) as bop_j_flag_2,
       eccp_op_exec_uniq_bld as bop_uniq_bld,
       eccp_op_exec_uniq_prb as bop_uniq_prb,
       eccp_op_exec_uniq     as bop_uniq,
       ccp_uniq_1        as bop_uniq_1,
       ccp_uniq_2        as bop_uniq_2,
       eccp_swap_exec    as bop_swap,
       eccp_ccp_left     as bop_ccp_left,
       eccp_ccp_right    as bop_ccp_right,
       eccp_pc           as bop_pc,
       pc1.pcd_card      as bop_card_left,
       pc2.pcd_card      as bop_card_right,
       pc1.pcd_size      as bop_size_left,
       pc2.pcd_size      as bop_size_right,
       ccp_nodv_1        as bop_nodv_1,
       ccp_nodv_2        as bop_nodv_2, 
       eop_m_min         as bop_cost_exec,
       eccp_cost_exec    as bop_cost_exec_2, -- just to check whether they are equal to bop_cost_exec
       eop_exec_loc      as bop_cost_exec_loc,
from dpe_ccp,
     host_table,
     join_impl,
     pc_desc pc1,
     pc_desc pc2,
     csg_cmp_pair,
     dpe_op
where eccp_host_id      = ho_id and
      eccp_op_exec_impl = ji_id and
      eccp_qg           = pc1.pcd_qg and
      eccp_ccp_left     = pc1.pcd_pc and
      eccp_qg           = pc2.pcd_qg and
      eccp_ccp_right    = pc2.pcd_pc and
      eccp_qg           = ccp_qg   and
      eccp_ccp_left     = ccp_pc_1 and
      eccp_ccp_right    = ccp_pc_2 and
      eccp_host_id      = eop_host_id and
      eccp_qg           = eop_qg and
      eccp_byp          = eop_byp and
      eccp_like         = eop_like and
      eccp_codegen_kind = eop_codegen_kind and
      eccp_cf_host_ref  = eop_cf_host_ref and
      eccp_timestamp    = eop_timestamp and
      eccp_ccp_left     = eop_ccp_left and
      eccp_ccp_right    = eop_ccp_right and
      eccp_op_exec_impl = eop_op_impl and
      eccp_swap_exec    = eop_swap
);

-- project v_bop on some relevant attributes
-- and restrict it to host-ref = 2 (pluto/gen1)

create or replace temporary view
v_bop_proj as
(select bop_host_ref      as hid,       -- control
        bop_card_left     as card_1,    -- input
        bop_card_right    as card_2,    -- input
        ceil(log2(bop_card_left )) as l_1,
        ceil(log2(bop_card_right)) as l_2,
        bop_size_left     as size_1,    -- input
        bop_size_right    as size_2,    -- input
        bop_uniq_1        as uniq_1,    -- input
        bop_uniq_2        as uniq_2,    -- input
        bop_nodv_1        as nodv_1,    -- (possible) input
        bop_nodv_2        as nodv_2,    -- (possible) input
        bop_swap          as swap,      -- predict
        bop_j_impl        as j_impl,    -- control
        bop_j_hj          as hj_kind,   -- predict
        bop_j_packed      as hj_pkd,    -- predict
        bop_j_flag_1      as hj_flag_1, -- predict
        bop_j_flag_2      as hj_flag_2  -- predict
from v_bop
where bop_host_ref = 2
);

create or replace temporary view
v_bop_proj_w_cost as
(select bop_host_ref      as hid,       -- control
        bop_card_left     as card_1,    -- input
        bop_card_right    as card_2,    -- input
        ceil(log2(bop_card_left )) as l_1,
        ceil(log2(bop_card_right)) as l_2,
        bop_size_left     as size_1,    -- input
        bop_size_right    as size_2,    -- input
        bop_uniq_1        as uniq_1,    -- input
        bop_uniq_2        as uniq_2,    -- input
        bop_nodv_1        as nodv_1,    -- (possible) input
        bop_nodv_2        as nodv_2,    -- (possible) input
        bop_swap          as swap,      -- predict
        bop_j_impl        as j_impl,    -- control
        bop_j_hj          as hj_kind,   -- predict
        bop_j_packed      as hj_pkd,    -- predict
        bop_j_flag_1      as hj_flag_1, -- predict
        bop_j_flag_2      as hj_flag_2, -- predict
        bop_cost_exec_loc as cost_loc,  -- control
        bop_cost_exec     as cost_tot   -- control
from v_bop
where bop_host_ref = 2
);


