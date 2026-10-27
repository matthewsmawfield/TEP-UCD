#!/usr/bin/env python3
"""AUD-1 / T1.5 -- BTFR under the two-branch sector.

Two zero-parameter tests:

A. Exact-flux-law outer-edge prediction.  For every SPARC galaxy take
   the outermost Table-2 radii where the curve flattens, compute the
   baryonic Newtonian field g_N from the mass model
   (Vgas/Vdisk/Vbul at the standard MLRs), predict g_obs through the
   two-branch flux law  u P_X(u) = g_N/g_t, g_obs = g_t u (P_X + 2),
   and compare v_pred = sqrt(g_obs R) with the observed velocity there.
   No free parameters: k = 16.03 was fixed by the wide-binary/Solar
   crossover and the deep-tail RAR.

B. Asymptotic BTFR.  v_flat^4 = G M_b a_eff with
   a_eff = 4 sqrt(2) g_t / k = 0.353 g_t = 1.2e-10 m/s^2, the deep-
   tail limit (valid only where u << 1 -- finite-u corrections are
   computed explicitly since SPARC outer points sit at u ~ 0.1-0.3).

M_b = Ups_d L[3.6] + 1.33 M_HI (Lelli+2016 convention, Ups_d = 0.5;
bulge light folded into L[3.6] at disk MLR).

Outputs results/outputs/step_13_two_branch_btfr.json
(migrated from Paper 0 step_66).
"""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

K = 16.03
SQRT2 = np.sqrt(2.0)
# Canonical shear scale shared with step_10 and Paper 0 (R11):
# g_t = c H0 / (2 beta_A^2), H0 = 70 km/s/Mpc, beta_A^2 = 1.
C_LIGHT = 2.998e8
H0_SI = 70.0e3 / 3.086e22
G_T = C_LIGHT * H0_SI / 2.0                     # 3.40e-10 m/s^2
G_SI = 6.674e-11
MSUN = 1.989e30
KMS = 1e3
KPC = 3.086e19
UPS_D, UPS_B = 0.5, 0.7
HI_FAC = 1.33
A_EFF = 4.0 * SQRT2 * G_T / K

REPO = Path(__file__).resolve().parents[2] / "data" / "sparc"


def PX(u):
    u = np.abs(u)
    return K * u / SQRT2 + u * u


def g_obs_of_gN(gN):
    """g_obs = g_t u (P_X + 2) for u P_X = gN/g_t (scalar, gN>=0)."""
    y = gN / G_T
    if y <= 0:
        return 0.0
    hi = 1.0
    while hi * PX(hi) < y:
        hi *= 4.0
    u = brentq(lambda uu: uu * PX(uu) - y, 0.0, hi,
               xtol=1e-13, rtol=1e-12)
    return G_T * u * (PX(u) + 2.0)


def parse_table1(path):
    rows = {}
    for line in path.read_text().splitlines():
        p = line.split()
        if len(p) < 19:
            continue
        try:
            rows[p[0]] = {"T": int(p[1]), "inc": float(p[5]),
                          "L36": float(p[7]), "MHI": float(p[13]),
                          "Vflat": float(p[15]), "eVflat": float(p[16]),
                          "Q": int(p[17])}
        except ValueError:
            continue
    return rows


def parse_table2(path):
    """Return per-galaxy list of (R_kpc, Vobs, eV, Vgas, Vdisk, Vbul).
    Table-2 columns: ID, D, R, Vobs, e_Vobs, Vgas, Vdisk, Vbul,
    [SBdisk, SBbul]."""
    rows = {}
    for line in path.read_text().splitlines():
        p = line.split()
        if len(p) < 8:
            continue
        try:
            name = p[0]
            vals = [float(x) for x in p[1:8]]
        except ValueError:
            continue
        D, R, Vo, eV, Vg, Vd, Vb = vals
        rows.setdefault(name, []).append((R, Vo, eV, Vg, Vd, Vb))
    return rows


