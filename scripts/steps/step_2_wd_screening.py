import os
import sys
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# --- Publication Style Configuration ---
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.style import COLORS, FIG_SCALE, FIG_SIZE
from utils.style import set_pub_style as set_shared_style

try:
    from utils.logger import TEPLogger, set_step_logger, print_status
except ImportError:
    pass

from core.constants import M_EARTH, M_SUN, R_SUN, SCREENING_LENGTH_KM, RHO_C

FIG_PRESET = "web_tall"


def set_pub_style():
    set_shared_style(scale=FIG_SCALE[FIG_PRESET])


def run_wd_screening():
    """Generate Figure 3: White dwarf screening test."""
    logger = TEPLogger("step_2_wd_screening", log_file_path=os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'step_2_wd_screening.log'))
    set_step_logger(logger)

    set_pub_style()
    print_status("Initializing white dwarf screening analysis", "PROCESS")

    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results", "figures")
    os.makedirs(output_dir, exist_ok=True)
    outputs_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results", "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    # --- Constants ---
    M_earth = M_EARTH
    M_sun = M_SUN
    R_sun = R_SUN
    rho_T = RHO_C  # g/cm³
    rho_T_kg_m3 = rho_T * 1000  # kg/m³

    # --- The TEP Parameter (Calibrated from GNSS) ---
    # Compute R_T for Earth directly from rho_T for consistency with step_3 and step_6
    R_TEP_earth = ((3 * M_earth) / (4 * np.pi * rho_T_kg_m3)) ** (1/3)  # meters
    print_status(f"TEP screening length: {R_TEP_earth:.1f} m (from rho_T = {rho_T} g/cm³)", "INFO")

    # --- Mass Range: White Dwarf Domain (0.1 to 1.4 Solar Masses) ---
    masses_solar = np.linspace(0.1, 1.44, 200)  # Up to Chandrasekhar limit
    masses_kg = masses_solar * M_sun
    print_status(f"WD mass range: {masses_solar[0]:.2f} to {masses_solar[-1]:.2f} M_sun ({len(masses_solar)} points)", "INFO")

    # --- Line A: White Dwarf Physical Radius (Baryonic Reality) ---
    print_status("Computing WD physical radius R_WD ~ M^(-1/3)", "PROCESS")
    R_WD_solar = 0.01 * masses_solar ** (-1 / 3)  # in solar radii
    R_WD_km = R_WD_solar * R_sun / 1000  # convert to km

    # --- Line B: TEP Soliton Radius (Scalar Field Extent) ---
    print_status("Computing TEP soliton radius R_T ~ M^(1/3)", "PROCESS")
    R_T_m = R_TEP_earth * (masses_kg / M_earth) ** (1 / 3)
    R_T_km = R_T_m / 1000

    # --- Key Reference Points ---
    sirius_b_mass = 1.018
    sirius_b_radius = 5800  # km
    sirius_b_R_T = (R_TEP_earth * ((sirius_b_mass * M_sun) / M_earth) ** (1 / 3)) / 1000
    screening_factor_sirius = sirius_b_R_T / sirius_b_radius
    print_status(f"Sirius B: R_phys = {sirius_b_radius:.0f} km, R_T = {sirius_b_R_T:.2e} km, S = {screening_factor_sirius:.0f}x", "INFO")

    chandra_mass = 1.44
    chandra_radius = 0.01 * chandra_mass ** (-1 / 3) * R_sun / 1000
    chandra_R_T = (R_TEP_earth * ((chandra_mass * M_sun) / M_earth) ** (1 / 3)) / 1000
    screening_factor_chandra = chandra_R_T / chandra_radius
    print_status(f"Chandrasekhar limit: R_phys = {chandra_radius:.0f} km, R_T = {chandra_R_T:.2e} km, S = {screening_factor_chandra:.0f}x", "INFO")

    # --- Plotting ---
    print_status("Generating WD screening figure", "PROCESS")
    fig, ax = plt.subplots(figsize=FIG_SIZE[FIG_PRESET])

    c_phys = COLORS["secondary"]
    c_sol = COLORS["accent"]
    c_fill = COLORS["accent"]

    ax.fill_between(
        masses_solar,
        R_WD_km,
        R_T_km,
        alpha=0.06,
        color=c_fill,
        label="Screened Regime (Shear Suppressed)",
    )

    ax.semilogy(
        masses_solar,
        R_WD_km,
        label=r"Physical Radius ($R_{WD} \propto M^{-1/3}$)",
        color=c_phys,
        linewidth=2.5,
    )

    ax.semilogy(
        masses_solar,
        R_T_km,
        label=r"$R_T$ Radius ($R_T \propto M^{1/3}$)",
        color=c_sol,
        linewidth=2.5,
        linestyle="--",
    )

    ax.scatter(
        [sirius_b_mass],
        [sirius_b_radius],
        color=c_phys,
        s=100,
        zorder=10,
        marker="o",
        edgecolors="white",
        linewidth=1,
    )
    ax.scatter(
        [sirius_b_mass],
        [sirius_b_R_T],
        color=c_sol,
        s=100,
        zorder=10,
        marker="s",
        edgecolors="white",
        linewidth=1,
    )

    ax.vlines(
        sirius_b_mass,
        sirius_b_radius,
        sirius_b_R_T,
        colors="black",
        linestyles=":",
        linewidth=1.5,
        zorder=5,
    )

    ax.text(
        sirius_b_mass + 0.02,
        (sirius_b_radius * sirius_b_R_T) ** 0.5,
        f"Sirius B\nScreening: {screening_factor_sirius:.0f}×",
        fontsize=10,
        color="black",
        va="center",
    )

    ax.axvline(x=1.44, color="gray", linestyle=":", linewidth=1.5)
    ax.text(
        1.43,
        2e5,
        "Chandrasekhar Limit",
        fontsize=9,
        color="gray",
        ha="right",
        rotation=90,
        va="center",
    )

    ax.set_title("White Dwarf Screening Test")
    ax.set_xlabel(r"White Dwarf Mass ($M/M_\odot$)")
    ax.set_ylabel("Radius (km)")
    ax.set_xlim(0.1, 1.5)
    ax.set_ylim(1e3, 1e6)
    ax.grid(True, which="major", ls="-", alpha=0.3)
    ax.grid(True, which="minor", ls=":", alpha=0.1)
    ax.legend(loc="upper right", frameon=False)

    ax.text(
        0.3,
        3000,
        "Dense Matter Flattens Topology\n(GR Recovered)",
        ha="center",
        color=COLORS["text"],
    )
    ax.text(
        0.6, 2e5, "Saturation scale extends beyond baryonic surface", ha="center", color=COLORS["text"]
    )

    plt.tight_layout()
    output_path = os.path.join(output_dir, "figure_3_wd_screening.png")
    plt.savefig(output_path, transparent=True)
    print_status("Figure saved to results/figures/figure_3_wd_screening.png", "SUCCESS")

    # Save numerical outputs
    output_data = {
        "sirius_b_mass": float(sirius_b_mass),
        "sirius_b_radius_km": float(sirius_b_radius),
        "sirius_b_R_T_km": float(sirius_b_R_T),
        "screening_factor_sirius": float(screening_factor_sirius),
        "chandra_mass": float(chandra_mass),
        "chandra_radius_km": float(chandra_radius),
        "chandra_R_T_km": float(chandra_R_T),
        "screening_factor_chandra": float(screening_factor_chandra)
    }
    with open(os.path.join(outputs_dir, 'step_2_wd_screening.json'), 'w') as f:
        json.dump(output_data, f, indent=2)
    try:
        print_status("Numerical outputs saved to results/outputs/step_2_wd_screening.json", "SUCCESS")
    except Exception:
        pass

    return output_data


if __name__ == '__main__':
    run_wd_screening()
