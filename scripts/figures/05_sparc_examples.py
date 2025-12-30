import os
import sys
from collections import defaultdict

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Publication Style Configuration ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import set_pub_style as set_shared_style, COLORS, FIG_SIZE, FIG_SCALE

FIG_PRESET = 'web_grid_3x3'

set_shared_style(scale=FIG_SCALE[FIG_PRESET])

# --- Constants ---
ML_DISK = 0.5
ML_BULGE = 0.7

# From the manuscript fixed-alpha normalization (kpc / M_sun^(1/3))
K_TEP = 7.86e-4


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
                rotation_curves[name]['Vgas'].append(abs(float(parts[5])))
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
    return np.sqrt(rc['Vgas']**2 + ML_DISK * rc['Vdisk']**2 + ML_BULGE * rc['Vbul']**2)


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
    repo_root = os.path.join(os.path.dirname(__file__), '..', '..')
    data_dir = os.path.join(repo_root, 'data', 'sparc')
    output_dir = os.path.join(repo_root, 'site', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    table1 = os.path.join(data_dir, 'Table1.mrt')
    table2 = os.path.join(data_dir, 'Table2.mrt')

    if not (os.path.exists(table1) and os.path.exists(table2)):
        # Fallback: generate a small synthetic illustration if SPARC tables are absent.
        np.random.seed(7)
        fig, axes = plt.subplots(3, 3, figsize=FIG_SIZE[FIG_PRESET], constrained_layout=True)
        for i, ax in enumerate(axes.flat):
            R = np.linspace(0.1, 10, 40)
            Vbar = 50 + 50 * (1 - np.exp(-R / 2.0))
            Vobs = Vbar + 30 * (1 - np.exp(-np.maximum(R - 3, 0) / 2.0))
            ax.plot(R, Vbar, color=COLORS['secondary'], lw=1.8, label='Baryonic')
            ax.errorbar(R, Vobs, yerr=0.05 * Vobs, fmt='o', ms=2.5, color=COLORS['primary'],
                        ecolor=COLORS['primary_light'], elinewidth=0.8, capsize=0, label='Observed')
            ax.axvline(3.0, color=COLORS['highlight'], ls='--', lw=1.2, label=r'$R_{\rm trans}$')
            ax.axvline(4.0, color=COLORS['accent'], ls=':', lw=1.2, label=r'$R_{\rm DM}$')
            ax.set_title(f'Synthetic {i+1}', fontsize=9)
            ax.set_xlabel('R (kpc)')
            ax.set_ylabel('V (km/s)')
            ax.grid(True, alpha=0.25)
            ax.legend(fontsize=6, frameon=False, loc='lower right')

        out_path = os.path.join(output_dir, 'figure_5_sparc_examples.png')
        plt.savefig(out_path, transparent=True)
        print(f"Saved synthetic example figure to {out_path}")
        return

    props = parse_table1(table1)
    curves = parse_table2(table2)

    records = []
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

    if len(records) < 9:
        raise RuntimeError(f"Not enough valid SPARC galaxies to build examples: got {len(records)}")

    # Select 9 representative galaxies across the mass range
    records.sort(key=lambda r: r['M_bar'])
    idxs = np.linspace(0, len(records) - 1, 9).round().astype(int)
    selection = [records[i] for i in idxs]

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
        ax.plot(R, Vbar, color=COLORS['secondary'], lw=1.8, label='Baryonic')
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
            label='Observed',
        )

        # Vertical markers
        ax.axvline(rec['R_pred'], color=COLORS['highlight'], ls='--', lw=1.2, label=r'$R_{\rm trans}$')
        ax.axvline(rec['R_dm'], color=COLORS['accent'], ls=':', lw=1.2, label=r'$R_{\rm DM}$')

        # Title
        logM = np.log10(rec['M_bar'])
        ax.set_title(
            f"{rec['name']}\n" + fr"$M_{{\rm bar}} \approx 10^{{{logM:.1f}}}\,M_\odot$",
        )

        ax.set_xlabel(r"$R$ (kpc)")
        ax.set_ylabel(r"$V$ (km/s)")
        ax.grid(True, alpha=0.25)

        # Keep legends small and local for readability in the 3x3 panel
        ax.legend(fontsize=6, frameon=False, loc='lower right', handlelength=2)

    out_path = os.path.join(output_dir, 'figure_5_sparc_examples.png')
    plt.savefig(out_path, transparent=True)
    print(f"Saved: {out_path}")


if __name__ == '__main__':
    run()
