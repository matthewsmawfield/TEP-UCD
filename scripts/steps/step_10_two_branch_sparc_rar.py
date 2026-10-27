#!/usr/bin/env python3
"""Static spherical solve under the two-branch kinetic sector + SPARC
radial-acceleration test (plan AUD-1 / T1.1).

Physics (closure/MASTER_SECTOR_LEDGER.md, Sec. 2):

  Static spherical flux law is EXACTLY algebraic:
      P_X(xi) u' = |beta_A| M(r) / (4 pi M_Pl^2 r^2)
  With u = phi/M_Pl, xi = |X|/Lambda^4 = u'^2/(2 H0^2) (natural units),
  define the normalized shear ubar = c^2 u'/(2|beta_A| g_t).  Then

      P_X(ubar^2/2) * ubar  =  y ,      y = g_N / g_t

  and the matter-frame acceleration is additive:
      g_obs = g_N + 2 beta_A^2 g_t ubar        (beta_A^2 = 1)

  Deep tail (ubar << 1):  ubar = sqrt(sqrt(2) y / k)
      -> g_obs^2 = a_eff g_N,  a_eff = 4 sqrt(2) g_t / k
      -> V_flat^4 = G M a_eff                        (BTFR)

  High-g tail (ubar >> 1):  ubar = y^{1/3} -> scalar branch suppressed
  (the Solar-System observables additionally carry the nested-operator
  vertex factors of steps 19/30; the algebraic law is the isolated-source
  channel appropriate to galaxies in a weak cosmic-web ambient).

No free parameters: k = 16.03 is fixed by a_eff = a_0 = 1.2e-10 m/s^2
(plan T1.0; the fit below also scans k to test that normalization
against the SPARC distribution itself).

Data: TEP-UCD/data/sparc/Table2.mrt (SPARC mass models, Lelli,
McGaugh, Schombert) -- Vgas/Vdisk/Vbul at M/L=1; baryonic acceleration
uses the standard signed-quadratic convention
      V_bar^2 = |Vgas| Vgas + Ups_d |Vdisk| Vdisk + Ups_b |Vbul| Vbul
with Ups_d = 0.5, Ups_b = 0.7 (SPARC canonical).
"""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize_scalar

# ---------------------------------------------------------------------------
# constants
# ---------------------------------------------------------------------------
c = 2.998e8
G = 6.674e-11
H0 = 70.0e3 / 3.086e22
BETA2 = 1.0
g_t = c * H0 / (2.0 * BETA2)               # 3.4e-10 m/s^2
KPC_M = 3.086e19
KMS_MS = 1e3
A0 = 1.2e-10

K_STAR = 4.0 * np.sqrt(2.0) * g_t / A0     # = 16.03

UPS_D, UPS_B = 0.5, 0.7

REPO = Path(__file__).resolve().parents[2] / "data" / "sparc"


# ---------------------------------------------------------------------------
# kinetic-sector candidates (same registry as step_54, with explicit
# zero-gradient regulator eps_reg = 1e-3 so P_X(0) = eps_reg > 0,
# Checklist Item 11)
# ---------------------------------------------------------------------------
EPS_REG = 1.0e-3

def PX_two_branch(xi, k=K_STAR, eps_reg=EPS_REG):
    return eps_reg + k * np.sqrt(xi) + 2.0 * xi

def PX_baseline(xi):
    return 1.0 + 2.0 * xi

def PX_exp_interp(xi, k=K_STAR):
    return (1.0 - np.exp(-k * np.sqrt(xi))) + 2.0 * xi

def PX_unit_variant(xi, k=K_STAR):
    return 1.0 + k * np.sqrt(xi) + 2.0 * xi


