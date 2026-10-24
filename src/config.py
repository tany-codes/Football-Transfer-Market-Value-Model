"""Project-wide settings: paths and analysis scope."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "reports" / "figures"

# Scope: current Premier League players, last 5 years of data only.
LEAGUE_ID = "GB1"  # Transfermarkt competition id for the Premier League
YEARS_BACK = 5
