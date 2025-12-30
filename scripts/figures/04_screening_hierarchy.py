import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import sys

# --- Publication Style Configuration ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import set_pub_style as set_shared_style, COLORS, FIG_SIZE, FIG_SCALE

FIG_PRESET = 'web_two_panel'


def set_pub_style():
    set_shared_style(scale=FIG_SCALE[FIG_PRESET])


set_pub_style()

output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'site', 'figures')
os.makedirs(output_dir, exist_ok=True)

# --- Constants ---
M_earth = 5.972e24   # kg
M_sun = 1.989e30     # kg
R_sun = 6.96e8       # meters
R_earth = 6.371e6    # meters
R_TEP_earth = 4200e3  # meters
rho_c = 20  # g/cm³ (saturation threshold)

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
    R_sol = R_TEP_earth * (obj['M'] / M_earth)**(1/3) / 1000  # km
    obj['R_sol'] = R_sol
    obj['screening'] = R_sol / obj['R']

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

# --- Panel A: Screening Factor vs Density ---
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
ax1.axvline(x=rho_c, color='k', linestyle='--', alpha=0.5)
ax1.text(rho_c*1.5, 0.6, r'$\rho_c \approx 20$ g/cm³', rotation=90, va='bottom')

# Unity Line
ax1.axhline(y=1, color='gray', linestyle=':', alpha=0.5)
ax1.text(1e-1, 1.1, 'No Screening', color='gray')

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel(r'Mean Density $\rho$ (g/cm³)')
ax1.set_ylabel(r'Screening Factor $S = R_{sol}/R_{phys}$')
ax1.set_xlim(1e-1, 1e16)
ax1.set_ylim(0.5, 1e8)
ax1.grid(True, which='major', alpha=0.3)

# Dummy points for legend
for t in colors:
    ax1.scatter([], [], color=colors[t], marker=markers[t], label=labels[t], edgecolors='k')
ax1.legend(loc='upper left', frameon=False)

# --- Panel B: Physical vs Soliton Radius ---
ax2 = axes[1]
ax2.set_title(r"$\bf{b)}$ Physical vs Scalar Radius", loc='left')

for name, obj in objects.items():
    t = obj['type']
    ax2.scatter(obj['R'], obj['R_sol'], color=colors[t], marker=markers[t], 
                s=80, edgecolors='k', lw=0.5, zorder=5)
    
    if name in ['Earth', 'Sirius B', 'Typical NS']:
        ax2.annotate(name, (obj['R'], obj['R_sol']), xytext=(5, -5), 
                     textcoords='offset points')

# Unity Line
r_line = np.logspace(0, 6, 10)
ax2.plot(r_line, r_line, 'k--', alpha=0.5, label='Unity ($R_{sol}=R_{phys}$)')

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel(r'Physical Radius $R_{phys}$ (km)')
ax2.set_ylabel(r'Soliton Radius $R_{sol}$ (km)')
ax2.grid(True, which='major', alpha=0.3)

# Annotations
ax2.text(1e1, 1e5, "Screened Regime\n(Scalar Field > Physical)", ha='center', color=COLORS['primary'])

output_path = os.path.join(output_dir, 'figure_4_screening_hierarchy.png')
plt.savefig(output_path, transparent=True)
print(f"Figure saved to {output_path}")
