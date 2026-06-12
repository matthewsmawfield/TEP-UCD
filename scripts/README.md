# TEP-UCD Analysis Scripts

Analysis code for the TEP-UCD manuscript: "Universal Critical Density: Cross-Scale Consistency of ρ_T"

## Directory Structure

```
scripts/
├── steps/                # Step-based analysis and figure generation scripts
│   ├── step_0_download_data.py
│   ├── step_1_scaling.py
│   ├── step_2_wd_screening.py
│   ├── step_3_screening_hierarchy.py
│   ├── step_4_sparc_analysis.py
│   ├── step_4b_sparc_examples.py
│   ├── step_5_ultimate_screening.py
│   ├── step_6_sensitivity.py
│   └── step_7_sparc_residuals.py
├── utils/                # Shared utilities (style, logging)
├── verification/         # Verification audits
│   └── verify_screening_claim.py
├── generate_site_pdf.py
├── run_pipeline.py        # Master pipeline orchestrator
└── README.md
```

## Clean-Run Command Sequence

```bash
cd "/Users/matthewsmawfield/www/Temporal Equivalence Principle/TEP-UCD"
pip install -r requirements.txt

# Run the full analysis pipeline (downloads data, generates figures, runs verification)
python3 scripts/run_pipeline.py

# Build site and regenerate manuscript markdown + PDF
cd site && npm run build
```

## Scripts

| Script | Output | Description |
|--------|--------|-------------|
| `steps/step_0_download_data.py` | — | Download SPARC Tables 1 & 2 if missing |
| `steps/step_1_scaling.py` | `figure_2_scaling.png` | Universal scaling law (TEP vs GR) |
| `steps/step_2_wd_screening.py` | `figure_3_wd_screening.png` | White dwarf screening test |
| `steps/step_3_screening_hierarchy.py` | `figure_4_screening_hierarchy.png` | Screening hierarchy across object classes |
| `steps/step_4_sparc_analysis.py` | `figure_5_sparc_enhanced.png` | **Primary SPARC scaling analysis** |
| `steps/step_4b_sparc_examples.py` | `figure_6_sparc_examples.png` | Example rotation curves |
| `steps/step_5_ultimate_screening.py` | `screening_comprehensive.png` | Comprehensive screening plot (not in manuscript) |
| `steps/step_6_sensitivity.py` | `figure_8_sensitivity.png` | Sensitivity and feasibility analysis |
| `steps/step_7_sparc_residuals.py` | `figure_7_sparc_residuals.png` | Residual analysis (baryonic vs screening proxies) |
| `verification/verify_screening_claim.py` | — | Verifies S ∝ rho^0.334 claim from object data |

## SPARC Scaling Analysis (`step_4_sparc_analysis.py`)

This is the primary galactic validation script. It performs the following steps:

1. **Data loading:** Parses SPARC Table1.mrt (galaxy properties) and Table2.mrt (rotation curves).
2. **Baryonic mass:** $M_{\rm bar} = M_* + 1.33 M_{\rm HI}$ with $(M/L)_{3.6\mu} = 0.5$.
3. **Newtonian velocity:** $V_{\rm bar}^2 = V_{\rm gas}^2 + (M/L)_{\rm disk} V_{\rm disk}^2 + (M/L)_{\rm bulge} V_{\rm bulge}^2$.
4. **Onset radius:** $R_{\rm DM}$ = first radius where $V_{\rm obs}/V_{\rm bar} > \text{threshold}$.
5. **Threshold marginalization:** Fits $\alpha$ independently at thresholds 1.1–1.5 (step 0.05), then computes a weighted-average exponent.
6. **Bootstrap resampling:** 1000 galaxy-level bootstrap resamples. For each resample, the threshold-marginalized exponent is recomputed. The bootstrap standard deviation is reported as the robust uncertainty.
7. **Fixed-alpha fit:** With $\alpha = 1/3$ fixed, the normalization $k$ is fitted, yielding an implied screening density $\rho_{\rm trans}$.

### Robustness Checks Documented

- **Threshold variation:** Exponents range from 0.28 (loose) to 0.42 (strict); ensemble converges near 1/3.
- **Bootstrap uncertainty:** 1000 resamples yield $\alpha = 0.355 \pm 0.043$; combined with the definition systematic ($\pm 0.07$), the headline value is $\alpha_{\rm SPARC} = 0.355 \pm 0.043 \text{ (stat)} \pm 0.07 \text{ (definition)}$.
- **Sample size:** 167 of 175 SPARC galaxies yield valid $R_{\rm DM}$ at threshold 1.3 (8 excluded because $V_{\rm obs}/V_{\rm bar}$ never exceeds threshold).
- **RAR-based transition:** Alternative definition using $g_{\rm bar} < a_0$ yields a steeper slope (~0.57), flagged as degenerate with the MOND scale and not used as the primary estimator.

## SPARC Residual Analysis (`step_7_sparc_residuals.py`)

Discriminates baryonic feedback from field-theory interpretations by correlating residuals from the $M^{1/3}$ fit with:
- Gas fraction, surface brightness, inclination (baryonic proxies)
- Central density (screening proxy)

**Result:** Maximum baryonic correlation $|r| = 0.297$ (inclination, likely deprojection systematic). Central density shows no significant correlation ($r = -0.108$, $p = 0.16$), favoring the field-theory interpretation.

## Screening Verification (`verify_screening_claim.py`)

Reproduces the screening hierarchy fit $S \propto \rho^{\beta_{\rm scr}}$ across 26 objects. The theoretical expectation is $\beta_{\rm scr} = 1/3$ because $S = R_T/R_{\rm phys}$ and both radii follow mass-density relations. The script confirms the high $R^2$ but flags this as an algebraic consistency check, not independent confirmation of TEP.

## Requirements

```bash
pip install -r ../requirements.txt
```

Dependencies: `numpy`, `scipy`, `matplotlib` (plus `utils/style.py` for publication formatting).

## Citation

If you use this code, please cite:

```bibtex
@article{smawfield2025ucd,
  author = {Smawfield, Matthew Lukin},
  title = {Universal Critical Density: Cross-Scale Consistency of ρ_T},
  year = {2025},
  doi = {10.5281/zenodo.18064365}
}
```

## License

CC-BY-4.0