def ubar_solve(y, pxfun, k=K_STAR):
    """Solve P_X(ubar^2/2) ubar = y for ubar >= 0."""
    if y <= 0:
        return 0.0
    f = lambda w: pxfun(w * w / 2.0) * w - y
    hi = max(1.0, y)
    while f(hi) < 0:
        hi *= 4.0
        if hi > 1e15:
            break
    return brentq(f, 0.0, hi, xtol=1e-30, rtol=1e-12)


def g_obs_curve(gN, pxfun, k=K_STAR, quadrature=False):
    """TEP prediction: scalar-additive g_N + a_phi or orthogonal two-sector
    quadrature sqrt(g_N^2 + a_phi^2), where a_phi = 2 beta_A^2 g_t ubar."""
    gN = np.asarray(gN, dtype=float)
    out = np.empty_like(gN)
    for i, g in enumerate(gN.flat):
        u = ubar_solve(g / g_t, lambda xi: pxfun(xi, k) if k is not None
                     else pxfun(xi))
        ap = 2.0 * BETA2 * g_t * u
        out.flat[i] = np.hypot(g, ap) if quadrature else (g + ap)
    return out


# ---------------------------------------------------------------------------
# parse SPARC Table 2 (fixed width)
# ---------------------------------------------------------------------------
def parse_table2(path):
    rows = []
    for line in path.read_text().splitlines():
        if len(line) < 59 or line[0] in "=|-TABC" and "CamB" not in line:
            continue
        try:
            gid = line[0:11].strip()
            if not gid:
                continue
            R = float(line[19:25]); Vobs = float(line[26:32])
            eV = float(line[33:38]); Vgas = float(line[39:45])
            Vdisk = float(line[46:52]); Vbul = float(line[53:59])
        except (ValueError, IndexError):
            continue
        rows.append((gid, R, Vobs, eV, Vgas, Vdisk, Vbul))
    return rows


rows = parse_table2(REPO / "Table2.mrt")
galaxies = sorted(set(r[0] for r in rows))

# ---------------------------------------------------------------------------
# build the RAR point set
# ---------------------------------------------------------------------------
g_obs_list, g_bar_list, e_list, gid_list = [], [], [], []
for gid, R, Vobs, eV, Vgas, Vdisk, Vbul in rows:
    Vbar2 = (abs(Vgas) * Vgas + UPS_D * abs(Vdisk) * Vdisk
             + UPS_B * abs(Vbul) * Vbul)
    if Vbar2 <= 0 or Vobs <= 0 or R <= 0:
        continue
    gobs = (Vobs * KMS_MS) ** 2 / (R * KPC_M)
    gbar = Vbar2 * (KMS_MS ** 2) / (R * KPC_M)
    egobs = 2.0 * gobs * (eV / max(Vobs, 1e-6))
    g_obs_list.append(gobs); g_bar_list.append(gbar)
    e_list.append(max(egobs, 1e-14)); gid_list.append(gid)

g_obs = np.array(g_obs_list); g_bar = np.array(g_bar_list)
e_gobs = np.array(e_list); gids = np.array(gid_list)
NPTS = len(g_obs)

OUT = {"step": "sparc_rar_two_branch",
       "constants": {"g_t": g_t, "k_star": K_STAR,
                     "a_eff_predicted": 4.0 * np.sqrt(2) * g_t / K_STAR,
                     "Upsilon_disk": UPS_D, "Upsilon_bulge": UPS_B},
       "n_points": NPTS, "n_galaxies": len(set(gid_list))}


# ---------------------------------------------------------------------------
# 1. predicted curve vs the full RAR point cloud
# ---------------------------------------------------------------------------
pred_tb = g_obs_curve(g_bar, PX_two_branch, quadrature=False)
pred_tb_quad = g_obs_curve(g_bar, PX_two_branch, quadrature=True)
pred_bl = g_obs_curve(g_bar, lambda xi: PX_baseline(xi), k=None, quadrature=False)

logresid_tb = np.log10(g_obs / pred_tb)
logresid_tb_quad = np.log10(g_obs / pred_tb_quad)
logresid_bl = np.log10(g_obs / pred_bl)


