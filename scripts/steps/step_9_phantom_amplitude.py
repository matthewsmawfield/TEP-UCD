#!/usr/bin/env python3
"""
Step 9: Phantom-mass amplitude and radial-profile test on SPARC.

Issue 6-4: the onset radius alone does not test the mechanism. The discriminating
content of the phantom-mass claim lives in (i) the plateau amplitude and
(ii) the radial profile of the enhancement.

Under a conformal coupling with charge beta_A, an unscreened scalar adds a
centripetal channel of order 2*beta_A^2 times the Newtonian one, so

    V_obs^2 / V_bar^2 = 1 + 2*beta_A^2 * S_eff(R)

where S_eff is the effective (environmentally weighted) unscreened fraction.
For the bare coupling |beta_A| = 1 at full saturation (S_eff -> 1) the plateau
ratio is sqrt(3) ~ 1.732; observed SPARC asymptotic ratios ~1.5-2.5.

This script measures, on the real SPARC catalogue:
  1. The per-galaxy plateau ratio (median V_obs/V_bar over the outer third of
     each rotation curve) and the distribution of implied S_eff^plateau =
     (ratio^2 - 1) / (2*beta_A^2).
  2. The radial profile of the enhancement factor E(R) = V_obs^2/V_bar^2 - 1
     (equivalently M_ph/M_bar(<R)): its outer-region log-log slope tells whether
     the phantom response grows with radius (screened inside -> unscreened
     outside, the TEP transition picture) or is constant (a global rescaling).
  3. The fraction of galaxies whose plateau requires S_eff > 1, i.e. a response
     exceeding the bare |beta_A| = 1 coupling -- quantifying the amplitude-level
     demand on the response-normalization sector.

Real data only: aborts if the archived SPARC tables are absent. No synthetic
fallback.
"""

import os
import sys
import numpy as np
import json
from scipy import stats

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.logger import TEPLogger, set_step_logger, print_status
except ImportError:
    def print_status(msg, level="INFO"):
        print(msg)

def print_header(title):
    print_status(title, "TITLE")

ML_DISK = 0.5
ML_BULGE = 0.7
GAS_FACTOR = 1.33
BETA_A = 1.0          # |beta_A| for the bare conformal coupling
OUTER_FRACTION = 0.34  # outer third of points defines the plateau
MIN_POINTS = 6         # minimum valid radial points per galaxy
VBAR_MIN = 5.0         # km/s floor for a usable baryonic velocity (step-4 convention)