def main():
    t1 = parse_table1(REPO / "Table1.mrt")
    t2 = parse_table2(REPO / "Table2.mrt")

    outer_vobs, outer_vpred, outer_vpred_coupled, outer_vpred_quad, outer_gN, names = [], [], [], [], [], []
    for name, t1row in t1.items():
        curve = t2.get(name)
        if not curve or t1row["Vflat"] <= 0:
            continue
        arr = np.array(curve)
        # outer edge: last 3 valid points
        tail = arr[-3:]
        for R, Vo, eV, Vg, Vd, Vb in tail:
            if R <= 0 or Vo <= 0:
                continue
            vbar2 = (abs(Vg) * Vg + UPS_D * abs(Vd) * Vd
                     + UPS_B * abs(Vb) * Vb)
            if vbar2 <= 0:
                continue
            gN = vbar2 * KMS ** 2 / (R * KPC)
            gp = g_obs_of_gN(gN)
            ap = gp - gN
            gp_coupled = 0.5 * gN + np.sqrt((0.5 * gN) ** 2 + gN * A_EFF)
            gp_quad = np.hypot(gN, ap)
            vp = np.sqrt(gp * R * KPC) / KMS
            vp_coupled = np.sqrt(gp_coupled * R * KPC) / KMS
            vp_quad = np.sqrt(gp_quad * R * KPC) / KMS
            outer_vobs.append(Vo); outer_vpred.append(vp)
            outer_vpred_coupled.append(vp_coupled)
            outer_vpred_quad.append(vp_quad)
            outer_gN.append(gN / G_T); names.append(name)

    outer_vobs = np.array(outer_vobs)
    outer_vpred = np.array(outer_vpred)
    outer_vpred_coupled = np.array(outer_vpred_coupled)
    outer_vpred_quad = np.array(outer_vpred_quad)
    ratio_coupled = outer_vobs / outer_vpred_coupled
    logres_coupled = np.log10(ratio_coupled)
    outer_gN = np.array(outer_gN)
    ratio = outer_vobs / outer_vpred
    logres = np.log10(ratio)
    ratio_quad = outer_vobs / outer_vpred_quad
    logres_quad = np.log10(ratio_quad)

    out = {"step": "btfr_two_branch", "k": K, "g_t": G_T,
           "a_eff_ms2": float(A_EFF), "a_eff_over_g_t":
               float(A_EFF / G_T),
           "ups": [UPS_D, UPS_B], "hi_factor": HI_FAC,
           "outer_edge": {
            "median_vobs_over_vpred_coupled_additive": float(np.median(ratio_coupled)),
            "median_log10_resid_coupled_additive": float(np.median(logres_coupled)),
            "rms_log10_resid_coupled_additive": float(np.sqrt(np.mean(logres_coupled ** 2))),
               "n_points": int(len(ratio)),
               "n_galaxies": int(len(set(names))),
               "median_vobs_over_vpred_quadrature": float(np.median(ratio_quad)),
               "median_log10_resid_quadrature": float(np.median(logres_quad)),
               "rms_log10_resid_quadrature": float(np.sqrt(np.mean(logres_quad ** 2))),
               "median_vobs_over_vpred": float(np.median(ratio)),
               "median_log10_resid": float(np.median(logres)),
               "rms_log10_resid": float(np.sqrt(np.mean(logres ** 2))),
               "median_gN_over_gt": float(np.median(outer_gN))}}

    # B. asymptotic BTFR on Table-1 Vflat
    Mb, vo, evo, inc_arr, q_arr = [], [], [], [], []
    for name, r in t1.items():
        if r["Vflat"] > 0 and (r["L36"] > 0 or r["MHI"] > 0):
            Mb.append((UPS_D * r["L36"] + HI_FAC * r["MHI"]) * 1e9)
            vo.append(r["Vflat"])
            evo.append(r["eVflat"])
            inc_arr.append(r["inc"])
            q_arr.append(r["Q"])
    Mb = np.array(Mb) * MSUN
    vo = np.array(vo) * KMS
    evo = np.array(evo) * KMS
    inc_arr = np.array(inc_arr)
    q_arr = np.array(q_arr)
    vpred_asym = (G_SI * Mb * A_EFF) ** 0.25
    res = np.log10(vo / vpred_asym)
    lx, ly = np.log10(vo), np.log10(Mb / MSUN)
    b, a = np.polyfit(lx, ly, 1)
    b_xy, _ = np.polyfit(ly, lx, 1)
    b_inv = float(1.0 / b_xy)

    # Lelli et al. (2016) quality-filtered subset (Q <= 2, inc >= 30 deg)
    clean_mask = (q_arr <= 2) & (inc_arr >= 30.0)
    lx_c, ly_c = lx[clean_mask], ly[clean_mask]
    vo_c, Mb_c, evo_c = vo[clean_mask], Mb[clean_mask], evo[clean_mask]
    b_c, _ = np.polyfit(lx_c, ly_c, 1)
    b_xy_c, _ = np.polyfit(ly_c, lx_c, 1)
    b_inv_c = float(1.0 / b_xy_c)
    sig_lx_c = evo_c / (vo_c * np.log(10.0))
    w_c = 1.0 / (sig_lx_c ** 2 + 0.02 ** 2)
    b_winv_c = float(np.cov(ly_c, aweights=w_c) / np.cov(lx_c, ly_c, aweights=w_c)[0, 1])
    res_c = np.log10(vo_c / ((G_SI * Mb_c * A_EFF) ** 0.25))

    # High-quality subset (Q == 1, inc >= 30 deg)
    q1_mask = (q_arr == 1) & (inc_arr >= 30.0)
    lx_1, ly_1 = lx[q1_mask], ly[q1_mask]
    vo_1, evo_1 = vo[q1_mask], evo[q1_mask]
    b_xy_1, _ = np.polyfit(ly_1, lx_1, 1)
    b_inv_1 = float(1.0 / b_xy_1)
    sig_lx_1 = evo_1 / (vo_1 * np.log(10.0))
    w_1 = 1.0 / (sig_lx_1 ** 2 + 0.02 ** 2)
    b_winv_1 = float(np.cov(ly_1, aweights=w_1) / np.cov(lx_1, ly_1, aweights=w_1)[0, 1])

    # Theoretical finite-radius two-branch slope across SPARC mass range (10^8 - 10^11.5 Msun)
    M_grid = np.logspace(8.0, 11.5, 50) * MSUN
    R_out_grid = 2.5 * KPC * ((M_grid / (1e9 * MSUN)) ** 0.32)
    gN_grid = G_SI * M_grid / (R_out_grid ** 2)
    g_add_grid = np.array([g_obs_of_gN(g) for g in gN_grid])
    g_quad_grid = np.array([np.hypot(g, g_obs_of_gN(g) - g) for g in gN_grid])
    V_add_grid = np.sqrt(g_add_grid * R_out_grid)
    V_quad_grid = np.sqrt(g_quad_grid * R_out_grid)
    s_tep_add, _ = np.polyfit(np.log10(V_add_grid), np.log10(M_grid / MSUN), 1)
    s_tep_quad, _ = np.polyfit(np.log10(V_quad_grid), np.log10(M_grid / MSUN), 1)

    out["asymptotic"] = {
        "n": int(len(vo)),
        "median_vobs_over_vpred_deep_limit":
            float(np.median(vo / vpred_asym)),
        "rms_log10_deep_limit": float(np.sqrt(np.mean(res ** 2))),
        "empirical_slope_Mb_vs_v": float(b),
        "empirical_slope_inverse_ols_all": b_inv,
        "quality_filtered_Q_le_2_inc_ge_30": {
            "n": int(clean_mask.sum()),
            "rms_log10_deep_limit": float(np.sqrt(np.mean(res_c ** 2))),
            "slope_ols_Mb_on_v": float(b_c),
            "slope_inverse_ols_v_on_Mb": b_inv_c,
            "slope_weighted_inverse_ols": b_winv_c,
        },
        "high_quality_Q_eq_1_inc_ge_30": {
            "n": int(q1_mask.sum()),
            "slope_inverse_ols_v_on_Mb": b_inv_1,
            "slope_weighted_inverse_ols": b_winv_1,
        },
        "predicted_finite_radius_two_branch_slope": {
            "additive": float(s_tep_add),
            "quadrature": float(s_tep_quad),
            "deep_tail_asymptote": 4.0,
        },
        "median_implied_a_eff_ms2": float(
            np.median(vo ** 4 / (G_SI * Mb))),
        "note": ("deep-limit formula underpredicts v_flat at finite u (g_N/g_t ~ 0.02 at outer radii), "
                 "where the two-branch finite-radius slope is 3.53-3.64 and inverse-OLS on the quality-filtered "
                 "sample recovers 3.76-3.86; the outer-edge test is the direct finite-u comparison")}

    dest = Path(__file__).resolve().parents[2] / "results" / "outputs" / \
        "step_13_two_branch_btfr.json"
    dest.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["outer_edge"], indent=1))
    print(json.dumps(out["asymptotic"], indent=1))
    print("wrote", dest)
    return str(dest)


if __name__ == "__main__":
    main()
