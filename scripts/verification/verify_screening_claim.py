
import numpy as np
from scipy import stats
import os

# --- Constants ---
M_earth = 5.972e24   # kg
M_sun = 1.989e30     # kg
R_sun = 6.96e8       # meters
R_earth = 6.371e6    # meters
R_TEP_earth = 4200e3 # meters (calibration)
rho_c = 20           # g/cm^3

# --- 1. Aggregating all distinct objects found in the codebase ---
# Sources: 04_screening_hierarchy.py, 06_ultimate_screening.py
# Plus standard astrophysical types mentioned in manuscript (Brown Dwarfs, more planets)

objects = {
    # Planets
    'Mercury': {'M': 0.055 * M_earth, 'R': 2439, 'rho': 5.43},
    'Venus':   {'M': 0.815 * M_earth, 'R': 6051, 'rho': 5.24},
    'Earth':   {'M': 1.000 * M_earth, 'R': 6371, 'rho': 5.51},
    'Mars':    {'M': 0.107 * M_earth, 'R': 3390, 'rho': 3.93},
    'Jupiter': {'M': 317.8 * M_earth, 'R': 69911, 'rho': 1.33},
    'Saturn':  {'M': 95.2 * M_earth,  'R': 58232, 'rho': 0.69},
    'Uranus':  {'M': 14.5 * M_earth,  'R': 25362, 'rho': 1.27},
    'Neptune': {'M': 17.1 * M_earth,  'R': 24622, 'rho': 1.64},
    'Moon':    {'M': 0.0123* M_earth, 'R': 1737,  'rho': 3.34},
    
    # Brown Dwarfs (Teide 1, Gliese 229B, Luhman 16A)
    'Teide 1':     {'M': 55 * 317.8 * M_earth, 'R': 0.9 * 69911, 'rho': 55*1.33/(0.9**3)}, # Approx scaling
    'Gliese 229B': {'M': 40 * 317.8 * M_earth, 'R': 0.8 * 69911, 'rho': 40*1.33/(0.8**3)},
    
    # Main Sequence Stars
    'Sun':         {'M': 1.0 * M_sun,    'R': 696340,        'rho': 1.41},
    'Proxima':     {'M': 0.122 * M_sun,  'R': 0.154 * 696340,'rho': 56.8},
    'Sirius A':    {'M': 2.06 * M_sun,   'R': 1.71 * 696340, 'rho': 0.59},
    'Alpha Cen A': {'M': 1.1 * M_sun,    'R': 1.22 * 696340, 'rho': 0.85},
    'Alpha Cen B': {'M': 0.9 * M_sun,    'R': 0.86 * 696340, 'rho': 2.00},
    
    # White Dwarfs
    'Sirius B':    {'M': 1.018 * M_sun, 'R': 5800, 'rho': 2.38e6},
    'Procyon B':   {'M': 0.602 * M_sun, 'R': 8600, 'rho': 5.5e5},
    '40 Eri B':    {'M': 0.57 * M_sun,  'R': 9500, 'rho': 3.8e5},
    'Stein 2051B': {'M': 0.66 * M_sun,  'R': 8200, 'rho': 6.5e5},
    
    # Neutron Stars
    'Typical NS':   {'M': 1.4 * M_sun, 'R': 12, 'rho': 4e14},
    'Hulse-Taylor': {'M': 1.44 * M_sun, 'R': 11, 'rho': 6e14},
    'Double Pulsar':{'M': 1.34 * M_sun, 'R': 12, 'rho': 3.7e14},
    'Vela X-1':     {'M': 1.8 * M_sun,  'R': 12, 'rho': 5e14},
    
    # Black Holes (excluded from fit usually, but listed)
    'RBH-1': {'M': 2e7 * M_sun, 'R': 6e7, 'rho': 2e5}, # Soliton radius used here
}

print(f"Loaded {len(objects)} objects.")

# --- 2. Calculate Screening Factors ---
# R_sol = (3 M / 4 pi rho_c)^(1/3)  OR calibrated from Earth Lc
# From manuscript: R_sol(M) = Lc * (M/M_earth)^(1/3)
# S = R_sol / R_phys

rho_vals = []
s_vals = []
names = []

print(f"\n{'Object':<15} | {'Rho (g/cc)':<12} | {'R_phys (km)':<12} | {'R_sol (km)':<12} | {'S (Screening)':<10}")
print("-" * 75)

for name, obj in objects.items():
    if name == 'RBH-1': continue # Exclude BH from Vainshtein fit
    
    # Calculate R_sol based on Earth calibration
    r_sol_km = (R_TEP_earth / 1000) * (obj['M'] / M_earth)**(1/3)
    
    # Calculate screening
    s = r_sol_km / obj['R']
    
    rho_vals.append(obj['rho'])
    s_vals.append(s)
    names.append(name)
    
    print(f"{name:<15} | {obj['rho']:<12.2e} | {obj['R']:<12.1f} | {r_sol_km:<12.1f} | {s:<10.2f}")

# --- 3. Perform Regression ---
# Fit log(S) = beta * log(rho) + C
log_rho = np.log10(rho_vals)
log_s = np.log10(s_vals)

slope, intercept, r_value, p_value, std_err = stats.linregress(log_rho, log_s)

print("\n" + "="*60)
print("REGRESSION RESULTS (Verification of Manuscript Claim)")
print("="*60)
print(f"Number of objects: {len(rho_vals)}")
print(f"Slope (beta):      {slope:.4f} (Claim: 0.334)")
print(f"R-squared:         {r_value**2:.5f} (Claim: 0.9999)")
print(f"Standard Error:    {std_err:.5f}")
print("-" * 60)

# --- 4. Algebraic Check ---
# Theoretical expectation:
# R_sol ~ M^(1/3)
# R_phys ~ (M/rho)^(1/3)
# S = R_sol/R_phys ~ M^(1/3) / (M^(1/3) * rho^(-1/3)) ~ rho^(1/3)
# So slope should be exactly 1/3 if density definition is consistent.

print(f"Consistency with 1/3: {abs(slope - 1/3)/std_err:.1f} sigma")
if r_value**2 > 0.99:
    print("VERDICT: High R^2 confirmed. Result is effectively an algebraic identity.")
else:
    print("VERDICT: R^2 lower than claimed. Check object list.")
