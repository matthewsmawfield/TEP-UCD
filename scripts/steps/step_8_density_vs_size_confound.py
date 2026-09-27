"""
Step 8: Density-Threshold vs Size-Scaling Confound Test

The flagship SPARC result R_DM ∝ M^{1/3} is potentially degenerate with the
disk size-mass relation: for approximately self-similar exponential disks, a
fixed velocity-ratio crossing occurs at a nearly fixed multiple of the disk
scale length R_d, and the mass-size relation R_d ∝ M^0.3-0.4 would then
produce alpha ~ 0.3-0.4 without any density threshold.

This step runs the discriminating null directly on the SPARC sample:
  (i)  size-scaling null     — R_DM / R_d should be mass-independent;
  (ii) density-threshold TEP — the enclosed mean baryonic density
       rho_bar(<R_DM) = 3 M_bar(<R_DM) / (4 pi R_DM^3) should be
       mass-independent;
with M_bar(<R) estimated from the baryonic rotation curve,
M_bar(<R) = V_bar(R)^2 R / G (spherical estimate).

Outputs scatter (dex), mass-correlation slope and Spearman rho for each
candidate invariant, at three velocity-ratio thresholds, and records which
invariant survives.
"""

import numpy as np
import os
import sys
import json
from collections import defaultdict
from scipy import stats

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from utils.logger import TEPLogger, set_step_logger, print_status
except ImportError:
    pass

# --- Constants ---
G_KPC = 4.30091e-6   # kpc (km/s)^2 / Msun
MSUN_PC3 = 1e-9      # Msun/kpc^3 -> Msun/pc^3

ML_DISK = 0.5
ML_BULGE = 0.7
GAS_FACTOR = 1.33

THRESHOLDS = [1.2, 1.3, 1.4]
PRIMARY_THRESHOLD = 1.3


def parse_table1(filepath):
    """Parse SPARC Table1: luminosity, HI mass, disk scale length."""
    galaxies = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('---'):
            data_start = i + 1
    for line in lines[data_start:]:
        if line.strip() == '':
            continue
        try:
            parts = line.split()
            if len(parts) < 14:
                continue
            name = parts[0]
            galaxies[name] = {
                'L_36': float(parts[7]) * 1e9,     # 10^9 Lsun -> Lsun
                'R_d': float(parts[11]),           # disk scale length, kpc
                'MHI': float(parts[13]) * 1e9,     # 10^9 Msun -> Msun
            }
        except (ValueError, IndexError):
            continue
    return galaxies


