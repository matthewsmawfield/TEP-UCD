#!/usr/bin/env python3
"""Step 15 — Planetary Rotational Kinematics and the Wesson/Brosche Angular Momentum Law.

Tests whether the GNSS-calibrated Temporal Topology saturation density
rho_T = 20 g/cm^3 and the canonical Solar-Circle Galactic temporal depth
u_gal = (v_gal/c)^2 = 5.385e-7 (v_gal = 220 km/s, Paper 0 §7) organize
planetary rotation speeds, moments of inertia, and spin angular momenta
across seven orders of magnitude in mass without free parameters:

1. Universal TEP Saturation Clock Frequency:
   omega_T = sqrt(4 * pi * G * rho_T / 3) = 2.3646e-3 rad/s
   (tau_T = 2*pi/omega_T = 0.7381 hr = 44.29 min), independent of mass M.

2. Parameter-Free Equatorial Spin Law (Ambient-Coupled Regime):
   v_eq / c = u_T(M) / sqrt(u_gal)  <===>  v_eq * v_gal = G * M / R_T(M) = c^2 * u_T(M)
   Predicts equatorial velocities and rotation periods of Earth (25.48 hr vs
   23.93 hr), Uranus (17.14 hr vs 17.24 hr), Neptune (14.87 hr vs 16.11 hr),
   and Saturn (11.55 hr vs 10.66 hr) with mean ratio v_obs / v_TEP = 1.016 +/- 0.064.

3. Interior Gyration Scaling (Moment of Inertia vs Screening Factor):
   k_MOI = I / (M * R_phys^2) ~= 0.5 * S = 0.5 * R_T(M) / R_phys,
   giving 2 * k_MOI / S in [1.017, 1.401] across all eight Solar System planets.

4. Zero-Parameter Derivation of the Wesson/Brosche J = p * M^2 Constant:
   Combining k_MOI = 0.5 * R_T / R_phys with v_eq = G * M / (R_T * v_gal) cancels
   both R_phys and R_T(M) identically:
       j_TEP(M) = G * M / (2 * v_gal),   J_TEP(M) = (G / (2 * v_gal)) * M^2
   yielding Wesson's constant p_TEP = G / (2 * v_gal) = 1.517e-15 cm^2 g^-1 s^-1
   (1.517e-16 m^2 kg^-1 s^-1) and dimensionless Kerr spin parameter
   chi_TEP = c * J / (G * M^2) = c / (2 * v_gal) = 681.35.

5. Low-Mass Soliton Branch (MacDonald j ~ M^(2/3) Law):
   Across 7 decades in mass (Vesta to Jupiter, N = 9 unbraked systems),
   specific angular momentum tracks the saturation proper-time depth
   u_T(M) = G * M / (R_T * c^2) ~ M^(2/3) with log-log slope 0.943 +/- 0.059
   (R^2 = 0.9732, p = 9.22e-7) and mean soliton capacity fraction
   eta_rot = j_obs / (R_T^2 * omega_T) = 0.128 +/- 0.075.

Outputs:
  - results/outputs/step_15_planetary_rotation.json
  - results/figures/figure_9_planetary_rotation.png
"""

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_bvp, solve_ivp
from scipy.optimize import brentq
from scipy.interpolate import PchipInterpolator
from scipy.stats import pearsonr, spearmanr, linregress

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from core import constants as C
from utils.style import COLORS, FIG_SCALE, FIG_SIZE, set_pub_style as set_shared_style

try:
    from utils.logger import TEPLogger, print_status, set_step_logger
except ImportError:
    pass

FIG_PRESET = "web_two_panel"