def parse_table1(filepath):
    """SPARC Table 1: galaxy names with rotation-curve companions."""
    galaxies = {}
    data_start = 0
    with open(filepath) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith('---'):
            data_start = i + 1
    for line in lines[data_start:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 14:
            continue
        galaxies[parts[0]] = True
    return galaxies


def parse_table2(filepath):
    """SPARC Table 2: rotation curves (same indices as step_4/step_8)."""
    curves = {}
    with open(filepath) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            try:
                name = parts[0]
                r = float(parts[2])
                vobs = float(parts[3])
                vgas = float(parts[5])
                vdisk = float(parts[6])
                vbul = float(parts[7])
            except (ValueError, IndexError):
                continue
            curves.setdefault(name, {'R': [], 'Vobs': [], 'Vgas': [], 'Vdisk': [], 'Vbul': []})
            curves[name]['R'].append(r)
            curves[name]['Vobs'].append(vobs)
            curves[name]['Vgas'].append(vgas)
            curves[name]['Vdisk'].append(vdisk)
            curves[name]['Vbul'].append(vbul)
    for name in curves:
        for k in curves[name]:
            curves[name][k] = np.array(curves[name][k])
    return curves


def baryonic_velocity(rc):
    """V_bar^2 = V_gas^2 + ML_DISK V_disk^2 + ML_BULGE V_bul^2 (step-4 convention)."""
    v2 = rc['Vgas']**2 + ML_DISK * rc['Vdisk']**2 + ML_BULGE * rc['Vbul']**2
    return np.sqrt(np.clip(v2, 0, None))


def galaxy_amplitude(rc):
    """Plateau ratio and outer-region enhancement-profile slope for one galaxy."""
    R, Vobs = rc['R'], rc['Vobs']
    Vbar = baryonic_velocity(rc)
    valid = (Vbar > VBAR_MIN) & (Vobs > 0) & np.isfinite(Vobs) & np.isfinite(Vbar)
    if valid.sum() < MIN_POINTS:
        return None
    R, Vobs, Vbar = R[valid], Vobs[valid], Vbar[valid]

    # Plateau: outer OUTER_FRACTION of valid points by radius
    n_outer = max(2, int(round(len(R) * OUTER_FRACTION)))
    ratio_all = Vobs / Vbar
    plateau_ratio = float(np.median(ratio_all[-n_outer:]))
    s_plateau = (plateau_ratio**2 - 1.0) / (2.0 * BETA_A**2)

    # Enhancement profile E(R) = V_obs^2/V_bar^2 - 1 = M_ph / M_bar(<R)
    E = ratio_all**2 - 1.0
    ok = E > 0
    slope = np.nan
    if ok.sum() >= 4:
        slope, _, _, _, _ = stats.linregress(np.log10(R[ok]), np.log10(E[ok]))

    return {
        'R_last': float(R[-1]),
        'n_points': int(len(R)),
        'plateau_ratio': plateau_ratio,
        'S_eff_plateau': float(s_plateau),
        'enhancement_profile_slope': float(slope),
        'E_outer_median': float(np.median(E[-n_outer:])),
        'E_inner_median': float(np.median(E[:max(2, len(R) - 2 * n_outer)]))
        if len(R) > 2 * n_outer else np.nan,
    }


def summarize(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return {
        'n': int(len(x)),
        'median': float(np.median(x)),
        'p16': float(np.percentile(x, 16)),
        'p84': float(np.percentile(x, 84)),
        'mean': float(np.mean(x)),
    }


def run_amplitude_test():
    print_header("Step 9: Phantom-Mass Amplitude and Profile Test")

    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sparc')
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    t1 = os.path.join(data_dir, 'Table1.mrt')
    t2 = os.path.join(data_dir, 'Table2.mrt')
    if not (os.path.exists(t1) and os.path.exists(t2)):
        print_status("SPARC tables not found; real data required. Aborting.", "ERROR")
        return {'status': 'aborted_no_data'}

    galaxy_props = parse_table1(t1)
    rotation_curves = parse_table2(t2)
    print_status(f"Loaded {len(rotation_curves)} rotation curves, {len(galaxy_props)} galaxy properties", "INFO")

    per_galaxy = {}
    for name, rc in rotation_curves.items():
        if name not in galaxy_props:
            continue
        res = galaxy_amplitude(rc)
        if res is not None:
            per_galaxy[name] = res

    ratios = np.array([g['plateau_ratio'] for g in per_galaxy.values()])
    s_plat = np.array([g['S_eff_plateau'] for g in per_galaxy.values()])
    slopes = np.array([g['enhancement_profile_slope'] for g in per_galaxy.values()])
    e_out = np.array([g['E_outer_median'] for g in per_galaxy.values()])
    e_in = np.array([g['E_inner_median'] for g in per_galaxy.values()])

    finite_slope = np.isfinite(slopes)
    n_rising = int(np.sum(slopes[finite_slope] > 0))
    rise_test = stats.wilcoxon(slopes[finite_slope]) if finite_slope.sum() > 10 else None

    bare_saturation = np.sqrt(1.0 + 2.0 * BETA_A**2)  # sqrt(3) ~ 1.732

    results = {
        'description': 'Phantom-mass amplitude and radial-profile test on SPARC',
        'method': (
            'Plateau ratio = median V_obs/V_bar over outer third of each curve. '
            'S_eff = (ratio^2 - 1)/(2 beta_A^2) with |beta_A| = 1. '
            'Enhancement profile slope = d log E / d log R with '
            'E = V_obs^2/V_bar^2 - 1 = M_ph/M_bar(<R). '
            f'V_bar floor {VBAR_MIN} km/s, >= {MIN_POINTS} valid points required.'
        ),
        'ml_disk': ML_DISK, 'ml_bulge': ML_BULGE, 'gas_factor': GAS_FACTOR,
        'beta_A': BETA_A,
        'bare_saturation_ratio_sqrt3': float(bare_saturation),
        'n_galaxies_analyzed': int(len(per_galaxy)),
        'plateau_ratio': summarize(ratios),
        'S_eff_plateau': summarize(s_plat),
        'fraction_S_eff_gt_1': float(np.mean(s_plat > 1.0)),
        'fraction_S_eff_gt_0': float(np.mean(s_plat > 0.0)),
        'enhancement_profile_slope': summarize(slopes),
        'n_profile_positive': n_rising,
        'n_profile_finite': int(finite_slope.sum()),
        'profile_wilcoxon_p': float(rise_test.pvalue) if rise_test is not None else None,
        'E_outer_median': summarize(e_out),
        'E_inner_median': summarize(e_in),
        'per_galaxy': per_galaxy,
    }

    out_path = os.path.join(outputs_dir, 'step_9_phantom_amplitude.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=4)
    print_status(f"n={len(per_galaxy)}  plateau ratio median={np.median(ratios):.3f} "
                 f"(bare sqrt3={bare_saturation:.3f})  S_eff median={np.median(s_plat):.2f} "
                 f"frac>1={np.mean(s_plat > 1):.2f}", "SUCCESS")
    print_status(f"Enhancement profile slope median={np.nanmedian(slopes):.3f} "
                 f"({n_rising}/{finite_slope.sum()} positive"
                 + (f", Wilcoxon p={rise_test.pvalue:.2e}" if rise_test is not None else "")
                 + ")", "SUCCESS")
    print_status(f"Results written to {out_path}", "SUCCESS")
    return results


if __name__ == '__main__':
    run_amplitude_test()
