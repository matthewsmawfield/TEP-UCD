#!/usr/bin/env python3
"""K(phi)-corrected SPARC RAR (step_59 follow-up): the kinetic sector's
field-VALUE dependence.

The two-centre solve showed the merged pair well stiffens the medium
when P(X,phi) carries a factor K(phi) = e^{c psi} with c > 0 (flux
focussing through the deep bridge).  For an isolated galaxy the same
structure suppresses the INNER response: the enclosed flux is fixed by
the source, so a = J/(K f) is reduced where the well depth psi is
large.  SPARC found the two-branch curve sits ~20% HIGH vs the data
(step_10), so an inner suppression is the right direction.

Radial solve per galaxy (r in r_* units, u in g_t units):

    K(psi) * P_X(q^2/2) * q = g_bar/g_t,   d psi/dr = -q,
    psi(r_max) = 0  (ambient level absorbed in the convention phi=0)

integrated inward, then g_obs = g_bar + 2 beta_A^2 g_t q as in
step_10.  Sweeps c over {0, 0.25, 0.5, 1.0} to see whether the
normalization offset shrinks without breaking the tail shape.
"""
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import step_10_two_branch_sparc_rar as s10

KMS_MS = s10.KMS_MS if hasattr(s10, "KMS_MS") else 1000.0
KPC_M = s10.KPC_M
G_T = s10.G_T if hasattr(s10, "G_T") else s10.g_t
g_t = s10.g_t
G_SI = 6.674e-11
M_SUN = 1.989e30
BETA2 = s10.BETA2
K_STAR = s10.K_STAR


def PX(xi):
    return K_STAR * np.sqrt(max(xi, 0.0)) + 2.0 * xi


def solve_galaxy(R_kpc, g_bar, c_k):
    """Inward integration; returns g_obs(r) prediction array."""
    order = np.argsort(R_kpc)
    R = np.asarray(R_kpc)[order]
    gb = np.asarray(g_bar)[order]
    # characteristic radius from outermost point (baryonic tail mass)
    M_tot = gb[-1] * (R[-1] * KPC_M) ** 2 / G_SI   # M = g R^2 / G
    r_star_m = np.sqrt(G_SI * M_tot / g_t)
    x = R * KPC_M / r_star_m
    psi = 0.0
    u = np.zeros_like(x)
    for i in range(len(x) - 1, -1, -1):
        y = gb[i] / g_t
        Kval = np.exp(np.clip(c_k * psi, -60.0, 60.0))
        f = lambda w: Kval * PX(w * w / 2.0) * w - y
        hi = max(1.0, y / max(Kval, 1e-12))
        while f(hi) < 0:
            hi *= 4.0
            if hi > 1e15:
                break
        u[i] = brentq(f, 0.0, hi, xtol=1e-28, rtol=1e-12)
        if i > 0:
            psi += u[i] * (x[i] - x[i - 1])
    g_pred = gb + 2.0 * BETA2 * g_t * u
    return order, g_pred


def run(c_k):
    res = []
    for gid in sorted(set(s10.gid_list)):
        rows_gid = [r for r in s10.rows if r[0] == gid]
        R = np.array([r[1] for r in rows_gid])
        Vobs = np.array([r[2] for r in rows_gid])
        eV = np.array([r[3] for r in rows_gid])
        Vgas = np.array([r[4] for r in rows_gid])
        Vdisk = np.array([r[5] for r in rows_gid])
        Vbul = np.array([r[6] for r in rows_gid])
        Vbar2 = (np.abs(Vgas) * Vgas + s10.UPS_D * np.abs(Vdisk) * Vdisk
                 + s10.UPS_B * np.abs(Vbul) * Vbul)
        mask = (Vbar2 > 0) & (Vobs > 0) & (R > 0)
        if mask.sum() < 4:
            continue
        R, Vobs, Vbar2 = R[mask], Vobs[mask], Vbar2[mask]
        gb = Vbar2 * KMS_MS ** 2 / (R * KPC_M)
        gobs = (Vobs * KMS_MS) ** 2 / (R * KPC_M)
        order, g_pred = solve_galaxy(R, gb, c_k)
        res.extend(np.log10(gobs[order] / g_pred))
    res = np.array(res)
    res = res[np.isfinite(res)]
    return {"c": c_k, "n": int(len(res)),
            "rms": float(np.sqrt(np.mean(res ** 2))),
            "median": float(np.median(res)),
            "frac_01dex": float(np.mean(np.abs(res) < 0.1))}


def main():
    out = {"model": ("J_i = K(psi) f(q) a_i, K = e^{c psi}, psi = "
                     "inward-integrated pair-well depth per galaxy"),
           "note": ("c=0 recovers step_10 two-branch pointwise result "
                    "up to the radial integration convention")}
    # psi scale diagnostic first (sets the useful c range)
    import numpy as _np
    psimax = []
    for gid in sorted(set(s10.gid_list))[:40]:
        rows_gid = [r for r in s10.rows if r[0] == gid]
        R = _np.array([r[1] for r in rows_gid])
        Vbar2 = (_np.abs(_np.array([r[4] for r in rows_gid]))
                 * _np.array([r[4] for r in rows_gid])
                 + s10.UPS_D * _np.abs(_np.array([r[5] for r in rows_gid]))
                 * _np.array([r[5] for r in rows_gid])
                 + s10.UPS_B * _np.abs(_np.array([r[6] for r in rows_gid]))
                 * _np.array([r[6] for r in rows_gid]))
        mask = (Vbar2 > 0) & (R > 0)
        if mask.sum() < 4:
            continue
        R = R[mask]; Vbar2 = Vbar2[mask]
        gb = Vbar2 * KMS_MS ** 2 / (R * KPC_M)
        order = _np.argsort(R); R = R[order]; gb = gb[order]
        M_tot = gb[-1] * (R[-1] * KPC_M) ** 2 / G_SI
        x = R * KPC_M / _np.sqrt(G_SI * M_tot / g_t)
        psi = 0.0
        for i in range(len(x) - 1, -1, -1):
            psi += s10.ubar_solve(gb[i] / g_t, lambda xi: PX(xi)) * \
                (x[i] - x[i - 1] if i > 0 else 0.0)
        psimax.append(psi)
    out["psi_interior_scale"] = {"median": float(_np.median(psimax)),
                                 "range": [float(min(psimax)),
                                           float(max(psimax))]}
    print("psi_interior median", _np.median(psimax), flush=True)

    # grid spans both signs: the WB pair channel prefers physical
    # e^{-c phi} (K<1 in wells) -- negative c here -- while the RAR
    # prefers e^{+c phi}; recording both documents the sign tension.
    for c in (-3.0, -1.0, -0.5, -0.25, 0.0, 0.005, 0.01, 0.02, 0.05,
              0.1, 0.25, 0.5, 1.0, 2.0, 3.0):
        r = run(c)
        out[f"c={c}"] = r
        print(f"c={c}: rms={r['rms']:.4f} median={r['median']:.4f} "
              f"<0.1dex={r['frac_01dex']:.3f} (n={r['n']})", flush=True)
    dest = Path(__file__).resolve().parents[2] / "results" / "outputs" / \
        "step_11_kphi_sparc.json"
    dest.write_text(json.dumps(out, indent=2))
    print("wrote", dest)
    return str(dest)


if __name__ == "__main__":
    main()