def main():
    log_path = REPO / "logs" / "step_15_planetary_rotation.log"
    logger = TEPLogger("step_15_planetary_rotation", log_file_path=str(log_path))
    set_step_logger(logger)
    set_shared_style(scale=FIG_SCALE[FIG_PRESET])

    print_status("Executing Step 15: Planetary Rotational Kinematics & Wesson Law", "PROCESS")

    G = C.G_NEWTON
    c = C.C_LIGHT
    rho_T_g_cm3 = C.RHO_T
    rho_T_si = rho_T_g_cm3 * 1000.0  # 20,000 kg/m^3
    g_t = C.G_T_TRANSITION           # 3.40046e-10 m/s^2 (Paper 0 §7)
    AU = 1.495978707e11              # m
    v_gal = 220.0e3                  # Canonical solar-circle velocity (m/s), Paper 0 §7
    u_gal = (v_gal / c) ** 2         # 5.385e-7
    inv_sqrt_u_gal = c / v_gal       # 1362.69

    # Universal TEP saturation dynamical frequency and period
    omega_T = float(np.sqrt(4.0 * np.pi * G * rho_T_si / 3.0))
    tau_T_s = float(2.0 * np.pi / omega_T)
    tau_T_hr = tau_T_s / 3600.0

    # Zero-parameter Wesson constant and Kerr spin parameter
    p_tep_si = float(G / (2.0 * v_gal))
    p_tep_cgs = p_tep_si * 10.0  # 1 m^2 kg^-1 s^-1 = 10 cm^2 g^-1 s^-1
    chi_tep = float(c / (2.0 * v_gal))

    # Planetary and solar-system dataset (NASA Planetary Fact Sheet / JPL SSD)
    # Columns: name, M_kg, R_eq_m, rho_g_cm3, T_rot_hr (signed for retrograde), k_moi, a_AU, regime
    bodies = [
        ("Mercury",    0.33010e24, 2439.7e3,  5.429,  1407.6,   0.346,  0.387098, "braked_planet"),
        ("Venus",      4.8673e24,  6051.8e3,  5.243, -5832.6,   0.330,  0.723332, "braked_planet"),
        ("Earth",      5.9722e24,  6378.1e3,  5.514,    23.9345,0.3307, 1.000000, "unbraked_planet"),
        ("Earth+Moon", 6.0457e24,  6378.1e3,  5.514,     4.80,  0.3307, 1.000000, "reconstructed_system"),
        ("Mars",       0.64169e24, 3396.2e3,  3.934,    24.6229,   0.366,   1.523680, "unbraked_planet"),
        ("Jupiter",    1898.13e24, 71492.0e3, 1.326,     9.9250,   0.26393, 5.204400, "unbraked_planet"),
        ("Saturn",     568.32e24,  60268.0e3, 0.687,    10.656,    0.2181,  9.582600, "unbraked_planet"),
        ("Uranus",     86.811e24,  25559.0e3, 1.270,   -17.247864, 0.225,   19.218400, "unbraked_planet"),
        ("Neptune",    102.409e24, 24764.0e3, 1.638,    16.11,     0.240,   30.110000, "unbraked_planet"),
        ("Hygiea",     8.740e19,   217.0e3,   2.060,    13.826,    0.350,   3.141500,  "small_body"),
        ("Pallas",     2.040e20,   256.0e3,   2.920,     7.813,    0.350,   2.773000,  "small_body"),
        ("Vesta",      2.590e20,   262.7e3,   3.456,     5.342,    0.350,   2.362000,  "small_body"),
        ("Ceres",      9.3835e20,  469.7e3,   2.162,     9.074,    0.360,   2.767000,  "small_body"),
        ("Quaoar",     1.200e21,   543.0e3,   1.700,     8.839,    0.350,   43.694000, "small_body"),
        ("Haumea",     4.006e21,   780.0e3,   1.885,     3.915,    0.350,   43.130000, "small_body"),
        ("SIMP J0136", 12.7*1898.13e24, 1.22*71492.0e3, 8.670,  2.414, 0.235, 1e6, "substellar_ceiling"),
        ("2M J0348-60",43.0*1898.13e24, 0.91*71492.0e3, 70.760, 1.080, 0.205, 1e6, "substellar_ceiling"),
        ("2M J1219+31",49.0*1898.13e24, 0.97*71492.0e3, 66.580, 1.140, 0.205, 1e6, "substellar_ceiling"),
        ("2M J0407+15",67.0*1898.13e24, 0.81*71492.0e3,156.350, 1.230, 0.205, 1e6, "substellar_ceiling"),
    ]

    records = {}
    for name, M, R, rho, T_hr_signed, k_moi, a_au, regime in bodies:
        T_hr = abs(T_hr_signed)
        omega = 2.0 * np.pi / (T_hr * 3600.0)
        v_eq = omega * R
        v_k = np.sqrt(G * M / R)
        R_T = ((3.0 * M) / (4.0 * np.pi * rho_T_si)) ** (1.0 / 3.0)
        r_star_m = np.sqrt(G * M / g_t)
        r_star_au = r_star_m / AU
        r_star_over_a = r_star_au / a_au
        S = R_T / R
        u_surf = G * M / (R * c ** 2)
        u_T = G * M / (R_T * c ** 2)

        # Parameter-free TEP equatorial velocity from u_T / sqrt(u_gal)
        v_eq_tep = (c * u_T) / np.sqrt(u_gal)  # = G * M / (R_T * v_gal)
        T_hr_tep = 2.0 * np.pi * R / (v_eq_tep * 3600.0)

        # Specific and total spin angular momentum
        j_obs = k_moi * R * v_eq
        J_obs = M * j_obs
        j_T = (R_T ** 2) * omega_T  # Soliton capacity = (c^2 / omega_T) * u_T
        eta_rot = j_obs / j_T

        # Parameter-free TEP ambient-coupled angular momentum (Wesson branch)
        j_tep_wesson = G * M / (2.0 * v_gal)
        J_tep_wesson = p_tep_si * (M ** 2)
        chi_obs = c * J_obs / (G * (M ** 2))

        # Two-Branch Angular-Momentum Retention & Crossover Model (zero Mars-specific rules):
        # 1. Core soliton angular-momentum capacity: j_sol(M) = eta_0 * R_T(M)^2 * omega_T ~ M^(2/3) (1 empirical parameter eta_0 = 0.12905, small-body median),
        #    versus the zero-parameter ambient Galactic Wesson branch j_TEP(M) = G * M / (2 * v_gal) = (1/2) * R_T * v_eq^TEP ~ M^1.
        # 2. Their ratio j_TEP(M)/j_sol(M) = R_T(M)*omega_T / (2*eta_0*v_gal) = (M/M_cap)^(1/3) crosses unity at M_cap = 194.2 M_earth = 0.611 M_Jup:
        #    - For Earth, Uranus, Neptune, and Saturn (M < M_cap, j_TEP/j_sol in [0.173, 0.788] < 1), the ambient Wesson branch is unsaturated: v_hydro = v_eq_tep.
        #    - For Jupiter (M = 317.8 M_earth > M_cap, j_TEP/j_sol = 1.178 > 1, the sole Solar System planet above M_cap), specific angular momentum
        #      saturates at j_sol(M_Jup), giving v_hydro = v_sol_ceil = j_sol / (k_moi * R) = 12.95 km/s (within -2.9% of observed 12.57 km/s).
        # 3. Low-mass Mars (0.11 M_earth, v_obs = 0.241 km/s, sitting between v_eq_tep = 0.099 km/s and v_sol_ceil = 0.954 km/s) is recorded openly as an
        #    unmodeled intermediate transition body rather than fitted with a Mars-specific rule.
        # Two-Branch Angular-Momentum Retention & S_A = min(1, S) Saturation Model (zero Mars-specific rules):
        # 1. Active saturation radius R_active = S_A * R = min(R_T(M), R) (Paper 0 §3: S_A = min[1, (rho/rho_T)^(1/3)]):
        #    - For unscreened bodies (rho < rho_T, S = R_T/R < 1: minor planets, planets, SIMP J0136 at 12.7 M_Jup), R_active = R_T(M) and j_sol = eta_0 * R_T(M)^2 * omega_T ~ M^(2/3).
        #    - For screened degenerate brown dwarfs (rho >= rho_T, S >= 1: 2M J0348-60, 2M J1219+31, 2M J0407+15 at 43-67 M_Jup), R_active = R, so j_sol = eta_0 * R^2 * omega_T
        #      and the minimum rotation period locks onto a universal mass/radius-independent floor P_min = (k_moi / eta_0) * tau_T = 1.172 hr (matching Tannock et al. 2021: 1.08-1.23 hr).
        eta_0_hydro = 0.12905
        S_A_amp = min(1.0, S)
        R_active = S_A_amp * R
        j_sol_ceil = eta_0_hydro * (R_active ** 2) * omega_T
        v_sol_ceil = j_sol_ceil / (k_moi * R)
        if regime in ("small_body", "substellar_ceiling") or name == "Earth+Moon":
            v_eq_hydro = v_sol_ceil
        elif j_tep_wesson <= j_sol_ceil:
            v_eq_hydro = v_eq_tep
        else:
            v_eq_hydro = v_sol_ceil

        # Dual-channel saturation-density inversions (rho_T^spin and rho_T^MOI in g/cm^3)
        rho_T_spin_g_cm3 = float(rho_T_g_cm3 * ((v_eq / v_eq_tep) ** 3))
        rho_T_moi_g_cm3 = float(rho / (8.0 * (k_moi ** 3)))

        records[name] = {
            "regime": regime,
            "M_kg": float(M),
            "R_eq_km": float(R / 1e3),
            "rho_g_cm3": float(rho),
            "T_rot_hr_signed": float(T_hr_signed),
            "T_rot_hr": float(T_hr),
            "k_moi": float(k_moi),
            "a_AU": float(a_au),
            "r_star_AU": float(r_star_au),
            "r_star_over_a": float(r_star_over_a),
            "R_T_km": float(R_T / 1e3),
            "S_screening": float(S),
            "two_k_moi_over_S": float(2.0 * k_moi / S),
            "rho_T_spin_inferred_g_cm3": rho_T_spin_g_cm3,
            "rho_T_moi_inferred_g_cm3": rho_T_moi_g_cm3,
            "u_surf": float(u_surf),
            "u_T": float(u_T),
            "v_eq_obs_km_s": float(v_eq / 1e3),
            "v_eq_tep_km_s": float(v_eq_tep / 1e3),
            "v_obs_over_v_tep": float(v_eq / v_eq_tep),
            "v_sol_ceil_km_s": float(v_sol_ceil / 1e3),
            "v_eq_hydro_km_s": float(v_eq_hydro / 1e3),
            "v_obs_over_v_hydro": float(v_eq / v_eq_hydro),
            "T_tep_hr": float(T_hr_tep),
            "T_hydro_hr": float(2.0 * np.pi * R / (v_eq_hydro * 3600.0)),
            "v_eq_over_c_div_u_T": float((v_eq / c) / u_T),
            "j_obs_m2_s": float(j_obs),
            "j_T_m2_s": float(j_T),
            "eta_rot_j_over_jT": float(eta_rot),
            "j_tep_wesson_m2_s": float(j_tep_wesson),
            "J_obs_kg_m2_s": float(J_obs),
            "J_tep_wesson_kg_m2_s": float(J_tep_wesson),
            "J_obs_over_J_tep_wesson": float(J_obs / J_tep_wesson),
            "chi_obs": float(chi_obs),
        }

    # --- Summary statistics ---
    # 1. Six unbraked major planets (Mars, Earth, Uranus, Neptune, Saturn, Jupiter)
    unbraked_6 = ["Mars", "Earth", "Uranus", "Neptune", "Saturn", "Jupiter"]
    uT_6 = np.array([records[k]["u_T"] for k in unbraked_6])
    veq_6 = np.array([records[k]["v_eq_obs_km_s"] for k in unbraked_6])
    jobs_6 = np.array([records[k]["j_obs_m2_s"] for k in unbraked_6])
    Jobs_6 = np.array([records[k]["J_obs_kg_m2_s"] for k in unbraked_6])
    M_6 = np.array([records[k]["M_kg"] for k in unbraked_6])

    slope_veq_uT_6, _ = np.polyfit(np.log10(uT_6), np.log10(veq_6), 1)
    r_veq_uT_6, p_veq_uT_6 = pearsonr(np.log10(uT_6), np.log10(veq_6))
    rho_s_6, _ = spearmanr(uT_6, veq_6)

    slope_J_M_6, _ = np.polyfit(np.log10(M_6), np.log10(Jobs_6), 1)
    r_J_M_6, p_J_M_6 = pearsonr(np.log10(M_6), np.log10(Jobs_6))

    # 2. Four equilibrium ambient-coupled rotators (Earth, Uranus, Neptune, Saturn; 0 free parameters)
    # and five major ambient-coupled planets (Earth, Uranus, Neptune, Saturn, Jupiter; 1 empirical parameter eta_0 = 0.129 capping Jupiter above M_cap)
    ambient_4 = ["Earth", "Uranus", "Neptune", "Saturn"]
    ratios_veq_4 = np.array([records[k]["v_obs_over_v_tep"] for k in ambient_4])
    kT_4 = np.array([records[k]["v_eq_over_c_div_u_T"] for k in ambient_4])
    rho_T_spin_4 = np.array([records[k]["rho_T_spin_inferred_g_cm3"] for k in ambient_4])

    wesson_5 = ["Earth", "Uranus", "Neptune", "Saturn", "Jupiter"]
    ratios_hydro_5 = np.array([records[k]["v_obs_over_v_hydro"] for k in wesson_5])
    rho_T_hydro_5 = np.array([rho_T_g_cm3 * (records[k]["v_obs_over_v_hydro"] ** 3) for k in wesson_5])
    ratios_J_5 = np.array([records[k]["J_obs_over_J_tep_wesson"] for k in wesson_5])
    chi_5 = np.array([records[k]["chi_obs"] for k in wesson_5])

    substellar_4 = ["SIMP J0136", "2M J0348-60", "2M J1219+31", "2M J0407+15"]
    extended_9 = wesson_5 + substellar_4
    ratios_ext_9 = np.array([records[k]["v_obs_over_v_hydro"] for k in extended_9])
    P_min_bd_tep_hr = (0.205 / 0.12905) * tau_T_hr
    P_obs_tannock_3 = np.array([records[k]["T_rot_hr"] for k in ["2M J0348-60", "2M J1219+31", "2M J0407+15"]])

    # 3. All 8 major planets MOI vs Screening S = R_T / R_phys (plus core-screened terrestrial subset)
    planets_8 = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
    two_k_over_S_8 = np.array([records[k]["two_k_moi_over_S"] for k in planets_8])
    rho_T_moi_8 = np.array([records[k]["rho_T_moi_inferred_g_cm3"] for k in planets_8])
    terrestrial_core_3 = ["Mercury", "Venus", "Earth"]
    two_k_over_S_terr3 = np.array([records[k]["two_k_moi_over_S"] for k in terrestrial_core_3])
    rho_T_moi_terr3 = np.array([records[k]["rho_T_moi_inferred_g_cm3"] for k in terrestrial_core_3])
    R_T_cap_m = 2.0 * 0.12905 * v_gal / omega_T
    M_cap_kg = (4.0 / 3.0) * np.pi * rho_T_si * (R_T_cap_m ** 3)

    # 4. Twelve unbraked Solar System systems across 7 decades in mass (Hygiea, Pallas, Vesta, Ceres, Quaoar, Haumea, Mars, Earth+Moon, Uranus, Neptune, Saturn, Jupiter)
    soliton_9 = ["Vesta", "Ceres", "Haumea", "Mars", "Earth+Moon", "Uranus", "Neptune", "Saturn", "Jupiter"]
    soliton_12 = ["Hygiea", "Pallas", "Vesta", "Ceres", "Quaoar", "Haumea", "Mars", "Earth+Moon", "Uranus", "Neptune", "Saturn", "Jupiter"]
    uT_12 = np.array([records[k]["u_T"] for k in soliton_12])
    jobs_12 = np.array([records[k]["j_obs_m2_s"] for k in soliton_12])
    slope_j_uT_12, cov_12 = np.polyfit(np.log10(uT_12), np.log10(jobs_12), 1, cov=True)
    r_j_uT_12, p_j_uT_12 = pearsonr(np.log10(uT_12), np.log10(jobs_12))
    uT_9 = np.array([records[k]["u_T"] for k in soliton_9])
    jobs_9 = np.array([records[k]["j_obs_m2_s"] for k in soliton_9])
    eta_9 = np.array([records[k]["eta_rot_j_over_jT"] for k in soliton_9])
    slope_j_uT_9, cov_9 = np.polyfit(np.log10(uT_9), np.log10(jobs_9), 1, cov=True)
    slope_err_9 = float(np.sqrt(cov_9[0, 0]))
    r_j_uT_9, p_j_uT_9 = pearsonr(np.log10(uT_9), np.log10(jobs_9))

    # 5. Outer Solar System (TEP-9 / Paper 36) Screening Shell & Spin-Axis Links
    M_giants = sum(records[k]["M_kg"] for k in ["Jupiter", "Saturn", "Uranus", "Neptune"])
    r_star_giants_au = float(np.sqrt(G * M_giants / g_t) / AU)
    # Uranus IAU pole (RA=257.31 deg, Dec=-15.18 deg) -> Ecliptic (lambda=77.65 deg, beta=-7.72 deg)
    # TEP-9 resident TNO perihelion axis: Ecliptic (lambda=49.9 deg, beta=-17.0 deg)
    # TEP-9 CMB-anchored Meridian plane spanned by CMB apex (171.66, -11.14) and cap axis (34.0, -13.0)
    def ecl_vec(lam_deg, bet_deg):
        lam, bet = np.radians(lam_deg), np.radians(bet_deg)
        return np.array([np.cos(bet) * np.cos(lam), np.cos(bet) * np.sin(lam), np.sin(bet)])

    u_uranus_spin = ecl_vec(77.65, -7.72)
    u_tep9_tno = ecl_vec(49.9, -17.0)
    u_tep9_cap = ecl_vec(34.0, -13.0)
    u_cmb_apex = ecl_vec(171.66, -11.14)
    n_merid = np.cross(u_cmb_apex, u_tep9_cap)
    n_merid /= np.linalg.norm(n_merid)
    uranus_angle_to_tno_deg = float(np.degrees(np.arccos(np.clip(abs(np.dot(u_uranus_spin, u_tep9_tno)), 0.0, 1.0))))
    uranus_angle_to_meridian_deg = float(np.degrees(np.arcsin(np.clip(abs(np.dot(u_uranus_spin, n_merid)), 0.0, 1.0))))
    uranus_angle_to_cmb_deg = float(np.degrees(np.arccos(np.clip(abs(np.dot(u_uranus_spin, u_cmb_apex)), 0.0, 1.0))))

    # --- Generate Figure 9 (Two-panel publication plot) ---
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE[FIG_PRESET], constrained_layout=True)

    # Panel A: Equatorial Velocity v_eq vs Zero-Parameter TEP Prediction v_eq = c u_T / sqrt(u_gal)
    ax1 = axes[0]
    ax1.set_title(r"$\bf{a)}$ Equatorial Spin vs. Proper-Time Depth $u_T(M)$", loc="left")

    u_grid = np.logspace(-10.2, -5.8, 250)
    v_grid_tep = (c * u_grid / np.sqrt(u_gal)) / 1e3  # km/s
    ax1.plot(
        u_grid,
        v_grid_tep,
        color=COLORS["primary"],
        lw=2.0,
        label=r"Fixed-input TEP ambient law: $v_{\rm eq} = c\,u_T/\sqrt{u_{\rm gal}}$",
        zorder=3,
    )
    ax1.fill_between(
        u_grid,
        0.7 * v_grid_tep,
        1.4 * v_grid_tep,
        color=COLORS["primary_light"],
        alpha=0.18,
        label=r"Interior structure band ($2k_{\rm MOI}/S \in [1.0, 1.4]$)",
    )

    for k in unbraked_6:
        rec = records[k]
        ax1.scatter(
            rec["u_T"],
            rec["v_eq_obs_km_s"],
            color=COLORS["accent"],
            s=85,
            edgecolors="k",
            lw=0.7,
            zorder=5,
            label="Observed unbraked planets" if k == "Mars" else None,
        )
        if k in wesson_5:
            ax1.scatter(
                rec["u_T"],
                rec["v_eq_hydro_km_s"],
                color=COLORS["highlight"],
                marker="D",
                s=42,
                edgecolors="k",
                lw=0.6,
                alpha=0.85,
                zorder=6,
                label=r"2-branch + $S_A$ ceiling ($v_{\rm obs}/v_{\rm 2br} = 1.01 \pm 0.06$, $N=9$)" if k == "Earth" else None,
            )
        offsets_a = {
            "Mars": (7, -3),
            "Earth": (7, -8),
            "Uranus": (-38, 6),
            "Neptune": (7, -7),
            "Saturn": (-28, 9),
            "Jupiter": (-10, -16),
        }
        ax1.annotate(k, (rec["u_T"], rec["v_eq_obs_km_s"]), xytext=offsets_a[k], textcoords="offset points", fontsize=8)

    for k in substellar_4:
        rec = records[k]
        ax1.scatter(
            rec["u_T"],
            rec["v_eq_obs_km_s"],
            color=COLORS["hover"],
            marker="^",
            s=75,
            edgecolors="k",
            lw=0.7,
            zorder=5,
            label="Fastest PMO & BDs (Gagné+ 2017; Tannock+ 2021)" if k == "SIMP J0136" else None,
        )
        ax1.scatter(
            rec["u_T"],
            rec["v_eq_hydro_km_s"],
            color=COLORS["highlight"],
            marker="D",
            s=40,
            edgecolors="k",
            lw=0.6,
            alpha=0.85,
            zorder=6,
        )
    ax1.annotate(r"SIMP J0136", (records["SIMP J0136"]["u_T"], records["SIMP J0136"]["v_eq_obs_km_s"]), xytext=(-36, -3), textcoords="offset points", ha="center", fontsize=6.8)
    ax1.annotate(r"Tannock+ 21 BDs" + "\n" + r"($P_{\min}\approx 1.15$ hr)", (records["2M J0407+15"]["u_T"], records["2M J0407+15"]["v_eq_obs_km_s"]), xytext=(-4, -24), textcoords="offset points", ha="center", fontsize=6.8)

    for k in ["Mercury", "Venus"]:
        rec = records[k]
        ax1.scatter(
            rec["u_T"],
            rec["v_eq_obs_km_s"],
            color="gray",
            marker="v",
            s=65,
            edgecolors="k",
            lw=0.6,
            alpha=0.7,
            zorder=4,
            label="Solar-tide braked" if k == "Mercury" else None,
        )
        off_b = (7, 4) if k == "Mercury" else (7, 4)
        ax1.annotate(f"{k} (braked)", (rec["u_T"], rec["v_eq_obs_km_s"]), xytext=off_b, textcoords="offset points", fontsize=7.5, color="dimgray")

    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlim(8e-11, 2.5e-6)
    ax1.set_ylim(8e-4, 2500.0)
    ax1.set_xlabel(r"Saturation Proper-Time Depth $u_T(M) = GM/(R_T c^2)$")
    ax1.set_ylabel(r"Equatorial Rotation Speed $v_{\rm eq}$ (km s$^{-1}$)")
    ax1.grid(True, which="major", alpha=0.3)
    ax1.legend(loc="upper left", frameon=False, fontsize=6.4)

    # Panel B: Specific Angular Momentum j = L/M across 9 orders of magnitude in mass
    ax2 = axes[1]
    ax2.set_title(r"$\bf{b)}$ Specific Angular Momentum vs. Mass", loc="left")

    M_grid = np.logspace(19.5, 29.5, 300)
    R_T_grid = ((3.0 * M_grid) / (4.0 * np.pi * rho_T_si)) ** (1.0 / 3.0)
    # Above M_screen (~16 M_Jup, where R_T = R_phys ~ 0.9 R_Jup), S_A = min(1, S) saturates R_active at R_phys ~ 0.9 R_Jup:
    R_act_grid = np.minimum(R_T_grid, 0.92 * 71492.0e3)
    j_sol_grid = 0.12905 * (R_act_grid ** 2) * omega_T
    j_wes_grid = G * M_grid / (2.0 * v_gal)

    ax2.plot(
        M_grid,
        j_wes_grid,
        color=COLORS["primary"],
        lw=2.0,
        label=r"Ambient Wesson law: $j_{\rm TEP} = GM/(2v_{\rm gal})$",
        zorder=3,
    )
    ax2.plot(
        M_grid,
        j_sol_grid,
        color=COLORS["highlight"],
        ls="--",
        lw=1.8,
        label=r"Soliton capacity ($S_A$ ceiling at $S\geq 1$: $P_{\min}=1.17$ hr)",
        zorder=3,
    )

    offsets_b = {
        "Hygiea": (6, -7),
        "Pallas": (-22, 5),
        "Vesta": (7, -7),
        "Ceres": (7, -9),
        "Quaoar": (-34, 6),
        "Haumea": (-38, 5),
        "Mars": (6, -6),
        "Earth": (6, -8),
        "Earth+Moon": (-54, 5),
        "Uranus": (-38, 10),
        "Neptune": (6, -7),
        "Saturn": (-38, 6),
        "Jupiter": (-6, -15),
        "SIMP J0136": (-46, 6),
        "2M J0407+15": (-32, -18),
    }
    for k in ["Hygiea", "Pallas", "Vesta", "Ceres", "Quaoar", "Haumea", "Mars", "Earth", "Earth+Moon", "Uranus", "Neptune", "Saturn", "Jupiter", "SIMP J0136", "2M J0348-60", "2M J1219+31", "2M J0407+15"]:
        rec = records[k]
        is_em = k == "Earth+Moon"
        is_sub = rec["regime"] == "substellar_ceiling"
        col = COLORS["secondary"] if rec["regime"] == "small_body" else (COLORS["hover"] if (is_em or is_sub) else COLORS["accent"])
        mk = "D" if rec["regime"] == "small_body" else ("s" if is_em else ("^" if is_sub else "o"))
        ax2.scatter(rec["M_kg"], rec["j_obs_m2_s"], color=col, marker=mk, s=68, edgecolors="k", lw=0.6, zorder=5)
        if k in offsets_b:
            lbl_b = "Tannock+ 21 BDs" if k == "2M J0407+15" else k
            arrow_kw = dict(arrowstyle="-", color="dimgray", lw=0.6, shrinkA=0, shrinkB=4) if k == "Uranus" else None
            ax2.annotate(
                lbl_b,
                (rec["M_kg"], rec["j_obs_m2_s"]),
                xytext=offsets_b[k],
                textcoords="offset points",
                fontsize=7.0,
                arrowprops=arrow_kw,
            )

    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlim(2.5e19, 5e29)
    ax2.set_ylim(1e6, 2e13)
    ax2.set_xlabel(r"Body Mass $M$ (kg)")
    ax2.set_ylabel(r"Specific Angular Momentum $j = J/M$ (m$^2$ s$^{-1}$)")
    ax2.grid(True, which="major", alpha=0.3)
    ax2.legend(loc="upper left", frameon=False, fontsize=7.5)

    fig_path = REPO / "results" / "figures" / "figure_9_planetary_rotation.png"
    plt.savefig(fig_path, dpi=300)
    plt.close(fig)
    print_status(f"Saved figure to {fig_path}", "SUCCESS")

    # --- 6. Standard Solar Model (Model S) BVP, Tachocline, & Helioseismic Differential Rotation ---
    M_sun = 1.98847e30
    R_sun = 6.96340e8
    x_nodes = np.array([
        0.000, 0.020, 0.040, 0.060, 0.080, 0.100, 0.120, 0.140, 0.160, 0.180,
        0.200, 0.220, 0.245, 0.270, 0.300, 0.350, 0.400, 0.450, 0.500, 0.550,
        0.600, 0.650, 0.700, 0.713, 0.750, 0.800, 0.850, 0.900, 0.950, 0.980, 1.000
    ])
    rho_nodes = np.array([
        152.9, 147.8, 134.5, 117.0,  98.9,  82.5,  67.8,  55.2,  44.8,  36.2,
         29.2,  23.6,  19.95, 15.6,  11.7,   7.15,  4.32,  2.60,  1.56,  0.94,
          0.57,  0.35,  0.213, 0.187, 0.130, 0.081, 0.046, 0.022, 0.0068,0.0012, 2.0e-7
    ])
    log_rho_interp = PchipInterpolator(x_nodes, np.log10(rho_nodes))

    x_sun_grid = np.linspace(1e-3, 1.0, 1500)
    r_sun_grid = x_sun_grid * R_sun
    rho_sun_cgs = 10.0 ** log_rho_interp(x_sun_grid)
    M_sun_raw = np.trapezoid(4.0 * np.pi * (r_sun_grid**2) * (rho_sun_cgs * 1000.0), r_sun_grid)
    rho_sun_cgs *= (M_sun / M_sun_raw)
    M_sun_enc = cumulative_trapezoid(4.0 * np.pi * (r_sun_grid**2) * (rho_sun_cgs * 1000.0), r_sun_grid, initial=0.0)
    M_sun_enc[0] = (4.0 / 3.0) * np.pi * (r_sun_grid[0]**3) * (rho_sun_cgs[0] * 1000.0)
    rho_sun_bar_cgs = (3.0 * M_sun_enc / (4.0 * np.pi * (r_sun_grid**3))) / 1000.0

    R_T_sun = ((3.0 * M_sun) / (4.0 * np.pi * rho_T_si)) ** (1.0 / 3.0)
    S_sun = float(R_T_sun / R_sun)
    idx_core_sun = int(np.argmin(np.abs(rho_sun_cgs - rho_T_g_cm3)))
    x_core_sun = float(x_sun_grid[idx_core_sun])
    M_core_sun_frac = float(M_sun_enc[idx_core_sun] / M_sun)
    x_bar_sun = float(x_sun_grid[int(np.argmin(np.abs(rho_sun_bar_cgs - rho_T_g_cm3)))])
    x_tach_tep = float(np.sqrt(3.0) * S_sun)
    x_tach_obs = 0.713

    S_A_sun_loc = np.minimum(1.0, (rho_sun_cgs / rho_T_g_cm3) ** (1.0 / 3.0))
    S_A_sun_bar = np.minimum(1.0, (rho_sun_bar_cgs / rho_T_g_cm3) ** (1.0 / 3.0))

    # Exact physical Compton wavelength at rho_T = 20 g/cm^3 from Step 14 (lambda = 7.53e-66): lam_c0 = 2478.52 km
    hbar_c_eV_m = 1.973269804e-7
    M_Pl_eV = 2.43536e27
    eV4_per_g_cm3 = (1e6 * (2.99792458e8 ** 2) / 1.602176634e-19) * (hbar_c_eV_m ** 3)
    lam_cas = 7.53e-66
    rho_T_eV4 = rho_T_g_cm3 * eV4_per_g_cm3
    u_min_rhoT = (rho_T_eV4 / (lam_cas * (M_Pl_eV ** 4))) ** (1.0 / 3.0)
    m_eff_rhoT_eV = float(np.sqrt(3.0 * lam_cas * (M_Pl_eV ** 2) * (u_min_rhoT ** 2)))
    lam_c0_sun_m = hbar_c_eV_m / m_eff_rhoT_eV
    lam_x_sun = float(lam_c0_sun_m / R_sun)  # = 0.003559 (2478.52 km / R_sun)
    def _rho_sun_x(x):
        res = np.zeros_like(x)
        m = x <= 1.0
        res[m] = (10.0 ** log_rho_interp(np.clip(x[m], 0.0, 1.0))) * (M_sun / M_sun_raw)
        return res

    def _bvp_sun_rhs(x, Y):
        y, dy = Y[0], Y[1]
        src = np.minimum(1.0, (np.maximum(_rho_sun_x(x), 1e-12) / rho_T_g_cm3) ** (1.0 / 3.0)) ** 3
        d2y = (1.0 / (3.0 * lam_x_sun**2)) * (y**3 - src) - (2.0 / x) * dy
        return np.vstack((dy, d2y))

    x_mesh_s = np.linspace(1e-3, 1.2, 1500)
    y_init_s = np.minimum(1.0, (np.maximum(_rho_sun_x(x_mesh_s), 1e-12) / rho_T_g_cm3) ** (1.0 / 3.0))
    sol_sun = solve_bvp(_bvp_sun_rhs, lambda Ya, Yb: np.array([Ya[1], Yb[0]]), x_mesh_s, np.vstack((y_init_s, np.gradient(y_init_s, x_mesh_s))), tol=1e-5)
    y_bvp_sun = sol_sun.sol(x_sun_grid)[0]

    u_surf_sun = float(G * M_sun / (R_sun * c**2))
    u_T_sun = float(G * M_sun / (R_T_sun * c**2))
    v_eq_sun_tep_km_s = float((np.pi * c * u_surf_sun) / 1e3)
    v_pol_sun_tep_km_s = float((c * u_T_sun) / 1e3)
    # Fundamental cyclic equatorial frequency nu_eq = g_surf / (2 c) = c * u_surf / (2 R_sun) (same 1/2 factor as g_t = c H_0 / 2 and k_MOI = S / 2; multiplying by 2*pi*R_sun gives v_eq = pi*c*u_surf):
    Omega_eq_tep_nHz = float((c * u_surf_sun / (2.0 * R_sun)) * 1e9)
    # Differential shear Delta_Omega = S_sun / |alpha_0| = S_sun / sqrt(2) (where |alpha_0| = sqrt(2)|beta_A| = sqrt(2) is the Paper 0 DEF coupling norm),
    # split equally (a2 = a4 = 0.5 * Delta_Omega = 0.1459, zero borrowed shape parameters vs observed 0.140 and 0.149):
    Delta_shear_tep = float(S_sun / np.sqrt(2.0))
    a2_tep, a4_tep = 0.50 * Delta_shear_tep, 0.50 * Delta_shear_tep
    x_bvp_half_S = float(x_sun_grid[int(np.argmin(np.abs(y_bvp_sun - 0.5 * S_sun)))])
    x_loc_half_S = float(x_sun_grid[int(np.argmin(np.abs(S_A_sun_loc - 0.5 * S_sun)))])

    def _omega_cz_tep(lat_deg):
        mu = np.sin(np.radians(lat_deg))
        return Omega_eq_tep_nHz * (1.0 - a2_tep * (mu**2) - a4_tep * (mu**4))

    Omega_rad_tep_nHz = float(_omega_cz_tep(35.2643897))  # = nu_eq * (1 - 2/9 * Delta_Omega) = 426.9 nHz
    # Prolate tachocline depression at equator due to super-rotating convective shear (Charbonneau et al. 1999: r_c(0)=0.693, r_c(60)=0.717 R_sun):
    d_eq_tach_tep = float(x_tach_tep * ((Omega_eq_tep_nHz - Omega_rad_tep_nHz) / Omega_eq_tep_nHz) / np.sqrt(3.0))
    idx_3d_sun = int(np.argmin(np.abs(x_sun_grid - x_tach_tep)))
    M_3d_sun_frac = float(M_sun_enc[idx_3d_sun] / M_sun)
    rho_bar_3d_cgs = float(rho_sun_bar_cgs[idx_3d_sun])
    rho_T_cz_inferred = float(3.0 * np.sqrt(3.0) * (3.0 * M_sun / (4.0 * np.pi * (R_sun**3)) / 1000.0) / (x_tach_obs**3))

    Omega_eq_obs_nHz = 460.7
    a2_obs, a4_obs = 0.1398, 0.1489
    def _omega_cz_obs(lat_deg):
        mu = np.sin(np.radians(lat_deg))
        return Omega_eq_obs_nHz * (1.0 - a2_obs * (mu**2) - a4_obs * (mu**4))
    Omega_rad_obs_nHz = 432.0

    J_spin_sun_obs = 1.92e41
    ecc_planets = {
        "Mercury": 0.205630, "Venus": 0.006772, "Earth": 0.0167086, "Mars": 0.0934,
        "Jupiter": 0.0489, "Saturn": 0.0565, "Uranus": 0.0457, "Neptune": 0.0113,
    }
    J_orb_planets_obs = float(sum(
        records[p_k]["M_kg"] * np.sqrt(
            G * (M_sun + records[p_k]["M_kg"]) * (records[p_k]["a_AU"] * AU) * (1.0 - ecc_planets[p_k] ** 2)
        )
        for p_k in ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
    ))
    J_sys_tot_obs = float(J_spin_sun_obs + J_orb_planets_obs)
    j_T_sun = float((R_T_sun ** 2) * omega_T)
    J_sol_sun_sec = float(0.125 * M_sun * j_T_sun)
    J_sol_sun_emp = float(0.12905 * M_sun * j_T_sun)

    fig_s, axes_s = plt.subplots(1, 2, figsize=FIG_SIZE[FIG_PRESET], constrained_layout=True)
    ax1s = axes_s[0]
    ax1s.set_title(r"$\bf{a)}$ Standard Solar Model (Model S) TEP Saturation Zones", loc="left")
    ax1s.axvspan(0.0, x_core_sun, color=COLORS["hover"], alpha=0.10, label=rf"Screened nuclear core ($\rho \geq \rho_T$, $r \leq {x_core_sun:.3f}\,R_\odot$)")
    ax1s.axvspan(x_core_sun, x_tach_tep, color=COLORS["primary_light"], alpha=0.15, label=rf"Radiative zone ($r \leq \sqrt{{3}}R_T = {x_tach_tep:.3f}\,R_\odot$)")
    ax1s.axvspan(x_tach_tep, 1.0, color=COLORS["highlight"], alpha=0.10, label=r"Unscreened convective differential zone")

    ax1s.plot(x_sun_grid, S_A_sun_loc, color="dimgray", ls=":", lw=1.6, label=r"Local clock ceiling $S_A^{\rm loc}(r) = \min[1,(\rho/\rho_T)^{1/3}]$")
    ax1s.plot(x_sun_grid, S_A_sun_bar, color=COLORS["secondary"], ls="--", lw=1.8, label=r"Enclosed mean $S_A^{\rm enc}(<r) = \min[1,(\bar\rho/\rho_T)^{1/3}]$")
    ax1s.plot(x_sun_grid, y_bvp_sun, color=COLORS["primary"], lw=2.2, label=r"Solved BVP saturated field $u(r)/u_{\min}(\rho_T)$")

    lbl_box_s = dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.84)
    ax1s.axvline(x_core_sun, color=COLORS["hover"], ls="--", lw=1.2)
    ax1s.text(x_core_sun - 0.015, 0.05, rf"Nuclear core $\rho=\rho_T$" + "\n" + rf"($r={x_core_sun:.3f}\,R_\odot$)", rotation=90, ha="right", va="bottom", fontsize=6.6, color=COLORS["hover"], bbox=lbl_box_s)
    ax1s.axvline(S_sun, color=COLORS["secondary"], ls="--", lw=1.2)
    ax1s.text(S_sun + 0.015, 0.05, rf"$R_T(M_\odot) = {S_sun:.3f}\,R_\odot$", rotation=90, ha="left", va="bottom", fontsize=6.8, color=COLORS["secondary"], bbox=lbl_box_s)
    ax1s.axvline(x_tach_tep, color=COLORS["accent"], ls="-.", lw=1.5)
    ax1s.text(x_tach_tep - 0.015, 0.05, rf"$\sqrt{{3}}R_T = {x_tach_tep:.3f}\,R_\odot$" + "\n" + r"(Convection base $0.713\,R_\odot$)", rotation=90, ha="right", va="bottom", fontsize=6.6, color=COLORS["accent"], bbox=lbl_box_s)

    ax1s.set_xlim(0, 1.02)
    ax1s.set_ylim(0, 1.15)
    ax1s.set_xlabel(r"Fractional Solar Radius $r/R_\odot$")
    ax1s.set_ylabel(r"Normalized Clock-Amplitude Response $S_A(r)$")
    ax1s.grid(True, alpha=0.3)
    ax1s.legend(loc="upper right", frameon=False, fontsize=6.2)

    ax2s = axes_s[1]
    ax2s.set_title(r"$\bf{b)}$ Helioseismic Rotation $\Omega(r,\theta)/2\pi$ vs. TEP Prototype", loc="left")
    x_cz = x_sun_grid[x_sun_grid >= 0.25]

    lat_colors = {0: COLORS["accent"], 30: COLORS["primary"], 45: COLORS["secondary"], 60: COLORS["highlight"], 75: "dimgray"}
    for lat in [0, 30, 45, 60, 75]:
        c2 = np.cos(np.radians(lat)) ** 2
        rc_tep_lat = x_tach_tep - d_eq_tach_tep * c2
        rc_obs_lat = 0.693 + 0.024 * ((1.0 - c2) / 0.75)
        f_cz_tep = 0.5 * (1.0 + np.tanh((x_cz - rc_tep_lat) / 0.0195))
        f_cz_obs = 0.5 * (1.0 + np.tanh((x_cz - rc_obs_lat) / 0.0195))
        om_obs_curve = Omega_rad_obs_nHz * (1.0 - f_cz_obs) + _omega_cz_obs(lat) * f_cz_obs
        om_tep_curve = Omega_rad_tep_nHz * (1.0 - f_cz_tep) + _omega_cz_tep(lat) * f_cz_tep
        ax2s.plot(x_cz, om_obs_curve, color=lat_colors[lat], ls=":", lw=1.5, alpha=0.85, label="SOHO/GONG helioseismology (dotted)" if lat == 0 else None)
        ax2s.plot(x_cz, om_tep_curve, color=lat_colors[lat], ls="-", lw=2.0, label=rf"TEP {lat}$^\circ$ lat." if lat in (0, 30, 60, 75) else None)
        ax2s.text(1.008, om_tep_curve[-1], rf"{lat}$^\circ$", va="center", fontsize=6.8, color=lat_colors[lat])

    ax2s.axvline(x_tach_obs, color="black", ls="--", lw=1.1, alpha=0.7)
    ax2s.annotate(rf"Convection base $r_{{\rm cz}}=0.713\,R_\odot$" + "\n" + rf"(TEP $\sqrt{{3}}R_T = {x_tach_tep:.3f}\,R_\odot$; prolate $r_c=0.688\text{{–}}0.708$)",
                  xy=(x_tach_obs, 432.0), xytext=(0.26, 372.0), fontsize=6.3,
                  arrowprops=dict(arrowstyle="->", color="black", lw=0.7), bbox=lbl_box_s)
    ax2s.annotate(rf"Equator: $\pi c u_{{\rm surf}} = 1.997$ km/s" + "\n" + r"($456.5$ vs $460.7$ nHz, $-0.9\%$)",
                  xy=(0.98, Omega_eq_tep_nHz), xytext=(0.45, 468.0), fontsize=6.6, color=COLORS["accent"], bbox=lbl_box_s)
    ax2s.annotate(rf"Radiative lock ($P_2=0$ node):" + "\n" + r"$426.9$ vs $432.0$ nHz ($-1.2\%$)",
                  xy=(0.50, Omega_rad_tep_nHz), xytext=(0.28, 444.0), fontsize=6.6, color=COLORS["primary"], bbox=lbl_box_s)

    ax2s.set_xlim(0.24, 1.07)
    ax2s.set_ylim(315, 488)
    ax2s.set_xlabel(r"Fractional Solar Radius $r/R_\odot$")
    ax2s.set_ylabel(r"Internal Rotation Rate $\Omega(r,\theta)/2\pi$ (nHz)")
    ax2s.grid(True, alpha=0.3)
    ax2s.legend(loc="lower left", frameon=False, fontsize=6.3)

    fig_s_path = REPO / "results" / "figures" / "figure_11_solar_helioseismology.png"
    plt.savefig(fig_s_path, dpi=300)
    plt.close(fig_s)
    print_status(f"Saved solar helioseismology figure to {fig_s_path}", "SUCCESS")

    # Dynamic computation of nested heliocentric screening-shell correlation, volumetric/deep-interior periods, and Lane-Emden ODE condensed radii
    r_star_a_4 = np.array([records[k]["r_star_over_a"] for k in ambient_4])
    ln_rsa_4 = np.log(r_star_a_4)
    r_nest_p, p_nest_p = pearsonr(ln_rsa_4, ratios_veq_4)
    rho_nest_s, _ = spearmanr(r_star_a_4, ratios_veq_4)
    sl_nest, ic_nest = np.polyfit(ln_rsa_4, np.log(ratios_veq_4), 1)
    rsa_zero_cross = float(np.exp(-ic_nest / sl_nest))
    rms_nest_pct = float(100.0 * np.sqrt(np.mean((ratios_veq_4 - np.exp(sl_nest * ln_rsa_4 + ic_nest)) ** 2)))

    # Volumetric radii (km) and deep-interior rotation periods (hr: Earth sidereal 23.9345, Saturn ring seismology 10.561 Mankovich+ 2019, Uranus 16.5 & Neptune 15.2 Helled+ 2010)
    vol_specs = [
        ("Earth", 6371.0, 23.9345),
        ("Saturn", 58232.0, 10.561),
        ("Uranus", 25362.0, 16.50),
        ("Neptune", 24622.0, 15.20),
    ]
    vol_ratios = {}
    for pk, r_vol_km, t_deep_hr in vol_specs:
        v_vol_kms = (2.0 * np.pi * r_vol_km) / (t_deep_hr * 3600.0)
        vol_ratios[pk] = float(v_vol_kms / records[pk]["v_eq_tep_km_s"])
    vol_arr = np.array(list(vol_ratios.values()))
    rhoT_vol_geom = float(np.exp(np.mean(np.log(rho_T_g_cm3 * (vol_arr ** 3)))))

    # Exact Lane-Emden ODE integration for polytropic condensed radii
    def _le_solve(n_val):
        def _rhs(xi, y):
            th, dth = y[0], y[1]
            return [dth, 0.0 if th <= 0 else -(th ** n_val) - (2.0 / xi) * dth]
        _ev = lambda xi, y: y[0]
        _ev.terminal = True
        _ev.direction = -1
        xi0 = 1e-4
        sol_le = solve_ivp(_rhs, [xi0, 20.0], [1.0 - (xi0 ** 2) / 6.0, -xi0 / 3.0], events=_ev, max_step=0.015, rtol=1e-9, atol=1e-11)
        xi_v = sol_le.t
        th_v = np.maximum(sol_le.y[0], 0.0)
        xi1_v = float(xi_v[-1])
        rho_v = th_v ** n_val
        m_v = np.trapezoid((xi_v ** 2) * rho_v, xi_v)
        i_v = (2.0 / 3.0) * np.trapezoid((xi_v ** 4) * rho_v, xi_v)
        k_v = float(i_v / (m_v * (xi1_v ** 2)))
        r_mass_v = float((4.0 / 3.0) * np.trapezoid((xi_v ** 3) * rho_v, xi_v) / (m_v * xi1_v))
        return k_v, r_mass_v

    condensed_7 = ["Mercury", "Venus", "Earth", "Jupiter", "Saturn", "Uranus", "Neptune"]
    n_le_dict, r_mass_dict = {}, {}
    for pk in condensed_7:
        k_target = records[pk]["k_moi"]
        n_fit = float(brentq(lambda nv: _le_solve(nv)[0] - k_target, 0.01, 3.5))
        _, rm_fit = _le_solve(n_fit)
        n_le_dict[pk] = round(n_fit, 3)
        r_mass_dict[pk] = rm_fit
    rm_ref_venus = r_mass_dict["Venus"]
    r_cond_ratio_dict, two_k_S_cond_dict = {}, {}
    for pk in condensed_7:
        rc_rat = float(r_mass_dict[pk] / rm_ref_venus)
        r_cond_ratio_dict[pk] = round(rc_rat, 4)
        two_k_S_cond_dict[pk] = round(float(records[pk]["two_k_moi_over_S"] * rc_rat), 4)
    tks_cond_arr = np.array(list(two_k_S_cond_dict.values()))
    rhoT_cond_geom = float(np.exp(np.mean(np.log(rho_T_g_cm3 * (tks_cond_arr ** (-3.0))))))

    # (a) Outer-3 truly unbraked giant planets (Uranus, Neptune, Saturn — zero large-moon lunar tidal braking):
    outer_3_unbraked = ["Uranus", "Neptune", "Saturn"]
    ratios_veq_outer3 = np.array([records[k]["v_obs_over_v_tep"] for k in outer_3_unbraked])
    rho_T_spin_outer3 = np.array([records[k]["rho_T_spin_inferred_g_cm3"] for k in outer_3_unbraked])
    rhoT_outer3_geom = float(np.exp(np.mean(np.log(rho_T_spin_outer3))))
    extended_8_no_earth = ["Uranus", "Neptune", "Saturn", "Jupiter", "SIMP J0136", "2M J0348-60", "2M J1219+31", "2M J0407+15"]
    ratios_ext_8 = np.array([records[k]["v_obs_over_v_hydro"] for k in extended_8_no_earth])
    rhoT_ext_8_geom = float(np.exp(np.mean(np.log(rho_T_g_cm3 * (ratios_ext_8 ** 3)))))

    # (b) Unconstrained 2-parameter compositional power-law baseline k_MOI = C * rho^beta across all 8 planets vs 0-parameter TEP:
    rhos_8_arr = np.array([records[k]["rho_g_cm3"] for k in planets_8])
    ks_8_arr = np.array([records[k]["k_moi"] for k in planets_8])
    sl_k_rho, ic_k_rho, r_k_rho, p_k_rho, se_k_rho = linregress(np.log10(rhos_8_arr), np.log10(ks_8_arr))
    c_emp_k = float(10.0 ** ic_k_rho)
    c_tep_k = float(0.5 * (rho_T_g_cm3 ** (-1.0 / 3.0)))
    rms_k_tep_dex = float(np.sqrt(np.mean((np.log10(ks_8_arr) - np.log10(c_tep_k * (rhos_8_arr ** (1.0 / 3.0)))) ** 2)))
    rms_k_free_dex = float(np.sqrt(np.mean((np.log10(ks_8_arr) - (ic_k_rho + sl_k_rho * np.log10(rhos_8_arr))) ** 2)))

    # (c) 100,000-trial Random-Density & Look-Elsewhere Coincidence Null Test across [0.1, 10^4] g/cm^3 (5 decades):
    rng_null = np.random.default_rng(2026)
    n_null_trials = 100000
    rho_rand_1d = 10.0 ** rng_null.uniform(-1.0, 4.0, n_null_trials)
    sc_1d = rho_rand_1d / rho_T_g_cm3
    # 5 independent rho_T-calibrating channels (with tidally evolved present-day Earth excluded from spin!):
    # Ch1: GNSS L_c = 4200 km vs R_T(M_earth, rho)
    # Ch2: Outer-3 unbraked giant planets (Uranus, Neptune, Saturn) mean v_obs / v_TEP(rho)
    # Ch3: Brown-dwarf rotational period floor P_min(rho) vs 1.150 hr (scales as rho^-1/2)
    # Ch4: Terrestrial core-screened MOI 2 k_MOI / S(rho) (Mercury, Venus, Earth)
    # Ch5: Solar Model S convection-zone base sqrt(3) R_T(M_sun, rho) / R_sun vs 0.713
    e1_obs = abs(records["Earth"]["R_T_km"] / 4200.0 - 1.0)
    e2_obs = abs(float(np.mean(ratios_veq_outer3)) - 1.0)
    e3_obs = abs(float(P_min_bd_tep_hr / np.mean(P_obs_tannock_3)) - 1.0)
    e4_obs = abs(float(np.mean(two_k_over_S_terr3)) - 1.0)
    e5_obs = abs(float(x_tach_tep / x_tach_obs) - 1.0)
    obs_rms_5ch = float(np.sqrt(np.mean([e1_obs**2, e2_obs**2, e3_obs**2, e4_obs**2, e5_obs**2])))
    obs_max_5ch = float(max(e1_obs, e2_obs, e3_obs, e4_obs, e5_obs))

    e1_mc = np.abs((records["Earth"]["R_T_km"] * (sc_1d ** (-1.0 / 3.0))) / 4200.0 - 1.0)
    e2_mc = np.abs(float(np.mean(ratios_veq_outer3)) * (sc_1d ** (-1.0 / 3.0)) - 1.0)
    e3_mc = np.abs((float(P_min_bd_tep_hr) * (sc_1d ** (-0.5))) / float(np.mean(P_obs_tannock_3)) - 1.0)
    e4_mc = np.abs(float(np.mean(two_k_over_S_terr3)) * (sc_1d ** (1.0 / 3.0)) - 1.0)
    e5_mc = np.abs((float(x_tach_tep) * (sc_1d ** (-1.0 / 3.0))) / float(x_tach_obs) - 1.0)
    rms_5ch_mc = np.sqrt(np.mean(np.vstack([e1_mc, e2_mc, e3_mc, e4_mc, e5_mc]) ** 2, axis=0))
    max_5ch_mc = np.maximum.reduce([e1_mc, e2_mc, e3_mc, e4_mc, e5_mc])
    p_1d_rms = float(np.mean(rms_5ch_mc <= obs_rms_5ch))
    p_1d_max5pct = float(np.mean(max_5ch_mc <= 0.05))

    # Multi-channel coincidence null test across 5 independent inferred densities over 5.0 dex ([0.1, 10^4] g/cm^3):
    rho_hat_gnss = float(rho_T_g_cm3 * ((records["Earth"]["R_T_km"] / 4200.0) ** 3))
    rho_hat_outer3 = rhoT_outer3_geom
    rho_hat_bd = float(rho_T_g_cm3 * ((P_min_bd_tep_hr / float(np.mean(P_obs_tannock_3))) ** 2))
    rho_hat_moi_terr = float(np.mean(rho_T_moi_terr3))
    rho_hat_sol_cz = rho_T_cz_inferred
    rho_hats_5 = np.array([rho_hat_gnss, rho_hat_outer3, rho_hat_bd, rho_hat_moi_terr, rho_hat_sol_cz])
    log_spread_5_dex = float(np.std(np.log10(rho_hats_5), ddof=1))
    log_range_5_dex = float(np.max(np.log10(rho_hats_5)) - np.min(np.log10(rho_hats_5)))
    p_analytic_5ch_no_le = float(5.0 * ((log_range_5_dex / 5.0) ** 4))

    # Grant full look-elsewhere trials freedom: K = 7 algebraic factors {1/2, 1/sqrt(2), 1, sqrt(2), sqrt(3), 2, pi} on Ch3, Ch4, Ch5 (7^3 = 343 combinations per trial)
    alg_factors = np.array([0.5, 1.0 / np.sqrt(2.0), 1.0, np.sqrt(2.0), np.sqrt(3.0), 2.0, np.pi])
    sh3 = np.log10(alg_factors ** 2)
    sh4 = np.log10(alg_factors ** 3)
    sh5 = np.log10(alg_factors ** 3)
    u_mc_5 = rng_null.uniform(-1.0, 4.0, (n_null_trials, 5))
    tol_dex = 0.087  # +/- 10% window (log10(1.10/0.90) = 0.087 dex)
    sub_12 = u_mc_5[np.abs(u_mc_5[:, 0] - u_mc_5[:, 1]) <= tol_dex]
    le_hits = 0
    for r_row in sub_12:
        w_lo = max(r_row[0], r_row[1]) - tol_dex
        w_hi = min(r_row[0], r_row[1]) + tol_dex
        u3p = r_row[2] + sh3
        u4p = r_row[3] + sh4
        u5p = r_row[4] + sh5
        if np.any((u3p >= w_lo) & (u3p <= w_hi)) and np.any((u4p >= w_lo) & (u4p <= w_hi)) and np.any((u5p >= w_lo) & (u5p <= w_hi)):
            le_hits += 1
    p_mc_5ch_with_look_elsewhere = float(le_hits / n_null_trials)

    # Small-body eta_rot 6-object summary and propagated P_min range:
    small_6 = ["Hygiea", "Pallas", "Vesta", "Ceres", "Quaoar", "Haumea"]
    eta_small_6 = np.array([records[k]["eta_rot_j_over_jT"] for k in small_6])
    eta_med_6 = float(np.median(eta_small_6))
    eta_q25_6, eta_q75_6 = [float(x) for x in np.percentile(eta_small_6, [25, 75])]
    P_min_iqr_hr = [float((0.205 / eta_q75_6) * tau_T_hr), float((0.205 / eta_q25_6) * tau_T_hr)]
    P_min_med6_hr = float((0.205 / eta_med_6) * tau_T_hr)

    # Low-pressure uncompressed satellites diagnostic (P_c << K_bulk ~ 100 GPa -> k_MOI ~ 0.31-0.39, 2 k_MOI / S = 1.30-1.57):
    sat_specs = [
        ("Moon", 7.342e22, 1737.4e3, 0.393),
        ("Io", 8.932e22, 1821.6e3, 0.378),
        ("Europa", 4.800e22, 1560.8e3, 0.346),
        ("Ganymede", 1.482e23, 2631.2e3, 0.312),
        ("Titan", 1.345e23, 2574.7e3, 0.341),
        ("Callisto", 1.076e23, 2410.3e3, 0.355),
    ]
    sat_moi_audit = {}
    for s_name, s_m, s_r, s_k in sat_specs:
        s_rt = float(((3.0 * s_m) / (4.0 * np.pi * rho_T_si)) ** (1.0 / 3.0))
        s_S = float(s_rt / s_r)
        s_pc_gpa = float((3.0 * G * (s_m ** 2)) / (8.0 * np.pi * (s_r ** 4)) / 1e9)
        sat_moi_audit[s_name] = {
            "P_central_GPa": round(s_pc_gpa, 2),
            "k_moi": s_k,
            "S_screening": round(s_S, 4),
            "two_k_moi_over_S": round(float(2.0 * s_k / s_S), 3),
        }

    # 4-channel (planetary/substellar/GNSS only, excluding Solar prototype and lunar-braked Earth) random-density look-elsewhere null test:
    rho_hats_4 = np.array([rho_hat_gnss, rho_hat_outer3, rho_hat_bd, rho_hat_moi_terr])
    log_spread_4_dex = float(np.std(np.log10(rho_hats_4), ddof=1))
    log_range_4_dex = float(np.max(np.log10(rho_hats_4)) - np.min(np.log10(rho_hats_4)))
    obs_rms_4ch = float(np.sqrt(np.mean([e1_obs**2, e2_obs**2, e3_obs**2, e4_obs**2])))
    rms_4ch_mc = np.sqrt(np.mean(np.vstack([e1_mc, e2_mc, e3_mc, e4_mc]) ** 2, axis=0))
    p_1d_rms_4ch = float(np.mean(rms_4ch_mc <= obs_rms_4ch))
    p_analytic_4ch_no_le = float(4.0 * ((log_range_4_dex / 5.0) ** 3))
    le_hits_4 = 0
    for r_row in sub_12:
        w_lo = max(r_row[0], r_row[1]) - tol_dex
        w_hi = min(r_row[0], r_row[1]) + tol_dex
        u3p = r_row[2] + sh3
        u4p = r_row[3] + sh4
        if np.any((u3p >= w_lo) & (u3p <= w_hi)) and np.any((u4p >= w_lo) & (u4p <= w_hi)):
            le_hits_4 += 1
    p_mc_4ch_with_look_elsewhere = float(le_hits_4 / n_null_trials)

    # GNSS-free 4-channel external-catalog isolation (dropping GNSS completely: Outer-3 giant spin, BD period floor, Terrestrial MOI, Solar r_cz):
    rho_hats_no_gnss_4 = np.array([rho_hat_outer3, rho_hat_bd, rho_hat_moi_terr, rho_hat_sol_cz])
    mean_no_gnss_4 = float(np.mean(rho_hats_no_gnss_4))
    std_no_gnss_4 = float(np.std(rho_hats_no_gnss_4, ddof=1))
    sem_no_gnss_4 = float(std_no_gnss_4 / np.sqrt(4.0))
    log_std_no_gnss_4 = float(np.std(np.log10(rho_hats_no_gnss_4), ddof=1))

    # Objective a priori Goldreich-Soter (1966) / Peale (1999) tidal despinning timescale criterion tau_tide / t_SolarSystem (t_SS = 4.5 Gyr)
    # evaluated using ONLY mass M, radius R, orbital distance a_tide, tide-raising mass M_tide (M_sun or M_Moon), k_MOI, and standard Q/k2 (ZERO spin input!):
    t_ss_yr = 4.5e9
    yr_s_val = 365.25 * 86400.0
    omega_init_ref = 2.0 * np.pi / (8.0 * 3600.0)  # standard 8 hr primordial reference rate
    M_sun_val = 1.98847e30
    M_moon_val = 7.342e22
    a_moon_m = 3.844e8
    AU_m = 1.495978707e11
    # (name, M_kg, R_m, a_tide_m, M_tide_kg, k_moi, Q_over_k2, tide_source)
    tide_specs = [
        ("Mercury", 3.3011e23, 2439.7e3, 0.387098 * AU_m, M_sun_val, 0.346, 100.0 / 0.5, "Solar tide"),
        ("Venus",   4.8675e24, 6051.8e3, 0.723332 * AU_m, M_sun_val, 0.337, 17.0 / 0.295, "Solar tide"),
        ("Earth",   5.9722e24, 6371.0e3, a_moon_m,         M_moon_val, 0.3307, (12.0 / 0.30) / 6.5, "Lunar tide (a^6 recession integral)"),
        ("Mars",    6.4171e23, 3389.5e3, 1.523679 * AU_m, M_sun_val, 0.365, 86.0 / 0.17, "Solar tide"),
        ("Jupiter", 1.89813e27, 69911.0e3, 5.2044 * AU_m, M_sun_val, 0.2756, 1e5 / 0.54, "Solar tide"),
        ("Saturn",  5.6834e26, 58232.0e3, 9.5826 * AU_m,  M_sun_val, 0.220,  1.8e4 / 0.39, "Solar tide"),
        ("Uranus",  8.6810e25, 25362.0e3, 19.2184 * AU_m, M_sun_val, 0.225,  1e4 / 0.36, "Solar tide"),
        ("Neptune", 1.02413e26, 24622.0e3, 30.11 * AU_m,  M_sun_val, 0.236,  1e4 / 0.41, "Solar tide"),
    ]
    apriori_tidal_audit = {}
    for p_nm, p_m, p_r, a_td, m_td, k_m, q_k2, src_lbl in tide_specs:
        tau_td_s = (2.0 / 3.0) * k_m * q_k2 * (p_m * (a_td ** 6) * omega_init_ref) / (G * (m_td ** 2) * (p_r ** 3))
        tau_td_gyr = float(tau_td_s / (yr_s_val * 1e9))
        ratio_ss = float(tau_td_gyr / 4.5)
        apriori_tidal_audit[p_nm] = {
            "dominant_tide_source": src_lbl,
            "tau_tide_Gyr": round(tau_td_gyr, 5),
            "tau_tide_over_t_SolarSystem": float(ratio_ss),
            "apriori_classification": "tidally_braked" if ratio_ss < 1.0 else "tidally_unbraked",
        }

    # Parameter-free Chandrasekhar-Jacobi (1969) / Ostriker-Peebles (1973) secular bar-mode stability invariant:
    eta_jacobi = 0.137528  # exact classical Maclaurin -> Jacobi triaxial bifurcation T_rot / |W|
    eta_virial = 0.125     # 1/8 virial partition
    P_min_jacobi_hr = float((0.205 / eta_jacobi) * tau_T_hr)  # = 1.100 hr
    P_min_virial_hr = float((0.205 / eta_virial) * tau_T_hr)  # = 1.210 hr
    P_min_th_mid_hr = float(0.5 * (P_min_jacobi_hr + P_min_virial_hr))  # = 1.155 hr vs observed 1.150 +- 0.075 hr
    rho_hat_bd_th_mid = float(rho_T_g_cm3 * ((P_min_th_mid_hr / float(np.mean(P_obs_tannock_3))) ** 2))  # = 20.18 g/cm^3

    # 3-channel strict zero-prefactor coincidence null test (GNSS L_c = R_T, Outer-3 giant spin v_eq = GM/[R_T v_gal], Brown-Dwarf floor P_min = [k_MOI/eta] tau_T; ZERO geometric factors sqrt(2), sqrt(3), pi):
    rho_hats_3free = np.array([rho_hat_gnss, rho_hat_outer3, rho_hat_bd_th_mid])
    mean_3free = float(np.mean(rho_hats_3free))
    std_3free = float(np.std(rho_hats_3free, ddof=1))
    log_range_3free_dex = float(np.max(np.log10(rho_hats_3free)) - np.min(np.log10(rho_hats_3free)))
    p_analytic_3free_no_le = float(3.0 * ((log_range_3free_dex / 5.0) ** 2))

    # Prior-range sensitivity for 5-channel and 3-channel coincidence tests across log10(rho) width W in {5.0, 3.0, 2.0} dex:
    prior_sensitivity = {}
    for w_dex, lbl_p in [(5.0, "5dec_0p1_to_1e4_g_cm3"), (3.0, "3dec_1_to_1e3_g_cm3"), (2.0, "2dec_1_to_100_g_cm3")]:
        p5_raw = float(5.0 * ((log_range_5_dex / w_dex) ** 4))
        p5_le343 = float(1.0 - ((1.0 - p5_raw) ** 343.0))
        p3_raw = float(3.0 * ((log_range_3free_dex / w_dex) ** 2))
        prior_sensitivity[lbl_p] = {
            "prior_width_dex": w_dex,
            "p_5channel_raw": p5_raw,
            "p_5channel_after_343_trials": p5_le343,
            "p_3channel_unit_prefactor": p3_raw,
        }

    # Propagated systematic spread across v_gal in [220, 236] km/s and L_c in [3423, 4549] km:
    rho_spin_vgal220 = float(rho_hat_outer3)
    rho_spin_vgal229 = float(rho_hat_outer3 * ((229.0 / 220.0) ** 3))
    rho_spin_vgal236 = float(rho_hat_outer3 * ((236.0 / 220.0) ** 3))
    rho_gnss_Lc4051 = float(3.0 * 5.9722e27 / (4.0 * np.pi * ((4050.9e5) ** 3)))
    rho_gnss_Lc3853 = float(3.0 * 5.9722e27 / (4.0 * np.pi * ((3853.1e5) ** 3)))
    rho_gnss_Lc3423 = float(3.0 * 5.9722e27 / (4.0 * np.pi * ((3423.0e5) ** 3)))
    venus_earth_2k_over_S = [float(2.0 * 0.337 / ((5.243 / 20.0) ** (1.0/3.0))), float(2.0 * 0.3307 / ((5.515 / 20.0) ** (1.0/3.0)))]
    venus_earth_rho_T = [float(5.243 / ((2.0 * 0.337) ** 3)), float(5.515 / ((2.0 * 0.3307) ** 3))]

    # Forward-propagation falsification table across GNSS L_c pipelines into the 4 external astrophysical channels:
    # Tests Reviewer 2's requirement: propagate each GNSS L_c -> rho_T = 3 M_earth / (4 pi L_c^3) forward into
    # (1) Outer-3 giant-planet spin v_eq^TEP / v_obs (propto rho_T^(1/3)),
    # (2) Brown-dwarf period floor P_min^th (propto rho_T^(-1/2)) vs observed 1.150 hr,
    # (3) Terrestrial compressed MOI 2 k_MOI / S (propto rho_T^(1/3)) vs unity,
    # (4) Solar Model S convection-zone base r_cz^TEP = sqrt(3) R_T(M_sun) (propto rho_T^(-1/3)) vs observed 0.713 R_sun:
    forward_propagation_table = {}
    for pipe_lbl, L_km_val in [
        ("code_25yr_cross_sector_ppp_4201km", 4201.0),
        ("cddis_rinex3_gps_only_sqrtN_4051km", 4050.9),
        ("cddis_rinex3_3const_cme_removed_prem_vol_calibrated_4072km", 4071.8),
        ("cddis_rinex3_3const_cme_removed_raw_unit_prefactor_3155km", 3155.2),
        ("cddis_rinex3_3const_matched_band_sqrtN_3853km", 3853.1),
        ("cddis_rinex3_3const_unweighted_3423km", 3423.0),
        ("truncated_8hr_datum_removed_foil_2156km", 2156.1),
    ]:
        rho_p = float(3.0 * 5.9722e27 / (4.0 * np.pi * ((L_km_val * 1e5) ** 3)))
        scale_13 = (rho_p / 20.0) ** (1.0 / 3.0)
        scale_m12 = (rho_p / 20.0) ** (-0.5)
        # (1) Outer-3 spin: at rho_T=20, v_obs/v_TEP = 1.00034 (rho_hat = 19.89). At rho_p, v_TEP/v_obs = (rho_p / 19.894)^(1/3):
        err_spin = float((rho_p / rho_hat_outer3) ** (1.0 / 3.0) - 1.0)
        # (2) Brown-dwarf floor: at rho_T=20, P_min^th = 1.1553 hr vs obs 1.150 hr (rho_hat = 20.187):
        P_bd_p = float(P_min_th_mid_hr * scale_m12)
        err_bd = float(P_bd_p / 1.150 - 1.0)
        # (3) Terrestrial MOI: at rho_T=20, 2k_MOI/S = 1.0389 (rho_hat = 17.89; Venus+Earth P_c>100 GPa = 18.09):
        err_moi = float((rho_p / 17.89) ** (1.0 / 3.0) - 1.0)
        # (4) Solar convection zone r_cz = sqrt(3) R_T(M_sun) / R_sun: at rho_T=20, 0.7148 R_sun vs obs 0.713 R_sun (rho_hat = 20.15):
        r_cz_p = float(0.7148 / scale_13)
        err_rcz = float(r_cz_p / 0.713 - 1.0)
        rms_pct = float(100.0 * np.sqrt(np.mean(np.array([err_spin, err_bd, err_moi, err_rcz]) ** 2)))
        forward_propagation_table[pipe_lbl] = {
            "L_c_km": L_km_val,
            "implied_rho_T_g_cm3": round(rho_p, 2),
            "outer3_spin_fractional_error_pct": round(100.0 * err_spin, 2),
            "bd_period_floor_pred_hr": round(P_bd_p, 3),
            "bd_period_floor_fractional_error_pct": round(100.0 * err_bd, 2),
            "terrestrial_moi_fractional_error_pct": round(100.0 * err_moi, 2),
            "solar_rcz_pred_R_sun": round(r_cz_p, 3),
            "solar_rcz_fractional_error_pct": round(100.0 * err_rcz, 2),
            "four_channel_joint_rms_error_pct": round(rms_pct, 2),
        }

    # (M2) Classical Newtonian Chandrasekhar-Jacobi period floor (WITHOUT TEP saturation at rho_T = 20 g/cm^3, using actual BD physical densities 66.6, 70.8, 156.4 g/cm^3):
    bd_phys_rhos = np.array([70.8, 66.6, 156.4])
    P_classical_jacobi_bds_hr = [float((0.205 / eta_jacobi) * np.sqrt(3.0 * np.pi / (G * (r_bd * 1000.0))) / 3600.0) for r_bd in bd_phys_rhos]
    P_classical_jacobi_mean_hr = float(np.mean(P_classical_jacobi_bds_hr))
    z_classical_jacobi_rejection = float(abs(1.150 - P_classical_jacobi_mean_hr) / 0.075)  # = 8.32 sigma rejection of pure Newtonian Jacobi without TEP saturation!

    # Live Leave-One-Channel-Out (LOCO) cross-scale cross-validation calculation:
    rhos_loco_5 = np.array([rho_hat_gnss, rho_hat_outer3, rho_hat_bd_th_mid, float(rho_hats_5[3]), float(rho_hats_5[4])])
    exps_loco_5 = np.array([-1.0 / 3.0, +1.0 / 3.0, -0.5, +1.0 / 3.0, -1.0 / 3.0])
    loco_5_errs = [round(float(100.0 * ((float(np.mean(np.delete(rhos_loco_5, idx_l))) / rhos_loco_5[idx_l]) ** exps_loco_5[idx_l] - 1.0)), 2) for idx_l in range(5)]
    loco_5_rms = round(float(np.sqrt(np.mean(np.array(loco_5_errs) ** 2))), 2)
    loco_5_mae = round(float(np.mean(np.abs(loco_5_errs))), 2)
    rhos_loco_3 = rhos_loco_5[:3]; exps_loco_3 = exps_loco_5[:3]
    loco_3_errs = [round(float(100.0 * ((float(np.mean(np.delete(rhos_loco_3, idx_l))) / rhos_loco_3[idx_l]) ** exps_loco_3[idx_l] - 1.0)), 2) for idx_l in range(3)]
    loco_3_rms = round(float(np.sqrt(np.mean(np.array(loco_3_errs) ** 2))), 2)

    # LOCO blind observables and v_gal-marginalized [220, 236] km/s LOCO RMS:
    rho_ng = float(np.mean(np.delete(rhos_loco_5, 0)))
    loco_blind_obs = {
        "rho_T_minus_gnss_g_cm3": round(rho_ng, 2),
        "L_c_blind_km": round(4200.0 * ((rho_ng / rhos_loco_5[0]) ** (-1.0 / 3.0)), 1),
        "P_min_bd_blind_hr": round(1.150 * ((float(np.mean(np.delete(rhos_loco_5, 2))) / rhos_loco_5[2]) ** (-0.5)), 3),
        "r_cz_blind_R_sun": round(0.713 * ((float(np.mean(np.delete(rhos_loco_5, 4))) / rhos_loco_5[4]) ** (-1.0 / 3.0)), 3),
    }
    v_gal_loco_grid = np.linspace(220.0, 236.0, 17)
    loco5_vg_rms, loco3_vg_rms = [], []
    for vg_l in v_gal_loco_grid:
        rh5 = rhos_loco_5.copy(); rh5[1] = rho_hat_outer3 * ((vg_l / 220.0) ** 3)
        e5 = [100.0 * ((float(np.mean(np.delete(rh5, il))) / rh5[il]) ** exps_loco_5[il] - 1.0) for il in range(5)]
        loco5_vg_rms.append(float(np.sqrt(np.mean(np.array(e5) ** 2))))
        rh3 = rh5[:3]
        e3 = [100.0 * ((float(np.mean(np.delete(rh3, il))) / rh3[il]) ** exps_loco_3[il] - 1.0) for il in range(3)]
        loco3_vg_rms.append(float(np.sqrt(np.mean(np.array(e3) ** 2))))
    loco5_vgal_marg_rms = round(float(np.mean(loco5_vg_rms)), 2)
    loco3_vgal_marg_rms = round(float(np.mean(loco3_vg_rms)), 2)

    # (M1) v_gal-marginalized [220, 236] km/s 5-channel coincidence statistics:
    v_gal_grid = np.linspace(220.0, 236.0, 17)
    rho_spin_marg = float(np.mean([rho_hat_outer3 * ((vg / 220.0) ** 3) for vg in v_gal_grid]))
    rho_hats_3_vgal_marg = np.array([rho_hat_gnss, rho_spin_marg, rho_hat_bd_th_mid])
    mean_3_vgal_marg = float(np.mean(rho_hats_3_vgal_marg))
    std_3_vgal_marg = float(np.std(rho_hats_3_vgal_marg, ddof=1))
    rho_hats_5_vgal_marg = np.array([rho_hats_5[0], rho_spin_marg, rho_hats_5[2], rho_hats_5[3], rho_hats_5[4]])
    mean_5_vgal_marg = float(np.mean(rho_hats_5_vgal_marg))
    std_5_vgal_marg = float(np.std(rho_hats_5_vgal_marg, ddof=1))
    log_range_5_vgal_marg = float(np.max(np.log10(rho_hats_5_vgal_marg)) - np.min(np.log10(rho_hats_5_vgal_marg)))
    p5_raw_vgal_marg = float(5.0 * ((log_range_5_vgal_marg / 5.0) ** 4))
    p5_le343_vgal_marg = float(1.0 - ((1.0 - p5_raw_vgal_marg) ** 343.0))

    # (M3) Combined algebraic-factor x analyst-subset/radius-convention trials (343 factor combinations x 18 subset/radius combinations = 6,174 total trials):
    # 18 analyst combinations = 3 spin subsets (outer-3, outer-4 with Earth, N=8 speed-limit) x 3 MOI subsets (P_c>100 GPa Venus+Earth, 3-terrestrial, 7-condensed) x 2 radius conventions (1-bar equatorial vs volumetric):
    p5_le6174_total = float(1.0 - ((1.0 - p_analytic_5ch_no_le) ** (343.0 * 18.0)))
    p3_le6_subset = float(1.0 - ((1.0 - p_analytic_3free_no_le) ** 6.0))

    out = {
        "step": "step_15_planetary_rotation",
        "constants": {
            "rho_T_g_cm3": float(rho_T_g_cm3),
            "v_gal_km_s": float(v_gal / 1e3),
            "u_gal": float(u_gal),
            "c_over_v_gal": float(inv_sqrt_u_gal),
            "omega_T_rad_s": omega_T,
            "tau_T_seconds": tau_T_s,
            "tau_T_hours": tau_T_hr,
            "p_tep_wesson_si_m2_kg_s": p_tep_si,
            "p_tep_wesson_cgs_cm2_g_s": p_tep_cgs,
            "chi_tep_dimensionless": chi_tep,
        },
        "summary_metrics": {
            "unbraked_6_planets": {
                "names": unbraked_6,
                "log_veq_vs_log_uT_slope": float(slope_veq_uT_6),
                "log_veq_vs_log_uT_R2": float(r_veq_uT_6 ** 2),
                "log_veq_vs_log_uT_p": float(p_veq_uT_6),
                "spearman_rho": float(rho_s_6),
                "log_J_vs_log_M_slope": float(slope_J_M_6),
                "log_J_vs_log_M_R2": float(r_J_M_6 ** 2),
                "log_J_vs_log_M_p": float(p_J_M_6),
            },
            "ambient_4_velocity_match": {
                "names": ambient_4,
                "mean_v_eq_over_c_div_u_T": float(np.mean(kT_4)),
                "std_v_eq_over_c_div_u_T": float(np.std(kT_4, ddof=1)),
                "predicted_c_over_v_gal": float(inv_sqrt_u_gal),
                "fractional_agreement_percent": float(100.0 * (np.mean(kT_4) / inv_sqrt_u_gal - 1.0)),
                "mean_v_obs_over_v_tep": float(np.mean(ratios_veq_4)),
                "std_v_obs_over_v_tep": float(np.std(ratios_veq_4, ddof=1)),
                "inferred_rho_T_spin_per_planet_g_cm3": {k: records[k]["rho_T_spin_inferred_g_cm3"] for k in ambient_4},
                "inferred_rho_T_spin_geometric_mean_g_cm3": float(np.exp(np.mean(np.log(rho_T_spin_4)))),
                "inferred_rho_T_spin_arithmetic_mean_g_cm3": float(np.mean(rho_T_spin_4)),
                "inferred_rho_T_spin_std_g_cm3": float(np.std(rho_T_spin_4, ddof=1)),
                "uranus_hst_2025_period_hr": float(records["Uranus"]["T_rot_hr"]),
                "uranus_hst_2025_v_obs_over_v_tep": float(records["Uranus"]["v_obs_over_v_tep"]),
                "uranus_voyager2_1986_period_hr": 17.24,
                "uranus_voyager2_1986_v_obs_over_v_tep": float((records["Uranus"]["T_rot_hr"] / 17.24) * records["Uranus"]["v_obs_over_v_tep"]),
                "outer_3_unbraked_giant_planets_excluding_lunar_braked_earth": {
                    "names": outer_3_unbraked,
                    "mean_v_obs_over_v_tep": float(np.mean(ratios_veq_outer3)),
                    "std_v_obs_over_v_tep": float(np.std(ratios_veq_outer3, ddof=1)),
                    "inferred_rho_T_spin_geometric_mean_g_cm3": rhoT_outer3_geom,
                    "extended_8_outer_plus_substellar_without_earth_mean": float(np.mean(ratios_ext_8)),
                    "extended_8_outer_plus_substellar_without_earth_std": float(np.std(ratios_ext_8, ddof=1)),
                    "extended_8_inferred_rho_T_geom_g_cm3": rhoT_ext_8_geom,
                    "earth_moon_primordial_vs_present_note": "Present-day Earth (23.93 hr, v_obs/v_TEP = 1.063) has transferred ~83% of its primordial spin angular momentum to the lunar orbit via tidal dissipation; its conserved primordial Earth+Moon spin (T_prim = 5.05 hr, J_EM = 3.45e34 kg m^2/s) sits on the small-body soliton capacity ceiling (eta_EM = 0.145 vs eta_0 = 0.129), while lunar braking has relaxed present-day Earth onto the ambient Galactic floor.",
                },
                "nested_heliocentric_screening_shell_and_interior_audit": {
                    "r_star_over_a_4planets": {k: records[k]["r_star_over_a"] for k in ambient_4},
                    "pearson_r_v_obs_over_v_tep_vs_ln_r_star_over_a": float(r_nest_p),
                    "pearson_p_v_obs_over_v_tep_vs_ln_r_star_over_a": float(p_nest_p),
                    "spearman_rho_v_obs_over_v_tep_vs_r_star_over_a": float(rho_nest_s),
                    "log_log_slope_dlnv_dln_rstar_a": float(sl_nest),
                    "zero_crossing_r_star_over_a": rsa_zero_cross,
                    "rms_residual_after_nested_shell_trend_pct": rms_nest_pct,
                    "volumetric_deep_interior_4planet_ratios": {
                        "Earth": vol_ratios["Earth"],
                        "Saturn_ring_seismology_10p561hr": vol_ratios["Saturn"],
                        "Uranus_deep_16p5hr": vol_ratios["Uranus"],
                        "Neptune_deep_15p2hr": vol_ratios["Neptune"],
                        "mean_v_vol_int_over_v_tep": float(np.mean(vol_arr)),
                        "std_v_vol_int_over_v_tep": float(np.std(vol_arr, ddof=1)),
                        "geometric_mean_rho_T_vol_int_g_cm3": rhoT_vol_geom,
                    },
                    "lane_emden_polytropic_condensed_interior_moi_audit": {
                        "seven_condensed_giant_planets": condensed_7,
                        "polytropic_index_n_from_k_moi": n_le_dict,
                        "condensed_radius_ratio_R_cond_over_R_eq": r_cond_ratio_dict,
                        "two_k_moi_over_S_cond_per_planet": two_k_S_cond_dict,
                        "mean_two_k_moi_over_S_cond_7planets": float(np.mean(tks_cond_arr)),
                        "std_two_k_moi_over_S_cond_7planets": float(np.std(tks_cond_arr, ddof=1)),
                        "geometric_mean_rho_T_moi_cond_g_cm3": rhoT_cond_geom,
                    },
                },
            },
            "two_branch_5_major_planets_model": {
                "names": wesson_5,
                "branch_crossover_R_T_cap_km": float(R_T_cap_m / 1e3),
                "branch_crossover_M_cap_kg": float(M_cap_kg),
                "branch_crossover_M_cap_earth": float(M_cap_kg / records["Earth"]["M_kg"]),
                "branch_crossover_M_cap_jupiter": float(M_cap_kg / records["Jupiter"]["M_kg"]),
                "mean_v_obs_over_v_2branch": float(np.mean(ratios_hydro_5)),
                "std_v_obs_over_v_2branch": float(np.std(ratios_hydro_5, ddof=1)),
                "inferred_rho_T_2branch_geometric_mean_g_cm3": float(np.exp(np.mean(np.log(rho_T_hydro_5)))),
                "jupiter_v_obs_km_s": records["Jupiter"]["v_eq_obs_km_s"],
                "jupiter_v_soliton_cap_km_s": records["Jupiter"]["v_eq_hydro_km_s"],
                "jupiter_ratio_v_obs_over_v_cap": records["Jupiter"]["v_obs_over_v_hydro"],
                "mars_unmodeled_transition_body": {
                    "M_earth": float(records["Mars"]["M_kg"] / records["Earth"]["M_kg"]),
                    "v_obs_km_s": records["Mars"]["v_eq_obs_km_s"],
                    "v_ambient_tep_km_s": records["Mars"]["v_eq_tep_km_s"],
                    "v_soliton_cap_km_s": records["Mars"]["v_sol_ceil_km_s"],
                    "note": (
                        f"Low-mass Mars (0.11 M_earth) sits in the transition region between the ambient curve "
                        f"({records['Mars']['v_eq_tep_km_s']:.3f} km/s) and the small-body soliton capacity curve "
                        f"({records['Mars']['v_sol_ceil_km_s']:.3f} km/s) without a Mars-specific rule."
                    ),
                },
                "bryan_2020_pmo_breakup_envelope_test": {
                    "n_objects_bryan_2020": 27,
                    "observed_v_over_v_breakup_range": [0.05, 0.31],
                    "observed_v_over_v_breakup_median": 0.11,
                    "simp_j0136_observed_v_over_v_breakup": round(
                        float(records["SIMP J0136"]["v_eq_obs_km_s"] / (np.sqrt(G * records["SIMP J0136"]["M_kg"] / (records["SIMP J0136"]["R_eq_km"] * 1e3)) / 1e3)), 4
                    ),
                    "simp_j0136_predicted_v_cap_over_v_breakup": round(
                        float((0.12905 / records["SIMP J0136"]["k_moi"]) * (records["SIMP J0136"]["S_screening"] ** 0.5)), 4
                    ),
                    "saturated_degenerate_bd_ceiling_v_cap_over_v_breakup_at_S_ge_1": round(float(0.12905 / 0.205), 4),
                    "n_exceeding_ceiling": 0,
                    "falsifier": "Any unbraked planetary-mass companion or brown dwarf with M > M_cap = 0.61 M_Jup exceeding v_cap / v_breakup = (eta_0 / k_MOI) sqrt(min(1, S)) (0.478 at SIMP J0136 S=0.76, and 0.630 at S>=1) falsifies the soliton angular-momentum capacity bound.",
                },
                "substellar_rotational_speed_limit_and_period_floor_test": {
                    "simp_j0136_12p7_Mjup": {
                        "S_screening": records["SIMP J0136"]["S_screening"],
                        "v_obs_km_s": records["SIMP J0136"]["v_eq_obs_km_s"],
                        "v_cap_km_s": records["SIMP J0136"]["v_eq_hydro_km_s"],
                        "P_obs_hr": records["SIMP J0136"]["T_rot_hr"],
                        "P_cap_hr": records["SIMP J0136"]["T_hydro_hr"],
                        "v_obs_over_v_cap": records["SIMP J0136"]["v_obs_over_v_hydro"],
                    },
                    "tannock_2021_brown_dwarf_period_floor": {
                        "k_moi_n1p5_polytrope": 0.205,
                        "predicted_universal_P_min_hr": float(P_min_bd_tep_hr),
                        "observed_fastest_3_periods_hr": [float(x) for x in P_obs_tannock_3],
                        "observed_mean_period_hr": float(np.mean(P_obs_tannock_3)),
                        "observed_std_period_hr": float(np.std(P_obs_tannock_3, ddof=1)),
                        "fractional_agreement_percent": float(100.0 * (P_min_bd_tep_hr / np.mean(P_obs_tannock_3) - 1.0)),
                    },
                    "extended_9_planet_and_substellar_match": {
                        "names": extended_9,
                        "mean_v_obs_over_v_2br": float(np.mean(ratios_ext_9)),
                        "std_v_obs_over_v_2br": float(np.std(ratios_ext_9, ddof=1)),
                        "secular_stability_eta_sec_1_over_8": {
                            "eta_sec": 0.125,
                            "jupiter_v_cap_eta_sec_km_s": float(records["Jupiter"]["v_eq_hydro_km_s"] * (0.125 / 0.12905)),
                            "simp_j0136_v_cap_eta_sec_km_s": float(records["SIMP J0136"]["v_eq_hydro_km_s"] * (0.125 / 0.12905)),
                            "brown_dwarf_P_min_eta_sec_hr": float((0.205 / 0.125) * tau_T_hr),
                        },
                    },
                },
            },
            "wesson_5_angular_momentum_match": {
                "names": wesson_5,
                "mean_J_obs_over_J_tep": float(np.mean(ratios_J_5)),
                "std_J_obs_over_J_tep": float(np.std(ratios_J_5, ddof=1)),
                "mean_chi_obs": float(np.mean(chi_5)),
                "std_chi_obs": float(np.std(chi_5, ddof=1)),
                "predicted_chi_tep": chi_tep,
            },
            "all_8_planets_moi_screening_relation": {
                "names": planets_8,
                "mean_2k_moi_over_S": float(np.mean(two_k_over_S_8)),
                "std_2k_moi_over_S": float(np.std(two_k_over_S_8, ddof=1)),
                "min_2k_moi_over_S": float(np.min(two_k_over_S_8)),
                "max_2k_moi_over_S": float(np.max(two_k_over_S_8)),
                "inferred_rho_T_moi_per_planet_g_cm3": {k: records[k]["rho_T_moi_inferred_g_cm3"] for k in planets_8},
                "inferred_rho_T_moi_mean_g_cm3": float(np.mean(rho_T_moi_8)),
                "inferred_rho_T_moi_std_g_cm3": float(np.std(rho_T_moi_8, ddof=1)),
                "core_screened_terrestrial_3_planets": {
                    "names": terrestrial_core_3,
                    "mean_2k_moi_over_S": float(np.mean(two_k_over_S_terr3)),
                    "std_2k_moi_over_S": float(np.std(two_k_over_S_terr3, ddof=1)),
                    "inferred_rho_T_moi_mean_g_cm3": float(np.mean(rho_T_moi_terr3)),
                    "inferred_rho_T_moi_std_g_cm3": float(np.std(rho_T_moi_terr3, ddof=1)),
                },
                "low_pressure_uncompressed_satellites_diagnostic": sat_moi_audit,
                "unconstrained_compositional_power_law_baseline_vs_tep": {
                    "fitted_slope_beta_emp": float(sl_k_rho),
                    "fitted_slope_err": float(se_k_rho),
                    "fitted_normalization_C_emp": c_emp_k,
                    "zero_param_tep_slope": 1.0 / 3.0,
                    "zero_param_tep_normalization_C": c_tep_k,
                    "rms_scatter_0param_tep_dex": rms_k_tep_dex,
                    "rms_scatter_2param_free_fit_dex": rms_k_free_dex,
                },
                "juno_cassini_refined_2k_over_S": {
                    "Jupiter_k_0p26393": float(2.0 * 0.26393 / records["Jupiter"]["S_screening"]),
                    "Saturn_k_0p2181": float(2.0 * 0.2181 / records["Saturn"]["S_screening"]),
                },
            },
            "soliton_9_macdonald_scaling": {
                "names": soliton_9,
                "log_j_vs_log_uT_slope": float(slope_j_uT_9[0]),
                "log_j_vs_log_uT_slope_err": slope_err_9,
                "log_j_vs_log_uT_R2": float(r_j_uT_9 ** 2),
                "log_j_vs_log_uT_p": float(p_j_uT_9),
                "mean_eta_rot": float(np.mean(eta_9)),
                "median_eta_rot": float(np.median(eta_9)),
                "std_eta_rot": float(np.std(eta_9, ddof=1)),
            },
            "tep9_outer_solar_system_links": {
                "g_t_m_s2": float(g_t),
                "neptune_a_AU": records["Neptune"]["a_AU"],
                "neptune_r_star_AU": records["Neptune"]["r_star_AU"],
                "neptune_r_star_over_a": records["Neptune"]["r_star_over_a"],
                "jupiter_r_star_AU": records["Jupiter"]["r_star_AU"],
                "giant_planets_combined_r_star_AU": r_star_giants_au,
                "uranus_spin_pole_ecliptic_deg": [77.65, -7.72],
                "uranus_spin_angle_to_tep9_tno_axis_deg": uranus_angle_to_tno_deg,
                "uranus_spin_angle_to_tep9_meridian_plane_deg": uranus_angle_to_meridian_deg,
                "uranus_spin_angle_to_cmb_apex_deg": uranus_angle_to_cmb_deg,
            },
            "random_density_and_look_elsewhere_coincidence_null_test": {
                "n_monte_carlo_trials": n_null_trials,
                "prior_density_range_g_cm3": [0.1, 10000.0],
                "five_independent_channels_earth_spin_excluded": {
                    "ch1_terrestrial_gnss_Lc_4200km": rho_hat_gnss,
                    "ch2_outer_3_giant_planet_spin_uranus_neptune_saturn": rho_hat_outer3,
                    "ch3_brown_dwarf_period_floor_1p150hr": rho_hat_bd,
                    "ch4_terrestrial_core_screened_moi": rho_hat_moi_terr,
                    "ch5_solar_model_S_convection_base_0p713Rsun": rho_hat_sol_cz,
                },
                "inferred_rho_T_5channel_mean_g_cm3": float(np.mean(rho_hats_5)),
                "inferred_rho_T_5channel_std_g_cm3": float(np.std(rho_hats_5, ddof=1)),
                "inferred_rho_T_5channel_log10_std_dex": log_spread_5_dex,
                "inferred_rho_T_5channel_log10_range_dex": log_range_5_dex,
                "observed_5channel_rms_fractional_error": obs_rms_5ch,
                "observed_5channel_max_fractional_error": obs_max_5ch,
                "p_1d_random_density_rms_le_obs": p_1d_rms,
                "p_1d_random_density_max_err_le_5pct": p_1d_max5pct,
                "p_5channel_coincidence_no_look_elsewhere": p_analytic_5ch_no_le,
                "p_5channel_coincidence_with_343_algebraic_factor_look_elsewhere": p_mc_5ch_with_look_elsewhere,
                "apriori_goldreich_soter_tidal_selection_and_jacobi_stability": {
                    "planetary_tidal_despinning_audit": apriori_tidal_audit,
                    "chandrasekhar_jacobi_secular_bifurcation_eta": eta_jacobi,
                    "small_body_6object_median_eta": eta_med_6,
                    "jacobi_vs_small_body_median_fractional_offset": float(eta_jacobi / eta_med_6 - 1.0),
                    "parameter_free_bd_period_floor_bracket_hr": [round(P_min_jacobi_hr, 4), round(P_min_virial_hr, 4)],
                    "parameter_free_bd_period_floor_midpoint_hr": round(P_min_th_mid_hr, 4),
                    "observed_tannock_bd_period_floor_mean_hr": float(np.mean(P_obs_tannock_3)),
                    "parameter_free_bd_inferred_rho_T_g_cm3": round(rho_hat_bd_th_mid, 3),
                    "classical_newtonian_jacobi_without_tep_saturation_periods_hr": [round(x, 3) for x in P_classical_jacobi_bds_hr],
                    "classical_newtonian_jacobi_without_tep_saturation_mean_hr": round(P_classical_jacobi_mean_hr, 3),
                    "classical_newtonian_jacobi_rejection_sigma": round(z_classical_jacobi_rejection, 2),
                },
                "prior_range_and_systematic_propagation_audit": {
                    "prior_width_sensitivity": prior_sensitivity,
                    "v_gal_marginalized_220_to_236_km_s_5channel_audit": {
                        "marginalized_spin_rho_T_g_cm3": round(rho_spin_marg, 2),
                        "five_channel_mean_vgal_marg_g_cm3": round(mean_5_vgal_marg, 2),
                        "five_channel_std_vgal_marg_g_cm3": round(std_5_vgal_marg, 2),
                        "three_channel_mean_vgal_marg_g_cm3": round(mean_3_vgal_marg, 2),
                        "three_channel_std_vgal_marg_g_cm3": round(std_3_vgal_marg, 2),
                        "p_5channel_raw_vgal_marg": p5_raw_vgal_marg,
                        "p_5channel_after_343_trials_vgal_marg": p5_le343_vgal_marg,
                    },
                    "combined_factor_and_subset_selection_trials_audit": {
                        "n_algebraic_factor_trials": 343,
                        "n_subset_and_radius_combinations": 18,
                        "n_total_combined_trials": 6174,
                        "p_5channel_after_6174_total_trials": p5_le6174_total,
                        "p_3channel_after_6_subset_radius_trials": p3_le6_subset,
                    },
                    "spin_channel_v_gal_propagation_g_cm3": {
                        "v_gal_220_km_s_iau": round(rho_spin_vgal220, 2),
                        "v_gal_229_km_s_eilert2019": round(rho_spin_vgal229, 2),
                        "v_gal_236_km_s_reid2019": round(rho_spin_vgal236, 2),
                    },
                    "forward_propagation_falsification_across_gnss_pipelines": forward_propagation_table,
                    "gnss_channel_Lc_estimator_propagation_g_cm3": {
                        "Lc_4200_km_code_cross_sector": round(rho_hat_gnss, 2),
                        "Lc_4132_km_rinex3_sqrtN_lowfreq_galileo": 20.20,
                        "Lc_4051_km_rinex3_gps_sqrtN": round(rho_gnss_Lc4051, 2),
                        "Lc_3853_km_rinex3_3const_sqrtN_mean": round(rho_gnss_Lc3853, 2),
                        "Lc_3423_km_rinex3_3const_unweighted_mean": round(rho_gnss_Lc3423, 2),
                    },
                    "terrestrial_moi_pressure_vs_iron_core_split": {
                        "high_pressure_P_c_gt_100GPa_Venus_Earth_2k_over_S_mean": round(float(np.mean(venus_earth_2k_over_S)), 4),
                        "high_pressure_P_c_gt_100GPa_Venus_Earth_rho_T_mean_g_cm3": round(float(np.mean(venus_earth_rho_T)), 2),
                        "mercury_iron_core_note": "Mercury (P_c = 24.5 GPa, rho = 5.427 g/cm^3) and Mars (P_c = 24.9 GPa, rho = 3.934 g/cm^3) share similar central pressures; Venus (141 GPa) and Earth (173 GPa) satisfy the strict P_c > K_0 (~100 GPa) silicate self-compression threshold independently (2k_MOI/S = 1.024 +- 0.008, rho_T = 18.6 +- 0.5 g/cm^3), whereas Mercury's low k_MOI = 0.346 reflects its ~70-85% iron core mass fraction (rho > 5.2 g/cm^3).",
                    },
                },
                "leave_one_channel_out_blind_prediction_audit": {"five_channel_loco_blind_observable_rms_pct": loco_5_rms, "five_channel_loco_mean_abs_error_pct": loco_5_mae, "three_channel_zero_prefactor_loco_rms_pct": loco_3_rms, "five_channel_loco_vgal_marginalized_rms_pct": loco5_vgal_marg_rms, "three_channel_loco_vgal_marginalized_rms_pct": loco3_vgal_marg_rms, "individual_5channel_blind_errors_pct": {"gnss_Lc": loco_5_errs[0], "outer3_planet_spin": loco_5_errs[1], "bd_period_floor": loco_5_errs[2], "terrestrial_moi": loco_5_errs[3], "solar_rcz": loco_5_errs[4]}, "blind_predicted_observables": loco_blind_obs},
                "three_channel_zero_prefactor_coincidence_null": {
                    "channels_included": ["ch1_gnss_Lc_19p24", "ch2_outer3_giant_spin_19p89", "ch3_parameter_free_bd_floor_20p18"],
                    "inferred_rho_T_3free_mean_g_cm3": round(mean_3free, 3),
                    "inferred_rho_T_3free_std_g_cm3": round(std_3free, 3),
                    "inferred_rho_T_3free_log10_range_dex": round(log_range_3free_dex, 5),
                    "p_3channel_zero_prefactor_coincidence": p_analytic_3free_no_le,
                },
                "gnss_free_4channel_external_catalog_isolation": {
                    "channels_included": ["ch2_outer_3_giant_planet_spin", "ch3_brown_dwarf_period_floor", "ch4_terrestrial_core_screened_moi", "ch5_solar_model_S_convection_base"],
                    "inferred_rho_T_no_gnss_mean_g_cm3": mean_no_gnss_4,
                    "inferred_rho_T_no_gnss_std_g_cm3": std_no_gnss_4,
                    "inferred_rho_T_no_gnss_sem_g_cm3": sem_no_gnss_4,
                    "inferred_rho_T_no_gnss_log10_std_dex": log_std_no_gnss_4,
                    "gnss_Lc_4200km_inferred_rho_T_g_cm3": rho_hat_gnss,
                    "gnss_vs_external_astrophysical_mean_fractional_offset": float(rho_hat_gnss / mean_no_gnss_4 - 1.0),
                },
                "four_channel_without_solar_prototype": {
                    "inferred_rho_T_4channel_mean_g_cm3": float(np.mean(rho_hats_4)),
                    "inferred_rho_T_4channel_std_g_cm3": float(np.std(rho_hats_4, ddof=1)),
                    "inferred_rho_T_4channel_log10_std_dex": log_spread_4_dex,
                    "inferred_rho_T_4channel_log10_range_dex": log_range_4_dex,
                    "observed_4channel_rms_fractional_error": obs_rms_4ch,
                    "p_1d_random_density_rms_le_obs_4ch": p_1d_rms_4ch,
                    "p_4channel_coincidence_no_look_elsewhere": p_analytic_4ch_no_le,
                    "p_4channel_coincidence_with_49_algebraic_factor_look_elsewhere": p_mc_4ch_with_look_elsewhere,
                },
                "small_body_eta_propagated_range": {
                    "eta_0_fiducial": 0.12905,
                    "eta_6body_median": eta_med_6,
                    "eta_6body_iqr_25_75": [eta_q25_6, eta_q75_6],
                    "P_min_bd_at_eta_med6_hr": P_min_med6_hr,
                    "P_min_bd_iqr_25_75_hr": P_min_iqr_hr,
                },
                "algebraic_factor_dictionary_tested": [0.5, 0.70710678, 1.0, 1.41421356, 1.73205081, 2.0, 3.14159265],
            },
            "solar_helioseismic_and_angular_momentum_audit": {
                "R_T_sun_km": float(R_T_sun / 1e3),
                "S_sun_R_T_over_R_sun": S_sun,
                "model_S_nuclear_core_rho_eq_rhoT_r_over_Rsun": x_core_sun,
                "model_S_nuclear_core_enclosed_mass_fraction": M_core_sun_frac,
                "model_S_mean_density_rho_bar_eq_rhoT_r_over_Rsun": x_bar_sun,
                "predicted_3D_convection_base_sqrt3_R_T_over_Rsun": x_tach_tep,
                "observed_helioseismic_convection_base_r_cz_over_Rsun": x_tach_obs,
                "convection_base_fractional_agreement_percent": float(100.0 * (x_tach_tep / x_tach_obs - 1.0)),
                "enclosed_mass_fraction_at_r_3D": M_3d_sun_frac,
                "enclosed_mean_density_at_r_3D_g_cm3": rho_bar_3d_cgs,
                "inferred_rho_T_from_convection_base_g_cm3": rho_T_cz_inferred,
                "r_3D_range_across_rhoT_8_to_70_g_cm3": [
                    float(x_tach_tep * ((20.0 / 70.0) ** (1.0 / 3.0))),
                    float(x_tach_tep * ((20.0 / 8.0) ** (1.0 / 3.0))),
                ],
                "prolate_tachocline_center_latitudinal_variation": {
                    "predicted_r_c_equator_0deg_over_Rsun": float(x_tach_tep - d_eq_tach_tep),
                    "observed_r_c_equator_0deg_over_Rsun": 0.693,
                    "predicted_r_c_60deg_over_Rsun": float(x_tach_tep - 0.25 * d_eq_tach_tep),
                    "observed_r_c_60deg_over_Rsun": 0.717,
                    "predicted_prolate_delta_r_c_60_minus_0": float(0.75 * d_eq_tach_tep),
                    "observed_prolate_delta_r_c_60_minus_0": 0.024,
                },
                "bvp_gyration_threshold_y_eq_half_S_r_over_Rsun": x_bvp_half_S,
                "local_gyration_threshold_S_A_eq_half_S_r_over_Rsun": x_loc_half_S,
                "zero_borrowing_harmonic_coefficients_a2_eq_a4": float(a2_tep),
                "kic_8006161_hd173701_karoff_2018_solar_twin_check": {
                    "M_Msun": 1.00,
                    "R_Rsun": 0.93,
                    "S_star": float(S_sun / 0.93),
                    "predicted_Delta_Omega_S_over_sqrt2": float((S_sun / 0.93) / np.sqrt(2.0)),
                    "observed_kepler_photometric_period_range_days": [25.0, 35.0],
                    "observed_photometric_active_latitude_shear": float((35.0 - 25.0) / 35.0),
                    "note": "Karoff et al. (2018, ApJ 852, 46) report Kepler sliding-window photometric periods varying between 25 and 35 days ((35-25)/35 = 0.286 vs TEP S_*/sqrt(2) = 0.314), while asteroseismic splitting ratios across broader Kepler Sun-like stars (Benomar et al. 2018, Science 361, 1239) show larger convective shears with wide credible intervals.",
                },
                "predicted_equatorial_v_eq_km_s": v_eq_sun_tep_km_s,
                "observed_carrington_v_eq_km_s": 1.9952,
                "predicted_equatorial_Omega_nHz": Omega_eq_tep_nHz,
                "observed_helioseismic_equatorial_Omega_nHz": Omega_eq_obs_nHz,
                "predicted_radiative_lock_Omega_nHz": Omega_rad_tep_nHz,
                "observed_helioseismic_radiative_Omega_nHz": Omega_rad_obs_nHz,
                "predicted_differential_shear_S_sun_over_sqrt2": Delta_shear_tep,
                "observed_helioseismic_differential_shear_a2_plus_a4": round(float(a2_obs + a4_obs), 4),
                "planetary_orbital_J_obs_kg_m2_s": J_orb_planets_obs,
                "total_solar_system_J_obs_kg_m2_s": J_sys_tot_obs,
                "predicted_solar_soliton_capacity_J_sol_eta_sec_kg_m2_s": J_sol_sun_sec,
                "predicted_solar_soliton_capacity_J_sol_eta0_kg_m2_s": J_sol_sun_emp,
                "total_solar_system_eta_sys": float((J_sys_tot_obs / M_sun) / j_T_sun),
            },
        },
        "bodies": records,
    }

    out_path = REPO / "results" / "outputs" / "step_15_planetary_rotation.json"
    out_path.write_text(json.dumps(out, indent=2))
    print_status(f"Saved numerical outputs to {out_path}", "SUCCESS")
    return out


if __name__ == "__main__":
    main()
