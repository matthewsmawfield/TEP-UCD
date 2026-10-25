import os
import sys
import json
from collections import defaultdict

import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Publication Style Configuration ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import set_pub_style as set_shared_style, COLORS, FIG_SIZE, FIG_SCALE

try:
    from utils.logger import TEPLogger, set_step_logger, print_status
except ImportError:
    pass

FIG_PRESET = 'web_grid_3x3'

set_shared_style(scale=FIG_SCALE[FIG_PRESET])

# --- Constants ---
ML_DISK = 0.5
ML_BULGE = 0.7
C_LIGHT = 2.998e8
H0_SI = 70.0e3 / 3.086e22
G_T = C_LIGHT * H0_SI / 2.0  # 3.40e-10 m/s^2 (Paper 0 §7)
A0_MOND = 1.2e-10            # m/s^2
K_STAR = 4.0 * np.sqrt(2.0) * G_T / A0_MOND  # 16.03
EPS_REG = 1.0e-3
KPC_M = 3.086e19
KMS_MS = 1.0e3


def compute_v_tep_two_branch(R_kpc, Vbar_kms, quadrature=False):
    """Compute fixed-input two-branch TEP rotation velocity V_TEP(R) (Step 10)."""
    R_m = np.asarray(R_kpc, dtype=float) * KPC_M
    Vbar_ms = np.asarray(Vbar_kms, dtype=float) * KMS_MS
    g_bar = np.where(R_m > 0, (Vbar_ms ** 2) / R_m, 0.0)
    v_tep_kms = np.zeros_like(Vbar_ms)
    for i, g in enumerate(g_bar):
        if g <= 0 or R_m[i] <= 0:
            continue
        y = g / G_T
        f = lambda w: (EPS_REG + K_STAR * (w / np.sqrt(2.0)) + (w ** 2)) * w - y
        hi = max(1.0, y)
        while f(hi) < 0 and hi < 1e15:
            hi *= 4.0
        ubar = brentq(f, 0.0, hi, xtol=1e-30, rtol=1e-12)
        a_phi = 2.0 * G_T * ubar
        g_tot = np.hypot(g, a_phi) if quadrature else (g + a_phi)
        v_tep_kms[i] = np.sqrt(g_tot * R_m[i]) / KMS_MS
    return v_tep_kms

# Load fitted normalization from step_4 output, fallback to canonical value
_K_FALLBACK = 7.96e-4
_step4_json = os.path.join(
    os.path.dirname(__file__), '..', '..', 'results', 'outputs', 'step_4_sparc_analysis.json'
)
try:
    with open(_step4_json, 'r') as _f:
        _step4_data = json.load(_f)
    K_TEP = float(_step4_data.get('k', _K_FALLBACK))
except Exception:
    K_TEP = _K_FALLBACK


def parse_table1(filepath):
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
            L_36 = float(parts[7]) * 1e9
            MHI = float(parts[13]) * 1e9
            galaxies[name] = {'L_36': L_36, 'MHI': MHI}
        except Exception:
            continue
    return galaxies


def parse_table2(filepath):
    rotation_curves = defaultdict(lambda: {
        'R': [],
        'Vobs': [],
        'e_Vobs': [],
        'Vgas': [],
        'Vdisk': [],
        'Vbul': [],
    })

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
                rotation_curves[name]['Vgas'].append(float(parts[5]))
                rotation_curves[name]['Vdisk'].append(float(parts[6]))
                rotation_curves[name]['Vbul'].append(float(parts[7]))
        except Exception:
            continue

    for name in rotation_curves:
        for key in rotation_curves[name]:
            rotation_curves[name][key] = np.array(rotation_curves[name][key])

    return dict(rotation_curves)


def calculate_baryonic_mass(props):
    return props['L_36'] * ML_DISK + 1.33 * props['MHI']


def calculate_newtonian_velocity(rc):
    v2 = np.abs(rc['Vgas']) * rc['Vgas'] + ML_DISK * np.abs(rc['Vdisk']) * rc['Vdisk'] + ML_BULGE * np.abs(rc['Vbul']) * rc['Vbul']
    return np.sqrt(np.clip(v2, 0.0, None))


def find_rdm_for_threshold(R, Vobs, Vbar, threshold=1.3):
    valid = (Vbar > 5) & (Vobs > 0) & (R > 0)
    if not np.any(valid):
        return np.nan
    R_valid = R[valid]
    ratio = Vobs[valid] / Vbar[valid]
    mask = ratio > threshold
    if np.any(mask):
        return R_valid[np.argmax(mask)]
    return np.nan


