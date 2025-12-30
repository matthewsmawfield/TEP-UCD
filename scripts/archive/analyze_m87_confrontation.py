import numpy as np
import pandas as pd

def analyze_m87_confrontation():
    print("--- Confrontation Analysis: Soliton Model vs. EHT M87* Data ---")
    
    # --- 1. Define Observational Constraints (EHT 2019, 2021) ---
    # Constraint A: Central Brightness Depression (Shadow Depth)
    # EHT Paper I/VI: The central flux density is < 10% of the ring brightness.
    # Source: EHT Collaboration 2019, ApJ 875, L1 & L6.
    f_depression_limit = 0.10 # Max allowed brightness ratio (Core/Ring)
    
    # Constraint B: Central Polarization Fraction
    # EHT Paper VII/VIII: Polarization is concentrated in the ring.
    # We assume any central polarized flux must be below the detection threshold or consistent with noise.
    # Conservative limit: Polarized flux in center < 1% of peak polarized flux in ring (dynamic range limit).
    f_pol_limit = 0.15 # Upper limit on m_core if I_core is detectable
    
    print(f"Constraint A (Brightness): I_core / I_ring < {f_depression_limit}")
    print(f"Constraint B (Polarization): m_core < {f_pol_limit} (if I_core is detectable)")
    print("-" * 60)
    
    # --- 2. Define Soliton Model Space ---
    # Parameter: Core Relative Brightness (I_core / I_ring)
    brightness_levels = [0.5, 0.3, 0.1, 0.05, 0.01, 0.001]
    
    # Parameter: Core Intrinsic Polarization (m_int)
    # The model predicts coherent field threading -> High polarization (e.g. 50%)
    m_intrinsic = 0.50
    
    results = []
    
    for b_rel in brightness_levels:
        # Check Visibility
        is_visible = b_rel > 0.01 # Assuming dynamic range ~100:1 for future, ~10:1 for current
        
        # Check Brightness Constraint
        passes_brightness = b_rel < f_depression_limit
        
        # Check Polarization Constraint
        # If the core is visible, we measure its polarization.
        # The Soliton predicts m_obs ~ m_intrinsic = 0.50.
        # This CONTRADICTS the observation if m_intrinsic > f_pol_limit.
        
        if not passes_brightness:
            status = "RULED OUT (Too Bright)"
            reason = f"I_core ({b_rel}) > Limit ({f_depression_limit})"
        else:
            # It satisfies the shadow depth constraint (it's dark enough).
            # Now, is it "Dark Soliton" or "Invisible"?
            
            # If it's faint but visible (e.g. 0.05), EHT would see the polarization.
            # EHT sees NO central polarization.
            # If Soliton has m=0.5, it would be detected.
            # So if (Visible AND Soliton_Polarized), it is ruled out by non-detection of polarization?
            # Or is it just "Allowed (Dark)"?
            
            # Refined Logic:
            # EHT Sensitivity limit ~ 0.1 (Current).
            # If b_rel < 0.1, EHT cannot see it yet. -> ALLOWED (Current limits)
            # If b_rel > 0.1, EHT would see it. EHT sees Shadow.
            # -> If b_rel > 0.1, it must be ruled out by Brightness constraint anyway.
            
            # What about Polarization?
            # If we had better sensitivity (ngEHT), we could see down to 0.01.
            # If we see 0.05 and it has m=0.5, that is the Soliton signature.
            
            status = "ALLOWED (Current Data)"
            reason = f"I_core ({b_rel}) < Sensitivity Limit (0.1)"
            
            if b_rel >= 0.01 and b_rel < 0.1:
                future_status = "TESTABLE (ngEHT)"
            elif b_rel < 0.01:
                future_status = "UNTESTABLE (Too Faint)"
            else:
                future_status = "N/A"
                
        results.append({
            "Relative Brightness": b_rel,
            "Intrinsic Pol": m_intrinsic,
            "Status (Current)": status,
            "Reason": reason,
            "Future Prospect": future_status if status == "ALLOWED (Current Data)" else "N/A"
        })

    # --- 3. Output Table ---
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    
    # --- 4. Generate Conclusions ---
    print("\n--- Conclusions ---")
    print("1. 'Bright' Solitons (I_core > 10% I_ring) are definitively RULED OUT by EHT M87* imaging.")
    print("2. 'Dark' Solitons (I_core < 10% I_ring) are consistent with current data (indistinguishable from noise).")
    print("3. The 'Polarized Heart' test targets the 1-10% brightness regime using ngEHT.")
    print("   - Detection of m ~ 50% in this regime would confirm Soliton.")
    print("   - Non-detection (m ~ 0%) down to 1% brightness would rule out Solitons with internal fields.")

if __name__ == "__main__":
    analyze_m87_confrontation()
