"""Step 16: Unscreened-Planet Interior Solve — Saturn (and Jupiter cross-check).

The corpus's nonlinear 1-D spherical Picard solve (Step 14) was executed only
for Earth (S = 0.651, PREM). Saturn is the least-screened major planet
(S = 0.314) and the only body with seismically measured interior clocks
(C-ring kronoseismology 10h33m38s, Mankovich et al. 2019; PV frame 10h34m13s,
Read et al. 2009; drifting SKR 10.6-10.8 hr). This step solves the same
damped Picard two-branch operator nabla.(P_,X nabla u) = m^2 u on a Lane-Emden
polytropic interior normalized to each planet's measured mass, volumetric
radius, and moment-of-inertia factor, and reports:

  * the r^2-weighted interior gradient centroid R_grad vs R_T(M),
  * the u(r) profile at the TEP saturation radius R_T, the diffuse-core
    boundary, the wind-decay base, and the surface,
  * the implied interior "clock gradient" (fractional field variation across
    depths) as the dynamical quantity the layered-clock data probe,
  * Picard convergence residual.

Outputs: results/outputs/step_16_saturn_interior.json
         results/figures/figure_12_saturn_interior.png
"""

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.linalg import solve_banded
from scipy.integrate import solve_ivp

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from utils.logger import print_status  # noqa: E402

G = 6.6743e-11
C_LIGHT = 299792458.0
G_T = 3.40e-10
V_GAL = 220.0e3
RHO_T = 20.0  # g/cm^3
RHO_T_SI = RHO_T * 1e3  # kg/m^3


def r_t_km_from_mass(M_kg):
    """Exact TEP saturation radius R_T(M) = (3 M / 4 pi rho_T)^(1/3) in km."""
    return float(((3.0 * M_kg) / (4.0 * np.pi * RHO_T_SI)) ** (1.0 / 3.0) / 1e3)


def lane_emden_density(n_eff, R_km, M_kg, N=4000):
    """Return rho(r) [g/cm^3] on an N-point radius grid [km] for a polytrope
    of index n_eff normalized to total mass M_kg within radius R_km."""
    def rhs(xi, y):
        th, dth = y
        return [dth, 0.0 if th <= 0 else -(th ** n_eff) - (2.0 / xi) * dth]
    def ev(xi, y):
        return y[0]
    ev.terminal = True
    ev.direction = -1
    xi0 = 1e-5
    sol = solve_ivp(rhs, [xi0, 30.0], [1.0 - xi0**2 / 6.0, -xi0 / 3.0],
                    events=ev, max_step=0.01, rtol=1e-10, atol=1e-12)
    xi1 = float(sol.t[-1])
    r = np.linspace(0.0, R_km, N)
    x = np.clip(r / R_km * xi1, xi0, xi1 * 0.999999)
    th = np.interp(x, sol.t, np.maximum(sol.y[0], 0.0))
    rho_prof = th ** n_eff
    rho_prof[x > sol.t[-1]] = 0.0
    # normalize so 4 pi int rho r^2 dr = M
    m_int = 4.0 * np.pi * np.trapezoid(rho_prof * (r * 1e3) ** 2, r * 1e3)
    rho_c = M_kg / m_int  # kg/m^3
    return r, rho_prof * rho_c / 1e3  # g/cm^3


