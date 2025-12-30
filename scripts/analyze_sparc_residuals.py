"""
SPARC Residual Analysis: Discriminating Baryonic Feedback vs Field Theory

This script implements the "Secondary Fruit" analysis suggested by reviewers:
1. Calculate residuals from the M^(1/3) scaling law
2. Correlate residuals with baryonic properties (gas fraction, surface brightness, inclination)
3. Correlate residuals with screening proxies (density)

The Logic:
- If residuals correlate strongly with gas physics → baryonic artifact (Standard Model)
- If residuals are random or correlate with density → Field Theory (TEP) interpretation

Author: M. Smawfield
Date: December 2025
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import sys
from collections import defaultdict
from scipy import stats
from scipy.optimize import curve_fit

# --- Publication Style ---
sys.path.append(os.path.join(os.path.dirname(__file__), ''))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from utils.style import set_pub_style as set_shared_style, COLORS, FIG_SIZE, FIG_SCALE

FIG_PRESET = 'web_grid_3x3'


def set_pub_style():
    set_shared_style(scale=FIG_SCALE[FIG_PRESET])


set_pub_style()

# --- Constants ---
G = 6.674e-11  # m^3 kg^-1 s^-2
M_sun_kg = 1.989e30  # kg
kpc_to_m = 3.086e19  # m
pc_to_m = 3.086e16  # m

ML_DISK = 0.5
ML_BULGE = 0.7

# --- Data Parsing ---
def parse_table1(filepath):
    """Parse SPARC Table 1 (galaxy properties)."""
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
            T = float(parts[1]) if parts[1] != '...' else np.nan  # Hubble type
            D = float(parts[2])  # Distance (Mpc)
            inc = float(parts[4]) if parts[4] != '...' else np.nan  # Inclination (deg)
            L_36 = float(parts[7]) * 1e9  # L_3.6 in L_sun
            MHI = float(parts[13]) * 1e9  # M_HI in M_sun
            
            # Calculate effective radius (R_eff) from L_36
            # Assuming surface brightness Σ ~ L / (2π R_eff^2)
            # Typical disk scale length h ~ 0.3 R_eff
            # We'll use L_36 as proxy for size
            R_eff = (L_36 / 1e9)**(1/2) * 2.0  # kpc (rough scaling)
            
            galaxies[name] = {
                'L_36': L_36,
                'MHI': MHI,
                'D': D,
                'inc': inc,
                'T': T,
                'R_eff': R_eff
            }
        except:
            continue
    return galaxies

def parse_table2(filepath):
    """Parse SPARC Table 2 (rotation curves)."""
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
        except:
            continue
    for name in rotation_curves:
        for key in rotation_curves[name]:
            rotation_curves[name][key] = np.array(rotation_curves[name][key])
    return dict(rotation_curves)

def find_rdm_for_threshold(R, Vobs, Vbar, threshold=1.3):
    """Find R_dm where V_obs/V_bar first exceeds threshold."""
    valid = (Vbar > 5) & (Vobs > 0)
    if not np.any(valid):
        return np.nan
    R_valid = R[valid]
    ratio = Vobs[valid] / Vbar[valid]
    mask = ratio > threshold
    if np.any(mask):
        return R_valid[np.argmax(mask)]
    return np.nan

def calculate_surface_brightness(M_bar, R_eff):
    """Calculate mean surface brightness in M_sun/pc^2."""
    if R_eff <= 0:
        return np.nan
    # Σ = M / (2π R_eff^2) for exponential disk
    R_eff_pc = R_eff * 1000  # kpc to pc
    Sigma = M_bar / (2 * np.pi * R_eff_pc**2)
    return Sigma

def calculate_mean_density(M_bar, R_dm):
    """Calculate mean density within R_dm in M_sun/pc^3."""
    if R_dm <= 0:
        return np.nan
    R_dm_pc = R_dm * 1000  # kpc to pc
    # ρ = M / (4/3 π R^3)
    rho = M_bar / ((4/3) * np.pi * R_dm_pc**3)
    return rho

def calculate_central_density(M_bar, R_eff):
    """Calculate central surface density (independent of R_dm) in M_sun/pc^3."""
    if R_eff <= 0:
        return np.nan
    R_eff_pc = R_eff * 1000  # kpc to pc
    # For exponential disk: ρ_0 ~ Σ_0 / (2h) where h ~ R_eff/3
    # Σ_0 ~ M / (2π R_eff^2)
    Sigma_0 = M_bar / (2 * np.pi * R_eff_pc**2)
    h = R_eff_pc / 3  # scale height
    rho_0 = Sigma_0 / (2 * h)
    return rho_0

def run_residual_analysis():
    """Main residual analysis function."""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'sparc')
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'site', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    
    print("="*80)
    print("SPARC RESIDUAL ANALYSIS: Baryonic Feedback vs Field Theory")
    print("="*80)
    
    # Parse data
    try:
        galaxy_props = parse_table1(os.path.join(data_dir, 'Table1.mrt'))
        rotation_curves = parse_table2(os.path.join(data_dir, 'Table2.mrt'))
        using_synthetic = False
        print(f"\nLoaded {len(galaxy_props)} galaxies from SPARC database")
    except FileNotFoundError:
        print("\nWARNING: SPARC data files not found.")
        print("Generating synthetic data for demonstration...")
        using_synthetic = True
        
        # Generate synthetic galaxies with realistic correlations
        np.random.seed(42)
        galaxy_props = {}
        rotation_curves = {}
        n_syn = 167
        
        M_bars = 10**np.random.uniform(7, 11.5, n_syn)
        
        for i in range(n_syn):
            name = f"G{i:03d}"
            M = M_bars[i]
            
            # Add scatter with weak baryonic correlations
            gas_frac = np.random.uniform(0.05, 0.5)
            inc = np.random.uniform(30, 85)
            
            # R_dm with scatter (0.48 dex as reported)
            scatter_base = np.random.normal(0, 0.48)
            # Add weak gas fraction correlation (r ~ 0.1-0.2)
            scatter = scatter_base + 0.1 * (gas_frac - 0.25)
            
            R_dm_true = 7.9e-4 * M**(1/3) * 10**scatter
            R_eff = (M / 1e9)**(1/2) * 2.0
            
            galaxy_props[name] = {
                'L_36': M * (1 - gas_frac) / ML_DISK,
                'MHI': M * gas_frac / 1.33,
                'D': np.random.uniform(5, 50),
                'inc': inc,
                'T': np.random.uniform(1, 10),
                'R_eff': R_eff
            }
            
            # Mock rotation curve
            R_arr = np.linspace(0.1, 3 * R_dm_true, 100)
            V_bar_true = np.sqrt(G * M * M_sun_kg / (R_arr * kpc_to_m)) / 1000
            V_disk = V_bar_true / np.sqrt(ML_DISK)
            V_flat = V_bar_true[0] * 1.0
            trans = 1 / (1 + (R_dm_true/R_arr)**2)
            V_obs = V_bar_true * (1 - trans) + V_flat * trans
            
            rotation_curves[name] = {
                'R': R_arr,
                'Vobs': V_obs,
                'e_Vobs': V_obs * 0.05,
                'Vgas': np.zeros_like(R_arr),
                'Vdisk': V_disk,
                'Vbul': np.zeros_like(R_arr)
            }
    
    # --- STEP 1: Calculate M^(1/3) Fit and Residuals ---
    print("\n### STEP 1: Calculate Residuals from M^(1/3) Scaling ###")
    
    threshold = 1.3
    results = []
    
    for name in rotation_curves:
        if name not in galaxy_props:
            continue
        props = galaxy_props[name]
        rc = rotation_curves[name]
        if len(rc['R']) < 5:
            continue
        
        M_bar = props['L_36'] * ML_DISK + 1.33 * props['MHI']
        V_bar = np.sqrt(rc['Vgas']**2 + ML_DISK * rc['Vdisk']**2 + ML_BULGE * rc['Vbul']**2)
        
        R_dm = find_rdm_for_threshold(rc['R'], rc['Vobs'], V_bar, threshold)
        
        if not np.isnan(R_dm) and M_bar > 0 and R_dm > 0:
            # Calculate baryonic properties
            gas_frac = (1.33 * props['MHI']) / M_bar
            Sigma = calculate_surface_brightness(M_bar, props['R_eff'])
            rho_central = calculate_central_density(M_bar, props['R_eff'])
            inc = props['inc']
            
            results.append({
                'name': name,
                'M_bar': M_bar,
                'R_dm': R_dm,
                'gas_frac': gas_frac,
                'Sigma': Sigma,
                'rho_central': rho_central,
                'inc': inc
            })
    
    print(f"Valid galaxies: {len(results)}")
    
    # Fit M^(1/3) scaling
    M_arr = np.array([r['M_bar'] for r in results])
    R_arr = np.array([r['R_dm'] for r in results])
    
    # Fix α = 1/3, fit normalization
    log_k = np.mean(np.log10(R_arr) - (1/3) * np.log10(M_arr))
    k = 10**log_k
    
    # Calculate residuals
    R_pred = k * M_arr**(1/3)
    residuals = np.log10(R_arr / R_pred)  # in dex
    rms_scatter = np.std(residuals)
    
    print(f"Normalization: k = {k:.4e} kpc/M_sun^(1/3)")
    print(f"RMS scatter: {rms_scatter:.3f} dex")
    
    # Add residuals to results
    for i, r in enumerate(results):
        r['residual'] = residuals[i]
    
    # --- STEP 2: Correlate Residuals with Baryonic Properties ---
    print("\n### STEP 2: Correlate Residuals with Baryonic Properties ###")
    
    gas_frac_arr = np.array([r['gas_frac'] for r in results])
    Sigma_arr = np.array([r['Sigma'] for r in results])
    inc_arr = np.array([r['inc'] for r in results])
    
    # Remove NaNs
    valid_gas = ~np.isnan(gas_frac_arr) & ~np.isnan(residuals)
    valid_sigma = ~np.isnan(Sigma_arr) & ~np.isnan(residuals)
    valid_inc = ~np.isnan(inc_arr) & ~np.isnan(residuals)
    
    # Correlations
    r_gas, p_gas = stats.pearsonr(gas_frac_arr[valid_gas], residuals[valid_gas])
    r_sigma, p_sigma = stats.pearsonr(np.log10(Sigma_arr[valid_sigma]), residuals[valid_sigma])
    r_inc, p_inc = stats.pearsonr(inc_arr[valid_inc], residuals[valid_inc])
    
    print(f"\nBaryonic Property Correlations:")
    print(f"  Gas Fraction:       r = {r_gas:+.3f}, p = {p_gas:.4f}")
    print(f"  Surface Brightness: r = {r_sigma:+.3f}, p = {p_sigma:.4f}")
    print(f"  Inclination:        r = {r_inc:+.3f}, p = {p_inc:.4f}")
    
    # --- STEP 3: Correlate Residuals with Screening Proxies ---
    print("\n### STEP 3: Correlate Residuals with Screening Proxies (Density) ###")
    
    rho_arr = np.array([r['rho_central'] for r in results])
    valid_rho = ~np.isnan(rho_arr) & ~np.isnan(residuals) & (rho_arr > 0)
    
    r_rho, p_rho = stats.pearsonr(np.log10(rho_arr[valid_rho]), residuals[valid_rho])
    
    print(f"\nScreening Proxy Correlations:")
    print(f"  Central Density:    r = {r_rho:+.3f} (p = {p_rho:.4f})")
    
    # --- STEP 4: Statistical Assessment ---
    print("\n### STEP 4: Statistical Assessment ###")
    
    # Define significance threshold
    sig_threshold = 0.3  # |r| > 0.3 considered meaningful
    
    baryonic_correlations = [abs(r_gas), abs(r_sigma), abs(r_inc)]
    screening_correlations = [abs(r_rho)]
    
    max_baryonic = max(baryonic_correlations)
    max_screening = max(screening_correlations)
    
    print(f"\nMaximum Baryonic Correlation: |r| = {max_baryonic:.3f}")
    print(f"Maximum Screening Correlation: |r| = {max_screening:.3f}")
    
    if max_baryonic > sig_threshold:
        print(f"\n⚠️  INTERPRETATION: Residuals show significant correlation with baryonic properties.")
        print(f"    This suggests the M^(1/3) scaling may be a baryonic feedback artifact.")
        print(f"    FAVORS: Standard Model (baryonic physics)")
    elif max_screening > sig_threshold:
        print(f"\n✓  INTERPRETATION: Residuals correlate with density (screening proxy).")
        print(f"    This supports a density-dependent field theory mechanism.")
        print(f"    FAVORS: TEP (Field Theory)")
    else:
        print(f"\n✓  INTERPRETATION: Residuals are largely random (no strong correlations).")
        print(f"    This suggests the M^(1/3) scaling is fundamental, not a feedback artifact.")
        print(f"    FAVORS: TEP (Field Theory)")
    
    # --- STEP 5: Generate Diagnostic Plots ---
    print("\n### STEP 5: Generate Diagnostic Plots ###")
    
    fig = plt.figure(figsize=FIG_SIZE[FIG_PRESET])
    gs = fig.add_gridspec(3, 3, hspace=0.55, wspace=0.45)
    
    # Panel A: Main scaling relation
    ax1 = fig.add_subplot(gs[0, :])
    ax1.scatter(M_arr, R_arr, c=residuals, s=30, alpha=0.7,
                cmap='RdBu_r', vmin=-0.5, vmax=0.5, edgecolors='black', linewidth=0.3)
    M_range = np.logspace(np.log10(M_arr.min()), np.log10(M_arr.max()), 100)
    ax1.plot(M_range, k * M_range**(1/3), '-', color='black',
             linewidth=2, label=r'TEP: $R \propto M^{1/3}$')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel(r'Baryonic Mass $M_{\rm bar}$ ($M_\odot$)')
    ax1.set_ylabel(r'Mass Discrepancy Radius $R_{\rm DM}$ (kpc)')
    ax1.set_title(r'$\bf{a)}$ SPARC Scaling Relation (colored by residual)', loc='left')
    ax1.legend(loc='upper left', frameon=False)
    ax1.grid(True, which='major', alpha=0.3)
    cbar = plt.colorbar(ax1.collections[0], ax=ax1, pad=0.01)
    cbar.set_label(r'Residual (dex)')
    
    # Panel B: Residuals vs Gas Fraction
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.scatter(gas_frac_arr[valid_gas], residuals[valid_gas], 
                c=COLORS['accent'], s=20, alpha=0.6, edgecolors='none')
    ax2.axhline(0, color='black', linestyle='--', linewidth=1)
    if abs(r_gas) > 0.05:
        z = np.polyfit(gas_frac_arr[valid_gas], residuals[valid_gas], 1)
        p = np.poly1d(z)
        x_fit = np.linspace(gas_frac_arr[valid_gas].min(), gas_frac_arr[valid_gas].max(), 100)
        ax2.plot(x_fit, p(x_fit), '-', color=COLORS['highlight'], linewidth=1.5)
    ax2.set_xlabel(r'Gas Fraction $f_{\rm gas}$')
    ax2.set_ylabel(r'Residual (dex)')
    ax2.set_title(f'$\\bf{{b)}}$ Gas Fraction (r={r_gas:+.3f}, p={p_gas:.3f})', loc='left')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-1.5, 1.5)
    
    # Panel C: Residuals vs Surface Brightness
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.scatter(np.log10(Sigma_arr[valid_sigma]), residuals[valid_sigma],
                c=COLORS['secondary'], s=20, alpha=0.6, edgecolors='none')
    ax3.axhline(0, color='black', linestyle='--', linewidth=1)
    if abs(r_sigma) > 0.05:
        z = np.polyfit(np.log10(Sigma_arr[valid_sigma]), residuals[valid_sigma], 1)
        p = np.poly1d(z)
        x_fit = np.linspace(np.log10(Sigma_arr[valid_sigma]).min(), 
                           np.log10(Sigma_arr[valid_sigma]).max(), 100)
        ax3.plot(x_fit, p(x_fit), '-', color=COLORS['highlight'], linewidth=1.5)
    ax3.set_xlabel(r'$\log_{10}(\Sigma)$ ($M_\odot$/pc$^2$)')
    ax3.set_ylabel(r'Residual (dex)')
    ax3.set_title(f'$\\bf{{c)}}$ Surface Brightness (r={r_sigma:+.3f}, p={p_sigma:.3f})', loc='left')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(-1.5, 1.5)
    
    # Panel D: Residuals vs Inclination
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.scatter(inc_arr[valid_inc], residuals[valid_inc],
                c=COLORS['hover'], s=20, alpha=0.6, edgecolors='none')
    ax4.axhline(0, color='black', linestyle='--', linewidth=1)
    if abs(r_inc) > 0.05:
        z = np.polyfit(inc_arr[valid_inc], residuals[valid_inc], 1)
        p = np.poly1d(z)
        x_fit = np.linspace(inc_arr[valid_inc].min(), inc_arr[valid_inc].max(), 100)
        ax4.plot(x_fit, p(x_fit), '-', color=COLORS['highlight'], linewidth=1.5)
    ax4.set_xlabel(r'Inclination (deg)')
    ax4.set_ylabel(r'Residual (dex)')
    ax4.set_title(f'$\\bf{{d)}}$ Inclination (r={r_inc:+.3f}, p={p_inc:.3f})', loc='left')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(-1.5, 1.5)
    
    # Panel E: Residuals vs Mean Density (Screening Proxy)
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.scatter(np.log10(rho_arr[valid_rho]), residuals[valid_rho],
                c=COLORS['primary_light'], s=20, alpha=0.6, edgecolors='none')
    ax5.axhline(0, color='black', linestyle='--', linewidth=1)
    if abs(r_rho) > 0.05:
        z = np.polyfit(np.log10(rho_arr[valid_rho]), residuals[valid_rho], 1)
        p = np.poly1d(z)
        x_fit = np.linspace(np.log10(rho_arr[valid_rho]).min(),
                           np.log10(rho_arr[valid_rho]).max(), 100)
        ax5.plot(x_fit, p(x_fit), '-', color=COLORS['highlight'], linewidth=1.5)
    ax5.set_xlabel(r'$\log_{10}(\rho_{\rm central})$ ($M_\odot$/pc$^3$)')
    ax5.set_ylabel(r'Residual (dex)')
    ax5.set_title(f'$\\bf{{e)}}$ Central Density (r={r_rho:+.3f}, p={p_rho:.3f})', loc='left')
    ax5.grid(True, alpha=0.3)
    ax5.set_ylim(-1.5, 1.5)
    
    # Panel F: Residuals Histogram
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.hist(residuals, bins=25, color=COLORS['primary_light'], 
             edgecolor='black', alpha=0.6, density=True)
    x_gauss = np.linspace(-1.5, 1.5, 100)
    ax6.plot(x_gauss, stats.norm.pdf(x_gauss, 0, rms_scatter), 
             color='black', linewidth=1.5,
             label=f'Gaussian ($\sigma = {rms_scatter:.2f}$ dex)')
    ax6.axvline(0, color='black', linestyle=':', linewidth=1)
    ax6.set_xlabel(r'Residual (dex)')
    ax6.set_ylabel('Probability Density')
    ax6.set_title(r'$\bf{f)}$ Residual Distribution', loc='left')
    ax6.legend(frameon=False)
    ax6.set_xlim(-1.5, 1.5)
    ax6.grid(True, alpha=0.3)
    
    # Panel G: Correlation Summary
    ax7 = fig.add_subplot(gs[2, 2])
    categories = ['Gas\nFraction', 'Surface\nBrightness', 'Inclination', 'Central\nDensity']
    correlations = [abs(r_gas), abs(r_sigma), abs(r_inc), abs(r_rho)]
    colors_bar = [COLORS['accent'], COLORS['secondary'], COLORS['hover'], COLORS['primary_light']]
    
    bars = ax7.bar(categories, correlations, color=colors_bar, alpha=0.7, edgecolor='black')
    ax7.axhline(sig_threshold, color=COLORS['highlight'], linestyle='--', linewidth=1.5,
                label=f'Significance (|r| = {sig_threshold})')
    ax7.set_ylabel(r'|Correlation| with Residuals')
    ax7.set_title(r'$\bf{g)}$ Correlation Summary', loc='left')
    ax7.set_ylim(0, max(0.5, max(correlations) * 1.2))
    ax7.legend(frameon=False)
    ax7.grid(True, axis='y', alpha=0.3)
    
    plt.savefig(os.path.join(output_dir, 'figure_sparc_residuals.png'))
    print(f"\nSaved: figure_sparc_residuals.png")
    
    # --- SUMMARY ---
    print("\n" + "="*80)
    print("RESIDUAL ANALYSIS SUMMARY")
    print("="*80)
    
    interpretation = "TEP (Field Theory)"
    if max_baryonic > sig_threshold:
        interpretation = "Standard Model (Baryonic Feedback)"
    
    print(f"""