# Exact coupled-gradient additive closure (Paper 0 §7; Paper 22 §6):
# In the causal matter metric tilde_g_munu, the dielectric flux equation acts on the coupled gradient
# a_phi * (a_phi + g_N) = g_N * a_eff -> a_phi = sqrt((g_N/2)^2 + g_N * a_eff) - g_N/2:
pred_tb_coupled = 0.5 * g_bar + np.sqrt((0.5 * g_bar) ** 2 + g_bar * A0)
logresid_tb_coupled = np.log10(g_obs / pred_tb_coupled)

OUT["rar_prediction"] = {
    "n_points": NPTS,
    "primary_force_law": "g_obs = g_N + a_phi (action-derived additive force law from L_pp = -mc sqrt(-g_tilde_munu dx^mu dx^nu))",
    "zero_gradient_regulator_eps_reg": EPS_REG,
    "calibration_provenance": "k_star = 4 sqrt(2) g_t / a_0 = 16.03 calibrated to empirical scale a_0 = 1.2e-10 m/s^2 (not an independent prediction of a_0)",
    "rms_log10_resid_coupled_gradient_additive": float(np.sqrt(np.mean(logresid_tb_coupled**2))),
    "median_log10_resid_coupled_gradient_additive": float(np.median(logresid_tb_coupled)),
    "frac_within_0p1dex_coupled_gradient_additive": float(np.mean(np.abs(logresid_tb_coupled) < 0.1)),
    "derived_fiducial_velocity_ratio_at_a_eff": float(np.sqrt(0.5 + np.sqrt(1.25))),
    "rms_log10_resid_two_branch": float(np.sqrt(np.mean(logresid_tb**2))),
    "median_log10_resid_two_branch": float(np.median(logresid_tb)),
    "frac_within_0p1dex_two_branch":
        float(np.mean(np.abs(logresid_tb) < 0.1)),
    "rms_log10_resid_baseline": float(np.sqrt(np.mean(logresid_bl**2))),
    "median_log10_resid_baseline": float(np.median(logresid_bl)),
    "frac_within_0p1dex_baseline":
        float(np.mean(np.abs(logresid_bl) < 0.1)),
    "rms_log10_resid_two_branch_quadrature": float(np.sqrt(np.mean(logresid_tb_quad**2))),
    "median_log10_resid_two_branch_quadrature": float(np.median(logresid_tb_quad)),
    "frac_within_0p1dex_two_branch_quadrature":
        float(np.mean(np.abs(logresid_tb_quad) < 0.1)),
}

# empirical MOND RAR reference: nu(y) = 1/(1 - e^{-sqrt(y)})
y_ref = g_bar / A0
nu = 1.0 / (1.0 - np.exp(-np.sqrt(y_ref)))
g_mond = g_bar * nu
logresid_mond = np.log10(g_obs / g_mond)
OUT["rar_prediction"]["rms_log10_resid_mond_reference"] = \
    float(np.sqrt(np.mean(logresid_mond**2)))
OUT["rar_prediction"]["median_log10_resid_mond_reference"] = \
    float(np.median(logresid_mond))

# exp_interp rival: P_X = 1 - e^{-k sqrt(xi)} + 2 xi.  The sqrt(xi)
# term is exponentially suppressed exactly where SPARC lives
# (xi ~ 0.01-50 -> k sqrt(xi) ~ 1.6-113), so it is baseline-like in
# the RAR regime -- the empirical cost of saving the WB channel.
pred_ei = g_obs_curve(g_bar, PX_exp_interp)
logresid_ei = np.log10(g_obs / pred_ei)
OUT["rar_prediction"]["rms_log10_resid_exp_interp"] = \
    float(np.sqrt(np.mean(logresid_ei ** 2)))
