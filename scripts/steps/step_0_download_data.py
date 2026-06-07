"""
Step 0: Download external data dependencies.

Downloads SPARC (Spitzer Photometry and Accurate Rotation Curves) tables
if they are not already present in data/sparc/.

Source: Lelli, McGaugh & Schombert 2016, AJ, 152, 157
URL: http://astroweb.cwru.edu/SPARC/
"""

import os
import sys
from pathlib import Path
from urllib.request import urlretrieve

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import TEPLogger, set_step_logger, print_status

SPARC_BASE_URL = "http://astroweb.cwru.edu/SPARC/"
SPARC_FILES = ["Table1.mrt", "Table2.mrt"]


def download_file(url: str, dest: Path, logger=None) -> bool:
    """Download a file if it does not already exist."""
    if dest.exists():
        if logger:
            logger.info(f"Already exists: {dest}")
        else:
            print_status(f"Already exists: {dest}", "INFO")
        return True

    try:
        if logger:
            logger.info(f"Downloading {url} -> {dest}")
        else:
            print_status(f"Downloading {url} -> {dest}", "INFO")
        urlretrieve(url, dest)
        return True
    except Exception as e:
        if logger:
            logger.error(f"Failed to download {url}: {e}")
        else:
            print_status(f"Failed to download {url}: {e}", "ERROR")
        return False


def run_download_data():
    """Download all required external data."""
    logger = TEPLogger(
        "step_0_download_data",
        log_file_path=Path(__file__).resolve().parents[2] / "logs" / "step_0_download_data.log"
    )
    set_step_logger(logger)

    project_root = Path(__file__).resolve().parents[2]
    sparc_dir = project_root / "data" / "sparc"
    sparc_dir.mkdir(parents=True, exist_ok=True)

    print_status(f"SPARC data directory: {sparc_dir}", "INFO")
    print_status(f"Required files: {SPARC_FILES}", "INFO")

    all_ok = True
    for fname in SPARC_FILES:
        url = f"{SPARC_BASE_URL}{fname}"
        dest = sparc_dir / fname
        ok = download_file(url, dest, logger)
        if not ok:
            all_ok = False

    if all_ok:
        print_status("All data files present.", "SUCCESS")
    else:
        print_status("Some downloads failed. Pipeline may fall back to synthetic data.", "WARNING")

    return {"status": "ok" if all_ok else "partial", "dir": str(sparc_dir)}


if __name__ == "__main__":
    run_download_data()