def run():
    """Generate Figure 5b: SPARC example rotation curves."""
    logger = TEPLogger("step_4b_sparc_examples", log_file_path=os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'step_4b_sparc_examples.log'))
    set_step_logger(logger)

    repo_root = os.path.join(os.path.dirname(__file__), '..', '..')
    data_dir = os.path.join(repo_root, 'data', 'sparc')
    output_dir = os.path.join(repo_root, 'results', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    outputs_dir = os.path.join(repo_root, 'results', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    print_status("SPARC Example Rotation Curves", "PROCESS")

    table1 = os.path.join(data_dir, 'Table1.mrt')
    table2 = os.path.join(data_dir, 'Table2.mrt')

    if not (os.path.exists(table1) and os.path.exists(table2)):
        raise FileNotFoundError(
            f"SPARC tables absent ({table1}, {table2}); synthetic illustration fallback is disabled."
        )

    print_status("Parsing SPARC tables", "PROCESS")
    props = parse_table1(table1)
    curves = parse_table2(table2)
    print_status(f"Loaded {len(props)} galaxies, {len(curves)} rotation curves", "INFO")

    records = []
    print_status("Computing baryonic masses and R_dm for each galaxy", "PROCESS")
    for name, rc in curves.items():
        if name not in props:
            continue
        M_bar = calculate_baryonic_mass(props[name])
        if not np.isfinite(M_bar) or M_bar <= 0:
            continue
        V_bar = calculate_newtonian_velocity(rc)
        R_dm = find_rdm_for_threshold(rc['R'], rc['Vobs'], V_bar, threshold=1.3)
        if not np.isfinite(R_dm) or R_dm <= 0:
            continue
        records.append({
            'name': name,
            'M_bar': M_bar,
            'rc': rc,
            'V_bar': V_bar,
            'R_dm': R_dm,
            'R_pred': K_TEP * M_bar**(1/3),
        })

    print_status(f"Valid galaxies with R_dm: {len(records)}", "INFO")
    if len(records) < 9:
        raise RuntimeError(f"Not enough valid SPARC galaxies to build examples: got {len(records)}")

    # Select 9 representative galaxies across the mass range
    records.sort(key=lambda r: r['M_bar'])
    idxs = np.linspace(0, len(records) - 1, 9).round().astype(int)
    selection = [records[i] for i in idxs]
    print_status(f"Selected 9 representative galaxies (log M_bar = {np.log10(selection[0]['M_bar']):.1f} to {np.log10(selection[-1]['M_bar']):.1f})", "INFO")

    fig, axes = plt.subplots(3, 3, figsize=FIG_SIZE[FIG_PRESET], constrained_layout=True)

    for ax, rec in zip(axes.flat, selection):
        rc = rec['rc']
        R = rc['R']
        Vobs = rc['Vobs']
        eV = rc['e_Vobs']
        Vbar = rec['V_bar']

        # Clean to positive radii
        valid = (R > 0) & (Vobs > 0) & (Vbar > 0)
        R = R[valid]
        Vobs = Vobs[valid]
        eV = eV[valid]
        Vbar = Vbar[valid]

        # Screened zone shading (up to the predicted transition scale)
        R_shade = max(0.0, min(rec['R_pred'], np.max(R)))
        ax.axvspan(0, R_shade, color=COLORS['primary_light'], alpha=0.06)

        # Curves
        Vtep_add = compute_v_tep_two_branch(R, Vbar, quadrature=False)
        Vtep_quad = compute_v_tep_two_branch(R, Vbar, quadrature=True)
        ax.plot(R, Vbar, color=COLORS['secondary'], lw=1.6, label='Baryonic ($V_{\\rm bar}$)')
        ax.plot(R, Vtep_add, color=COLORS['accent'], lw=2.0, label='TEP 2-branch (additive)')
        ax.plot(R, Vtep_quad, color=COLORS['accent'], lw=1.3, ls='-.', alpha=0.80, label='Quadrature comparator')
        ax.errorbar(
            R,
            Vobs,
            yerr=eV,
            fmt='o',
            ms=2.4,
            color=COLORS['primary'],
            ecolor=COLORS['primary_light'],
            elinewidth=0.8,
            capsize=0,
            label='Observed ($V_{\\rm obs}$)',
        )

        # Vertical markers
        ax.axvline(rec['R_pred'], color=COLORS['highlight'], ls='--', lw=1.2, label=r'$R_{\rm trans}$ (pred.)')
        ax.axvline(rec['R_dm'], color='dimgray', ls=':', lw=1.3, label=r'$R_{\rm DM}$ (obs.)')

        # Title
        logM = np.log10(rec['M_bar'])
        ax.set_title(
            f"{rec['name']}\n" + fr"$M_{{\rm bar}} \approx 10^{{{logM:.1f}}}\,M_\odot$",
        )

        ax.set_xlabel(r"$R$ (kpc)")
        ax.set_ylabel(r"$V$ (km/s)")
        ax.grid(True, alpha=0.25)

    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc='outside upper center',
        ncol=6,
        frameon=False,
        fontsize=7.6,
        handlelength=1.8,
        columnspacing=1.0,
    )

    out_path = os.path.join(output_dir, 'figure_6_sparc_examples.png')
    plt.savefig(out_path)
    print_status(f"Saved: {out_path}", "SUCCESS")

    # Save numerical outputs
    output_data = {"figure": "figure_6_sparc_examples.png", "K_TEP": float(K_TEP)}
    with open(os.path.join(outputs_dir, 'step_4b_sparc_examples.json'), 'w') as f:
        json.dump(output_data, f, indent=2)
    try:
        print_status("Numerical outputs saved to results/outputs/step_4b_sparc_examples.json", "SUCCESS")
    except Exception:
        pass
    return output_data


if __name__ == '__main__':
    run()