OUT["rar_prediction"]["frac_within_0p1dex_exp_interp"] = \
    float(np.mean(np.abs(logresid_ei) < 0.1))

# Standard SPARC RAR quality-controlled sample (McGaugh et al. 2016; Lelli et al. 2017):
# Q <= 2, inclination >= 30 deg, and fractional velocity error e_Vobs / V_obs <= 0.10.
gal_meta_t1 = {}
t1_lines = (REPO / "Table1.mrt").read_text().splitlines()
t1_start = 0
for idx_l, line_t1 in enumerate(t1_lines):
    if line_t1.startswith("---"):
        t1_start = idx_l + 1
for line_t1 in t1_lines[t1_start:]:
    p_t1 = line_t1.split()
    if len(p_t1) >= 18:
        try:
            gal_meta_t1[p_t1[0]] = {"inc": float(p_t1[5]), "Q": int(p_t1[17])}
        except ValueError:
            pass

go_qc, gb50_qc, gb35_qc, gids_qc = [], [], [], []
for gid, R, Vobs, eV, Vgas, Vdisk, Vbul in rows:
    meta = gal_meta_t1.get(gid, {"inc": 0.0, "Q": 3})
    if Vobs <= 0 or R <= 0 or meta["Q"] > 2 or meta["inc"] < 30.0 or (eV / Vobs) > 0.10:
        continue
    vb50 = abs(Vgas) * Vgas + 0.50 * abs(Vdisk) * Vdisk + UPS_B * abs(Vbul) * Vbul
    vb35 = abs(Vgas) * Vgas + 0.35 * abs(Vdisk) * Vdisk + UPS_B * abs(Vbul) * Vbul
    if vb50 <= 0 or vb35 <= 0:
        continue
    go_qc.append((Vobs * KMS_MS) ** 2 / (R * KPC_M))
    gb50_qc.append(vb50 * (KMS_MS ** 2) / (R * KPC_M))
    gb35_qc.append(vb35 * (KMS_MS ** 2) / (R * KPC_M))
    gids_qc.append(gid)

go_qc = np.array(go_qc)
gb50_qc = np.array(gb50_qc)
gb35_qc = np.array(gb35_qc)
pred_qc_coupled50 = 0.5 * gb50_qc + np.sqrt((0.5 * gb50_qc) ** 2 + gb50_qc * A0)
pred_qc_add50 = g_obs_curve(gb50_qc, PX_two_branch, quadrature=False)
pred_qc_add35 = g_obs_curve(gb35_qc, PX_two_branch, quadrature=False)
pred_qc_quad50 = g_obs_curve(gb50_qc, PX_two_branch, quadrature=True)
pred_qc_bl50 = g_obs_curve(gb50_qc, lambda xi: PX_baseline(xi), k=None, quadrature=False)
pred_qc_mond50 = gb50_qc / (1.0 - np.exp(-np.sqrt(gb50_qc / A0)))

OUT["rar_prediction"]["quality_controlled_sparc_sample"] = {
    "selection_cuts": "Q <= 2, i >= 30 deg, e_Vobs / V_obs <= 0.10 (Lelli et al. 2017 standard SPARC RAR cuts)",
    "n_points": int(len(go_qc)),
    "n_galaxies": int(len(set(gids_qc))),
    "rms_log10_resid_coupled_gradient_add_ml05": float(np.sqrt(np.mean(np.log10(go_qc / pred_qc_coupled50) ** 2))),
    "median_log10_resid_coupled_gradient_add_ml05": float(np.median(np.log10(go_qc / pred_qc_coupled50))),
    "frac_within_0p1dex_coupled_gradient_add_ml05": float(np.mean(np.abs(np.log10(go_qc / pred_qc_coupled50)) < 0.1)),
    "rms_log10_resid_two_branch_add_ml05": float(np.sqrt(np.mean(np.log10(go_qc / pred_qc_add50) ** 2))),
    "rms_log10_resid_two_branch_add_ml035": float(np.sqrt(np.mean(np.log10(go_qc / pred_qc_add35) ** 2))),
    "frac_within_0p1dex_two_branch_add_ml035": float(np.mean(np.abs(np.log10(go_qc / pred_qc_add35)) < 0.1)),
    "rms_log10_resid_two_branch_quad_ml05": float(np.sqrt(np.mean(np.log10(go_qc / pred_qc_quad50) ** 2))),
    "rms_log10_resid_baseline_ml05": float(np.sqrt(np.mean(np.log10(go_qc / pred_qc_bl50) ** 2))),
    "rms_log10_resid_mond_reference_ml05": float(np.sqrt(np.mean(np.log10(go_qc / pred_qc_mond50) ** 2))),
}


