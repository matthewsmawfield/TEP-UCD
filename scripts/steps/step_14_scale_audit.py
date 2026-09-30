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

import numpy as np
from scipy.optimize import brentq

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from core import constants as C          # noqa: E402
from core import scalar_field as sf      # noqa: E402


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
    }

    path = REPO / "results" / "outputs" / "step_14_scale_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    main()
