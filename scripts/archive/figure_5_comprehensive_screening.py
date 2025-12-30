import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
from scipy import stats

# --- Publication Style Configuration ---
def set_pub_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'mathtext.fontset': 'stix',
        'font.size': 10,
        'axes.labelsize': 10,
        'axes.titlesize': 11,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.titlesize': 12,
        'figure.dpi': 300,
        'axes.linewidth': 0.8,
        'grid.linewidth': 0.5,
        'grid.linestyle': '--',
        'grid.alpha': 0.5,
        'lines.linewidth': 1.5,
        'text.usetex': False,
    })

set_pub_style()

output_dir = '../site/figures'
os.makedirs(output_dir, exist_ok=True)

# --- Constants ---
M_earth = 5.972e24
M_sun = 1.989e30
R_sun = 6.96e8
R_earth = 6.371e6
G = 6.674e-11
c = 2.998e8
R_TEP_earth = 4200e3
rho_c = 20

# --- Data Objects ---
objects = {
    'Earth': {'M': 1 * M_earth, 'R': 6371, 'type': 'planet', 'rho': 5.5},
    'Mars': {'M': 0.107 * M_earth, 'R': 3390, 'type': 'planet', 'rho': 3.93},
    'Jupiter': {'M': 317.8 * M_earth, 'R': 69911, 'type': 'planet', 'rho': 1.33},
    'Sun': {'M': 1.0 * M_sun, 'R': 696340, 'type': 'ms', 'rho': 1.41},
    'Proxima': {'M': 0.122 * M_sun, 'R': 107236, 'type': 'ms', 'rho': 56.8},
    'Sirius B': {'M': 1.018 * M_sun, 'R': 5800, 'type': 'wd', 'rho': 2.38e6},
    'Procyon B': {'M': 0.602 * M_sun, 'R': 8600, 'type': 'wd', 'rho': 5.5e5},
    'Typical NS': {'M': 1.4 * M_sun, 'R': 12, 'type': 'ns', 'rho': 4e14},
    'Hulse-Taylor': {'M': 1.44 * M_sun, 'R': 10, 'type': 'pulsar', 'rho': 7e14},
}

# Derived Metrics
for name, obj in objects.items():
    R_sol = R_TEP_earth * (obj['M'] / M_earth)**(1/3) / 1000
    obj['R_sol'] = R_sol
    obj['screening'] = R_sol / obj['R']
    obj['M_solar'] = obj['M'] / M_sun

# --- Plotting ---
fig = plt.figure(figsize=(10, 8), constrained_layout=True)
gs = fig.add_gridspec(2, 2)

# Colors
colors = {'planet': '#009E73', 'ms': '#E69F00', 'wd': '#56B4E9', 'ns': '#D55E00', 'pulsar': 'k'}
markers = {'planet': 'o', 'ms': 's', 'wd': '^', 'ns': 'D', 'pulsar': '*'}

# --- Panel A: Mass-Density Space ---
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_title(r"$\bf{a)}$ Mass-Density Phase Space", loc='left')

for name, obj in objects.items():
    t = obj['type']
    ax1.scatter(obj['M_solar'], obj['rho'], color=colors[t], marker=markers[t], s=60, edgecolors='k', lw=0.5, zorder=5)

ax1.axhline(rho_c, color='k', ls='--', alpha=0.5)
ax1.text(1e-5, rho_c*2, r'$\rho_c \approx 20$ g/cm³', fontsize=9)

ax1.axhspan(rho_c, 1e16, color='gray', alpha=0.1)
ax1.text(1e-4, 1e10, 'Screened (GR)', color='gray', fontweight='bold', ha='center')
ax1.text(1e-4, 1e-1, 'Unscreened (Scalar)', color='#009E73', fontweight='bold', ha='center')

ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlim(1e-6, 1e2)
ax1.set_ylim(1e-2, 1e16)
ax1.set_xlabel(r'Mass ($M_{\odot}$)')
ax1.set_ylabel(r'Mean Density (g/cm³)')
ax1.grid(True, which='major', alpha=0.3)