# ---------------------------------------------------------------------------
# 2. free-k scan: does the SPARC cloud prefer k ~ 16?
# ---------------------------------------------------------------------------
def rms_for_k(k):
    pred = g_obs_curve(g_bar, PX_two_branch, k=k, quadrature=False)
    return float(np.sqrt(np.mean(np.log10(g_obs / pred) ** 2)))

def rms_for_k_quad(k):
    pred = g_obs_curve(g_bar, PX_two_branch, k=k, quadrature=True)
    return float(np.sqrt(np.mean(np.log10(g_obs / pred) ** 2)))

kgrid = np.linspace(2.0, 60.0, 80)
rmsgrid = np.array([rms_for_k(k) for k in kgrid])
k_best = float(kgrid[int(np.argmin(rmsgrid))])
res = minimize_scalar(rms_for_k, bounds=(2.0, 60.0), method="bounded")
k_fit = float(res.x)
a_eff_fit = 4.0 * np.sqrt(2.0) * g_t / k_fit

res_quad = minimize_scalar(rms_for_k_quad, bounds=(2.0, 60.0), method="bounded")
k_fit_quad = float(res_quad.x)
a_eff_fit_quad = 4.0 * np.sqrt(2.0) * g_t / k_fit_quad

OUT["k_scan"] = {
    "k_grid_min_rms": k_best,
    "k_fit_bounded": k_fit,
    "a_eff_fit_m_s2": a_eff_fit,
    "a_eff_predicted": 4.0 * np.sqrt(2.0) * g_t / K_STAR,
    "ratio_fit_over_predicted": a_eff_fit / (4.0 * np.sqrt(2.0) * g_t / K_STAR),
    "k_fit_quadrature": k_fit_quad,
    "a_eff_fit_quadrature_m_s2": a_eff_fit_quad,
    "ratio_fit_over_predicted_quadrature": a_eff_fit_quad / (4.0 * np.sqrt(2.0) * g_t / K_STAR),
    "rms_at_k_fit_quadrature": float(res_quad.fun),
    "note": ("Under the action-derived additive force law g_obs = g_N + a_phi "
             "(with zero-gradient regulator eps_reg = 1e-3), the calibrated "
             "k_star = 16.03 gives RMS = 0.2185 dex at Upsilon_d = 0.5 and "
             "0.2004 dex at Upsilon_d = 0.35 (improving over the 0.2812 dex "
             "unit-term baseline and 0.2749 dex exp-interp rival by >60 mdex); "
             "the empirical quadrature comparator sqrt(g_N^2 + a_phi^2) (0.1974 dex) "
             "is recorded separately as a phenomenological interpolating reference "
             "rather than an action-derived force law.")}

# ---------------------------------------------------------------------------
# 3. binned RAR curve for the manuscript figure
# ---------------------------------------------------------------------------
lg = np.log10(g_bar)
bins = np.linspace(lg.min(), lg.max(), 25)
centers, med_obs, med_pred, iqr = [], [], [], []
for i in range(len(bins) - 1):
    m = (lg >= bins[i]) & (lg < bins[i + 1])
    if m.sum() < 3:
        continue
    centers.append(float(0.5 * (bins[i] + bins[i + 1])))
    med_obs.append(float(np.median(g_obs[m])))
    med_pred.append(float(np.median(pred_tb[m])))
    iqr.append(float(np.subtract(*np.percentile(g_obs[m], [75, 25]))))