def parse_table2(filepath):
    """Parse SPARC Table2 rotation curves (identical convention to step_4)."""
    rotation_curves = defaultdict(lambda: {'R': [], 'Vobs': [], 'e_Vobs': [],
                                            'Vgas': [], 'Vdisk': [], 'Vbul': []})
    with open(filepath, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith(('Title', 'Authors', 'Table', '===', '---', 'Byte', 'Note')) or \
           'Format' in line or line.strip() == '':
            continue
        try:
            parts = line.split()
            if len(parts) >= 9:
                name = parts[0]
                rotation_curves[name]['R'].append(float(parts[2]))
                rotation_curves[name]['Vobs'].append(float(parts[3]))
                rotation_curves[name]['e_Vobs'].append(float(parts[4]))
                rotation_curves[name]['Vgas'].append(abs(float(parts[5])))
                rotation_curves[name]['Vdisk'].append(float(parts[6]))
                rotation_curves[name]['Vbul'].append(float(parts[7]))
        except (ValueError, IndexError):
            continue
    for name in rotation_curves:
        for key in rotation_curves[name]:
            rotation_curves[name][key] = np.array(rotation_curves[name][key])
    return dict(rotation_curves)


def find_rdm_for_threshold(R, Vobs, Vbar, threshold):
    """First radius where Vobs/Vbar exceeds threshold (step_4 convention)."""
    valid = (Vbar > 5) & (Vobs > 0)
    if not np.any(valid):
        return np.nan
    R_valid = R[valid]
    ratio = Vobs[valid] / Vbar[valid]
    mask = ratio > threshold
    if np.any(mask):
        return R_valid[np.argmax(mask)]
    return np.nan


def enclosed_mean_density(R, Vbar, R_dm):
    """Enclosed mean baryonic density at R_dm via spherical V^2 R / G.

    Returns Msun/pc^3. Requires R_dm within the sampled radial range.
    """
    if R_dm < R.min() or R_dm > R.max():
        return np.nan
    V_at = np.interp(R_dm, R, Vbar)
    M_enc = V_at**2 * R_dm / G_KPC          # Msun
    rho_pc3 = 3.0 * M_enc / (4.0 * np.pi * R_dm**3) * MSUN_PC3
    return rho_pc3


def summarize_invariant(values, masses):
    """Scatter (dex), log-log slope vs mass, Spearman rho and p-value."""
    v = np.asarray(values)
    m = np.asarray(masses)
    ok = np.isfinite(v) & np.isfinite(m) & (v > 0) & (m > 0)
    v, m = v[ok], m[ok]
    n = len(v)
    if n < 20:
        return None
    lx, ly = np.log10(m), np.log10(v)
    slope, intercept, r_pearson, p_pearson, se = stats.linregress(lx, ly)
    rho_s, p_s = stats.spearmanr(m, v)
    resid = ly - (slope * lx + intercept)
    return {
        'n': int(n),
        'median': float(np.median(v)),
        'scatter_dex_raw': float(np.std(ly)),
        'scatter_dex_detrended': float(np.std(resid)),
        'slope_vs_mass': float(slope),
        'slope_err': float(se),
        'pearson_r': float(r_pearson),
        'pearson_p': float(p_pearson),
        'spearman_rho': float(rho_s),
        'spearman_p': float(p_s),
    }


def run_confound_test():
    """Run the R_d-size vs enclosed-density invariance test."""
    logger = TEPLogger("step_8_density_vs_size_confound", log_file_path=os.path.join(
        os.path.dirname(__file__), '..', '..', 'logs', 'step_8_density_vs_size_confound.log'))
    set_step_logger(logger)

    print_status("Step 8: Density-Threshold vs Size-Scaling Confound Test", "TITLE")

    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sparc')
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    galaxy_props = parse_table1(os.path.join(data_dir, 'Table1.mrt'))
    rotation_curves = parse_table2(os.path.join(data_dir, 'Table2.mrt'))
    print_status(f"Loaded {len(rotation_curves)} rotation curves, {len(galaxy_props)} galaxy properties", "INFO")

    # In-sample mass-size relation: the size-scaling channel predicts an
    # onset exponent equal to the R_d - M_bar slope, so it must be measured
    # on the same sample, not imported.
    ms_masses, ms_rd = [], []
    for name, props in galaxy_props.items():
        if name not in rotation_curves:
            continue
        R_d = props['R_d']
        M_bar = props['L_36'] * ML_DISK + GAS_FACTOR * props['MHI']
        if np.isfinite(R_d) and R_d > 0 and M_bar > 0:
            ms_masses.append(M_bar)
            ms_rd.append(R_d)
    ms_masses, ms_rd = np.array(ms_masses), np.array(ms_rd)
    ms_slope, ms_int, ms_r, ms_p, ms_se = stats.linregress(
        np.log10(ms_masses), np.log10(ms_rd))
    mass_size_relation = {
        'slope': float(ms_slope), 'slope_err': float(ms_se),
        'pearson_r': float(ms_r), 'pearson_p': float(ms_p),
        'n': int(len(ms_masses)),
    }
    print_status(f"In-sample mass-size relation: R_d ∝ M^{ms_slope:.3f} ± {ms_se:.3f} "
                 f"(r={ms_r:.3f}, n={len(ms_masses)})", "INFO")

    per_threshold = {}
    for thresh in THRESHOLDS:
        masses, rdm_over_rd, rho_enc, names = [], [], [], []
        for name, rc in rotation_curves.items():
            if name not in galaxy_props:
                continue
            props = galaxy_props[name]
            R_d = props['R_d']
            if not np.isfinite(R_d) or R_d <= 0:
                continue
            if len(rc['R']) < 5:
                continue
            V_bar = np.sqrt(rc['Vgas']**2 + ML_DISK * rc['Vdisk']**2 + ML_BULGE * rc['Vbul']**2)
            M_bar = props['L_36'] * ML_DISK + GAS_FACTOR * props['MHI']
            R_dm = find_rdm_for_threshold(rc['R'], rc['Vobs'], V_bar, thresh)
            if not np.isfinite(R_dm) or R_dm <= 0 or M_bar <= 0:
                continue
            rho = enclosed_mean_density(rc['R'], V_bar, R_dm)
            if not np.isfinite(rho) or rho <= 0:
                continue
            masses.append(M_bar)
            rdm_over_rd.append(R_dm / R_d)
            rho_enc.append(rho)
            names.append(name)

        size_stats = summarize_invariant(rdm_over_rd, masses)
        dens_stats = summarize_invariant(rho_enc, masses)

        verdict = None
        if size_stats and dens_stats:
            # The surviving invariant is the one with smaller mass-correlation
            # magnitude; scatter is reported for context.
            dens_wins = abs(dens_stats['slope_vs_mass']) < abs(size_stats['slope_vs_mass'])
            verdict = 'density_threshold' if dens_wins else 'size_scaling'
            print_status(
                f"thresh {thresh}: n={size_stats['n']}  "
                f"R_DM/R_d slope={size_stats['slope_vs_mass']:.3f} (p={size_stats['pearson_p']:.2e}), "
                f"rho_enc slope={dens_stats['slope_vs_mass']:.3f} (p={dens_stats['pearson_p']:.2e})  "
                f"-> {verdict}", "SUCCESS")

        per_threshold[f"{thresh:.2f}"] = {
            'n_galaxies': len(masses),
            'size_invariant_Rdm_over_Rd': size_stats,
            'density_invariant_rho_enc': dens_stats,
            'median_Rdm_over_Rd': float(np.median(rdm_over_rd)) if rdm_over_rd else None,
            'median_rho_enc_Msun_pc3': float(np.median(rho_enc)) if rho_enc else None,
            'verdict': verdict,
        }

    primary = per_threshold[f"{PRIMARY_THRESHOLD:.2f}"]
    result = {
        'description': 'Density-threshold vs disk size-mass confound test on SPARC',
        'method': ('R_DM = first radius with Vobs/Vbar > threshold (step_4 convention). '
                   'Size null: R_DM/R_d mass-independent. Density prediction: '
                   'rho_bar(<R_DM) = 3 M_enc/(4 pi R_DM^3) mass-independent, with '
                   'M_enc = V_bar(R_DM)^2 R_DM / G (spherical estimate).'),
        'ml_disk': ML_DISK, 'ml_bulge': ML_BULGE, 'gas_factor': GAS_FACTOR,
        'mass_size_relation_Rd_vs_Mbar': mass_size_relation,
        'primary_threshold': PRIMARY_THRESHOLD,
        'per_threshold': per_threshold,
        'primary_verdict': primary['verdict'],
    }

    out_path = os.path.join(outputs_dir, 'step_8_density_vs_size_confound.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)
    print_status(f"Results written to {out_path}", "SUCCESS")
    return result


if __name__ == "__main__":
    run_confound_test()
