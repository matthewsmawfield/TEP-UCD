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
G = 6.674e-11       # Gravitational Constant
c = 2.998e8         # Speed of Light

# --- The TEP Parameter (GNSS Derived) ---
R_TEP_earth = 4200 * 1000  # meters

# --- Mass Range ---
masses_kg = np.logspace(np.log10(M_earth), np.log10(1e11 * M_sun), 500)
masses_solar = masses_kg / M_sun

# --- Theoretical Curves ---
# 1. Soliton Radius: R ~ M^(1/3)
radius_tep_m = R_TEP_earth * (masses_kg / M_earth)**(1/3)
radius_tep_km = radius_tep_m / 1000

# 2. Schwarzschild Diameter: D = 4GM/c^2
# Note: Using Diameter as effective interaction scale for BH
diameter_sch_m = 4 * G * masses_kg / (c**2)
diameter_sch_km = diameter_sch_m / 1000

# --- RBH-1 Point ---
M_rbh_solar = 1.09e7 
# Recalculate exact point on curve for consistency
R_rbh_km = (R_TEP_earth * ((M_rbh_solar * M_sun) / M_earth)**(1/3)) / 1000

# --- Earth Anchor ---
M_earth_solar = M_earth / M_sun
R_earth_km = 4200

# --- Plotting ---
fig, ax = plt.subplots(figsize=(7, 5))

# Plot Lines
ax.loglog(masses_solar, radius_tep_km, color='#004488', label=r'Soliton Scale ($R \propto M^{1/3}$)')
ax.loglog(masses_solar, diameter_sch_km, color='black', linestyle='--', label=r'Event Horizon ($D \propto M$)')

# Plot Points
ax.scatter([M_rbh_solar], [R_rbh_km], color='#D55E00', s=100, zorder=5, marker='D', edgecolors='white', linewidth=0.8)
ax.scatter([M_earth_solar], [R_earth_km], color='#009E73', s=80, zorder=5, marker='o', edgecolors='white', linewidth=0.8)

# Annotations
# RBH-1
ax.annotate(r'$\bf{RBH}$-$\bf{1}$' + '\n' + r'($M \approx 10^7 M_{\odot}$)', 
            xy=(M_rbh_solar, R_rbh_km), xytext=(M_rbh_solar/20, R_rbh_km*5),
            arrowprops=dict(arrowstyle='->', color='#D55E00', lw=1.2),
            color='#D55E00', fontsize=10, ha='center')

# Earth
ax.annotate('Earth Calibration\n(GNSS)', 
            xy=(M_earth_solar, R_earth_km), xytext=(M_earth_solar*50, R_earth_km/10),
            arrowprops=dict(arrowstyle='->', color='#009E73', lw=1.2),
            color='#009E73', fontsize=10)

# Regime labels
ax.text(1e2, 1e7, "Scalar Field Dominated", rotation=12, color='#004488', fontsize=10, alpha=0.8)
ax.text(1e9, 5e7, "Gravity Dominated", rotation=40, color='black', fontsize=10, alpha=0.8)

# Formatting
ax.set_xlabel(r'Mass ($M/M_{\odot}$)')
ax.set_ylabel(r'Effective Radius $R$ (km)')
ax.set_title('Universal Mass-Radius Scaling Law')
ax.grid(True, which='major', linestyle='-', alpha=0.3)
ax.grid(True, which='minor', linestyle=':', alpha=0.1)

ax.legend(frameon=True, fancybox=False, edgecolor='k', fontsize=9, loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'figure_2_scaling.png'), bbox_inches='tight')
print(f"Figure saved to {os.path.join(output_dir, 'figure_2_scaling.png')}")