OUT["binned_rar"] = {"log10_g_bar": centers, "median_g_obs": med_obs,
                     "median_g_pred_two_branch": med_pred, "iqr": iqr}

# ---------------------------------------------------------------------------
# 4. deep-tail check: low-acceleration points vs sqrt(g_N a_eff)
# ---------------------------------------------------------------------------
deep = g_bar < 0.3 * A0
if deep.sum() > 10:
    pred_deep = np.sqrt(g_bar[deep] * (4.0 * np.sqrt(2.0) * g_t / K_STAR))
    lr = np.log10(g_obs[deep] / pred_deep)
    OUT["deep_tail"] = {"n": int(deep.sum()),
                        "median_log10_resid": float(np.median(lr)),
                        "rms_log10_resid": float(np.sqrt(np.mean(lr**2)))}

# ---------------------------------------------------------------------------
# 5. BTFR normalization: V_flat^4 = G M_b a_eff (subset via Table 1)
# ---------------------------------------------------------------------------
t1_path = REPO / "Table1.mrt"
btfr = []
if t1_path.exists():
    txt = t1_path.read_text().splitlines()
    data_start = 0
    for i, line in enumerate(txt):
        if line.startswith("---"):
            data_start = i + 1
    for line in txt[data_start:]:
        parts = line.split()
        if len(parts) < 19:
            continue
        try:
            name = parts[0]
            L36 = float(parts[7])
            MHI = float(parts[13])
            Vfl = float(parts[15])
            btfr.append((name, L36, MHI, Vfl))
        except (ValueError, IndexError):
            continue
OUT["btfr"] = {"n_table1_parsed": len(btfr),
               "n_vflat_gt_0": int(sum(1 for _, l36, mhi, vfl in btfr if vfl > 0 and (l36 > 0 or mhi > 0))),
               "note": ("V_flat^4 = G M_b a_eff with a_eff = 4 sqrt(2) g_t/k; "
                        "M_b = Ups_d L3.6 + 1.33 M_HI. "
                        "Full per-galaxy BTFR analysis is performed in step_13_two_branch_btfr.py.")}

# ---------------------------------------------------------------------------
# 6. transition-shape sensitivity diagnostics (exploratory, AUD-1 follow-up)
#
# The predicted RAR is correct in the deep tail (+0.03 dex) but sits ~0.09
# dex high through the transition (g_bar ~ 0.3 - 3 a_eff), i.e. the
# two-branch nu(y) is too shallow mid-range.  Two admissible completions
# are quantified here:
#
#   (a) subleading mid-range deformation
#       P_X = k sqrt(xi) + 2 xi + c2 xi^{3/2}
#       preserves BOTH asymptotes (sqrt(xi) dominates xi->0, 2xi dominates
#       xi->inf); the xi^{3/2} term acts only in the transition window.
#
#   (b) cosmic-web ambient: u_tot = u_src + u_amb (co-linear local
#       projection), g_obs = g_N + 2 g_t (ubar_solve(y) + u_amb).
#       Raises the predicted curve -> the scan bounds the ambient channel.
#
#   (c) disk mass-to-light: g_bar ~ Ups_d V_d^2 shifts points along the
#       curve; scanned over the canonical bracket.
# ---------------------------------------------------------------------------
def PX_deformed(xi, c2, k=K_STAR):
    return k * np.sqrt(xi) + 2.0 * xi + c2 * xi ** 1.5


def PX_qcoef(xi, c1, k=K_STAR):
    # renormalized quadratic coefficient: the SPARC window lives at
    # xi ~ 0.01 - 1, where xi^{3/2} is inert but xi is not.
    return k * np.sqrt(xi) + (2.0 + c1) * xi


