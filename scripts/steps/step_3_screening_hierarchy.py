import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import sys
import json

# --- Publication Style Configuration ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import set_pub_style as set_shared_style, COLORS, FIG_SIZE, FIG_SCALE

try:
    from utils.logger import TEPLogger, set_step_logger, print_status
except ImportError:
    pass

from core.constants import M_EARTH, M_SUN, R_EARTH, R_SUN, SCREENING_LENGTH_KM, RHO_C

FIG_PRESET = 'web_two_panel'


def set_pub_style():
    set_shared_style(scale=FIG_SCALE[FIG_PRESET])


def run_screening_hierarchy():
    """Generate Figure 4: Screening hierarchy across object classes."""
    logger = None
    try:
        logger = TEPLogger("step_3_screening_hierarchy", log_file_path=os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'step_3_screening_hierarchy.log'))
        set_step_logger(logger)
    except Exception:
        pass

    set_pub_style()

    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    # --- Constants ---
    M_earth = M_EARTH
    M_sun = M_SUN
    R_sun = R_SUN
    R_earth = R_EARTH
    R_TEP_earth = SCREENING_LENGTH_KM * 1000  # meters
    rho_T = RHO_C  # g/cm³ (saturation scale of temporal-field topology; not an on/off switch)

    # Physical constants for proximity axis
    M_E = 9.1093837015e-31     # kg
    HBAR = 1.054571817e-34      # J s
    C = 299792458.0             # m/s
    M_PROTON = 1.67262192369e-27  # kg
    Z_OVER_A = 0.5
    R_C = HBAR / (M_E * C)      # Compton radius ~ 3.86e-13 m
    LAMBDA_SCR = 2**0.5 * R_C   # Yukawa screening length

    # --- Data Objects ---
    objects = {
        'Earth': {'M': 1 * M_earth, 'R': 6371, 'type': 'planet', 'rho': 5.5},
        'Jupiter': {'M': 317.8 * M_earth, 'R': 69911, 'type': 'planet', 'rho': 1.33},
        'Sun': {'M': 1.0 * M_sun, 'R': 696340, 'type': 'ms', 'rho': 1.41},
        'Proxima': {'M': 0.122 * M_sun, 'R': 0.154 * 696340, 'type': 'ms', 'rho': 56.8},
        'Sirius B': {'M': 1.018 * M_sun, 'R': 5800, 'type': 'wd', 'rho': 2.38e6},
        'Procyon B': {'M': 0.602 * M_sun, 'R': 8600, 'type': 'wd', 'rho': 5.5e5},
        'Typical NS': {'M': 1.4 * M_sun, 'R': 12, 'type': 'ns', 'rho': 4e14},
    }

    # Calculations
    for name, obj in objects.items():
        R_T = R_TEP_earth * (obj['M'] / M_earth)**(1/3) / 1000  # km
        obj['R_T'] = R_T
        obj['screening'] = R_T / obj['R']

    # --- Plotting ---
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE[FIG_PRESET], constrained_layout=True)

    # Colors per type
    colors = {
        'planet': COLORS['accent'],
        'ms': COLORS['highlight'],
        'wd': COLORS['primary_light'],
        'ns': COLORS['hover']
    }
    markers = {
        'planet': 'o',
        'ms': 's',
        'wd': '^',
        'ns': 'D'
    }
    labels = {
        'planet': 'Planets',
        'ms': 'Main Sequence',
        'wd': 'White Dwarfs',
        'ns': 'Neutron Stars'
    }

    # --- Proximity helper ---
    def fermi_wavelength(rho_kg_m3):
        n_e = rho_kg_m3 * Z_OVER_A / M_PROTON
        k_F = (3.0 * np.pi**2 * n_e) ** (1.0 / 3.0)
        return 2.0 * np.pi / k_F

    def lambda_F_from_rho_g_cm3(rho_g_cm3):
        return fermi_wavelength(rho_g_cm3 * 1000.0)

    # --- Panel A: Screening Factor vs Density (with Proximity Axis) ---
    ax1 = axes[0]
    ax1.set_title(r"$\bf{a)}$ Screening Factor vs Density", loc='left')

    # Plot Objects
    for name, obj in objects.items():
        t = obj['type']
        ax1.scatter(obj['rho'], obj['screening'], color=colors[t], marker=markers[t],
                    s=80, edgecolors='k', lw=0.5, zorder=5)

        # Annotations
        if name in ['Earth', 'Sirius B', 'Typical NS']:
            ax1.annotate(name, (obj['rho'], obj['screening']), xytext=(0, 5),
                         textcoords='offset points', ha='center')

    # Theoretical lines
    ax1.axvline(x=rho_T, color='k', linestyle='--', alpha=0.5)
    ax1.text(rho_T*1.5, 0.6, r'$\rho_T \approx 20$ g/cm³', rotation=90, va='bottom')

    # Proximity regime bands (vertical, on primary axis)
    # Core overlap: lambda_F < r_c  =>  rho > ~10^4 g/cm³
    # Transition: r_c < lambda_F < 10*r_c
    # Dilute: lambda_F > 10*r_c
    rho_core = 1e4   # g/cm³ where lambda_F ~ r_c
    rho_trans_hi = rho_core
    rho_trans_lo = rho_core / 1000.0  # ~10 g/cm³ where lambda_F ~ 10*r_c
    ax1.axvspan(rho_trans_hi, 1e16, color='red', alpha=0.06, label='Core overlap')
    ax1.axvspan(rho_trans_lo, rho_trans_hi, color='orange', alpha=0.06, label='Transition')
    ax1.axvspan(1e-1, rho_trans_lo, color='green', alpha=0.06, label='Dilute')

    # Unity Line
    ax1.axhline(y=1, color='gray', linestyle=':', alpha=0.5)
    ax1.text(1e-1, 1.1, 'No Screening', color='gray')

    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel(r'Mean Density $\rho$ (g/cm³)  (observable proxy for proximity)')
    ax1.set_ylabel(r'Screening Factor $S = R_T/R_{phys}$')
    ax1.set_xlim(1e-1, 1e16)
    ax1.set_ylim(0.5, 1e8)
    ax1.grid(True, which='major', alpha=0.3)

    # Secondary x-axis: Fermi wavelength (top)
    ax1_top = ax1.twiny()
    ax1_top.set_xscale('log')
    ax1_top.set_xlim(ax1.get_xlim())

    # Map density ticks to lambda_F values
    tick_rhos = np.array([1e-1, 1e0, 1e1, 1e2, 1e4, 1e8, 1e12, 1e16])
    tick_lams = [lambda_F_from_rho_g_cm3(r) for r in tick_rhos]
    ax1_top.set_xticks(tick_rhos)
    ax1_top.set_xticklabels([f'{lam:.0e}' for lam in tick_lams])
    ax1_top.set_xlabel(r'Fermi wavelength $\lambda_F$ (m)')

    # Mark r_c and lambda_scr on top axis
    for x_rho, label, color in [(rho_core, r'$r_c$', 'red'),
                                   (rho_core/100, r'$\sqrt{2}r_c$', 'blue')]:
        ax1_top.axvline(x=x_rho, color=color, linestyle=':', alpha=0.4)

    # Dummy points for legend
    for t in colors:
        ax1.scatter([], [], color=colors[t], marker=markers[t], label=labels[t], edgecolors='k')
    ax1.legend(loc='upper left', frameon=False, fontsize=7)

    # --- Panel B: Physical vs TEP Radius ---
    ax2 = axes[1]
    ax2.set_title(r"$\bf{b)}$ Physical vs Scalar Radius", loc='left')

    for name, obj in objects.items():
        t = obj['type']
        ax2.scatter(obj['R'], obj['R_T'], color=colors[t], marker=markers[t], 
                    s=80, edgecolors='k', lw=0.5, zorder=5)
    
        if name in ['Earth', 'Sirius B', 'Typical NS']:
            ax2.annotate(name, (obj['R'], obj['R_T']), xytext=(5, -5), 
                         textcoords='offset points')

    # Unity Line
    r_line = np.logspace(0, 6, 10)
    ax2.plot(r_line, r_line, 'k--', alpha=0.5, label='Unity ($R_T=R_{phys}$)')

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xlabel(r'Physical Radius $R_{phys}$ (km)')
    ax2.set_ylabel(r'TEP Radius $R_T$ (km)')
    ax2.grid(True, which='major', alpha=0.3)

    # Annotations
    ax2.text(1e1, 1e5, "Screened Regime\n(Scalar Field > Physical)", ha='center', color=COLORS['primary'])

    output_path = os.path.join(output_dir, 'figure_4_screening_hierarchy.png')
    plt.savefig(output_path, transparent=True)
    print(f"Figure saved to {output_path}")

    # Save numerical outputs
    output_data = {
        "objects": len(objects),
        "rho_T_g_cm3": float(rho_T),
        "R_TEP_earth_km": float(R_TEP_earth / 1000),
        "screening_data": {
            name: {
                "M_kg": float(obj["M"]),
                "R_km": float(obj["R"]),
                "rho_g_cm3": float(obj["rho"]),
                "R_T_km": float(obj["R_T"]),
                "screening": float(obj["screening"]),
                "type": obj["type"],
            }
            for name, obj in objects.items()
        },
    }
    with open(os.path.join(outputs_dir, "step_3_screening_hierarchy.json"), "w") as f:
        json.dump(output_data, f, indent=2)
    try:
        print_status("Numerical outputs saved to results/outputs/step_3_screening_hierarchy.json", "SUCCESS")
    except Exception:
        pass
    return output_data

if __name__ == "__main__":
    run_screening_hierarchy()
