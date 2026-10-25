# Temporal Topology Saturation Scale: Cross-Scale Consistency of ρ_T

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18064365.svg)](https://doi.org/10.5281/zenodo.18064365)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

![Temporal Topology Saturation Scale](site/public/og-image.jpg)

**Author:** Matthew Lukin Smawfield
**Version:** v0.10 (New Delhi)
**First published:** 28 December 2025 · **Last updated:** 25 October 2026
**Status:** Preprint
**DOI:** [10.5281/zenodo.18064365](https://doi.org/10.5281/zenodo.18064365)
**Website:** [https://mlsmawfield.com/tep/ucd/](https://mlsmawfield.com/tep/ucd/)

## Abstract

<!-- Generated from site/components/1_abstract.html; update the manuscript source, then run tools/sync_current_corpus_readmes.py. -->

Gravitational anomalies across astrophysical scales exhibit an empirical regularity: the radius at which Newtonian dynamics fails scales as $R \propto M^{1/3}$ in the compact saturation regime and $R \propto M^{1/2}$ in the low-acceleration galactic regime, organized by a candidate saturation/proximity density scale $\rho_T$ in the Temporal Equivalence Principle (TEP) conformal time-field sector. The 25-year GNSS atomic-clock correlation length $L_c \approx 4{,}200$ km (CODE, IGS, ESA; raw-RINEX validated) establishes an Earth-scale correlation structure consistent with $R_T(M_\oplus) = (3M_\oplus/4\pi\rho_T)^{1/3} = 4{,}146$ km at $\rho_T \approx 20$ g/cm³ ($\rho_T \in [8,\,70]$ g/cm³ conditional mapping under $L_c \leftrightarrow R_T(M_\oplus)$). A 4-layer PREM Earth boundary-value integration confirms an order-unity geometric projection ($L_c^{\rm PREM} = 4{,}010$ km shell; $3{,}213$ km volume) governed by Earth's $R_{\rm CMB}$ and $R_\oplus$ structure, while Monte Carlo network injection–recovery simulations across $L_c^{\rm true} \in [1{,}000,\,6{,}000]$ km demonstrate that 1-constellation GPS-only processing recovers $L_c^{\rm true} = 4{,}200$ km ($\hat L_c^{\rm GPS} = 4{,}036 \pm 113$ km; white-noise null $|C(d)| = 0.009$; correlated orbital/datum dipole null concave-down with $d²C/dd² < 0$), whereas 4-constellation multi-GNSS inter-system-bias (ISB) projection compresses the same field to $\hat L_c^{\rm MGEX} = 2{,}277 \pm 47$ km per-epoch ($1.77\times$) and $2{,}485 \pm 45$ km daily-constant ($1.62\times$, matching the empirical $1.90\times$ MGEX offset).

Because the canonical terrestrial BVP is shaped by Earth's fixed geometry, quantitative calibration of $\rho_T \approx 20$ g/cm³ rests on direct $R_\oplus$-free cross-mass tests, separated from structural-exponent tests. Direct tests comprise the RBH-1 crossover ($M_\times = \sqrt{3c⁶/(32\pi G³\rho_T)} \approx 3.04 \times 10⁷\,M_\odot$, $R_T/R_S = 1.32$), the zero-parameter equatorial rotation relation $v_{\rm eq}/c = u_T(M)/\sqrt{u_{\rm gal}}$ ($v_{\rm gal} = 220$ km s$^{-1}$), which matches Earth, Uranus, Neptune, and Saturn at $v_{\rm obs}/v_{\rm TEP} = 1.016 \pm 0.073$ ($\rho_T^{\rm spin} = 20.9$ g/cm³ geometric mean; extending above $M_{\rm cap} = 194\,M_\oplus = 0.61\,M_{\rm Jup}$ with one small-body capacity parameter $\eta_0 = 0.129$ [or the parameter-free secular stability fraction $\eta_{\rm sec} = \tfrac{1}{8} = 0.125$] and $S_A = \min[1,\,S]$ matches Jupiter at $-2.9\%$ [$-0.2\%$ at $\eta_{\rm sec}$], the fastest planetary-mass rotator SIMP J0136 at $-2.8\%$ [$-0.3\%$], and the $1.15 \pm 0.08$ hr brown-dwarf period floor of Tannock et al. 2021 at $P_{\min}^{\rm TEP} = (k_{\rm MOI}/\eta_0)\tau_T = 1.17$ hr [$1.21$ hr at $\eta_{\rm sec}$], giving $v_{\rm obs}/v_{\rm 2br} = 1.008 \pm 0.060$ and $\rho_T^{\rm rot} = 21.1$ g/cm³ across $N = 9$ planetary and substellar systems), and cold-planet moments of inertia $k_{\rm MOI} \simeq \tfrac{1}{2}S$ ($\rho_T^{\rm MOI,\text{terr}} = 17.9 \pm 1.4$ g/cm³ across the three core-screened terrestrial planets; $2k_{\rm MOI}/S = 1.17 \pm 0.14$ across eight planets with a systematic trend toward $8$–$9$ g/cm³ in compressible gas giants). Structural and scale-cancellation tests comprise the SPARC onset scaling ($\alpha_{\rm SPARC} = 0.352 \pm 0.043$ discrete, $N = 168$; $\alpha_{\rm res} = 0.417 \pm 0.050$ on $n = 75$ resolved crossings compatible with a transition between the $M^{1/3}$ saturation and $M^{1/2}$ low-acceleration kinetic scales; Tobit rejection of $R_{\rm DM}/R_d$ invariance at $+0.323 \pm 0.034, z = 9.57, p < 10^{-4}$; fixed-radius non-circular partial $r(R_{\rm DM},\,V_{\rm bar}(2.2R_d)\mid R_d) = +0.547$, $p = 3.8 \times 10^{-7}$), the two-branch RAR/BTFR profile $P_{,X} = k\sqrt{\xi} + 2\xi$ ($0.139$–$0.152$ dex RMS on the quality-controlled SPARC sample), the Milky Way onset ($3.1 \pm 0.4$ kpc mean; $[1.0,\,9.4]$ kpc $1\sigma$ interval), the algebraic $S \propto \rho^{0.334}$ hierarchy ($R² = 0.99995$), and Wesson's constant $p_{\rm TEP} \equiv J/M² = G/(2v_{\rm gal}) = 1.52 \times 10^{-15}$ cm$²$ g$^{-1}$ s$^{-1}$ ($J_{\rm obs}/J_{\rm TEP} = 1.11 \pm 0.25$).

Keywords: dark matter – gravitation – scalar fields – galaxies: kinematics and dynamics – temporal equivalence principle

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
  note={Preprint v0.10 (New Delhi)}
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
