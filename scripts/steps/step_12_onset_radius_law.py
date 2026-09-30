#!/usr/bin/env python3
"""AUD-2 / R2.1 — zero-parameter onset-radius law test on SPARC.

The derived radius law is R_s(M) = sqrt(G M / a_eff) with
a_eff = 4 sqrt(2) g_t / k (k = 16.03 => a_eff = 1.20e-10 m/s^2).
For each galaxy the onset radius is defined by the RAR crossing
g_bar(R_onset) = a_eff — a definitional choice that removes the
ad-hoc discrepancy threshold (plan R2.1).  M_bar is estimated from
the outermost baryonic rotation component: M_bar = R_max V_bar^2/G.

Test: log-log fit of R_onset vs M_bar; compare slope to 1/2 and the
intercept to 0.5 log10(G/a_eff) — the zero-parameter prediction.
Also reports the free-slope fit for the record (the Paper 6 M^{1/3}
exponent is 0.355 +- 0.043 +- 0.07 def.; degenerate with the
size-mass relation, Paper 0 F5).

Outputs results/outputs/step_12_onset_radius_law.json
(migrated from Paper 0 step_63).
"""
import json
import os
from pathlib import Path

import numpy as np

G = 6.674e-11
MSUN = 1.989e30
KPC_M = 3.085677581e19
KMS_MS = 1.0e3
K_STAR = 16.03
G_T = 3.4e-10
A_EFF = 4.0 * np.sqrt(2.0) * G_T / K_STAR   # 1.20e-10 m/s^2

UPS_D, UPS_B = 0.5, 0.7

REPO = Path(__file__).resolve().parents[2]
sys_table = REPO / "data" / "sparc" / "Table2.mrt"


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


def main():
    rows = parse_table2(sys_table)
    galaxies = {}
    for gid, R, Vobs, eV, Vgas, Vdisk, Vbul in rows:
        Vbar2 = (abs(Vgas) * Vgas + UPS_D * abs(Vdisk) * Vdisk
                 + UPS_B * abs(Vbul) * Vbul)
        if Vbar2 <= 0 or R <= 0:
            continue
        gbar = Vbar2 * KMS_MS ** 2 / (R * KPC_M)
        galaxies.setdefault(gid, []).append((R, Vbar2, gbar))

    recs = []
    for gid, pts in galaxies.items():
        pts.sort()
        R = np.array([p[0] for p in pts])
        Vb2 = np.array([p[1] for p in pts])
        gb = np.array([p[2] for p in pts])
        if len(R) < 4:
            continue
        imax = int(np.argmax(Vb2))
        Mbar = R[imax] * KPC_M * Vb2[imax] * KMS_MS ** 2 / G
        # onset: outermost radius where g_bar crosses a_eff downward —
        # scan all sign changes and take the LAST (outermost) crossing,
        # robust to non-monotone tails (wiggles, plateaus)
        if gb[-1] < A_EFF < gb.max():
            lg = np.log10(gb); lR = np.log10(R)
            lgT = np.log10(A_EFF)
            crossings = [i for i in range(len(lg) - 1)
                         if (lg[i] - lgT) * (lg[i + 1] - lgT) < 0
                         and lg[i] > lgT > lg[i + 1]]
            if crossings:
                i = crossings[-1]
                # np.interp requires ASCENDING xp: at a downward
                # crossing lg[i] > lg[i+1], so reverse both arrays
                r_on = 10 ** np.interp(lgT, [lg[i + 1], lg[i]],
                                       [lR[i + 1], lR[i]])
                recs.append((gid, Mbar / MSUN, r_on))

    M = np.array([r[1] for r in recs])
    Ron = np.array([r[2] for r in recs])
    ok = (M > 0) & (Ron > 0)
    M, Ron = M[ok], Ron[ok]
    x, y = np.log10(M), np.log10(Ron)

    # free fit and fixed-slope fit
    slope_free, icept_free = np.polyfit(x, y, 1)
    resid_fixed = y - (0.5 * x + 0.5 * np.log10(G * MSUN / A_EFF)
        - np.log10(KPC_M))
    icept_fixed = float(np.mean(y - 0.5 * x))
    rms_fixed = float(np.sqrt(np.mean(
        (y - (0.5 * x + icept_fixed)) ** 2)))
    rms_free = float(np.sqrt(np.mean(
        (y - (slope_free * x + icept_free)) ** 2)))
    pred_ron = np.sqrt(G * M * MSUN / A_EFF) / KPC_M
    rms_zeropar = float(np.sqrt(np.mean((y - np.log10(pred_ron)) ** 2)))

    out = {
        "a_eff": float(A_EFF), "k": K_STAR, "g_t": G_T,
        "n_galaxies_bracketed": int(len(recs)),
        "free_fit": {"slope": float(slope_free),
                     "intercept": float(icept_free),
                     "rms_dex": rms_free},
        "fixed_slope_half": {"intercept_fitted": icept_fixed,
                             "intercept_predicted": float(
                                 0.5 * np.log10(G * MSUN / A_EFF)
                                 - np.log10(KPC_M)),
                             "rms_dex": rms_fixed},
        "zero_parameter": {"rms_dex": rms_zeropar,
                           "mean_resid_dex": float(np.mean(
                               y - np.log10(pred_ron)))},
        "samples": [{"galaxy": g, "M_msun": m, "r_onset_kpc": r}
                    for g, m, r in recs],
    }

    print(f"N={len(recs)} bracketed galaxies")
    print(f"free fit: slope={slope_free:.3f} icept={icept_free:.3f} "
          f"rms={rms_free:.3f} dex")
    print(f"fixed 1/2: icept={icept_fixed:.3f} "
          f"(pred {0.5*np.log10(G*MSUN/A_EFF)-np.log10(KPC_M):.3f}) "
          f"rms={rms_fixed:.3f}")
    print(f"zero-param rms={rms_zeropar:.3f} dex, "
          f"bias={out['zero_parameter']['mean_resid_dex']:.3f}")

    path = REPO / "results" / "outputs" / "step_12_onset_radius_law.json"
    path.write_text(json.dumps(out, indent=2))
    print("wrote", path)
    return str(path)


if __name__ == "__main__":
    main()