# --- Panel B: Mass-Radius Diagram with TEP Overlay ---
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_title(r"$\bf{b)}$ Mass-Radius Relations", loc='left')

# Curves
m_range = np.logspace(-6, 2, 100)
# TEP
r_tep = (R_TEP_earth/1000) * (m_range * M_sun / M_earth)**(1/3)
ax2.loglog(m_range, r_tep, '--', color='#D55E00', label=r'Soliton ($M^{1/3}$)')

# Schwarzschild
r_sch = 2 * G * (m_range * M_sun) / c**2 / 1000
ax2.loglog(m_range, r_sch, ':', color='k', label='Schwarzschild')

# Objects
for name, obj in objects.items():
    t = obj['type']
    ax2.scatter(obj['M_solar'], obj['R'], color=colors[t], marker=markers[t], s=60, edgecolors='k', lw=0.5)

ax2.set_xlabel(r'Mass ($M_{\odot}$)')
ax2.set_ylabel(r'Radius (km)')
ax2.legend(fontsize=8)
ax2.grid(True, which='major', alpha=0.3)

# --- Panel C: Vainshtein Screening Law ---
ax3 = fig.add_subplot(gs[1, 0])
ax3.set_title(r"$\bf{c)}$ Vainshtein Screening Law", loc='left')

# Fit
rho_vals = [obj['rho'] for obj in objects.values() if obj['rho'] > rho_c]
scr_vals = [obj['screening'] for obj in objects.values() if obj['rho'] > rho_c]
slope, intercept, _, _, _ = stats.linregress(np.log10(rho_vals), np.log10(scr_vals))

rho_line = np.logspace(1, 16, 10)
scr_line = 10**intercept * rho_line**slope
ax3.loglog(rho_line, scr_line, 'k--', alpha=0.6, label=r'Fit: $\propto \rho^{%.2f}$' % slope)

for name, obj in objects.items():
    t = obj['type']
    ax3.scatter(obj['rho'], obj['screening'], color=colors[t], marker=markers[t], s=60, edgecolors='k', lw=0.5)

ax3.axvline(rho_c, color='k', ls=':', alpha=0.5)
ax3.axhline(1, color='gray', ls='-', lw=0.5)

ax3.set_xlabel(r'Mean Density (g/cm³)')
ax3.set_ylabel(r'Screening Factor')
ax3.legend(fontsize=8)
ax3.grid(True, which='major', alpha=0.3)

# --- Panel D: GR Test Validation ---
ax4 = fig.add_subplot(gs[1, 1])
ax4.set_title(r"$\bf{d)}$ GR Test Precision vs Screening", loc='left')

# GR Tests
tests = [
    ('Solar System', 1e-5, objects['Sun']['screening']),
    ('Binary Pulsar', 1e-3, objects['Hulse-Taylor']['screening']),
    ('Double Pulsar', 5e-4, objects['Hulse-Taylor']['screening']*0.8), # Approx
    ('LIGO', 1e-2, 1e5) # Approx for BH merger
]

for name, prec, scr in tests:
    ax4.scatter(scr, prec, marker='*', s=150, color='gold', edgecolors='k')
    ax4.text(scr, prec*1.5, name, fontsize=8, ha='center')

# Theoretical deviation limit (cartoon)
s_range = np.logspace(0, 6, 100)
dev_limit = 0.1 / s_range
ax4.loglog(s_range, dev_limit, color='gray', ls='--', label='Max Scalar Deviation')

ax4.set_xlabel('Screening Factor')
ax4.set_ylabel('GR Test Precision')
ax4.set_ylim(1e-6, 1)
ax4.grid(True, which='major', alpha=0.3)

plt.savefig(os.path.join(output_dir, 'figure_5_comprehensive_screening.png'), bbox_inches='tight')
print(f"Figure saved to {os.path.join(output_dir, 'figure_5_comprehensive_screening.png')}")
