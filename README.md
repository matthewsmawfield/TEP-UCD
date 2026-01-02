# Universal Critical Density: Unifying Atomic, Galactic, and Compact Object Scales

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18064366.svg)](https://doi.org/10.5281/zenodo.18064366)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

![Universal Critical Density](site/public/og-image.jpg)

**Author:** Matthew Lukin Smawfield  
**Version:** v0.1 (New Delhi)  
**Date:** 28 December 2025  
**Status:** Preprint  
**DOI:** [10.5281/zenodo.18064366](https://doi.org/10.5281/zenodo.18064366)  
**Website:** [https://matthewsmawfield.github.io/TEP-UCD/](https://matthewsmawfield.github.io/TEP-UCD/)

## Abstract

Dark matter observations across cosmological scales exhibit a regularity in scaling: the characteristic radius at which Newtonian dynamics fails scales as R ∝ M^(1/3), consistent with a characteristic density ρ_c. This scaling appears in galaxy rotation curves (SPARC database), ultra-diffuse galaxies (DF2/DF4), the Milky Way's Keplerian transition, and compact object phenomena (magnetar anti-glitches). This pattern is analyzed within the conformal time-field sector of the Temporal Equivalence Principle (TEP), where gravitational solitons are predicted to form at a characteristic density threshold.

Terrestrial calibration—derived from a newly identified distance-structured correlation in GNSS atomic clocks—provides an independent measurement of this scale. Multi-center analysis (CODE, IGS, ESA) reveals correlations with characteristic length L_c ≈ 4200 km for Earth's mass, implying ρ_c ≈ 20 g/cm³. This calibration exhibits 25-year temporal stability and survives raw RINEX validation, strongly constraining processing-artifact explanations. The derived density scale is independently constrained by atomic physics: requiring the soliton radius to reproduce the Bohr radius at the proton mass scale yields ρ_c ~ 10–50 g/cm³, consistent with the GNSS measurement.

Galactic-scale validation comes from the SPARC rotation curve database (175 galaxies). The empirical dark matter onset scaling is α = 0.354 ± 0.014, consistent with the M^(1/3) prediction within 2σ. Vainshtein screening resolves the apparent conflict with precision GR tests. Analysis of 26 astrophysical objects spanning 15 orders of magnitude in density reveals an empirical scaling S ∝ ρ^0.334 (R² = 0.9999), confirming the predicted ρ^(1/3) dependence.

The saturation density ρ_c ≈ 20 g/cm³ is proposed as a physical organizing parameter, supported by consistency across multiple mass and density scales (proton to galaxy cluster; cosmological voids to neutron stars).

## Key Results

- **Terrestrial Calibration (GNSS):** L_c ≈ 4200 km → ρ_c ≈ 20 g/cm³
- **Atomic Constraint:** Bohr radius consistency yields ρ_c ~ 10–50 g/cm³
- **Galactic Validation:** SPARC scaling α = 0.354 ± 0.014 (M^(1/3) prediction)
- **Screening Hierarchy:** S ∝ ρ^0.334 (R² = 0.9999) across 26 objects
- **Magnetar Test:** P_crit ≈ 6.8 s prediction vs 1E 2259+586 at P = 6.98 s

## The TEP Research Program
 
| Paper | Repository | Title | DOI |
|-------|-----------|-------|-----|
| **Paper 0** | [TEP](https://github.com/matthewsmawfield/TEP) | Temporal Equivalence Principle: Dynamic Time & Emergent Light Speed | [10.5281/zenodo.16921911](https://doi.org/10.5281/zenodo.16921911) |
| **Paper 1** | [TEP-GNSS](https://github.com/matthewsmawfield/TEP-GNSS) | Global Time Echoes: Distance-Structured Correlations in GNSS Clocks | [10.5281/zenodo.17127229](https://doi.org/10.5281/zenodo.17127229) |
| **Paper 2** | [TEP-GNSS-II](https://github.com/matthewsmawfield/TEP-GNSS-II) | Global Time Echoes: 25-Year Temporal Evolution of Distance-Structured Correlations in GNSS Clocks | [10.5281/zenodo.17517141](https://doi.org/10.5281/zenodo.17517141) |
| **Paper 3** | [TEP-GNSS-RINEX](https://github.com/matthewsmawfield/TEP-GNSS-RINEX) | Global Time Echoes: Raw RINEX Validation of Distance-Structured Correlations in GNSS Clocks | [10.5281/zenodo.17860166](https://doi.org/10.5281/zenodo.17860166) |
| **Paper 4** | [TEP-GL](https://github.com/matthewsmawfield/TEP-GL) | Temporal-Spatial Coupling in Gravitational Lensing: A Reinterpretation of Dark Matter Observations | [10.5281/zenodo.17982540](https://doi.org/10.5281/zenodo.17982540) |
| **Synthesis** | [TEP-GTE](https://github.com/matthewsmawfield/TEP-GTE) | Global Time Echoes: Empirical Validation of the Temporal Equivalence Principle | [10.5281/zenodo.18004832](https://doi.org/10.5281/zenodo.18004832) |
| **Paper 7** | **TEP-UCD** (This repo) | Universal Critical Density: Unifying Atomic, Galactic, and Compact Object Scales | [10.5281/zenodo.18064366](https://doi.org/10.5281/zenodo.18064366) |
| **Paper 8** | [TEP-RBH](https://github.com/matthewsmawfield/TEP-RBH) | The Soliton Wake: A Runaway Black Hole as a Gravitational Soliton | [10.5281/zenodo.18059251](https://doi.org/10.5281/zenodo.18059251) |
| **Paper 9** | [TEP-SLR](https://github.com/matthewsmawfield/TEP-SLR) | Global Time Echoes: Optical Validation of the Temporal Equivalence Principle via Satellite Laser Ranging | [10.5281/zenodo.18064582](https://doi.org/10.5281/zenodo.18064582) |
| **Paper 10** | [TEP-EXP](https://github.com/matthewsmawfield/TEP-EXP) | What Do Precision Tests of General Relativity Actually Measure? | [10.5281/zenodo.18109761](https://doi.org/10.5281/zenodo.18109761) |

## Repository Structure

- `site/components/`: HTML components comprising the manuscript sections.
  - `1_abstract.html`: Paper abstract.
  - `2_introduction.html`: The Dark Matter problem as a temporal structure problem.
  - `3_gnss_calibration.html`: Derivation of $\rho_c$ from atomic clocks.
  - `4_sparc_validation.html`: Galactic rotation curve analysis.
  - `5_screening_hierarchy.html`: Vainshtein screening mechanism.
  - `6_atomic_boundary.html`: Connection to quantum scales.
  - `7_universal_scaling.html`: The unified scaling law.
  - `8_magnetar_test.html`: Magnetar anti-glitch validation.
  - `9_milky_way_test.html`: Local Milky Way Keplerian transition.
  - `10_discussion.html`: Theoretical implications (Phantom Mass).
  - `11_conclusion.html`: Summary of findings.
  - `12_visual_evidence.html`: Key figures.
  - `13_references.html`: Bibliography.

## Relationship to Other Papers

- **Preceded by:** Papers 0–4 and the Synthesis (TEP, TEP-GNSS series, TEP-GL, TEP-GTE), which establish the empirical reality of the clock correlations and the theoretical framework.
- **Companion to:** Paper 8 (**TEP-RBH**), which applies the ρ_c value derived here to test the soliton hypothesis for the runaway black hole candidate RBH-1.

## Citation

```bibtex
@article{smawfield2025ucd,
  title={Universal Critical Density: Unifying Atomic, Galactic, and Compact Object Scales},
  author={Smawfield, Matthew Lukin},
  journal={Zenodo},
  year={2025},
  doi={10.5281/zenodo.18064366},
  note={Preprint v0.1 (New Delhi)}
}
```

## License

This project is licensed under Creative Commons Attribution 4.0 International (CC-BY-4.0). See [LICENSE](LICENSE) for details.

---

## Open Science Statement

These are working preprints shared in the spirit of open science—all manuscripts, analysis code, and data products are openly available under Creative Commons and MIT licenses to encourage and facilitate replication. Feedback and collaboration are warmly invited and welcome.

---

**Contact:** matthewsmawfield@gmail.com  
**ORCID:** [0009-0003-8219-3159](https://orcid.org/0009-0003-8219-3159)

## Build Instructions

The manuscript is assembled from the HTML components in `site/components/`.
