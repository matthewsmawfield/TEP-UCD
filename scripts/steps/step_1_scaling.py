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

from core.constants import M_EARTH, M_SUN, G_NEWTON, C_LIGHT, SCREENING_LENGTH_KM, RHO_C

FIG_PRESET = 'web_standard'


def set_pub_style():
    set_shared_style(scale=FIG_SCALE[FIG_PRESET])


def run_scaling_analysis():
    """Generate Figure 1: Universal mass-radius scaling law."""
    logger = TEPLogger("step_1_scaling", log_file_path=os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'step_1_scaling.log'))
    set_step_logger(logger)

    set_pub_style()

    print_status("Initializing scaling law analysis", "PROCESS")

    # Ensure output directories exist
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    outputs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    # --- Constants ---
    M_earth = M_EARTH
    M_sun = M_SUN
    G = G_NEWTON
    c = C_LIGHT
    rho_T = RHO_C  # g/cm³
    rho_T_kg_m3 = rho_T * 1000  # kg/m³

    # --- The TEP Parameter (GNSS Derived) ---
    # Compute R_T for Earth directly from rho_T for consistency with step_3 and step_6
    R_TEP_earth = ((3 * M_earth) / (4 * np.pi * rho_T_kg_m3)) ** (1/3)  # meters
    print_status(f"TEP screening length (Earth): R_T = {R_TEP_earth:.1f} m (from rho_T = {rho_T} g/cm³)", "INFO")

    # --- Mass Range ---
    masses_kg = np.logspace(np.log10(M_earth), np.log10(1e11 * M_sun), 500)
    masses_solar = masses_kg / M_sun
    print_status(f"Mass range: {masses_solar[0]:.2e} to {masses_solar[-1]:.2e} M_sun ({len(masses_kg)} points)", "INFO")

    # --- Theoretical Curves ---
    print_status("Computing soliton radius R ~ M^(1/3)", "PROCESS")
    radius_tep_m = R_TEP_earth * (masses_kg / M_earth)**(1/3)
    radius_tep_km = radius_tep_m / 1000

    print_status("Computing Schwarzschild radius R_S = 2GM/c^2", "PROCESS")
    radius_sch_m = 2 * G * masses_kg / (c**2)
    radius_sch_km = radius_sch_m / 1000

    # --- RBH-1 Point ---
    M_rbh_solar = 2.0e7
    R_rbh_km = (R_TEP_earth * ((M_rbh_solar * M_sun) / M_earth)**(1/3)) / 1000
    R_rbh_S_km = 2 * G * M_rbh_solar * M_sun / c**2 / 1000
    print_status(f"RBH-1: M = {M_rbh_solar:.1e} M_sun, R_T = {R_rbh_km:.2e} km, R_S = {R_rbh_S_km:.2e} km", "INFO")

    # --- Exact R_T = R_S crossover mass: M_x = sqrt(3 c^6 / (32 pi G^3 rho_T)) ---
    M_cross_kg = np.sqrt(3 * c**6 / (32 * np.pi * G**3 * rho_T_kg_m3))
    M_cross_solar = M_cross_kg / M_sun
    R_cross_km = 2 * G * M_cross_kg / c**2 / 1000
    print_status(f"Crossover: M_x = {M_cross_solar:.3e} M_sun, R_T = R_S = {R_cross_km:.3e} km", "INFO")

    # --- Earth Anchor ---
    M_earth_solar = M_earth / M_sun
    R_earth_km = R_TEP_earth / 1000
    print_status(f"Earth anchor: M = {M_earth_solar:.2e} M_sun, R_T = {R_earth_km:.1f} km", "INFO")

    # --- Plotting ---
    print_status("Generating scaling law figure", "PROCESS")
    fig, ax = plt.subplots(figsize=FIG_SIZE[FIG_PRESET])

    ax.loglog(masses_solar, radius_tep_km, color=COLORS['accent'], label=r'Soliton Scale ($R_T \propto M^{1/3}$)')
    ax.loglog(masses_solar, radius_sch_km, color='black', linestyle='--', label=r'Schwarzschild Radius ($R_{\rm S} \propto M$)')

    ax.scatter([M_cross_solar], [R_cross_km], facecolors='none', edgecolors='black', s=95, zorder=6, marker='o', linewidth=1.3, label=r'Exact Crossover ($M_\times = 3.04 \times 10^7\,M_\odot$)')
    ax.scatter([M_rbh_solar], [R_rbh_km], color=COLORS['highlight'], s=100, zorder=5, marker='D', edgecolors='white', linewidth=0.8, label=r'RBH-1 ($M \approx 2 \times 10^7\,M_\odot$)')
    ax.scatter([M_earth_solar], [R_earth_km], color=COLORS['primary'], s=80, zorder=5, marker='o', edgecolors='white', linewidth=0.8)

    ax.annotate(r'$\bf{RBH}$-$\bf{1}$' + '\n' + r'($M \approx 2 \times 10^7 M_{\odot}$)',
                xy=(M_rbh_solar, R_rbh_km), xytext=(M_rbh_solar/25, R_rbh_km*8),
                arrowprops=dict(arrowstyle='->', color=COLORS['highlight'], lw=1.2),
                color=COLORS['highlight'], fontsize=10, ha='center')

    ax.annotate('Earth Calibration\n(GNSS)',
                xy=(M_earth_solar, R_earth_km), xytext=(M_earth_solar*50, R_earth_km/10),
                arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=1.2),
                color=COLORS['primary'], fontsize=10)

    ax.text(1e0, 1.5e6, r"$R_T > R_{\rm S}$: Saturation-Scale Regime", rotation=13, color=COLORS['accent'], fontsize=9.5, alpha=0.85)
    ax.text(3e8, 3e5, r"$R_{\rm S} > R_T$:" + "\nSchwarzschild-Scale Regime", rotation=13, ha='center', color=COLORS['text'], fontsize=9.2, alpha=0.85)

    ax.set_xlabel(r'Mass ($M/M_{\odot}$)')
    ax.set_ylabel(r'Effective Radius $R$ (km)')
    ax.set_ylim(1e-6, 3e12)
    ax.set_title('Saturation Radius vs. Schwarzschild Radius Across Mass Scales', color=COLORS['primary'])
    ax.grid(True, which='major', linestyle='-', alpha=0.3)
    ax.grid(True, which='minor', linestyle=':', alpha=0.1)

    ax.legend(loc='upper left', frameon=False)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'figure_2_scaling.png'))
    print_status("Figure saved to results/figures/figure_2_scaling.png", "SUCCESS")

    # Save numerical outputs
    output_data = {
        "M_earth_kg": float(M_earth),
        "R_TEP_earth_m": float(R_TEP_earth),
        "M_rbh_solar": float(M_rbh_solar),
        "R_rbh_km": float(R_rbh_km),
        "R_S_rbh_km": float(R_rbh_S_km),
        "R_T_over_R_S_rbh": float(R_rbh_km / R_rbh_S_km),
        "M_crossover_solar": float(M_cross_solar),
        "R_crossover_km": float(R_cross_km),
        "mass_range_solar": [float(masses_solar[0]), float(masses_solar[-1])],
        "radius_tep_range_km": [float(radius_tep_km[0]), float(radius_tep_km[-1])]
    }
    with open(os.path.join(outputs_dir, 'step_1_scaling.json'), 'w') as f:
        json.dump(output_data, f, indent=2)
    print_status("Numerical outputs saved to results/outputs/step_1_scaling.json", "SUCCESS")

    return output_data


if __name__ == '__main__':
    run_scaling_analysis()
