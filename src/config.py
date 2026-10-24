"""Project-wide settings: paths and analysis scope."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "reports" / "figures"

# Scope: current Premier League players, last 5 seasons of data only.
LEAGUE_ID = "GB1"  # Transfermarkt competition id for the Premier League
CURRENT_SEASON = 2025  # 2025/26, the latest season in the data (Transfermarkt labels a season by its start year)
SEASONS_BACK = 5  # 2021/22 .. 2025/26
START_DATE = f"{CURRENT_SEASON - SEASONS_BACK + 1}-07-01"  # first day of the oldest season we keep

# Per-90 stats are left blank for players with fewer Premier League minutes than this in a season.
MIN_MINUTES_PER90 = 450
