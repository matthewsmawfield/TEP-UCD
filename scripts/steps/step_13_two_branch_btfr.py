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
            rows[p[0]] = {"T": int(p[1]), "L36": float(p[7]),
                          "MHI": float(p[13]), "Vflat": float(p[15])}
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

    outer_vobs, outer_vpred, outer_gN, names = [], [], [], []
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
            vp = np.sqrt(gp * R * KPC) / KMS
            outer_vobs.append(Vo); outer_vpred.append(vp)
            outer_gN.append(gN / G_T); names.append(name)

    outer_vobs = np.array(outer_vobs)
    outer_vpred = np.array(outer_vpred)
    outer_gN = np.array(outer_gN)
    ratio = outer_vobs / outer_vpred
    logres = np.log10(ratio)

    out = {"step": "btfr_two_branch", "k": K, "g_t": G_T,
           "a_eff_ms2": float(A_EFF), "a_eff_over_g_t":
               float(A_EFF / G_T),
           "ups": [UPS_D, UPS_B], "hi_factor": HI_FAC,
           "outer_edge": {
               "n_points": int(len(ratio)),
               "n_galaxies": int(len(set(names))),
               "median_vobs_over_vpred": float(np.median(ratio)),
               "median_log10_resid": float(np.median(logres)),
               "rms_log10_resid": float(np.sqrt(np.mean(logres ** 2))),
               "median_gN_over_gt": float(np.median(outer_gN))}}

    # B. asymptotic BTFR on Table-1 Vflat
    Mb, vo = [], []
    for name, r in t1.items():
        if r["Vflat"] > 0 and r["L36"] > 0:
            Mb.append((UPS_D * r["L36"] + HI_FAC * r["MHI"]) * 1e9)
            vo.append(r["Vflat"])
    Mb = np.array(Mb) * MSUN
    vo = np.array(vo) * KMS
    vpred_asym = (G_SI * Mb * A_EFF) ** 0.25
    res = np.log10(vo / vpred_asym)
    b, a = np.polyfit(np.log10(vo), np.log10(Mb / MSUN), 1)
    out["asymptotic"] = {
        "n": int(len(vo)),
        "median_vobs_over_vpred_deep_limit":
            float(np.median(vo / vpred_asym)),
        "rms_log10_deep_limit": float(np.sqrt(np.mean(res ** 2))),
        "empirical_slope_Mb_vs_v": float(b),
        "median_implied_a_eff_ms2": float(
            np.median(vo ** 4 / (G_SI * Mb))),
        "note": "deep-limit formula underpredicts v_flat at finite u; "
                "the outer-edge test is the honest comparison"}

    dest = Path(__file__).resolve().parents[2] / "results" / "outputs" / \
        "step_13_two_branch_btfr.json"
    dest.write_text(json.dumps(out, indent=2))
    print(json.dumps(out["outer_edge"], indent=1))
    print(json.dumps(out["asymptotic"], indent=1))
    print("wrote", dest)
    return str(dest)


if __name__ == "__main__":
    main()
