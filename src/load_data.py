"""Read the raw CSVs and restrict them to the project scope (see config.py).

Scope: players who currently play in the Premier League, and only data from
the last SEASONS_BACK seasons.
"""
import pandas as pd

from src.config import CURRENT_SEASON, LEAGUE_ID, RAW_DIR, START_DATE


def fix_mojibake(s: pd.Series) -> pd.Series:
    """Repair text like 'SocietÃ ' that was UTF-8 decoded as cp1252 somewhere upstream."""

    def fix(x):
        if not isinstance(x, str):
            return x
        try:
            return x.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return x

    return s.map(fix)


def current_league_club_ids() -> set:
    """Ids of the clubs that played Premier League matches in the current season.

    players.csv tags many non-Premier League English clubs (Cardiff, Wigan, ...) with the
    same domestic competition id, so that column can't be used to find today's clubs.
    """
    a = pd.read_csv(
        RAW_DIR / "appearances.csv",
        usecols=["date", "competition_id", "player_club_id"],
        parse_dates=["date"],
    )
    a = a[(a["competition_id"] == LEAGUE_ID) & (a["date"] >= f"{CURRENT_SEASON}-07-01")]
    return set(a["player_club_id"])


def load_players() -> pd.DataFrame:
    """Players at a current Premier League club who were active this season."""
    df = pd.read_csv(
        RAW_DIR / "players.csv",
        parse_dates=["date_of_birth", "contract_expiration_date"],
    )
    df = df[
        df["current_club_id"].isin(current_league_club_ids())
        & (df["last_season"] == CURRENT_SEASON)
    ].copy()
    for col in ["name", "current_club_name"]:
        df[col] = fix_mojibake(df[col])
    return df.reset_index(drop=True)


def load_valuations(player_ids=None) -> pd.DataFrame:
    """Market value history since START_DATE, optionally limited to given player ids."""
    df = pd.read_csv(RAW_DIR / "player_valuations.csv", parse_dates=["date"])
    df = df[df["date"] >= START_DATE]
    if player_ids is not None:
        df = df[df["player_id"].isin(player_ids)]
    return df.reset_index(drop=True)


def load_appearances(player_ids=None) -> pd.DataFrame:
    """Per-match appearances since START_DATE (all competitions), optionally limited to given player ids."""
    cols = [
        "player_id", "game_id", "date", "competition_id", "player_club_id",
        "goals", "assists", "minutes_played", "yellow_cards", "red_cards",
    ]
    df = pd.read_csv(RAW_DIR / "appearances.csv", usecols=cols, parse_dates=["date"])
    df = df[df["date"] >= START_DATE]
    if player_ids is not None:
        df = df[df["player_id"].isin(player_ids)]
    return df.reset_index(drop=True)
