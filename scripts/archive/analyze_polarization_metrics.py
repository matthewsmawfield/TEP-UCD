import numpy as np

def analyze_polarization():
    # Grid generation (matching figure_6_polarization.py)
    N = 500  # Higher resolution for analysis
    x = np.linspace(-2, 2, N)
    y = np.linspace(-2, 2, N)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    Phi = np.arctan2(Y, X)

    # --- Model 1: Standard Black Hole ---
    # Intensity
    width = 0.25
    I_BH = np.exp(-(R - 1.0)**2 / (2 * width**2))
    mask_shadow = R < 0.6
    I_BH[mask_shadow] = 0.0

    # Polarization (Stokes Q, U proxies)
    # Simple model: Azimuthal field
    Psi_BH = Phi + np.pi/2 
    # Polarized intensity (assume proportional to I for simplicity in ring)
    P_BH_mag = I_BH * 0.4 # 40% polarization in ring
    Q_BH = P_BH_mag * np.cos(2*Psi_BH) # Note: Stokes Q/U use 2*Psi
    U_BH = P_BH_mag * np.sin(2*Psi_BH)
    
    # In shadow, P is 0
    Q_BH[mask_shadow] = 0
    U_BH[mask_shadow] = 0
    P_BH_total = np.sqrt(Q_BH**2 + U_BH**2)

    # --- Model 2: Gravitational Soliton ---
    # Intensity
    I_Sol = np.exp(-(R - 1.0)**2 / (2 * width**2))
    # Core emission (30% of peak ring brightness)
    I_Sol += 0.3 * np.exp(-R**2 / (2 * 0.6**2))

    # Polarization
    # Ring component (Azimuthal)
    P_Sol_Ring = I_Sol * 0.4 
    # Note: Using simple vector addition model for this analysis
    
    # Core component (Vertical/Uniform field)
    # In the figure we blended vectors. Here we model Stokes parameters.
    # Ring: Azimuthal
    Q_ring = P_Sol_Ring * np.cos(2*Psi_BH)
    U_ring = P_Sol_Ring * np.sin(2*Psi_BH)
    
    # Core: Uniform Vertical Field (Psi = pi/2) -> 2*Psi = pi -> cos=-1, sin=0
    # But wait, vertical means aligned with Y axis. Psi=pi/2.
    # Stokes Q = P * cos(2*theta), U = P * sin(2*theta)
    # If theta=90deg, 2*theta=180. Q=-P, U=0.
    
    # Define Core Region for mixing
    transition = 1 / (1 + np.exp((R - 0.8) * 10))
    
    # Core Polarization magnitude
    # Assume core emission is highly polarized (e.g. 60% due to orderly field)
    P_Core_Mag = 0.3 * np.exp(-R**2 / (2 * 0.6**2)) * 0.6
    
    # Construct Soliton Stokes (Linear blend approximation)
    # Outer dominated by Ring, Inner by Uniform Vertical
    Q_Sol = (1 - transition) * Q_ring + transition * (-P_Core_Mag)
    U_Sol = (1 - transition) * U_ring + transition * (0)
    
    P_Sol_total = np.sqrt(Q_Sol**2 + U_Sol**2)

    # --- Metrics ---
    
    # Define Regions
    # Core: R < 0.5
    # Ring: 0.8 < R < 1.2
    mask_core = R < 0.5
    mask_ring = (R > 0.8) & (R < 1.2)
    
    metrics = {}
    
    for name, P_map, I_map in [("Black Hole", P_BH_total, I_BH), ("Soliton", P_Sol_total, I_Sol)]:
        # 1. Total Polarized Flux in Core
        p_flux_core = np.sum(P_map[mask_core])
        
        # 2. Total Intensity in Core
        i_flux_core = np.sum(I_map[mask_core])
        
        # 3. Mean Fractional Polarization in Core (m = P/I)
        # Avoid divide by zero
        if i_flux_core > 1e-6:
            m_core = p_flux_core / i_flux_core
        else:
            m_core = 0.0
            
        # 4. Ring Peak Polarization
        p_peak_ring = np.max(P_map[mask_ring])
        
        # 5. Core Peak Polarization
        p_peak_core = np.max(P_map[mask_core])
        
        # 6. Core-to-Ring Polarization Ratio
        ratio = p_peak_core / p_peak_ring if p_peak_ring > 0 else 0
        
        metrics[name] = {
            "P_Flux_Core": p_flux_core,
            "I_Flux_Core": i_flux_core,
            "m_Core": m_core,
            "P_Peak_Core": p_peak_core,
            "Ratio_Core_Ring": ratio
        }

    # Print Results
    print("--- Polarization Analysis Results ---")
    print(f"{'Metric':<30} | {'Black Hole':<15} | {'Soliton':<15}")
    print("-" * 66)
    
    keys = ["I_Flux_Core", "P_Flux_Core", "m_Core", "P_Peak_Core", "Ratio_Core_Ring"]
    for k in keys:
        v1 = metrics["Black Hole"][k]
        v2 = metrics["Soliton"][k]
        print(f"{k:<30} | {v1:15.4f} | {v2:15.4f}")

    print("-" * 66)
    
    # Differential Signal
    diff_flux = metrics["Soliton"]["P_Flux_Core"] - metrics["Black Hole"]["P_Flux_Core"]
    print(f"\nExcess Core Polarized Flux (Soliton - BH): {diff_flux:.4f} (arbitrary units)")
    print(f"Core Fractional Polarization Improvement: {metrics['Soliton']['m_Core']*100:.1f}% vs {metrics['Black Hole']['m_Core']*100:.1f}%")

if __name__ == "__main__":
    analyze_polarization()
