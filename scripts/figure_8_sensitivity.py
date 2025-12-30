import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# --- TEP-GNSS Style Configuration ---
THEME_COLORS = {
    'primary': '#2D0140',       # Dark purple
    'secondary': '#495773',     # Blue-gray
    'accent': '#4A90C2',        # Medium blue
    'highlight': '#F39C12',     # Orange
    'text': '#220126',          # Dark text
    'background': '#F8F8FF',    # Off-white background
    'grid': '#CCCCCC',          # Light grey
}

def set_publication_style():
    """Sets matplotlib rcParams for consistent, publication-quality figures."""
    mpl_params = {
        'font.family': 'Times New Roman',
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'figure.dpi': 300,
        'axes.grid': True,
        'grid.color': THEME_COLORS['grid'],
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,
        'figure.facecolor': THEME_COLORS['background'],
        'axes.facecolor': THEME_COLORS['background'],
    }
    plt.rcParams.update(mpl_params)

set_publication_style()

def run_sensitivity_analysis():
    # Grid
    N = 200
    x = np.linspace(-2, 2, N)
    y = np.linspace(-2, 2, N)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    Phi = np.arctan2(Y, X)
    
    # Base Ring Model (Constant)
    width = 0.25
    I_Ring = np.exp(-(R - 1.0)**2 / (2 * width**2))
    P_Ring = I_Ring * 0.4 # 40% intrinsic polarization in ring
    
    # Parameters to vary
    core_brightness_levels = np.linspace(0.01, 1.0, 50) # relative to ring peak
    core_pol_fractions = [0.1, 0.3, 0.6, 0.9] # Intrinsic polarization of core emission
    
    plt.figure(figsize=(10, 6))
    
    colors = [THEME_COLORS['secondary'], THEME_COLORS['accent'], THEME_COLORS['primary'], THEME_COLORS['highlight']]
    
    print("Running sensitivity analysis...")
    print(f"{'Int. Pol':<10} | {'Min Brightness for Detection (m>10%)':<40}")
    print("-" * 55)

    for i, p_int in enumerate(core_pol_fractions):
        m_core_curve = []
        detection_threshold_crossed = False
        threshold_brightness = None
        
        for b_rel in core_brightness_levels:
            # Construct Model
            # Intensity
            I_Core = b_rel * np.exp(-R**2 / (2 * 0.6**2))
            I_Total = I_Ring + I_Core
            
            # Polarization
            # Ring is Azimuthal: Q = -P*cos(2phi), U = -P*sin(2phi)
            # (Derived from Psi = phi + pi/2)
            Psi_Ring = Phi + np.pi/2
            Q_Ring = P_Ring * np.cos(2*Psi_Ring)
            U_Ring = P_Ring * np.sin(2*Psi_Ring)
            
            # Core (Vertical -> Psi=90 -> 2Psi=180 -> cos=-1, sin=0)
            # Q = -P, U = 0
            P_Core_Mag = I_Core * p_int
            Q_Core = P_Core_Mag * (-1.0)
            U_Core = np.zeros_like(Q_Core)
            
            # Total Stokes
            Q_Tot = Q_Ring + Q_Core
            U_Tot = U_Ring + U_Core
            P_Tot = np.sqrt(Q_Tot**2 + U_Tot**2)
            
            # Calculate Metrics in Core (R < 0.5)
            mask_core = R < 0.5
            
            p_flux_core = np.sum(P_Tot[mask_core])
            i_flux_core = np.sum(I_Total[mask_core])
            
            m_core = p_flux_core / i_flux_core if i_flux_core > 0 else 0
            m_core_curve.append(m_core)
            
            if m_core > 0.10 and not detection_threshold_crossed:
                detection_threshold_crossed = True
                threshold_brightness = b_rel

        label_str = f'Intrinsic Core Pol ($p_{{int}}$) = {p_int*100:.0f}%'
        plt.plot(core_brightness_levels, m_core_curve, label=label_str, color=colors[i], linewidth=2.5)
        
        thresh_str = f"{threshold_brightness:.3f} x Ring Peak" if threshold_brightness else "Not Detected"
        print(f"{p_int*100:<9.0f}% | {thresh_str}")
        
    # --- Empirical Limits (EHT Data) ---
    # Current EHT (2017/2021): Dynamic Range ~10:1 (conservative) to ~20:1
    # This means features fainter than ~0.1 * Peak are hard to distinguish from noise/artifacts.
    limit_current = 0.10
    plt.axvline(x=limit_current, color='gray', linestyle=':', linewidth=2, label='Current EHT Limit (Dyn. Range ~10:1)')
    
    # Future ngEHT / High-SNR: Dynamic Range ~100:1
    limit_future = 0.01
    plt.axvline(x=limit_future, color='gray', linestyle='-.', linewidth=1.5, alpha=0.7, label='Future ngEHT Limit (Dyn. Range ~100:1)')

    # Shaded regions for feasibility
    plt.fill_betweenx([0, 0.6], 0, limit_future, color='gray', alpha=0.1, hatch='///', label='Instrumental Noise Floor')

    # Styling
    plt.axhline(y=0.10, color='#D32F2F', linestyle='--', alpha=0.7, linewidth=1.5, label=r'Detection Threshold ($m_{obs} > 10\%$)')
    
    plt.title("Sensitivity Analysis: Soliton Core Polarization Signature", fontsize=14, fontweight='bold', color=THEME_COLORS['primary'])
    plt.xlabel("Core Relative Brightness (Fraction of Ring Peak)", fontsize=12)
    plt.ylabel("Observed Core Fractional Polarization ($m_{obs}$)", fontsize=12)
    
    # Log scale for x-axis to better show the dynamic range
    plt.xscale('log')
    plt.xlim(0.005, 1.2)
    
    plt.legend(frameon=True, fancybox=True, framealpha=0.9, facecolor='white', loc='upper left', fontsize=9)
    
    # Annotations
    plt.text(0.15, 0.02, "Feasible with Current Data", fontsize=10, color='green', fontweight='bold')
    plt.text(0.012, 0.02, "Requires ngEHT", fontsize=10, color='#E67E22', fontweight='bold', rotation=90)
    
    plt.tight_layout()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, '../site/figures')
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'figure_8_sensitivity.png')
    plt.savefig(save_path, dpi=300, facecolor=THEME_COLORS['background'])
    print("-" * 55)
    print(f"Sensitivity plot saved to {save_path}")

if __name__ == "__main__":
    run_sensitivity_analysis()
