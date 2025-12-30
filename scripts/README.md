# TEP-UCD Analysis Scripts

Analysis code for the TEP-UCD manuscript: "Universal Critical Density: Unifying Atomic, Galactic, and Compact Object Scales"

## Directory Structure

```
scripts/
├── figures/           # Figure generation scripts
├── utils/             # Shared utilities
└── analyze_sparc_residuals.py  # Core SPARC analysis
```

## Scripts

| Script | Figure | Description |
|--------|--------|-------------|
| `figures/02_scaling.py` | Figure 1 | Universal scaling law (TEP vs GR) |
| `analyze_sparc_residuals.py` | Figure 2 | SPARC galaxy scaling analysis |
| `figures/03_wd_screening.py` | Figure 3 | White dwarf screening test |
| `figures/04_screening_hierarchy.py` | Figure 4 | Screening hierarchy across object classes |

## SPARC Analysis

The SPARC galaxy analysis (`analyze_sparc_residuals.py`) implements:
1. **Dark Matter Onset:** Determines the radius where mass discrepancy exceeds threshold
2. **Scaling Law Fit:** Fits $R \propto M^\alpha$ to the data
3. **Residual Analysis:** Checks for systematic deviations

## Requirements

```bash
pip install -r ../requirements.txt
```

## Citation

If you use this code, please cite:

```bibtex
@article{smawfield2025ucd,
  author = {Smawfield, Matthew Lukin},
  title = {Universal Critical Density: Unifying Atomic, Galactic, and Compact Object Scales},
  year = {2025},
  doi = {10.5281/zenodo.18064366}
}
```

## License

CC-BY-4.0
