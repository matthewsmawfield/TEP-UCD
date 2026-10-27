# Temporal Topology Saturation Scale: Cross-Scale Consistency of ρ_T

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18064365.svg)](https://doi.org/10.5281/zenodo.18064365)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

![Temporal Topology Saturation Scale](site/public/og-image.jpg)

**Author:** Matthew Lukin Smawfield
**Version:** v0.11 (New Delhi)
**First published:** 28 December 2025 · **Last updated:** 26 October 2026
**Status:** Preprint
**DOI:** [10.5281/zenodo.18064365](https://doi.org/10.5281/zenodo.18064365)
**Website:** [https://mlsmawfield.com/tep/ucd/](https://mlsmawfield.com/tep/ucd/)

## Abstract

<!-- Generated from site/components/1_abstract.html; update the manuscript source, then run tools/sync_current_corpus_readmes.py. -->

Gravitational anomalies across astrophysical scales exhibit a dual scaling regularity: the radius at which Newtonian dynamics fails scales as $R_T(M) = (3M/4\pi\rho_T)^{1/3} \propto M^{1/3}$ in the compact saturation regime and $R_{\rm DM} \propto M^{1/2}$ in the low-acceleration galactic regime. Within the Temporal Equivalence Principle (TEP) two-branch scalar action ($P(X,\phi) = P_{\rm kin}(X) - \tfrac{1}{4}\lambda M_{\rm Pl}⁴ u⁴$, $A(u) = e^{-u}$), the quartic confining potential fixes the cubic screening response $S = (\bar\rho/\rho_T)^{1/3}$ around the saturation density $\rho_T \approx 20$ g/cm³ (calibrated from terrestrial GNSS and tested across astrophysical systems), while the nonlinear kinetic branch $P_{,X}(\xi) = k\sqrt{\xi} + 2\xi$ ($k = 16.03$) governs unscreened ($S \ll 1$) galactic halos at $a_{\rm eff} = 1.20 \times 10^{-10}$ m s$^{-2}$ (predicting a star-forming spiral BBH host tracking fraction $\langle\epsilon_{\rm host}\rangle_{\rm SFR}^{\rm UCD} = 0.236 \pm 0.054$ [$0.197$ with $25\%$ bulge/NSC hosts] that matches the GWTC-1–5.0 optimum in Paper 22). Across a 4-layer PREM Earth boundary-value problem and 1-D spherical nonlinear Picard solve, the transition-shell ($4{,}010$ km; $3{,}957$ km nonlinear) and full-volume ($3{,}213$ km; $3{,}170$ km nonlinear, $L_c^{\rm vol}/R_T = 0.775$) kernels reproduce both the 25.3-year GPS PPP clock correlation length ($L_c = 4{,}201$ km, $\hat\rho_T = 19.2$ g/cm³) and 2023 CDDIS RINEX3 single-constellation GPS, Galileo, and GLONASS reprocessing ($3{,}853$ km $\sqrt{N}$-weighted, and $3{,}155 \pm 181$ km [$\mathrm{CV} = 5.7\%$] under full-day $\ell = 0$ common-mode removal, mapping via $L_c^{\rm vol}/R_T$ to $\hat\rho_T = 21.1$ g/cm³).

With $\rho_T = 20$ g/cm³ and $a_{\rm eff}$ held fixed and zero per-object refitting, three independent cross-scale tests follow. First, in 175 SPARC galaxies, an a priori Freeman-disk split separates 3-D rising-core onset scaling ($\alpha_{\rm rising} = 0.256 \pm 0.069$ vs. $1/3$) from 2-D Keplerian tails ($\alpha_{\rm tail} = 0.581 \pm 0.086$ vs. $1/2$; $p = 0.0031$), while the coupled-gradient force law reproduces the radial-acceleration ($0.1330$ dex RMS) and Baryonic Tully–Fisher ($R² = 0.956, 0.0807$ dex) relations. Second, four external $R_\oplus$-free astrophysical catalogs — outer-giant-planet spin ($19.89$ g/cm³), the brown-dwarf rotational period floor ($1.150 \pm 0.075$ hr vs. TEP-saturated Chandrasekhar–Jacobi $1.155$ hr [$20.19$ g/cm³], sitting $8.3\sigma$ above the unscreened Newtonian Jacobi instability limit of $0.527$ hr), compressed terrestrial moments of inertia ($17.89$ g/cm³), and the Solar Model S convection-zone base ($0.713\,R_\odot$ vs. $\sqrt{3}R_T(M_\odot) = 0.715\,R_\odot$ [$20.15$ g/cm³]) — converge with GNSS to $\hat\rho_T = 19.59 \pm 1.10$ g/cm³ ($19.68 \pm 1.25$ g/cm³ GNSS-free; $20.05 \pm 1.61$ g/cm³ $v_{\rm gal}$-marginalized; look-elsewhere $p = 2.9 \times 10^{-4}$ [$3.6\sigma$], $2.05\%$ leave-one-channel-out blind prediction RMS). Third, the horizon crossover $R_T(M_\times) = R_S$ occurs at $M_\times \approx 3.04 \times 10⁷\,M_\odot$, matching the runaway black hole candidate RBH-1.

Keywords: Temporal Equivalence Principle — dark matter: phantom mass — gravitation: modified — atomic clocks: GNSS — galaxies: kinematics and dynamics (SPARC) — planetary systems: rotation — compact objects: screening

Current manuscript source: [1_abstract.html](site/components/1_abstract.html).

## Key Findings

The current findings, numerical results and comparison assumptions are reported in [9. Conclusion](site/components/11_conclusion.html). The abstract above is synchronized from the current manuscript.

## The TEP Research Program

| Paper | Repository | Title | DOI |
|-------|-----------|-------|-----|
| **Paper 0** | [TEP](https://github.com/matthewsmawfield/TEP) | Temporal Equivalence Principle: Dynamic Time & Emergent Light Speed | [10.5281/zenodo.16921911](https://doi.org/10.5281/zenodo.16921911) |
| **Paper 1** | [TEP-GNSS](https://github.com/matthewsmawfield/TEP-GNSS) | Global Time Echoes: Distance-Structured Correlations in GNSS Clocks | [10.5281/zenodo.17127229](https://doi.org/10.5281/zenodo.17127229) |
| **Paper 2** | [TEP-GNSS-II](https://github.com/matthewsmawfield/TEP-GNSS-II) | Global Time Echoes: 25-Year Analysis of CODE Precise Clock Products | [10.5281/zenodo.17517141](https://doi.org/10.5281/zenodo.17517141) |
| **Paper 3** | [TEP-GNSS-RINEX](https://github.com/matthewsmawfield/TEP-GNSS-RINEX) | Global Time Echoes: Raw RINEX Consistency Test | [10.5281/zenodo.17860166](https://doi.org/10.5281/zenodo.17860166) |
| **Paper 4** | [TEP-GL](https://github.com/matthewsmawfield/TEP-GL) | Temporal-Spatial Coupling in Gravitational Lensing: A Reinterpretation of Dark Matter Observations | [10.5281/zenodo.17982540](https://doi.org/10.5281/zenodo.17982540) |
| **Paper 5** | [TEP-GTE](https://github.com/matthewsmawfield/TEP-GTE) | Global Time Echoes: Empirical Synthesis | [10.5281/zenodo.18004832](https://doi.org/10.5281/zenodo.18004832) |
| **Paper 6** | **TEP-UCD** (This repo) | Temporal Topology Saturation Scale: Cross-Scale Consistency of ρ_T | [10.5281/zenodo.18064365](https://doi.org/10.5281/zenodo.18064365) |
| **Paper 7** | [TEP-RBH](https://github.com/matthewsmawfield/TEP-RBH) | The Soliton Wake: Exploring RBH-1 as a Temporal Topology Candidate | [10.5281/zenodo.18059250](https://doi.org/10.5281/zenodo.18059250) |
| **Paper 8** | [TEP-SLR](https://github.com/matthewsmawfield/TEP-SLR) | Global Time Echoes: Optical-Domain Consistency Test via Satellite Laser Ranging | [10.5281/zenodo.18064581](https://doi.org/10.5281/zenodo.18064581) |
| **Paper 9** | [TEP-EXP](https://github.com/matthewsmawfield/TEP-EXP) | What Do Precision Tests of General Relativity Actually Measure? | [10.5281/zenodo.18109760](https://doi.org/10.5281/zenodo.18109760) |
| **Paper 10** | [TEP-COS](https://github.com/matthewsmawfield/TEP-COS) | The Temporal Equivalence Principle: Suppressed Density Scaling in Globular Cluster Pulsars | [10.5281/zenodo.18165798](https://doi.org/10.5281/zenodo.18165798) |
| **Paper 11** | [TEP-H0](https://github.com/matthewsmawfield/TEP-H0) | The Cepheid Bias: Resolving the Hubble Tension | [10.5281/zenodo.18209702](https://doi.org/10.5281/zenodo.18209702) |
| **Paper 12** | [TEP-JWST](https://github.com/matthewsmawfield/TEP-JWST) | The Temporal Equivalence Principle: A Unified Resolution to the JWST High-Redshift Anomalies | [10.5281/zenodo.19000827](https://doi.org/10.5281/zenodo.19000827) |
| **Paper 13** | [TEP-WB](https://github.com/matthewsmawfield/TEP-WB) | The Temporal Equivalence Principle: Temporal Shear Recovery in Gaia DR3 Wide Binaries | [10.5281/zenodo.19102061](https://doi.org/10.5281/zenodo.19102061) |
| **Paper 14** | [TEP-GNSS-MGEX](https://github.com/matthewsmawfield/TEP-GNSS-MGEX) | Global Time Echoes: Multi-GNSS MGEX Held-Out Replication and Processing-Chain Decomposition | [10.5281/zenodo.20572726](https://doi.org/10.5281/zenodo.20572726) |
| **Paper 15** | [TEP-EFA](https://github.com/matthewsmawfield/TEP-EFA) | Temporal Equivalence Principle and the Earth Flyby Anomaly: Clock-Sector Response and Coherent-Link Cancellation | [10.5281/zenodo.19454862](https://doi.org/10.5281/zenodo.19454862) |
| **Paper 16** | [TEP-J0437](https://github.com/matthewsmawfield/TEP-J0437) | Synchronization Holonomy in Pulsar Scintillation | [10.5281/zenodo.19454619](https://doi.org/10.5281/zenodo.19454619) |
| **Paper 17** | [TEP-LLR](https://github.com/matthewsmawfield/TEP-LLR) | Lunar Laser Ranging and the Nordtvedt Effect | [10.5281/zenodo.19446028](https://doi.org/10.5281/zenodo.19446028) |
| **Paper 18** | [TEP-HC](https://github.com/matthewsmawfield/TEP-HC) | Temporal Equivalence Principle: Native hi_class Conformal Implementation, Linear Perturbation Closure, and CMB Acoustic Peak Preservation | [10.5281/zenodo.20572722](https://doi.org/10.5281/zenodo.20572722) |
| **Paper 19** | [TEP-LENS](https://github.com/matthewsmawfield/TEP-LENS) | Temporal Equivalence Principle: Multiply-Imaged Supernova Time-Delay Cosmography and Unstretched-Space Refraction | [10.5281/zenodo.20572719](https://doi.org/10.5281/zenodo.20572719) |
| **Paper 22** | [TEP-LVK](https://github.com/matthewsmawfield/TEP-LVK) | Temporal Equivalence Principle: A Standard-Siren Test of Bi-Metric Gravitational-Wave Propagation | [10.5281/zenodo.20572695](https://doi.org/10.5281/zenodo.20572695) |
| **Paper 23** | [TEP-QF](https://github.com/matthewsmawfield/TEP-QF) | Temporal Equivalence Principle: The Dirac Limit of Dynamical Proper Time | [10.5281/zenodo.20572697](https://doi.org/10.5281/zenodo.20572697) |
| **Paper 26** | [TEP-C0](https://github.com/matthewsmawfield/TEP-C0) | Temporal Equivalence Principle: A Covariant Alternative to Cosmic Expansion | [10.5281/zenodo.20370143](https://doi.org/10.5281/zenodo.20370143) |
| **Paper 27** | [TEP-TH](https://github.com/matthewsmawfield/TEP-TH) | Temporal Equivalence Principle: Nonsingular Temporal-Horizon Closure and Cosmological Perturbation Regularity | [10.5281/zenodo.20723059](https://doi.org/10.5281/zenodo.20723059) |
| **Paper 28** | [TEP-BH](https://github.com/matthewsmawfield/TEP-BH) | Temporal Equivalence Principle: Nonsingular Temporal Wells and Black-Hole Horizon Regularity | [10.5281/zenodo.21677826](https://doi.org/10.5281/zenodo.21677826) |
| **Paper 29** | [TEP-BBN](https://github.com/matthewsmawfield/TEP-BBN) | Temporal Equivalence Principle: Dynamical Proper Time and the Illusion of Primordial Deuterium | [10.5281/zenodo.21841147](https://doi.org/10.5281/zenodo.21841147) |
| **Paper 36** | [TEP-9](https://github.com/matthewsmawfield/TEP-9) | Temporal Equivalence Principle: A Proper-Time Domain Boundary in the Outer Solar System | [10.5281/zenodo.22858190](https://doi.org/10.5281/zenodo.22858190) |

## Repository Structure

- `site/components/`: HTML components comprising the manuscript sections.
  - `1_abstract.html`: Paper abstract.
  - `2_introduction.html`: The Dark Matter problem as a temporal structure problem.
  - `3_gnss_calibration.html`: Derivation of $\rho_T$ from atomic clocks.
  - `4_sparc_validation.html`: Galactic rotation curve and two-branch RAR/BTFR analysis.
  - `5_screening_hierarchy.html`: Temporal Topology screening hierarchy and planetary rotational kinematics.
  - `6_atomic_boundary.html`: Physical constraints on $\rho_T$ (electron degeneracy, dimensional analysis).
  - `7_universal_scaling.html`: The unified $M^{1/3}$ scaling law and RBH-1 crossover.
  - `8_milky_way_test.html`: Local Milky Way dark-matter onset.
  - `10_discussion.html`: Theoretical implications (Phantom Mass and Cross-Domain Constraint Network).
  - `11_conclusion.html`: Summary of findings.
  - `13_references.html`: Bibliography.
  - `appendix_a_gnss.html`: Appendix A GNSS methodology summary.
  - `appendix_b_vulnerabilities.html`: Appendix B open questions, causal proof, and risk register.
  - `appendix_c_eft.html`: Appendix C candidate EFT realizations and scale dictionary.

## Relationship to Other Papers

- **Preceded by:** Papers 0–4 and the Synthesis (TEP, TEP-GNSS series, TEP-GL, TEP-GTE), which establish the empirical reality of the clock correlations and the theoretical framework.
- **Companion to:** Paper 7 (**TEP-RBH**), which applies the ρ_T value derived here to test the soliton hypothesis for the runaway black hole candidate RBH-1.

## Citation

```bibtex
@article{smawfield2025ucd,
  title={Temporal Topology Saturation Scale: Cross-Scale Consistency of ρ_T},
  author={Smawfield, Matthew Lukin},
  journal={Zenodo},
  year={2025},
  doi={10.5281/zenodo.18064365},
  note={Preprint v0.11 (New Delhi)}
}
```

## License

This project is licensed under Creative Commons Attribution 4.0 International (CC-BY-4.0). See [LICENSE](LICENSE) for details.

---

## Open Science Statement

These are working preprints shared in the spirit of open science—all manuscripts, analysis code, and data products are openly available under Creative Commons and MIT licenses to encourage and facilitate replication. Feedback and collaboration are warmly invited and welcome.

---

**Contact:** matthew@mlsmawfield.com
**ORCID:** [0009-0003-8219-3159](https://orcid.org/0009-0003-8219-3159)

## Build Instructions

The manuscript is assembled from the HTML components in `site/components/`.
