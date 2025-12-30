# Data Directory

## SPARC Database

**Source**: Lelli, F., McGaugh, S. S., & Schombert, J. M. 2016, *AJ*, 152, 157  
**URL**: http://astroweb.cwru.edu/SPARC/  
**License**: Public domain (astronomical data)  
**Citation**: [SPARC Database](https://ui.adsabs.harvard.edu/abs/2016AJ....152..157L)

### Files

- **`sparc/Table1.mrt`**: Galaxy properties (175 galaxies)
  - Luminosities, distances, HI masses, morphological types
  - Used for baryonic mass calculations

- **`sparc/Table2.mrt`**: Rotation curve data
  - Observed velocities, gas contributions, disk/bulge decompositions
  - Used for dark matter onset radius analysis

### Usage

These data files are used by `scripts/figure_5_sparc_analysis.py` to test the TEP prediction that the dark matter onset radius scales as $R_{\rm DM} \propto M_{\rm bar}^{1/3}$.

### Attribution

If you use this data, please cite:

```bibtex
@article{lelli2016sparc,
  title={SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves},
  author={Lelli, Federico and McGaugh, Stacy S and Schombert, James M},
  journal={The Astronomical Journal},
  volume={152},
  number={6},
  pages={157},
  year={2016},
  publisher={IOP Publishing}
}
```
