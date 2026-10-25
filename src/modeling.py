"""Linear regression of log market value on player features (statsmodels OLS)."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# Model A: profile + last season's value. Model B adds Premier League performance.
FORMULA_A = "log_value ~ age + I(age ** 2) + C(position) + height_in_cm + C(foot, Treatment('right')) + log_prev_value"
FORMULA_B = FORMULA_A + " + pl_minutes_k + goals_per90 + assists_per90"

NEEDED_A = ["log_value", "age", "position", "height_in_cm", "foot", "log_prev_value"]
NEEDED_B = NEEDED_A + ["pl_minutes_k", "goals_per90", "assists_per90"]

# The same two models without last season's value (A0, B0).
FORMULA_A0 = "log_value ~ age + I(age ** 2) + C(position) + height_in_cm + C(foot, Treatment('right'))"
FORMULA_B0 = FORMULA_A0 + " + pl_minutes_k + goals_per90 + assists_per90"

NEEDED_A0 = ["log_value", "age", "position", "height_in_cm", "foot"]
NEEDED_B0 = NEEDED_A0 + ["pl_minutes_k", "goals_per90", "assists_per90"]


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Add model columns. Rows without a previous-season value (the first season) can't be modelled."""
    df = df.copy()
    df["log_prev_value"] = np.log1p(df["prev_value"])
    df["pl_minutes_k"] = df["pl_minutes"] / 1000  # minutes in thousands
    return df


def usable_rows(df: pd.DataFrame, needed: list) -> pd.DataFrame:
    return df.dropna(subset=needed)


def time_split(df: pd.DataFrame, test_season: int):
    """Train on seasons before `test_season`, test on `test_season` itself."""
    return df[df["season"] < test_season], df[df["season"] == test_season]


def evaluate(pred_log: pd.Series, actual_log: pd.Series) -> dict:
    """Test-set scores: R2 and RMSE on the log scale, and typical error in euros / percent."""
    resid = actual_log - pred_log
    ss_res = (resid**2).sum()
    ss_tot = ((actual_log - actual_log.mean()) ** 2).sum()
    pred, actual = np.expm1(pred_log), np.expm1(actual_log)
    return {
        "n_test": len(actual_log),
        "R2": 1 - ss_res / ss_tot,
        "RMSE (log)": float(np.sqrt((resid**2).mean())),
        "median error (EUR M)": float((pred - actual).abs().median() / 1e6),
        "median error (%)": float(((pred - actual).abs() / actual).median() * 100),
    }


def fit_and_score(formula: str, train: pd.DataFrame, test: pd.DataFrame):
    model = smf.ols(formula, data=train).fit()
    return model, evaluate(model.predict(test), test["log_value"])


def readable_names(names) -> list:
    """Turn statsmodels term names like "C(position)[T.Goalkeeper]" into labels for charts."""
    fixed = {
        "log_prev_value": "Last season's value (log)",
        "pl_minutes_k": "PL minutes (per 1,000)",
        "goals_per90": "Goals per 90",
        "assists_per90": "Assists per 90",
        "height_in_cm": "Height (per cm)",
        "age": "Age",
        "I(age ** 2)": "Age squared",
    }
    out = []
    for n in names:
        if n.startswith("C(position)"):
            out.append(f"Position: {n.split('T.')[1].rstrip(']')} (vs Attack)")
        elif n.startswith("C(foot"):
            out.append(f"Foot: {n.split('T.')[1].rstrip(']')} (vs right)")
        else:
            out.append(fixed.get(n, n))
    return out
