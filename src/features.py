"""Build the player-season table: one row per player per season.

Target: the player's last market valuation of the season.
Performance stats count Premier League matches only.
"""
import numpy as np
import pandas as pd

from src.config import LEAGUE_ID, MIN_MINUTES_PER90


def add_season(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Add `season`, labelled by start year (July-June): 2025 = 2025/26."""
    d = df[date_col]
    df = df.copy()
    df["season"] = np.where(d.dt.month >= 7, d.dt.year, d.dt.year - 1)
    return df


def latest_valuation_per_season(valuations: pd.DataFrame) -> pd.DataFrame:
    """Keep each player's last valuation in each season; this is the target."""
    v = add_season(valuations).sort_values("date")
    last = v.groupby(["player_id", "season"]).tail(1)  # tail, not .last(): .last() mixes in non-null values from earlier rows
    last = last.rename(
        columns={
            "date": "value_date",
            "current_club_id": "club_id",
            "current_club_name": "club_name",
            "player_club_domestic_competition_id": "club_league_id",
        }
    )
    last["log_value"] = np.log1p(last["market_value_in_eur"])
    return last[
        ["player_id", "season", "value_date", "market_value_in_eur", "log_value",
         "club_id", "club_name", "club_league_id"]
    ]


def premier_league_season_stats(appearances: pd.DataFrame) -> pd.DataFrame:
    """Season totals from Premier League matches only."""
    a = add_season(appearances[appearances["competition_id"] == LEAGUE_ID])
    a = a.assign(start=(a["minutes_played"] >= 60).astype(int))
    stats = a.groupby(["player_id", "season"], as_index=False).agg(
        pl_apps=("game_id", "nunique"),
        pl_starts=("start", "sum"),
        pl_minutes=("minutes_played", "sum"),
        pl_goals=("goals", "sum"),
        pl_assists=("assists", "sum"),
        pl_yellow=("yellow_cards", "sum"),
        pl_red=("red_cards", "sum"),
    )
    return stats


def add_per90(df: pd.DataFrame, min_minutes: int = MIN_MINUTES_PER90) -> pd.DataFrame:
    """Goals/assists per 90, left blank when the player has too few minutes."""
    df = df.copy()
    enough = df["pl_minutes"] >= min_minutes
    df["goals_per90"] = np.where(enough, df["pl_goals"] / df["pl_minutes"] * 90, np.nan)
    df["assists_per90"] = np.where(enough, df["pl_assists"] / df["pl_minutes"] * 90, np.nan)
    return df


def add_profile(df: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
    """Add fixed player attributes and age at the valuation date."""
    prof = players[
        ["player_id", "name", "position", "sub_position", "foot", "height_in_cm",
         "country_of_citizenship", "date_of_birth", "current_club_name"]
    ].rename(columns={"current_club_name": "current_club"})
    df = df.merge(prof, on="player_id", how="left")
    df["age"] = (df["value_date"] - df["date_of_birth"]).dt.days / 365.25
    df["height_missing"] = df["height_in_cm"].isna()
    df["foot_missing"] = df["foot"].isna()
    return df.drop(columns="date_of_birth")


def add_momentum(df: pd.DataFrame) -> pd.DataFrame:
    """Previous season's value and the % change; blank if the player has no row for the previous season."""
    prev = df[["player_id", "season", "market_value_in_eur"]].copy()
    prev["season"] += 1
    prev = prev.rename(columns={"market_value_in_eur": "prev_value"})
    df = df.merge(prev, on=["player_id", "season"], how="left")
    df["value_change_pct"] = (df["market_value_in_eur"] / df["prev_value"] - 1) * 100
    return df


def build_player_season(players, valuations, appearances) -> pd.DataFrame:
    df = latest_valuation_per_season(valuations)
    df = df.merge(premier_league_season_stats(appearances), on=["player_id", "season"], how="left")
    # No Premier League appearances in a season (e.g. the player was in another league) means
    # "no data", not zero performance, so those stats stay blank instead of being filled with 0.
    df["no_pl_data"] = df["pl_apps"].isna()
    df = add_per90(df)
    df = add_profile(df, players)
    df = add_momentum(df)
    return df.sort_values(["player_id", "season"]).reset_index(drop=True)
