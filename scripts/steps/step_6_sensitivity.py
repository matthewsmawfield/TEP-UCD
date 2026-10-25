import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.style import set_pub_style as set_shared_style, COLORS, FIG_SIZE, FIG_SCALE

try:
    from utils.logger import TEPLogger, set_step_logger, print_status
except ImportError:
    pass

from core.constants import M_EARTH, M_SUN, R_EARTH, SCREENING_LENGTH_KM, RHO_C

FIG_PRESET = 'web_standard'

set_shared_style(scale=FIG_SCALE[FIG_PRESET])

def run_sensitivity_analysis():
    """Generate Figure 8: Sensitivity and feasibility analysis."""
    logger = TEPLogger("step_6_sensitivity", log_file_path=os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'step_6_sensitivity.log'))
    set_step_logger(logger)

    print_status("Initializing sensitivity and feasibility analysis", "PROCESS")

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
    
    print_status("Running sensitivity analysis", "PROCESS")
    print_status(f"Grid size: {N}x{N}, core pol fractions: {core_pol_fractions}, brightness levels: {len(core_brightness_levels)}", "INFO")
    print_status(f"{'Int. Pol':<10} | {'Min Brightness for Detection (m>10%)':<40}", "INFO")
    print_status("-" * 55, "INFO")

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

        thresh_str = f"{threshold_brightness:.3f} x Ring Peak" if threshold_brightness else "Not Detected"
        print_status(f"{p_int*100:<9.0f}% | {thresh_str}", "INFO")

    outputs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results', 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    print_status("-" * 55, "INFO")

    # EHT target predictions from rho_T
    rho_T = 20.0  # g/cm^3
    rho_T_kg_km3 = rho_T * 1e12  # kg/km^3

    M_m87 = 6.5e9 * M_SUN
    R_T_m87 = ((3 * M_m87) / (4 * np.pi * rho_T_kg_km3)) ** (1/3)
    print_status(f"M87* soliton core prediction: R_T = {R_T_m87:.2e} km ({R_T_m87/1.496e8:.2f} AU)", "INFO")

    M_sgr = 4.3e6 * M_SUN
    R_T_sgr = ((3 * M_sgr) / (4 * np.pi * rho_T_kg_km3)) ** (1/3)
    print_status(f"Sgr A* soliton core prediction: R_T = {R_T_sgr:.2e} km ({R_T_sgr/1.496e8:.2f} AU)", "INFO")

    # Save numerical outputs
    output_data = {
        "grid_size": int(N),
        "rho_T_g_cm3": float(rho_T),
        "M87_star": {
            "M_kg": float(M_m87),
            "M_solar": float(M_m87 / M_SUN),
            "R_T_km": float(R_T_m87),
            "R_T_AU": float(R_T_m87 / 1.496e8)
        },
        "Sgr_A_star": {
            "M_kg": float(M_sgr),
            "M_solar": float(M_sgr / M_SUN),
            "R_T_km": float(R_T_sgr),
            "R_T_AU": float(R_T_sgr / 1.496e8)
        }
    }
    with open(os.path.join(outputs_dir, 'step_6_sensitivity.json'), 'w') as f:
        json.dump(output_data, f, indent=2)
    try:
        print_status("Numerical outputs saved to results/outputs/step_6_sensitivity.json", "SUCCESS")
    except Exception:
        pass
    return output_data

if __name__ == "__main__":
    run_sensitivity_analysis()
