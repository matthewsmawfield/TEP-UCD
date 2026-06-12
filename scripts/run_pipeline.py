#!/usr/bin/env python3
"""
TEP-UCD Analysis Pipeline Master Script
=======================================
Orchestrates the full analysis pipeline for Paper 6:
"Universal Critical Density: Cross-Scale Consistency of ρ_T"

Workflow Steps:
0. Download Data       — Fetch SPARC Tables 1 & 2 if missing
1. Scaling Law          — Universal TEP vs GR comparison
2. White Dwarf Screening — Compact-object screening test
3. Screening Hierarchy   — Cross-object-class screening plot
4. SPARC Analysis      — Primary galactic validation (α_SPARC)
4b. SPARC Examples      — Example rotation curves
5. Ultimate Screening  — Comprehensive 26-object analysis
6. Sensitivity         — Feasibility and sensitivity analysis
7. SPARC Residuals     — Baryonic feedback vs field theory discriminant

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --skip-figures  # skip figure regeneration

Author: Matthew Lukin Smawfield
Date: June 2026
"""

import sys
import time
import json
from pathlib import Path
import traceback
import argparse

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from scripts.utils.logger import TEPLogger, set_step_logger, print_status


def ensure_dirs():
    """Ensure all output directories exist."""
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)
    (PROJECT_ROOT / "results" / "figures").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "results" / "outputs").mkdir(parents=True, exist_ok=True)


def run_step(step_name, step_module_path, func_name, skip=False):
    """Run a single pipeline step with logging."""
    if skip:
        print_status(f"Skipping {step_name}", "WARNING")
        return None

    logger = TEPLogger(
        step_name.lower().replace(" ", "_").replace("-", "_"),
        log_file_path=PROJECT_ROOT / "logs" / f"{step_name.lower().replace(' ', '_').replace('-', '_')}.log"
    )
    set_step_logger(logger)
    print_status(f"STEP: {step_name}", "TITLE")

    start = time.time()
    try:
        # Dynamic import
        import importlib.util
        spec = importlib.util.spec_from_file_location(step_module_path.stem, step_module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        func = getattr(mod, func_name)
        result = func()
        elapsed = time.time() - start
        print_status(f"Completed in {elapsed:.1f}s", "SUCCESS")
        return result
    except Exception as e:
        elapsed = time.time() - start
        print_status(f"FAILED after {elapsed:.1f}s: {e}", "ERROR")
        traceback.print_exc()
        return None


def save_pipeline_summary(results, elapsed_total):
    """Save a JSON summary of the full pipeline run."""
    summary = {
        "pipeline": "TEP-UCD",
        "version": "v0.6 (New Delhi)",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "elapsed_seconds": round(elapsed_total, 2),
        "steps": {}
    }
    for name, res in results.items():
        summary["steps"][name] = {
            "status": "completed" if res is not None else "failed",
            "outputs": str(res) if isinstance(res, (str, Path)) else (res if isinstance(res, dict) else None)
        }
    out_path = PROJECT_ROOT / "results" / "outputs" / "pipeline_summary.json"
    with open(out_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print_status(f"Pipeline summary saved to {out_path}", "INFO")


def run_pipeline():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--skip-figures", action="store_true", help="Skip figure generation steps")
    args = ap.parse_args()

    ensure_dirs()

    # Setup Global Logger
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    pipeline_logger = TEPLogger("pipeline_master", log_file_path=logs_dir / "pipeline_master.log")
    set_step_logger(pipeline_logger)

    print_status("TEP-UCD ANALYSIS PIPELINE INITIATED", "TITLE")
    print_status(f"Project Root: {PROJECT_ROOT}", "INFO")
    print_status("Starting execution sequence...", "INFO")

    steps_dir = PROJECT_ROOT / "scripts" / "steps"
    t0 = time.time()
    results = {}

    # Step 0: Download Data
    results["step_0_download_data"] = run_step(
        "step_0_download_data", steps_dir / "step_0_download_data.py",
        "run_download_data"
    )

    # Step 1: Scaling Law
    results["step_1_scaling"] = run_step(
        "step_1_scaling", steps_dir / "step_1_scaling.py",
        "run_scaling_analysis", skip=args.skip_figures
    )

    # Step 2: White Dwarf Screening
    results["step_2_wd_screening"] = run_step(
        "step_2_wd_screening", steps_dir / "step_2_wd_screening.py",
        "run_wd_screening", skip=args.skip_figures
    )

    # Step 3: Screening Hierarchy
    results["step_3_screening_hierarchy"] = run_step(
        "step_3_screening_hierarchy", steps_dir / "step_3_screening_hierarchy.py",
        "run_screening_hierarchy", skip=args.skip_figures
    )

    # Step 4: SPARC Analysis (primary)
    results["step_4_sparc_analysis"] = run_step(
        "step_4_sparc_analysis", steps_dir / "step_4_sparc_analysis.py",
        "run_enhanced_analysis"
    )

    # Step 4b: SPARC Examples
    results["step_4b_sparc_examples"] = run_step(
        "step_4b_sparc_examples", steps_dir / "step_4b_sparc_examples.py",
        "run", skip=args.skip_figures
    )

    # Step 5: Ultimate Screening
    results["step_5_ultimate_screening"] = run_step(
        "step_5_ultimate_screening", steps_dir / "step_5_ultimate_screening.py",
        "run_ultimate_screening", skip=args.skip_figures
    )

    # Step 6: Sensitivity
    results["step_6_sensitivity"] = run_step(
        "step_6_sensitivity", steps_dir / "step_6_sensitivity.py",
        "run_sensitivity_analysis", skip=args.skip_figures
    )

    # Step 7: SPARC Residuals
    results["step_7_sparc_residuals"] = run_step(
        "step_7_sparc_residuals", steps_dir / "step_7_sparc_residuals.py",
        "run_residual_analysis"
    )

    total_elapsed = time.time() - t0
    save_pipeline_summary(results, total_elapsed)

    print_status("=" * 60, "TITLE")
    print_status("PIPELINE COMPLETE", "TITLE")
    print_status(f"Total elapsed: {total_elapsed:.1f}s", "INFO")
    print_status("=" * 60, "TITLE")


if __name__ == '__main__':
    run_pipeline()