def solve_nl_interior(R_phys_km, rho_r_km, rho_g_cm3, N_g=1600, n_it=200, om=0.35):
    """Damped Picard solve of the nonlinear two-branch operator on a planet's
    density profile. Constants follow the Step-14 PREM normalization:
    ueq = 6.881e-9 (rho/rho_T)^(1/3); m^2 = (rho/rho_T)^(2/3)/lam_c^2 inside,
    vacuum 1/lam_vac^2 outside; stiffness w = 1 + 0.35 sqrt(xi) + 0.15 xi."""
    r_max = 1.6 * R_phys_km
    rk = np.linspace(max(20.0, R_phys_km / 500.0), r_max, N_g)
    dr_k = rk[1] - rk[0]
    rp = np.interp(rk, rho_r_km, rho_g_cm3, left=rho_g_cm3[0], right=0.0)
    rp[rk > R_phys_km] = 0.0
    ueq = 6.881e-9 * (np.maximum(rp, 0.0) / RHO_T) ** (1.0 / 3.0)
    msq = np.where(rp > 0, ((rp / RHO_T) ** (2.0 / 3.0)) / (2478.5 ** 2), 1.0 / (7808.0 ** 2))
    uv = ueq.copy()
    sc_ref = 6.881e-9 / 1000.0
    du_r = 0.0
    for _ in range(n_it):
        up = uv.copy()
        g_u = np.gradient(uv, dr_k)
        xi_r = (np.abs(g_u) / sc_ref) ** 2
        wnl = 1.0 + 0.35 * np.sqrt(xi_r) + 0.15 * xi_r
        wh = 0.5 * (wnl[:-1] + wnl[1:]) * ((0.5 * (rk[:-1] + rk[1:])) ** 2)
        dg = np.zeros(N_g); lw = np.zeros(N_g - 1); ub = np.zeros(N_g - 1); rh = np.zeros(N_g)
        dg[0] = 1.0; rh[0] = ueq[0]
        r2_v = (rk[1:-1] ** 2) * (dr_k ** 2)
        cl = wh[:-1] / r2_v; cr = wh[1:] / r2_v
        dg[1:-1] = cl + cr + msq[1:-1]
        lw[:-1] = -cl; ub[1:] = -cr
        rh[1:-1] = msq[1:-1] * ueq[1:-1]
        dg[-1] = 1.0; rh[-1] = 0.0
        ab = np.zeros((3, N_g)); ab[0, 1:] = ub; ab[1, :] = dg; ab[2, :-1] = lw
        un = solve_banded((1, 1), ab, rh)
        uv = (1.0 - om) * up + om * un
        du_r = float(np.max(np.abs(uv - up)) / np.max(np.abs(uv)))
    gu = np.gradient(uv, dr_k)
    m = rk <= R_phys_km
    r_grad = float(np.sum(rk[m] * np.abs(gu[m]) * rk[m] ** 2) / np.sum(np.abs(gu[m]) * rk[m] ** 2))
    return rk, rp, uv, gu, r_grad, du_r


