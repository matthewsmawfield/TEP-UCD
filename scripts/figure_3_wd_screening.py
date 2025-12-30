import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os

# --- Publication Style Configuration ---
def set_pub_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'mathtext.fontset': 'stix',
        'font.size': 12,
        'axes.labelsize': 12,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 14,
        'figure.dpi': 300,
        'axes.linewidth': 1.0,
        'grid.linewidth': 0.5,
        'grid.linestyle': '--',
        'grid.alpha': 0.5,
        'lines.linewidth': 2.0,
        'text.usetex': False,
    })

set_pub_style()

# Ensure output directory exists
output_dir = '../site/figures'
os.makedirs(output_dir, exist_ok=True)

# --- Constants ---
M_earth = 5.972e24  # kg
M_sun = 1.989e30    # kg
R_sun = 6.96e8      # meters

# --- The TEP Parameter (Calibrated from GNSS) ---
R_TEP_earth = 4200 * 1000  # 4200 km in meters

# --- Mass Range: White Dwarf Domain (0.1 to 1.4 Solar Masses) ---
masses_solar = np.linspace(0.1, 1.44, 200)  # Up to Chandrasekhar limit
masses_kg = masses_solar * M_sun

# --- Line A: White Dwarf Physical Radius (Baryonic Reality) ---
# Standard mass-radius relation: R_WD ≈ 0.01 R_☉ (M/M_☉)^{-1/3}
R_WD_solar = 0.01 * masses_solar**(-1/3)  # in solar radii
R_WD_km = R_WD_solar * R_sun / 1000       # convert to km

# --- Line B: TEP Soliton Radius (Scalar Field Extent) ---
# R_sol = 4200 km * (M / M_⊕)^{1/3}
R_sol_m = R_TEP_earth * (masses_kg / M_earth)**(1/3)
R_sol_km = R_sol_m / 1000

# --- Key Reference Points ---
# Sirius B
sirius_b_mass = 1.018
sirius_b_radius = 5800  # km
sirius_b_soliton = (R_TEP_earth * ((sirius_b_mass * M_sun) / M_earth)**(1/3)) / 1000
screening_factor_sirius = sirius_b_soliton / sirius_b_radius

# Chandrasekhar Limit
chandra_mass = 1.44
chandra_radius = 0.01 * chandra_mass**(-1/3) * R_sun / 1000
chandra_soliton = (R_TEP_earth * ((chandra_mass * M_sun) / M_earth)**(1/3)) / 1000
screening_factor_chandra = chandra_soliton / chandra_radius

# --- Plotting ---
fig, ax = plt.subplots(figsize=(8, 6))

# Colors
c_phys = '#004488'  # Blue
c_sol = '#D55E00'   # Vermillion
c_fill = '#D55E00'

# Fill the screening zone
ax.fill_between(masses_solar, R_WD_km, R_sol_km, 
                alpha=0.1, color=c_fill,
                label='Vainshtein Screening Zone')

# Line A: Physical Radius
ax.semilogy(masses_solar, R_WD_km, 
            label=r'Physical Radius ($R_{WD} \propto M^{-1/3}$)', 
            color=c_phys, linewidth=2.5)

# Line B: Soliton Radius
ax.semilogy(masses_solar, R_sol_km, 
            label=r'Soliton Radius ($R_{sol} \propto M^{1/3}$)', 
            color=c_sol, linewidth=2.5, linestyle='--')

# Mark Sirius B
ax.scatter([sirius_b_mass], [sirius_b_radius], color=c_phys, 
           s=100, zorder=10, marker='o', edgecolors='white', linewidth=1)
ax.scatter([sirius_b_mass], [sirius_b_soliton], color=c_sol, 
           s=100, zorder=10, marker='s', edgecolors='white', linewidth=1)

# Connection line for Sirius B
ax.vlines(sirius_b_mass, sirius_b_radius, sirius_b_soliton, 
          colors='black', linestyles=':', linewidth=1.5, zorder=5)

ax.text(sirius_b_mass + 0.02, (sirius_b_radius * sirius_b_soliton)**0.5, 
        f"Sirius B\nScreening: {screening_factor_sirius:.0f}×", 
        fontsize=10, color='black', va='center')

# Chandrasekhar Limit Line
ax.axvline(x=1.44, color='gray', linestyle=':', linewidth=1.5)
ax.text(1.43, 2e5, "Chandrasekhar Limit", fontsize=9, color='gray', 
        ha='right', rotation=90, va='center')

# Formatting
ax.set_title("White Dwarf Screening Test")
ax.set_xlabel(r"White Dwarf Mass ($M/M_\odot$)")
ax.set_ylabel("Radius (km)")
ax.set_xlim(0.1, 1.5)
ax.set_ylim(1e3, 1e6)
ax.grid(True, which="major", ls="-", alpha=0.3)
ax.grid(True, which="minor", ls=":", alpha=0.1)
ax.legend(fontsize=10, loc='upper right', frameon=True, fancybox=False, edgecolor='k')

# Annotations
ax.text(0.3, 3000, 'Dense Matter Screens Field\n(GR Recovered)', 
        fontsize=10, ha='center', color=c_phys)
ax.text(0.6, 2e5, 'Scalar Field Extends Beyond Surface', 
        fontsize=10, ha='center', color=c_sol)

plt.tight_layout()
output_path = os.path.join(output_dir, 'figure_3_wd_screening.png')
plt.savefig(output_path, bbox_inches='tight')
print(f"Figure saved to {output_path}")