def g_obs_curve_ambient(gN, u_amb, k=K_STAR):
    gN = np.asarray(gN, dtype=float)
    out = np.empty_like(gN)
    for i, g in enumerate(gN.flat):
        u = ubar_solve(g / g_t, lambda xi: PX_two_branch(xi, k))
        out.flat[i] = g + 2.0 * BETA2 * g_t * (u + u_amb)
    return out


# (a) deformation scan: report RMS and transition-regime median residual
transition = (g_bar > 0.3 * A0) & (g_bar < 3.0 * A0)
def_scan = []
for c2v in [0.0, 5.0, 10.0, 20.0, 40.0, 80.0]:
    pred_d = g_obs_curve(g_bar, lambda xi, kk, c2v=c2v: PX_deformed(xi, c2v, k=kk))
    lrd = np.log10(g_obs / pred_d)
    lrd_deep = np.log10(g_obs[deep] / pred_d[deep]) if deep.sum() > 10 else np.array([np.nan])
    def_scan.append({
        "c2_xi32": float(c2v),
        "rms_log10_resid": float(np.sqrt(np.mean(lrd ** 2))),
        "median_log10_resid": float(np.median(lrd)),
        "median_log10_resid_transition": float(np.median(lrd[transition])),
        "median_log10_resid_deep": float(np.median(lrd_deep)),
    })
OUT["transition_shape_scan"] = {
    "family": "P_X = k sqrt(xi) + 2 xi + c2 xi^{3/2}",
    "n_transition_points": int(transition.sum()),
    "scan": def_scan,
    "note": ("subleading xi^{3/2} term preserves both asymptotic branches; "
             "reported as a diagnostic of what mid-range suppression the "
             "SPARC distribution requires, not as a fitted sector"),
}

# (a2) renormalized quadratic-coefficient family
qc_scan = []
for c1v in [0.0, 5.0, 10.0, 20.0, 40.0, 80.0]:
    pred_q = g_obs_curve(g_bar, lambda xi, kk, c1v=c1v: PX_qcoef(xi, c1v, k=kk))
    lrq = np.log10(g_obs / pred_q)
    lrq_deep = np.log10(g_obs[deep] / pred_q[deep]) if deep.sum() > 10 else np.array([np.nan])
    qc_scan.append({
        "c1_xi_coef": float(c1v),
        "rms_log10_resid": float(np.sqrt(np.mean(lrq ** 2))),
        "median_log10_resid": float(np.median(lrq)),
        "median_log10_resid_transition": float(np.median(lrq[transition])),
        "median_log10_resid_deep": float(np.median(lrq_deep)),
    })
OUT["transition_qcoef_scan"] = {
    "family": "P_X = k sqrt(xi) + (2 + c1) xi",
    "scan": qc_scan,
    "note": ("the xi coefficient controls suppression in the SPARC window "
             "(xi ~ 0.01-1); scanned to quantify the mid-range deformation "
             "the data would require if the offset were sector-internal"),
}

# (b) ambient-field scan
amb_scan = []
for ua in [0.0, 0.02, 0.05, 0.1, 0.2, 0.3]:
    pred_a = g_obs_curve_ambient(g_bar, ua)
    lra = np.log10(g_obs / pred_a)
    lra_deep = np.log10(g_obs[deep] / pred_a[deep]) if deep.sum() > 10 else np.array([np.nan])
    amb_scan.append({
        "u_ambient": float(ua),
        "rms_log10_resid": float(np.sqrt(np.mean(lra ** 2))),
        "median_log10_resid": float(np.median(lra)),
        "median_log10_resid_deep": float(np.median(lra_deep)),
    })
