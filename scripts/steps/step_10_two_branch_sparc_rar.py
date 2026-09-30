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
# kinetic-sector candidates (same registry as step_54)
# ---------------------------------------------------------------------------
def PX_two_branch(xi, k=K_STAR):
    return k * np.sqrt(xi) + 2.0 * xi

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


def g_obs_curve(gN, pxfun, k=K_STAR):
    """TEP prediction g_obs = g_N + 2 g_t ubar, vectorized."""
    gN = np.asarray(gN, dtype=float)
    out = np.empty_like(gN)
    for i, g in enumerate(gN.flat):
        u = ubar_solve(g / g_t, lambda xi: pxfun(xi, k) if k is not None
                     else pxfun(xi))
        out.flat[i] = g + 2.0 * BETA2 * g_t * u
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
pred_tb = g_obs_curve(g_bar, PX_two_branch)
pred_bl = g_obs_curve(g_bar, lambda xi: PX_baseline(xi), k=None)

logresid_tb = np.log10(g_obs / pred_tb)
logresid_bl = np.log10(g_obs / pred_bl)

OUT["rar_prediction"] = {
    "n_points": NPTS,
    "rms_log10_resid_two_branch": float(np.sqrt(np.mean(logresid_tb**2))),
    "median_log10_resid_two_branch": float(np.median(logresid_tb)),
    "rms_log10_resid_baseline": float(np.sqrt(np.mean(logresid_bl**2))),
    "median_log10_resid_baseline": float(np.median(logresid_bl)),
    "frac_within_0p1dex_two_branch":
        float(np.mean(np.abs(logresid_tb) < 0.1)),
    "frac_within_0p1dex_baseline":
        float(np.mean(np.abs(logresid_bl) < 0.1)),
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


# ---------------------------------------------------------------------------
# 2. free-k scan: does the SPARC cloud prefer k ~ 16?
# ---------------------------------------------------------------------------
def rms_for_k(k):
    pred = g_obs_curve(g_bar, PX_two_branch, k=k)
    return float(np.sqrt(np.mean(np.log10(g_obs / pred) ** 2)))

kgrid = np.linspace(2.0, 60.0, 80)
rmsgrid = np.array([rms_for_k(k) for k in kgrid])
k_best = float(kgrid[int(np.argmin(rmsgrid))])
res = minimize_scalar(rms_for_k, bounds=(2.0, 60.0), method="bounded")
k_fit = float(res.x)
a_eff_fit = 4.0 * np.sqrt(2.0) * g_t / k_fit

OUT["k_scan"] = {
    "k_grid_min_rms": k_best,
    "k_fit_bounded": k_fit,
    "a_eff_fit_m_s2": a_eff_fit,
    "a_eff_predicted": 4.0 * np.sqrt(2.0) * g_t / K_STAR,
    "ratio_fit_over_predicted": a_eff_fit / (4.0 * np.sqrt(2.0) * g_t / K_STAR),
    "note": ("a_eff fit is the single normalization freedom; the SHAPE "
             "of the curve (p=1/2 tail + 2xi screening) is fixed")}

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
    # SPARC Table 1 (byte-by-byte): Name, D, L3.6 (1e9 Lsun), MHI (1e9 Msun), Vflat
    for line in txt:
        if len(line) < 60 or line.startswith(("Title", "Authors", "Table",
                                              "=", "-", " ", "Byte", "Note",
                                              "(", "Cam")):
            continue
        parts = line.split()
        if len(parts) < 8:
            continue
        try:
            name = parts[0]
            # find numeric tail: L36 eL36? MHI Vflat
            nums = [float(x) for x in parts[1:] if
                    x.replace(".", "").replace("-", "").replace("+", "")
                    .replace("e", "").replace("E", "").isdigit()
                    or "e" in x.lower()]
            L36 = nums[-3] if len(nums) >= 3 else np.nan
            MHI = nums[-2] if len(nums) >= 2 else np.nan
            Vfl = nums[-1]
            btfr.append((name, L36, MHI, Vfl))
        except (ValueError, IndexError):
            continue
OUT["btfr"] = {"n_table1_parsed": len(btfr),
               "note": ("V_flat^4 = G M_b a_eff with a_eff = 4 sqrt(2) g_t/k; "
                        "M_b = Ups_d L3.6 + Ups_b Lbul + 1.33 M_HI. "
                        "Detailed per-galaxy BTFR fit deferred to T1.1b "
                        "(Table-1 column layout to be confirmed).")}

# ---------------------------------------------------------------------------
dest = Path(__file__).resolve().parents[2] / "results" / "outputs" / \
    "step_10_two_branch_sparc_rar.json"
dest.write_text(json.dumps(OUT, indent=2))
print(json.dumps(OUT["rar_prediction"], indent=2))
print(json.dumps(OUT["k_scan"], indent=2))
print("wrote", dest)


def main():
    return str(dest)