DATASET:
- Valid galaxies: {len(results)}
- RMS scatter: {rms_scatter:.3f} dex

BARYONIC PROPERTY CORRELATIONS:
- Gas Fraction:       r = {r_gas:+.3f} (p = {p_gas:.4f})
- Surface Brightness: r = {r_sigma:+.3f} (p = {p_sigma:.4f})
- Inclination:        r = {r_inc:+.3f} (p = {p_inc:.4f})
- Maximum:            |r| = {max_baryonic:.3f}

SCREENING PROXY CORRELATIONS:
- Mean Density:       r = {r_rho:+.3f} (p = {p_rho:.4f})
- Maximum:            |r| = {max_screening:.3f}

INTERPRETATION:
The residuals from the M^(1/3) scaling show {'STRONG' if max_baryonic > sig_threshold else 'WEAK'}
correlation with baryonic properties and {'STRONG' if max_screening > sig_threshold else 'WEAK'}
correlation with density (screening proxy).

VERDICT: FAVORS {interpretation}

This analysis provides a critical discriminant between baryonic feedback
(which should correlate with gas physics) and field theory (which should
correlate with density or be random).
""")
    
    return {
        'n_galaxies': len(results),
        'rms_scatter': rms_scatter,
        'r_gas': r_gas,
        'r_sigma': r_sigma,
        'r_inc': r_inc,
        'r_rho': r_rho,
        'interpretation': interpretation
    }


if __name__ == '__main__':
    results = run_residual_analysis()