def main():
    raw_planets = [
        # (name, M_kg, R_vol_km, R_eq_km, n_eff, k_moi, extra_marks_frac)
        ("Saturn",          5.6834e26, 58232.0, 60268.0, 1.375, 0.2181, {"diffuse_core_outer_0.6R": 0.6, "wind_decay_base_0.825R": 0.825}),
        ("Jupiter",         1.89813e27,69911.0, 71492.0, 0.979, 0.26393,{"dilute_core_0.45R": 0.45, "wind_decay_base_0.95R": 0.95}),
        ("Uranus",          8.6810e25, 25362.0, 25559.0, 1.313, 0.225,  {}),
        ("Neptune",         1.02413e26,24622.0, 24764.0, 1.181, 0.240,  {}),
        ("Earth_polytrope", 5.9722e24,  6371.0,  6378.1, 0.465, 0.3307, {}),
        ("Venus",           4.8673e24,  6051.8,  6051.8, 0.470, 0.330,  {}),
        ("Mercury",         3.3011e23,  2439.7,  2439.7, 0.357, 0.346,  {}),
    ]
    planets = {}
    for nm, m_kg, r_vol, r_eq, n_e, k_m, m_fracs in raw_planets:
        rt_k = r_t_km_from_mass(m_kg)
        mks = {"R_T": rt_k}
        for mk_lbl, frac in m_fracs.items():
            mks[mk_lbl] = frac * r_vol
        planets[nm] = dict(M=m_kg, R_vol=r_vol, R_eq=r_eq, n_eff=n_e, k_moi=k_m, R_T=rt_k, marks=mks)

    results = {}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    groups = [["Saturn", "Jupiter", "Uranus", "Neptune"], ["Earth_polytrope", "Venus", "Mercury"]]
    for ax, group in zip(axes, groups):
        for name in group:
            p = planets[name]
            rr, rho = lane_emden_density(p["n_eff"], p["R_vol"], p["M"], N=6000)
            rk, rp, uv, gu, r_grad, du_r = solve_nl_interior(p["R_vol"], rr, rho)
            rho_c = float(rho[0]); rho_mean = float(p["M"] / (4.0 / 3.0 * np.pi * (p["R_vol"] * 1e3) ** 3) / 1e3)
            inside = rk <= p["R_vol"]
            u_at = {k: float(np.interp(v, rk, uv)) for k, v in p["marks"].items()}
            u_surf = float(np.interp(p["R_vol"], rk, uv))
            clock_grad = {k: float(u_at[k] / u_surf - 1.0) for k in u_at}
            results[name] = {
                "n_eff": p["n_eff"],
                "R_vol_km": p["R_vol"],
                "R_eq_km": p["R_eq"],
                "R_T_km": round(p["R_T"], 2),
                "S_screening": round(p["R_T"] / p["R_eq"], 4),
                "S_screening_volumetric": round(p["R_T"] / p["R_vol"], 4),
                "rho_c_g_cm3": round(rho_c, 3),
                "rho_mean_g_cm3": round(rho_mean, 3),
                "rho_c_over_rho_T": round(rho_c / RHO_T, 3),
                "interior_fully_unscreened_rho_below_rho_T_everywhere": bool(rho_c < RHO_T),
                "picard_convergence_du_inf": du_r,
                "gradient_centroid_R_grad_km": round(r_grad, 1),
                "R_grad_over_R_T": round(r_grad / p["R_T"], 4),
                "R_grad_over_R_vol": round(r_grad / p["R_vol"], 4),
                "u_surface": u_surf,
                "u_at_marks": u_at,
                "interior_clock_gradient_fractional": clock_grad,
                "interior_u_max_over_u_surf": round(float(np.max(uv[inside]) / u_surf), 4),
            }
            ax.plot(rk[inside] / p["R_vol"], np.maximum(uv[inside] / u_surf, 1e-12), lw=2,
                    label=fr"{name}: $R_{{\rm grad}}$={r_grad/p['R_vol']:.3f} $R$")
            ax.axvline(p["R_T"] / p["R_vol"], ls="--", lw=1.0, alpha=0.6)
            ax.axvline(r_grad / p["R_vol"], ls=":", lw=1.0, alpha=0.6)
        ax.set_xlabel(r"$r/R_{\rm vol}$")
        ax.set_ylabel(r"$u(r)/u(R_{\rm surf})$")
        ax.set_title("Giants" if "Saturn" in group else "Terrestrials")
        ax.legend(fontsize=8)
        ax.set_ylim(bottom=0)

    fig.suptitle("Unscreened-Planet Interior Field Solve (Step 16): nonlinear two-branch Picard BVP")
    fig.tight_layout()
    fpath = REPO / "results" / "figures" / "figure_12_saturn_interior.png"
    fig.savefig(fpath, dpi=300)
    plt.close(fig)
    print_status(f"Saved figure to {fpath}", "SUCCESS")

    # Saturn ring co-rotation audit: which clock's co-rotation surface crosses the ring plane
    # at the Cassini Division? a_sync(T) = (GM T^2 / 4 pi^2)^(1/3).
    M_sat = planets["Saturn"]["M"]
    R_T_sat_km = planets["Saturn"]["R_T"]
    R_T_sat_m = R_T_sat_km * 1e3
    v_tep_sat_m_s = float(G * M_sat / (R_T_sat_m * V_GAL))
    T_tep_sat_hr = float(2.0 * np.pi * (planets["Saturn"]["R_eq"] * 1e3) / (v_tep_sat_m_s * 3600.0))

    def a_sync_km(T_hr, M_body=M_sat):
        return float((G * M_body * (T_hr * 3600.0) ** 2 / (4.0 * np.pi ** 2)) ** (1.0 / 3.0) / 1e3)

    def roche_km(rho_m_g_cm3, R_T_p_km=R_T_sat_km):
        return float(2.456 * R_T_p_km * ((RHO_T / rho_m_g_cm3) ** (1.0 / 3.0)))

    B_in, B_out, CD_out, A_out, F_ring, C_in = 91975.0, 117580.0, 122170.0, 136775.0, 140180.0, 74658.0
    a_mimas_2_1 = float(185539.0 * (0.5) ** (2.0 / 3.0))

    # Dynamic 4-giant-planet co-rotation vs main-ring outer edge comparison:
    omega_T_val = float(np.sqrt(4.0 * np.pi * G * RHO_T_SI / 3.0))
    eta_0_val = 0.12905
    giant_ring_specs = [
        ("Jupiter", 129000.0, True),
        ("Saturn",  A_out,    False),
        ("Uranus",  51149.0,  False),
        ("Neptune", 62933.0,  False),
    ]
    four_giants_ring_corot = {}
    for g_nm, a_r_out, is_soliton_cap in giant_ring_specs:
        gp = planets[g_nm]
        if is_soliton_cap:
            v_2br = float(eta_0_val * ((gp["R_T"] * 1e3) ** 2) * omega_T_val / (gp["k_moi"] * gp["R_eq"] * 1e3))
        else:
            v_2br = float(G * gp["M"] / ((gp["R_T"] * 1e3) * V_GAL))
        t_2br_hr = float(2.0 * np.pi * (gp["R_eq"] * 1e3) / (v_2br * 3600.0))
        a_sy = a_sync_km(t_2br_hr, gp["M"])
        entry_g = {
            "a_ring_outer_km": a_r_out,
            "a_sync_TEP_km": round(a_sy, 1),
            "main_rings_span_corotation": bool(a_r_out > a_sy),
        }
        if g_nm == "Uranus":
            belinda_puck_mid = 0.5 * (75255.0 + 86004.0)
            entry_g["belinda_puck_gap_midpoint_km"] = belinda_puck_mid
            entry_g["a_sync_vs_belinda_puck_midpoint_pct"] = round(100.0 * (a_sy / belinda_puck_mid - 1.0), 2)
        four_giants_ring_corot[g_nm] = entry_g

    # Dynamic ring mass, screening shell, surface density, and particle-size window calculations:
    M_rings_obs = 1.54e19
    M_rings_err = 0.49e19
    u_T_sat = float(G * M_sat / (R_T_sat_m * (C_LIGHT ** 2)))
    S_sat_eq = float(R_T_sat_km / planets["Saturn"]["R_eq"])
    two_k_over_S_sat = float(2.0 * planets["Saturn"]["k_moi"] / S_sat_eq)
    M_rings_tep = float(u_T_sat * M_sat)
    M_rings_tep_2kS = float(two_k_over_S_sat * M_rings_tep)
    z_rings_tep = float((M_rings_tep - M_rings_obs) / M_rings_err)
    r_star_rings_obs_km = float(np.sqrt(G * M_rings_obs / G_T) / 1e3)
    r_star_rings_lo_km = float(np.sqrt(G * (M_rings_obs - M_rings_err) / G_T) / 1e3)
    r_star_rings_hi_km = float(np.sqrt(G * (M_rings_obs + M_rings_err) / G_T) / 1e3)
    r_star_rings_tep_km = float(np.sqrt(G * M_rings_tep / G_T) / 1e3)

    area_BA_m2 = float(np.pi * (((A_out * 1e3) ** 2) - ((B_in * 1e3) ** 2)))
    Sigma_tep_si = float(M_rings_tep / area_BA_m2)
    Sigma_obs_si = float(M_rings_obs / area_BA_m2)
    Omega_B_rad_s = float(np.sqrt(G * M_sat / ((105000.0e3) ** 3)))
    R_min_lo_mm = float(3.0 * G_T / (4.0 * np.pi * G * 900.0) * 1e3)
    R_min_hi_mm = float(3.0 * G_T / (4.0 * np.pi * G * 500.0) * 1e3)
    R_max_tep_m = float(2.0 * np.pi * G * Sigma_tep_si / (Omega_B_rad_s ** 2))
    R_max_obs_m = float(2.0 * np.pi * G * Sigma_obs_si / (Omega_B_rad_s ** 2))
    g_sheet_tep = float(2.0 * np.pi * G * Sigma_tep_si)
    g_sheet_B_lo = float(2.0 * np.pi * G * 700.0)
    g_sheet_B_hi = float(2.0 * np.pi * G * 1000.0)

    corotation = {
        "kronoseismology_10h33m38s": a_sync_km(10.5606),
        "voyager_SystemIII_10h39m24s": a_sync_km(10.6567),
        "SKR_slow_10h48m": a_sync_km(10.8),
        "TEP_ambient_11h33m": a_sync_km(T_tep_sat_hr),
        "B_ring_outer_edge_km": B_out,
        "Cassini_division_outer_edge_km": CD_out,
        "Mimas_2_1_ILR_km": a_mimas_2_1,
        "TEP_ambient_sync_inside_Cassini_division": bool(B_out < a_sync_km(T_tep_sat_hr) < CD_out),
        "TEP_ambient_sync_vs_B_edge_pct": round(100.0 * (a_sync_km(T_tep_sat_hr) / B_out - 1.0), 2),
        "TEP_ambient_sync_vs_Mimas_2_1_pct": round(100.0 * (a_sync_km(T_tep_sat_hr) / a_mimas_2_1 - 1.0), 2),
        "interior_clock_sync_vs_B_edge_pct": round(100.0 * (a_sync_km(10.5606) / B_out - 1.0), 2),
        "four_giant_planets_main_ring_vs_corotation": four_giants_ring_corot,
        "roche_R_T_cancellation_A_ring_over_R_T": round(A_out / R_T_sat_km, 3),
        "roche_R_T_cancellation_F_ring_over_R_T": round(F_ring / R_T_sat_km, 3),
        "compositional_sorting_and_ring_microphysics_audit": {
            "roche_boundaries_from_R_T_km": {
                "iron_core_5p0_g_cm3": round(roche_km(5.0), 0),
                "C_ring_inner_edge_observed_km": C_in,
                "silicate_rock_3p3_g_cm3": round(roche_km(3.3), 0),
                "hydrated_silicate_2p7_g_cm3": round(roche_km(2.7), 0),
                "C_to_B_ring_boundary_observed_km": B_in,
                "solid_water_ice_0p92_g_cm3": round(roche_km(0.92), 0),
                "porous_water_ice_0p75_g_cm3": round(roche_km(0.75), 0),
                "A_ring_outer_edge_observed_km": A_out,
            },
            "ring_mass_and_screening_shell": {
                "M_rings_obs_kg_Iess2019": M_rings_obs,
                "M_rings_obs_err_kg": M_rings_err,
                "M_rings_TEP_uT_M_Sat_kg": round(M_rings_tep, 3),
                "M_rings_TEP_2k_over_S_uT_M_Sat_kg": round(M_rings_tep_2kS, 3),
                "z_score_uT_M_Sat_vs_Iess2019": round(z_rings_tep, 2),
                "r_star_M_rings_obs_km": round(r_star_rings_obs_km, 1),
                "r_star_M_rings_1sigma_range_km": [round(r_star_rings_lo_km, 1), round(r_star_rings_hi_km, 1)],
                "r_star_M_rings_TEP_km": round(r_star_rings_tep_km, 1),
                "Hyperion_a_orb_km": 1481009.0,
            },
            "ring_surface_density_and_particle_size_window": {
                "Sigma_TEP_mean_B_plus_A_g_cm2": round(Sigma_tep_si / 10.0, 2),
                "Sigma_obs_mean_B_plus_A_g_cm2": round(Sigma_obs_si / 10.0, 2),
                "R_min_grain_g_surf_eq_gt_mm_range": [round(R_min_lo_mm, 2), round(R_min_hi_mm, 2)],
                "R_max_wake_2pi_G_Sigma_over_Omega2_TEP_m": round(R_max_tep_m, 2),
                "R_max_wake_2pi_G_Sigma_over_Omega2_obs_m": round(R_max_obs_m, 2),
                "observed_particle_size_range": "1 mm - 1 cm lower cutoff to 5 - 10 m upper cutoff and vertical thickness (Zebker et al. 1985)",
                "sheet_acceleration_2pi_G_Sigma_TEP_m_s2": float(f"{g_sheet_tep:.3e}"),
                "sheet_acceleration_B_core_70_to_100_g_cm2_m_s2": [float(f"{g_sheet_B_lo:.3e}"), float(f"{g_sheet_B_hi:.3e}")],
                "Cassini_Grand_Finale_empirical_acceleration_Iess2019_m_s2": 4.0e-7,
            },
        },
        "assessment": (
            "Across the four ringed giant planets, ONLY Saturn has a_ring_outer > a_sync so that "
            "its dense main ring sheet physically spans the co-rotation zone (for Jupiter, Uranus, "
            "and Neptune, the main rings terminate inside a_sync). At Saturn, three radii converge "
            "within ~1.5%: Mimas 2:1 ILR (116,882 km), the ambient-clock co-rotation (118,425 km = "
            "2.034 R_S), and the B-ring outer edge (117,580 km), placing the Cassini Division at "
            "the intersection of the moon-resonance and the ambient-branch co-rotation surface."),
    }

    out = {"step": "step_16_saturn_interior", "results": results,
           "saturn_ring_corotation_audit": corotation,
           "comparison_earth_prem_step14": {
               "S_earth": 0.651, "R_grad_km": 4810.0, "R_grad_over_R_T": 1.160,
               "note": "Earth (screened-side, PREM) for reference from Step 14."},
           "interpretation": (
               "For unscreened interiors (rho < rho_T everywhere), the field gradient tracks the "
               "density profile and the r^2-weighted gradient centroid R_grad marks where the "
               "interior temporal structure concentrates. Compare R_grad/R_T between Saturn "
               "(S=0.314, ambient branch) and Jupiter (S=0.405, soliton branch).")}
    opath = REPO / "results" / "outputs" / "step_16_saturn_interior.json"
    opath.write_text(json.dumps(out, indent=2))
    print_status(f"Saved numerical outputs to {opath}", "SUCCESS")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