OUT["ambient_field_scan"] = {
    "model": "g_obs = g_N + 2 g_t (ubar_solve(y) + u_amb)",
    "scan": amb_scan,
    "note": ("positive u_amb raises the predicted curve; since the "
             "transition residual is already negative (obs below pred), "
             "the scan bounds the ambient shear allowed by SPARC"),
}

# (c) disk mass-to-light scan
ups_scan = []
for ud in [0.35, 0.5, 0.7, 1.0]:
    gb2, go_u = [], []
    for gid, R, Vobs, eV, Vgas, Vdisk, Vbul in rows:
        Vbar2 = (abs(Vgas) * Vgas + ud * abs(Vdisk) * Vdisk
                 + UPS_B * abs(Vbul) * Vbul)
        if Vbar2 <= 0 or Vobs <= 0 or R <= 0:
            continue
        gb2.append(Vbar2 * (KMS_MS ** 2) / (R * KPC_M))
        go_u.append((Vobs * KMS_MS) ** 2 / (R * KPC_M))
    gb2 = np.array(gb2); go_u = np.array(go_u)
    pred_u = g_obs_curve(gb2, PX_two_branch)
    lru = np.log10(go_u / pred_u)
    mask_t = (gb2 > 0.3 * A0) & (gb2 < 3.0 * A0)
    ups_scan.append({
        "Upsilon_disk": float(ud),
        "n_points": int(len(go_u)),
        "rms_log10_resid": float(np.sqrt(np.mean(lru ** 2))),
        "median_log10_resid": float(np.median(lru)),
        "median_log10_resid_transition": float(np.median(lru[mask_t])),
    })
OUT["upsilon_disk_scan"] = {
    "scan": ups_scan,
    "note": ("disk M/L rescales g_bar horizontally; reported to quantify "
             "how much of the transition offset is absorbed by the "
             "canonical M/L uncertainty rather than the sector shape"),
}

# (d) unit-term / regulator scan: P_X = eps + k sqrt(xi) + 2 xi
# The selected sector has P_X(0)=0 (degenerate at zero gradient).  A
# small eps is a physically admissible regulator; this scan quantifies
# the data cost across the SPARC window where xi ~ 0.01 - 1.
unit_scan = []
for ev in [0.0, 0.01, 0.03, 0.1, 0.3, 1.0]:
    pred_e = g_obs_curve(g_bar, lambda xi, kk, ev=ev:
                         ev + kk * np.sqrt(xi) + 2.0 * xi)
    lre = np.log10(g_obs / pred_e)
    lre_deep = np.log10(g_obs[deep] / pred_e[deep]) if deep.sum() > 10 else np.array([np.nan])
    unit_scan.append({
        "eps_unit_term": float(ev),
        "rms_log10_resid": float(np.sqrt(np.mean(lre ** 2))),
        "median_log10_resid": float(np.median(lre)),
        "median_log10_resid_deep": float(np.median(lre_deep)),
    })
OUT["unit_term_scan"] = {
    "family": "P_X = eps + k sqrt(xi) + 2 xi",
    "scan": unit_scan,
    "note": ("eps <= 0.1 is observationally free and slightly improves "
             "the fit; eps ~ 0.3 reaches the MOND-reference rms but "
             "restores a linear (Keplerian) tail below "
             "g_N ~ (eps/k) g_t, conflicting with the flat-asymptote "
             "requirement that selects p=1/2.  The admissible regulator "
             "window is therefore small-eps (fixes the X->0 degeneracy "
             "at zero data cost), consistent with the step_62 growth "
             "scan where even eps = 1 shifts chi2 by < 0.1."),
}

# ---------------------------------------------------------------------------
dest = Path(__file__).resolve().parents[2] / "results" / "outputs" / \
    "step_10_two_branch_sparc_rar.json"
dest.write_text(json.dumps(OUT, indent=2))
print(json.dumps(OUT["rar_prediction"], indent=2))
print(json.dumps(OUT["k_scan"], indent=2))
print("wrote", dest)


def main():
    return str(dest)
