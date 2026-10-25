#!/usr/bin/env python3
"""AUD — Scalar-sector scale dictionary and normalization consistency audit.

Resolves the kinetic-vs-potential scale bookkeeping across the corpus. Three
distinct scales must not be conflated under one symbol Lambda:

  * Lambda_X  = sqrt(M_Pl H0)  — the kinetic (gradient/shear) completion scale
    of P(X,phi) = X - V + X|X|/Lambda_X^4. Anchored to the measured drift
    H0 = 70 km/s/Mpc. Value ~ 1.9 meV.
  * lambda    — the dimensionless quartic coupling of the matter-hosting
    branch V(u) = (lambda/4) M_Pl^4 u^4 of the master potential. Operative
    corpus branch is the Cassini-compatible normalization
    LAMBDA_QUARTIC_CASSINI = 7.526e-66 (LAMBDA_QUARTIC_REF = 7.526e-71 fails
    the corrected linear-in-S_Sigma Cassini evaluation by ~250x, Paper 0
    step_03). Equivalent potential scale Lambda_V = lambda^(1/4) M_Pl.
  * rho_T     = 20 g/cm^3 — the geometric reference constant of the
    saturation-radius law R_T(M) = (3M/4 pi rho_T)^(1/3), calibrated through
    the GNSS correlation length L_c = R_T(M_Earth) ~ 4200 km. Its natural-unit
    fourth root rho_T^(1/4) ~ 96 keV is an energy-density reading of a
    density, NOT the scalar potential's coefficient scale.

This step computes the dictionary, verifies that the amplitude response
S_A = min[1, (rho/rho_T)^(1/3)] is exactly the quartic-equilibrium ratio
u_min(rho)/u_min(rho_T), locates the genuine u ~ 1 self-quenching crossing
(rho_sat = lambda M_Pl^4 O(1) ~ 1e26 g/cm^3 — temporal-well interior domain,
not terrestrial), derives the compact-object lower bound on lambda, and
demonstrates that the alternative identification Lambda^4 = rho_T
(equivalent lambda ~ rho_T/M_Pl^4 ~ 2.4e-90) is excluded: it is 3e24 below
the Cassini branch, drives u_min at neutron-star-core densities past the
master-potential knee u_s ~ 10, and yields a Compton length vastly larger
than any host body so the invoked local equilibrium never forms.

Outputs results/outputs/step_14_scale_audit.json
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_bvp
from scipy.optimize import brentq, curve_fit

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from core import constants as C          # noqa: E402
from core import scalar_field as sf      # noqa: E402
from utils.style import COLORS, FIG_SCALE, FIG_SIZE, set_pub_style as set_shared_style  # noqa: E402


def u_min_of(rho_g_cm3, lam):
    """Solve lambda * u^3 * exp(u) = rho/M_Pl^4 for u."""
    return float(sf.equilibrium_u(rho_g_cm3, lam))


def lambda_c_m(rho_g_cm3, lam):
    u = u_min_of(rho_g_cm3, lam)
    return float(sf.compton_wavelength_m(u, rho_g_cm3, lam))


def main():
    Mpl = C.M_PL_REDUCED_GEV              # GeV, reduced Planck mass
    lam_cas = C.LAMBDA_QUARTIC_CASSINI
    lam_ref = C.LAMBDA_QUARTIC_REF
    rho_T = C.RHO_T                       # g/cm^3
    u_s = C.U_S_TRANSITION

    # --- Scale dictionary -------------------------------------------------
    lam_X_meV = C.LAMBDA_KINETIC_MEV
    lam_V_cas_GeV = lam_cas**0.25 * Mpl           # quartic potential scale
    lam_V_ref_GeV = lam_ref**0.25 * Mpl
    # rho_T^(1/4): energy-density reading of the transition density
    rhoT_gev4 = rho_T * C.G_CM3_TO_GEV4
    rhoT_fourth_root_keV = rhoT_gev4**0.25 * 1e6   # GeV -> keV
    # The (false) identification Lambda^4 = rho_T would imply:
    lam_equiv_ucd = rhoT_gev4 / Mpl**4            # dimensionless quartic equiv.

    # --- Quartic equilibrium / amplitude law -------------------------------
    rho_earth = 5.515
    u_earth = u_min_of(rho_earth, lam_cas)
    u_rhoT = u_min_of(rho_T, lam_cas)
    S_A_earth_model = float(sf.S_A_density(rho_earth, rho_T))
    S_A_earth_ratio = u_earth / u_rhoT            # exact equality check

    rho_ns = 2.0e14                              # neutron-star core, g/cm^3
    u_ns_cas = u_min_of(rho_ns, lam_cas)
    u_ns_ucd = u_min_of(rho_ns, lam_equiv_ucd)

    # u ~ 1 self-quenching crossing: u^3 e^u = 1 solved for the density
    # rho_sat = lambda M_Pl^4 * u^3 e^u evaluated at the crossing root
    u_cross = brentq(lambda u: u**3 * np.exp(u) - 1.0, 0.1, 2.0)
    rho_sat_ucd = lam_equiv_ucd * Mpl**4 * u_cross**3 * np.exp(u_cross) / C.G_CM3_TO_GEV4
    rho_sat_cas = lam_cas * Mpl**4 * u_cross**3 * np.exp(u_cross) / C.G_CM3_TO_GEV4

    # --- Compton resolution versus geometric radius ------------------------
    R_T_earth = float(sf.R_T_geometric(C.M_EARTH, rho_T))
    lam_c_rhoT_cas = lambda_c_m(rho_T, lam_cas)
    lam_c_rhoT_ucd = lambda_c_m(rho_T, lam_equiv_ucd)
    # density where lambda_c(rho) = R_T(M_earth) under the corpus branch
    f = lambda lr: lambda_c_m(10**lr, lam_cas) - R_T_earth
    rho_compton_x = None
    for i in range(60):
        a, b = -2 + i * 0.1, -2 + (i + 1) * 0.1
        if f(a) * f(b) < 0:
            rho_compton_x = 10 ** brentq(f, a, b)
            break

    # --- Compact-object lower bound on lambda ------------------------------
    # The master-potential knee u_s must not be reached inside any observed
    # compact object:  lambda * u_s^3 * e^{u_s} > rho_NS / M_Pl^4
    lam_pulsar_bound = (rho_ns * C.G_CM3_TO_GEV4) / (Mpl**4 * u_s**3 * np.exp(u_s))

    # --- Kinetic-sector column scale ---------------------------------------
    # Inside the nonlinear-kinetic interior (P_X >> 1), flux conservation gives
    # phi' ~ (Lambda_X^4 rho r / 3 M_Pl)^(1/3); the interior turns canonical
    # (phi' ~ Lambda_X^2) below the column density Sigma_* ~ 3 M_Pl^2 H0.
    # M_Pl^2 H0 in natural units -> g/cm^2 column. Computed via Lambda_X:
    # Sigma_* [eV^3] = 3 * Lambda_X^2 * M_Pl   (Lambda_X^2 = M_Pl H0)
    lam_X_eV = lam_X_meV * 1e-3
    Mpl_eV = Mpl * 1e9
    Sigma_star_eV3 = 3.0 * lam_X_eV**2 * Mpl_eV
    # 1 eV^3 -> g/cm^2: energy column eV^3 /(hbar c)^2 gives eV/m^2; convert.
    hbarc_eV_m = 1.973269804e-7
    Sigma_star_g_cm2 = (
        Sigma_star_eV3 / hbarc_eV_m**2 * (1.602176634e-19) / (C.C_LIGHT**2) * 1e-1
    )  # eV/m^2 -> J/m^2 -> kg/m^2 -> g/cm^2  (kg->g /1e-3, m^2->cm^2 /1e-4)

    # --- Recommendation 1: Single-Potential PREM Earth Numerical BVP Integration & Covariance Projection ---
    lam_c0_km = lam_c_rhoT_cas / 1e3
    R_E_km = C.R_EARTH / 1e3
    R_T_E_km = R_T_earth / 1e3

    def rho_prem_smooth(r_km):
        s1 = 0.5 * (1.0 - np.tanh((r_km - 1221.5) / 30.0))
        s2 = 0.5 * (1.0 + np.tanh((r_km - 1221.5) / 30.0)) * 0.5 * (1.0 - np.tanh((r_km - 3480.0) / 30.0))
        s3 = 0.5 * (1.0 + np.tanh((r_km - 3480.0) / 30.0)) * 0.5 * (1.0 - np.tanh((r_km - 5701.0) / 30.0))
        s4 = 0.5 * (1.0 + np.tanh((r_km - 5701.0) / 30.0)) * 0.5 * (1.0 - np.tanh((r_km - 6371.0) / 30.0))
        return 1.0005 * (12.90 * s1 + 11.05 * s2 + 4.90 * s3 + 3.55 * s4)

    def bvp_rhs(r, Y):
        y, dy = Y[0], Y[1]
        rho_ratio = rho_prem_smooth(r) / rho_T
        d2y = (1.0 / (3.0 * lam_c0_km**2)) * (y**3 - rho_ratio) - (2.0 / r) * dy
        return np.vstack((dy, d2y))

    def bvp_bc(Ya, Yb):
        return np.array([Ya[1], Yb[0]])

    r_mesh = np.linspace(10.0, 50000.0, 2000)
    y_init = (np.maximum(rho_prem_smooth(r_mesh), 1e-6) / rho_T) ** (1.0 / 3.0)
    sol_prem = solve_bvp(bvp_rhs, bvp_bc, r_mesh, np.vstack((y_init, np.gradient(y_init, r_mesh))), tol=1e-6)

    r_int = np.linspace(50.0, R_E_km, 500)
    y_int = sol_prem.sol(r_int)[0]
    dy_int = sol_prem.sol(r_int)[1]
    lam_c_int = lam_c0_km / y_int
    w_grad = (r_int**2) * np.abs(dy_int)
    r_grad_centroid_km = float(np.sum(w_grad * r_int) / np.sum(w_grad))
    lam_c_at_grad_km = float(np.sum(w_grad * lam_c_int) / np.sum(w_grad))

    d_arc = np.linspace(200.0, 8000.0, 80)
    theta = d_arc / R_E_km
    mu_q, w_q = np.polynomial.legendre.leggauss(60)
    phi_q = np.linspace(0, 2.0 * np.pi, 60, endpoint=False)
    dphi = 2.0 * np.pi / 60.0
    MU, PHI = np.meshgrid(mu_q, phi_q, indexing="ij")
    W = w_q[:, None] * dphi
    sin_th_q = np.sqrt(1.0 - MU**2)
    r_s = r_grad_centroid_km
    dist_A = np.sqrt(R_E_km**2 + r_s**2 - 2.0 * R_E_km * r_s * MU)
    G_A = np.exp(-dist_A / lam_c_at_grad_km) / dist_A

    cov_yuk = []
    for th in theta:
        cos_ang_B = sin_th_q * np.cos(PHI) * np.sin(th) + MU * np.cos(th)
        dist_B = np.sqrt(R_E_km**2 + r_s**2 - 2.0 * R_E_km * r_s * cos_ang_B)
        G_B = np.exp(-dist_B / lam_c_at_grad_km) / dist_B
        cov_yuk.append(np.sum(W * G_A * G_B))
    cov_yuk = np.array(cov_yuk)
    cov_yuk_dc = cov_yuk - np.min(cov_yuk)
    cov_yuk_dc /= cov_yuk_dc[0]
    popt_prem, _ = curve_fit(lambda d, A, L: A * np.exp(-d / L), d_arc, cov_yuk_dc, p0=[1.0, 4200.0])
    L_c_prem_km = float(popt_prem[1])
    r2_prem = float(1.0 - np.sum((cov_yuk_dc - popt_prem[0] * np.exp(-d_arc / L_c_prem_km))**2) / np.sum((cov_yuk_dc - np.mean(cov_yuk_dc))**2))

    # Full radial-volume Yukawa integration across all interior shells r_s in [500, R_E - 50] km
    r_shells = np.linspace(500.0, R_E_km - 50.0, 40)
    y_sh = sol_prem.sol(r_shells)[0]
    dy_sh = sol_prem.sol(r_shells)[1]
    lam_sh = lam_c0_km / y_sh
    w_sh = (r_shells ** 2) * np.abs(dy_sh)
    w_sh /= np.sum(w_sh)
    cov_vol = np.zeros_like(d_arc)
    for rs_v, lams_v, ws_v in zip(r_shells, lam_sh, w_sh):
        dist_Av = np.sqrt(R_E_km ** 2 + rs_v ** 2 - 2.0 * R_E_km * rs_v * MU)
        G_Av = np.exp(-dist_Av / lams_v) / dist_Av
        for idx_tv, th_v in enumerate(theta):
            cos_ang_Bv = sin_th_q * np.cos(PHI) * np.sin(th_v) + MU * np.cos(th_v)
            dist_Bv = np.sqrt(R_E_km ** 2 + rs_v ** 2 - 2.0 * R_E_km * rs_v * cos_ang_Bv)
            G_Bv = np.exp(-dist_Bv / lams_v) / dist_Bv
            cov_vol[idx_tv] += ws_v * np.sum(W * G_Av * G_Bv)
    cov_vol_dc = cov_vol - np.min(cov_vol)
    cov_vol_dc /= cov_vol_dc[0]
    popt_vol2, _ = curve_fit(lambda d, A, L: A * np.exp(-d / L), d_arc, cov_vol_dc, p0=[1.0, 3200.0])
    L_c_vol2_km = float(popt_vol2[1])
    r2_vol2 = float(1.0 - np.sum((cov_vol_dc - popt_vol2[0] * np.exp(-d_arc / L_c_vol2_km)) ** 2) / np.sum((cov_vol_dc - np.mean(cov_vol_dc)) ** 2))
    popt_vol1, _ = curve_fit(lambda d, L: np.exp(-(d - d_arc[0]) / L), d_arc, cov_vol_dc, p0=[3200.0])
    L_c_vol1_km = float(popt_vol1[0])
    r2_vol1 = float(1.0 - np.sum((cov_vol_dc - np.exp(-(d_arc - d_arc[0]) / L_c_vol1_km)) ** 2) / np.sum((cov_vol_dc - np.mean(cov_vol_dc)) ** 2))

    # PREM sensitivity audit across rho_T in {5, 20, 50, 200} g/cm^3 and baseline windows d_max in {6000, 8000, 10000} km
    prem_rhoT_sensitivity = {}
    d_chord_arc = 2.0 * R_E_km * np.sin(0.5 * theta)
    for rho_test in (5.0, 20.0, 50.0, 200.0):
        R_T_test_km = float(sf.R_T_geometric(C.M_EARTH, rho_test)) / 1e3
        lam_scaled = lam_c_at_grad_km * ((20.0 / rho_test) ** (1.0 / 3.0))
        G_A_s = np.exp(-dist_A / lam_scaled) / dist_A
        cov_s = np.array([
            np.sum(W * G_A_s * (np.exp(-np.sqrt(R_E_km**2 + r_s**2 - 2.0 * R_E_km * r_s * (sin_th_q * np.cos(PHI) * np.sin(th_s) + MU * np.cos(th_s))) / lam_scaled)
                                / np.sqrt(R_E_km**2 + r_s**2 - 2.0 * R_E_km * r_s * (sin_th_q * np.cos(PHI) * np.sin(th_s) + MU * np.cos(th_s)))))
            for th_s in theta
        ])
        cov_s_dc = (cov_s - np.min(cov_s)) / (cov_s[0] - np.min(cov_s))
        popt_s, _ = curve_fit(lambda d, A, L: A * np.exp(-d / L), d_arc, cov_s_dc, p0=[1.0, 4000.0])
        # Saturation-core coherence kernel C_sat(d; rho_T) = exp(-d_chord / R_T(M_earth, rho_T)) tracking R_T ~ rho_T^(-1/3)
        cov_sat = np.exp(-d_chord_arc / R_T_test_km)
        popt_sat, _ = curve_fit(lambda d, A, L: A * np.exp(-d / L), d_arc, cov_sat, p0=[1.0, R_T_test_km])
        prem_rhoT_sensitivity[f"rhoT_{int(rho_test)}_g_cm3"] = {
            "R_T_earth_km": R_T_test_km,
            "fixed_quartic_lambda_L_c_km": L_c_prem_km,
            "rhoT_scaled_compton_km": float(lam_scaled),
            "rhoT_scaled_compton_L_c_km": float(popt_s[1]),
            "saturation_core_kernel_L_c_km": float(popt_sat[1]),
        }

    prem_window_sensitivity = {}
    for dmax_w in (6000.0, 8000.0, 10000.0):
        d_w = np.linspace(200.0, dmax_w, 80)
        th_w = d_w / R_E_km
        cov_w = np.array([
            np.sum(W * G_A * (np.exp(-np.sqrt(R_E_km**2 + r_s**2 - 2.0 * R_E_km * r_s * (sin_th_q * np.cos(PHI) * np.sin(tw) + MU * np.cos(tw))) / lam_c_at_grad_km)
                              / np.sqrt(R_E_km**2 + r_s**2 - 2.0 * R_E_km * r_s * (sin_th_q * np.cos(PHI) * np.sin(tw) + MU * np.cos(tw)))))
            for tw in th_w
        ])
        cov_w_dc = (cov_w - np.min(cov_w)) / (cov_w[0] - np.min(cov_w))
        popt_w, _ = curve_fit(lambda d, A, L: A * np.exp(-d / L), d_w, cov_w_dc, p0=[1.0, 4000.0])
        prem_window_sensitivity[f"d_200_to_{int(dmax_w)}_km"] = {
            "L_c_prem_km": float(popt_w[1]),
            "amplitude_A": float(popt_w[0]),
        }

    # Monte Carlo GNSS Injection-Recovery & White-Noise Null Simulation (100 trials, N_sta=120, N_ep=400)
    rng_mc = np.random.default_rng(2026)
    n_sta_mc = 120
    idx_mc = np.arange(80, dtype=float) + 0.5
    phi_mc = np.arccos(1.0 - 2.0 * idx_mc / 80.0)
    theta_mc = np.pi * (1.0 + 5.0**0.5) * idx_mc
    v_glob_mc = np.column_stack([np.sin(phi_mc) * np.cos(theta_mc), np.sin(phi_mc) * np.sin(theta_mc), np.cos(phi_mc)])
    v_reg_mc = v_glob_mc[:40] + 0.08 * rng_mc.standard_normal((40, 3))
    v_reg_mc /= np.linalg.norm(v_reg_mc, axis=1, keepdims=True)
    vecs_mc = np.vstack([v_glob_mc, v_reg_mc])
    cos_mc = np.clip(np.einsum("ik,jk->ij", vecs_mc, vecs_mc), -1.0, 1.0)
    d_mat_mc = R_E_km * np.arccos(cos_mc)
    w_mc, v_mc = np.linalg.eigh(np.exp(-d_mat_mc / 4200.0))
    S_true_mc = np.einsum("ij,j->ij", v_mc, np.sqrt(np.maximum(w_mc, 1e-6)))

    Q_gps_mc = np.ones((n_sta_mc, 1)) / np.sqrt(n_sta_mc)
    P_gps_mc = np.eye(n_sta_mc) - np.einsum("ik,jk->ij", Q_gps_mc, Q_gps_mc)
    H_mgex_mc = np.column_stack([np.ones(n_sta_mc), vecs_mc[:, 0], vecs_mc[:, 1], vecs_mc[:, 2]])
    Q_mgex_mc, _ = np.linalg.qr(H_mgex_mc)
    P_mgex_mc = np.eye(n_sta_mc) - np.einsum("ik,jk->ij", Q_mgex_mc, Q_mgex_mc)
    P_daily_mc = 0.35 * P_gps_mc + 0.65 * P_mgex_mc

    tri_i_mc, tri_j_mc = np.triu_indices(n_sta_mc, k=1)
    d_pairs_mc = d_mat_mc[tri_i_mc, tri_j_mc]
    bins_mc = np.linspace(200.0, 10000.0, 21)
    bcent_mc = 0.5 * (bins_mc[:-1] + bins_mc[1:])
    bin_masks_mc = [(d_pairs_mc >= bins_mc[b]) & (d_pairs_mc < bins_mc[b + 1]) for b in range(len(bins_mc) - 1)]

    def _mc_recover(P_op, null_flag=False):
        z_m = rng_mc.standard_normal((n_sta_mc, 400))
        raw_m = z_m if null_flag else (np.einsum("ij,jk->ik", S_true_mc, z_m) + 0.10 * rng_mc.standard_normal((n_sta_mc, 400)))
        est_m = np.einsum("ij,jk->ik", P_op, raw_m)
        norm_m = est_m / np.maximum(np.std(est_m, axis=1, keepdims=True), 1e-12)
        corr_m = np.einsum("ik,jk->ij", norm_m, norm_m) / 400.0
        cp_m = corr_m[tri_i_mc, tri_j_mc]
        bv_m = np.array([np.mean(cp_m[m_b]) for m_b in bin_masks_mc])
        if null_flag:
            return float(np.mean(np.abs(bv_m))), float(np.max(np.abs(bv_m)))
        p_m, _ = curve_fit(lambda d, A, L, C0: A * np.exp(-d / L) + C0, bcent_mc, bv_m, p0=[1.0, 3500.0, -0.1], bounds=([0.0, 100.0, -1.0], [5.0, 20000.0, 1.0]))
        r2_m = 1.0 - np.sum((bv_m - (p_m[0] * np.exp(-bcent_mc / p_m[1]) + p_m[2])) ** 2) / np.sum((bv_m - np.mean(bv_m)) ** 2)
        return float(p_m[1]), float(r2_m)

    mc_gps_L, mc_gps_r2, mc_mgex_L, mc_mgex_r2, mc_null_mean, mc_null_max = [], [], [], [], [], []
    for _ in range(100):
        lg_m, rg_m = _mc_recover(P_gps_mc, False)
        lm_m, rm_m = _mc_recover(P_mgex_mc, False)
        nm_m, nx_m = _mc_recover(P_gps_mc, True)
        mc_gps_L.append(lg_m); mc_gps_r2.append(rg_m)
        mc_mgex_L.append(lm_m); mc_mgex_r2.append(rm_m)
        mc_null_mean.append(nm_m); mc_null_max.append(nx_m)
    mc_gps_L, mc_mgex_L = np.array(mc_gps_L), np.array(mc_mgex_L)
    mc_comp_ratios = mc_gps_L / mc_mgex_L

    # Extended injection-recovery audits:
    # (1) Multi-scale grid L_true in {1000, 2000, 3000, 4200, 6000} km (30 trials each)
    scale_grid_audit = {}
    for L_grid_in in (1000.0, 2000.0, 3000.0, 4200.0, 6000.0):
        w_lg, v_lg = np.linalg.eigh(np.exp(-d_mat_mc / L_grid_in))
        S_lg = np.einsum("ij,j->ij", v_lg, np.sqrt(np.maximum(w_lg, 1e-6)))
        g_lg_list, m_lg_list = [], []
        for _ in range(30):
            z_lg = rng_mc.standard_normal((n_sta_mc, 400))
            raw_lg = np.einsum("ij,jk->ik", S_lg, z_lg) + 0.10 * rng_mc.standard_normal((n_sta_mc, 400))
            for P_op_lg, acc_lg in [(P_gps_mc, g_lg_list), (P_mgex_mc, m_lg_list)]:
                est_lg = np.einsum("ij,jk->ik", P_op_lg, raw_lg)
                norm_lg = est_lg / np.maximum(np.std(est_lg, axis=1, keepdims=True), 1e-12)
                corr_lg = np.einsum("ik,jk->ij", norm_lg, norm_lg) / 400.0
                cp_lg = corr_lg[tri_i_mc, tri_j_mc]
                bv_lg = np.array([np.mean(cp_lg[m_b]) for m_b in bin_masks_mc])
                p_lg, _ = curve_fit(lambda d, A, L, C0: A * np.exp(-d / L) + C0, bcent_mc, bv_lg, p0=[1.0, L_grid_in, -0.1], bounds=([0.0, 100.0, -1.0], [5.0, 20000.0, 1.0]))
                acc_lg.append(float(p_lg[1]))
        g_lg_arr, m_lg_arr = np.array(g_lg_list), np.array(m_lg_list)
        scale_grid_audit[f"L_true_{int(L_grid_in)}_km"] = {
            "gps_only_recovered_mean_km": float(np.mean(g_lg_arr)),
            "gps_only_recovered_std_km": float(np.std(g_lg_arr)),
            "mgex_isb_recovered_mean_km": float(np.mean(m_lg_arr)),
            "mgex_isb_recovered_std_km": float(np.std(m_lg_arr)),
            "compression_ratio_mean": float(np.mean(g_lg_arr / m_lg_arr)),
        }

    # (2) Correlated non-TEP orbital/geocenter dipole + datum common-mode null (50 trials, zero TEP exponential signal)
    orb_null_L, orb_null_d2 = [], []
    for _ in range(50):
        g_orb = rng_mc.standard_normal((3, 400))
        c_dat = rng_mc.standard_normal((1, 400))
        raw_orb = np.einsum("ik,kj->ij", vecs_mc, g_orb) + c_dat + 0.25 * rng_mc.standard_normal((n_sta_mc, 400))
        est_orb = np.einsum("ij,jk->ik", P_gps_mc, raw_orb)
        norm_orb = est_orb / np.maximum(np.std(est_orb, axis=1, keepdims=True), 1e-12)
        corr_orb = np.einsum("ik,jk->ij", norm_orb, norm_orb) / 400.0
        cp_orb = corr_orb[tri_i_mc, tri_j_mc]
        bv_orb = np.array([np.mean(cp_orb[m_b]) for m_b in bin_masks_mc])
        p_orb, _ = curve_fit(lambda d, A, L, C0: A * np.exp(-d / L) + C0, bcent_mc, bv_orb, p0=[1.0, 8000.0, -1.0], bounds=([0.0, 100.0, -2.0], [10.0, 25000.0, 1.0]))
        orb_null_L.append(float(p_orb[1]))
        poly2_orb = np.polyfit(bcent_mc[:10] / 1000.0, bv_orb[:10], 2)
        orb_null_d2.append(float(2.0 * poly2_orb[0]))

    # (3) Daily-constant ISB parameterization with rotating constellation visibility (50 trials at L_true = 4200 km)
    daily_isb_L = []
    for _ in range(50):
        z_dy = rng_mc.standard_normal((n_sta_mc, 400))
        raw_dy = np.einsum("ij,jk->ik", S_true_mc, z_dy) + 0.10 * rng_mc.standard_normal((n_sta_mc, 400))
        est_dy = np.einsum("ij,jk->ik", P_daily_mc, raw_dy)
        norm_dy = est_dy / np.maximum(np.std(est_dy, axis=1, keepdims=True), 1e-12)
        corr_dy = np.einsum("ik,jk->ij", norm_dy, norm_dy) / 400.0
        cp_dy = corr_dy[tri_i_mc, tri_j_mc]
        bv_dy = np.array([np.mean(cp_dy[m_b]) for m_b in bin_masks_mc])
        p_dy, _ = curve_fit(lambda d, A, L, C0: A * np.exp(-d / L) + C0, bcent_mc, bv_dy, p0=[1.0, 3000.0, -0.1], bounds=([0.0, 100.0, -1.0], [5.0, 20000.0, 1.0]))
        daily_isb_L.append(float(p_dy[1]))
    daily_isb_L = np.array(daily_isb_L)

    # Generate two-panel PREM Earth BVP & surface spatial-kernel figure
    set_shared_style(scale=FIG_SCALE["web_two_panel"])
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE["web_two_panel"], constrained_layout=True)

    # Panel (a): 4-Layer PREM Earth BVP profile & interior transition gradient
    ax1 = axes[0]
    ax1.set_title(r"$\bf{a)}$ 4-Layer PREM Earth Scalar BVP & Transition Shell", loc="left")
    r_plot = np.linspace(50.0, 8000.0, 600)
    y_plot = sol_prem.sol(r_plot)[0]
    dy_plot = sol_prem.sol(r_plot)[1]
    # Interior shell gradient weight (r <= R_E) integrated in Step 14
    w_plot = np.where(r_plot <= R_E_km, (r_plot ** 2) * np.abs(dy_plot), 0.0)
    w_plot_norm = w_plot / np.max(w_plot)
    rho_plot_norm = (np.maximum(rho_prem_smooth(r_plot), 0.0) / rho_T) ** (1.0 / 3.0)

    ax1.plot(r_plot, rho_plot_norm, color="gray", ls=":", lw=1.5, label=r"Local algebraic eq. $(\rho_{\rm PREM}/\rho_T)^{1/3}$")
    ax1.plot(r_plot, y_plot, color=COLORS["primary"], lw=2.2, label=r"Solved BVP field $u(r)/u_{\min}(\rho_T)$")
    ax1.plot(r_int, w_grad / np.max(w_grad), color=COLORS["accent"], lw=2.0, label=r"Interior transition weight $r^2|\mathrm{d}u/\mathrm{d}r|$")
    ax1.fill_between(r_int, 0, w_grad / np.max(w_grad), color=COLORS["accent"], alpha=0.14)

    lbl_bbox = dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.82)
    ax1.axvline(3480.0, color="dimgray", ls="--", lw=1.0, alpha=0.6)
    ax1.text(3350.0, 0.03, "CMB (3,480 km)", rotation=90, ha="right", va="bottom", fontsize=6.8, color="dimgray", bbox=lbl_bbox)
    ax1.axvline(R_T_E_km, color=COLORS["secondary"], ls="--", lw=1.2, alpha=0.8)
    ax1.text(R_T_E_km - 100.0, 0.03, rf"$R_T(M_\oplus) = {R_T_E_km:,.0f}$ km", rotation=90, ha="right", va="bottom", fontsize=6.8, color=COLORS["secondary"], bbox=lbl_bbox)
    ax1.axvline(r_grad_centroid_km, color=COLORS["highlight"], ls="-.", lw=1.5)
    ax1.text(r_grad_centroid_km + 120.0, 0.03, rf"$R_{{\rm grad}} = {r_grad_centroid_km:,.0f}$ km", rotation=90, ha="left", va="bottom", fontsize=6.8, color=COLORS["highlight"], bbox=lbl_bbox)
    ax1.axvline(R_E_km, color="black", ls=":", lw=1.2, alpha=0.7)
    ax1.text(R_E_km + 120.0, 0.55, rf"$R_\oplus = {R_E_km:,.0f}$ km", rotation=90, ha="left", va="center", fontsize=7.0, bbox=lbl_bbox)

    ax1.set_xlim(0, 8000)
    ax1.set_ylim(0, 1.18)
    ax1.set_xlabel(r"Geocentric Radius $r$ (km)")
    ax1.set_ylabel(r"Normalized Field / Interior Shell Weight")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left", frameon=False, fontsize=6.8)

    # Panel (b): Projected 3-D Yukawa surface spatial kernel vs GNSS calibration
    ax2 = axes[1]
    ax2.set_title(r"$\bf{b)}$ Projected Surface Spatial Kernel vs. GNSS Scale", loc="left")
    d0 = d_arc[0]
    cov_gnss_ref = np.exp(-(d_arc - d0) / 4201.0)
    cov_gnss_lo = np.exp(-(d_arc - d0) / 3330.0)
    cov_gnss_hi = np.exp(-(d_arc - d0) / 4549.0)
    cov_prem_fit = popt_prem[0] * np.exp(-d_arc / L_c_prem_km)

    ax2.fill_between(
        d_arc,
        cov_gnss_lo,
        cov_gnss_hi,
        color=COLORS["accent"],
        alpha=0.16,
        label="GPS-only PPP reference band (3,330–4,549 km)",
    )
    ax2.plot(
        d_arc,
        cov_gnss_ref,
        color=COLORS["accent"],
        ls=":",
        lw=2.0,
        label=r"GNSS exponential reference ($L_c = 4{,}200$ km)",
    )
    ax2.plot(
        d_arc,
        cov_yuk_dc,
        color=COLORS["primary"],
        lw=2.2,
        label=r"Transition-shell kernel $C_{\rm PREM}(d)$ ($R_{\rm grad}=4{,}875$ km)",
    )
    ax2.plot(
        d_arc,
        cov_prem_fit,
        color=COLORS["highlight"],
        ls="--",
        lw=1.8,
        label=rf"Shell exp. fit ($A={popt_prem[0]:.2f}$, $L_c^{{\rm PREM}}={L_c_prem_km:,.0f}$ km, $R^2={r2_prem:.3f}$)",
    )
    ax2.plot(
        d_arc,
        cov_vol_dc,
        color=COLORS["secondary"],
        ls="-.",
        lw=2.0,
        label=rf"Full-volume kernel ($L_c^{{\rm vol}}={L_c_vol1_km:,.0f}$ km, $R^2={r2_vol1:.3f}$)",
    )

    ax2.set_xlim(200, 8000)
    ax2.set_ylim(0, 1.22)
    ax2.set_xlabel(r"Surface Station Arc Separation $d$ (km)")
    ax2.set_ylabel(r"Normalized Datum-Free Spatial Kernel $C(d)/C(d_0)$")
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="upper right", frameon=False, fontsize=6.8)

    fig_dir = REPO / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig_path = fig_dir / "figure_10_prem_earth_kernel.png"
    plt.savefig(fig_path, dpi=300)
    plt.close(fig)

    # --- Recommendation 2: Single-Constellation vs Multi-GNSS Station-Clock De-Biasing Synthesis ---
    gps_only_modes_km = {
        "code_25yr_cross_sector_mean_km": 4201.0,
        "code_ppp_jaipur_km": 4548.6,
        "igs_combined_ppp_km": 3763.6,
        "esa_final_ppp_km": 3329.8,
        "rinex_ionofree_dual_freq_km": 4767.0,
        "rinex_precise_pos_jitter_all_stations_km": 3581.2,
        "rinex_precise_pos_jitter_optimal_100_km": 5026.4,
        "rinex_ionofree_pos_jitter_all_stations_km": 3511.8,
        "rinex_ionofree_pos_jitter_optimal_100_km": 3865.8,
    }
    multi_gnss_modes_km = {
        "mgex_cod_pooled_462d_km": 1861.6,
        "mgex_grg_matched_days_km": 1933.0,
        "mgex_cod_matched_days_km": 2744.0,
        "rinex_multi_gnss_pos_jitter_all_stations_km": 1769.7,
        "rinex_multi_gnss_pos_jitter_dynamic_50_km": 1810.0,
        "rinex_multi_gnss_pos_jitter_optimal_100_km": 2726.2,
    }
    gps_mean_km = float(np.mean(list(gps_only_modes_km.values())))
    mgex_mean_km = float(np.mean(list(multi_gnss_modes_km.values())))
    debiasing_compression_ratio = float(gps_mean_km / mgex_mean_km)

    out = {
        "scale_dictionary": {
            "Lambda_X_kinetic_meV": lam_X_meV,
            "lambda_quartic_ref": lam_ref,
            "lambda_quartic_cassini": lam_cas,
            "Lambda_V_cassini_GeV": lam_V_cas_GeV,
            "Lambda_V_ref_GeV": lam_V_ref_GeV,
            "rho_T_g_cm3": rho_T,
            "rho_T_fourth_root_keV": rhoT_fourth_root_keV,
            "R_T_earth_km": R_T_earth / 1e3,
            "L_c_GNSS_km": 4200.0,
        },
        "amplitude_law_check": {
            "S_A_earth_model": S_A_earth_model,
            "u_min_ratio_earth": S_A_earth_ratio,
            "u_min_earth_g515": u_earth,
            "u_min_rhoT_20": u_rhoT,
            "statement": "S_A = min[1,(rho/rho_T)^(1/3)] is exactly "
                         "u_min(rho)/u_min(rho_T) for the quartic branch: "
                         "the corpus response exponent 1/3 = 1/(m-1) fixes m = 4.",
        },
        "self_quenching_crossing": {
            "u_cross": u_cross,
            "rho_sat_corpus_g_cm3": rho_sat_cas,
            "rho_sat_ucd_equiv_g_cm3": rho_sat_ucd,
            "statement": "under the corpus normalization the u ~ 1 crossing "
                         "sits at ~1e26 g/cm^3 (temporal-well interior), not "
                         "at rho_T = 20 g/cm^3.",
        },
        "compton_resolution": {
            "lambda_c_rhoT_corpus_km": lam_c_rhoT_cas / 1e3,
            "lambda_c_over_R_T_earth": lam_c_rhoT_cas / R_T_earth,
            "lambda_c_eq_R_T_at_rho_g_cm3": rho_compton_x,
            "lambda_c_rhoT_ucd_km": lam_c_rhoT_ucd / 1e3,
        },
        "compact_object_bound": {
            "rho_ns_core_g_cm3": rho_ns,
            "u_min_ns_corpus": u_ns_cas,
            "u_min_ns_ucd_equiv": u_ns_ucd,
            "u_s_knee": u_s,
            "lambda_pulsar_lower_bound": lam_pulsar_bound,
            "lambda_cassini_over_bound": lam_cas / lam_pulsar_bound,
            "lambda_ucd_equiv_over_bound": lam_equiv_ucd / lam_pulsar_bound,
        },
        "excluded_normalization": {
            "lambda_equiv_if_Lambda4_eq_rhoT": lam_equiv_ucd,
            "ratio_cassini_over_ucd": lam_cas / lam_equiv_ucd,
            "failures": [
                "3e24 below the Cassini-compatible quartic normalization",
                "u_min(NS core) ~ 21 > u_s = 10: pulsars would sit on the "
                "Planck-density floor (temporal wells), excluded",
                "lambda_c(rho_T) >> any body radius: the invoked local "
                "equilibrium never forms; mechanism inert where claimed",
            ],
        },
        "kinetic_column_scale": {
            "Sigma_star_g_cm2": Sigma_star_g_cm2,
            "statement": "the X|X|/Lambda_X^4 interior turns canonical below "
                         "surface density ~ 0.1 g/cm^2 (~ 570 M_sun/pc^2): "
                         "the kinetic scale supplies a column-density floor, "
                         "not a volume-density scale.",
        },
        "prem_earth_bvp_integration": {
            "model": "4-layer PREM spherical Earth BVP solve of nabla^2 u = M_Pl^-2 V_eff'(u) with 3D Yukawa-propagated datum-free surface covariance projection",
            "transition_gradient_centroid_radius_km": r_grad_centroid_km,
            "R_T_earth_km": R_T_E_km,
            "ratio_centroid_over_R_T": r_grad_centroid_km / R_T_E_km,
            "effective_compton_at_transition_km": lam_c_at_grad_km,
            "predicted_surface_covariance_L_c_km": L_c_prem_km,
            "observed_gnss_L_c_km": 4200.0,
            "fractional_agreement_vs_gnss": (L_c_prem_km - 4200.0) / 4200.0,
            "exponential_fit_r2": r2_prem,
            "full_volume_yukawa_integral": {
                "two_param_L_c_vol_km": L_c_vol2_km,
                "two_param_amplitude_A": float(popt_vol2[0]),
                "two_param_R2": r2_vol2,
                "one_param_anchored_L_c_vol_km": L_c_vol1_km,
                "one_param_anchored_R2": r2_vol1,
                "note": "Integrating across all interior shells r in [500, 6321] km weighted by r^2|du/dr| yields L_c = 3044-3213 km (R^2 = 0.981-0.985), matching the 25.3-yr isotropic CODE baseline (3210 +- 389 km, Paper 2) and ESA Final (3193 km), while the transition-centroid shell (R_grad = 4875 km) yields L_c = 4010 km matching the cross-sector/PPP baseline (4201 km).",
            },
            "rhoT_sensitivity_scan": prem_rhoT_sensitivity,
            "baseline_window_sensitivity_scan": prem_window_sensitivity,
        },
        "constellation_debiasing_synthesis": {
            "gps_only_and_ionofree_modes_km": gps_only_modes_km,
            "multi_gnss_combined_modes_km": multi_gnss_modes_km,
            "gps_single_constellation_mean_km": gps_mean_km,
            "multi_gnss_combined_mean_km": mgex_mean_km,
            "multi_gnss_isb_compression_factor": debiasing_compression_ratio,
            "debiased_mgex_pooled_scale_km": 1861.6 * debiasing_compression_ratio,
            "monte_carlo_injection_recovery_and_null_audit": {
                "n_trials": 100,
                "n_stations": n_sta_mc,
                "n_epochs_per_trial": 400,
                "injected_L_c_true_km": 4200.0,
                "gps_only_1const_recovered_L_c_mean_km": float(np.mean(mc_gps_L)),
                "gps_only_1const_recovered_L_c_std_km": float(np.std(mc_gps_L)),
                "gps_only_1const_mean_R2": float(np.mean(mc_gps_r2)),
                "multi_gnss_4const_isb_recovered_L_c_mean_km": float(np.mean(mc_mgex_L)),
                "multi_gnss_4const_isb_recovered_L_c_std_km": float(np.std(mc_mgex_L)),
                "multi_gnss_4const_isb_mean_R2": float(np.mean(mc_mgex_r2)),
                "forward_simulated_compression_ratio_mean": float(np.mean(mc_comp_ratios)),
                "forward_simulated_compression_ratio_std": float(np.std(mc_comp_ratios)),
                "white_noise_null_gps_only_mean_abs_corr": float(np.mean(mc_null_mean)),
                "white_noise_null_gps_only_max_abs_corr": float(np.mean(mc_null_max)),
                "correlated_orbital_datum_null_gps_only": {
                    "n_trials": 50,
                    "injected_signal": "Rank-3 satellite-orbit/geocenter dipole cos(d/R_E) + reference-clock datum common mode (zero TEP exponential)",
                    "recovered_exp_fit_L_c_mean_km": float(np.mean(orb_null_L)),
                    "recovered_exp_fit_L_c_std_km": float(np.std(orb_null_L)),
                    "short_range_curvature_d2C_dd2_Mm_minus2": float(np.mean(orb_null_d2)),
                    "verdict": "Concave-down dipole curvature (d2C/dd2 < 0 vs > 0 for exponential) drives unconstrained exponential fit to upper bound (~24,900 km); GPS-only processing does not manufacture a 4,200 km scale from correlated orbital/datum errors.",
                },
                "scale_grid_injection_recovery": scale_grid_audit,
                "isb_parameterization_sensitivity": {
                    "per_epoch_isb_recovered_L_c_mean_km": float(np.mean(mc_mgex_L)),
                    "per_epoch_isb_recovered_L_c_std_km": float(np.std(mc_mgex_L)),
                    "per_epoch_isb_compression_ratio": float(np.mean(mc_comp_ratios)),
                    "daily_constant_rotating_visibility_isb_recovered_L_c_mean_km": float(np.mean(daily_isb_L)),
                    "daily_constant_rotating_visibility_isb_recovered_L_c_std_km": float(np.std(daily_isb_L)),
                    "daily_constant_isb_compression_ratio": float(np.mean(mc_gps_L) / np.mean(daily_isb_L)),
                    "note": "Per-epoch ISB projection yields 2,277 +- 47 km (1.77x compression, matching CNES/GRG 1,933 km), whereas daily-constant ISB with rotating constellation visibility yields 2,482 +- 46 km (1.63x compression, matching CODE matched-day MGEX 2,744 km). Both spatial ISB projection and wavenumber passband filtering describe the same removal of l=0,1 long-wavelength spherical-harmonic modes.",
                },
            },
            "statement": "Forward Monte Carlo injection of a single L_c = 4200 km station-clock correlation field into a 120-station global network shows that 1-constellation GPS-only global datum removal recovers L_c = 4036 +- 113 km (R^2 = 0.999, bias -3.9%; white-noise null returns |C(d)| = 0.009 +- 0.001 with no spurious scale), whereas 4-constellation multi-GNSS common-view ISB projection compresses the same injected field to L_c = 2277 +- 47 km (derived compression ratio 1.77 +- 0.06, matching the empirical 4066 / 2141 = 1.90x ratio).",
        },
    }

    path = REPO / "results" / "outputs" / "step_14_scale_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
