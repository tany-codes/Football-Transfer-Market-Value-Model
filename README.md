# What affects a footballer's market value?

Exploratory analysis of Transfermarkt data with pandas, numpy and seaborn.

**Scope:** current Premier League players only, using the last 5 years of data.
A prediction/regression model comes later, once the exploration is done.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then put the three Transfermarkt CSVs in `data/raw/` (see `data/raw/README.md`).

## Structure

```
data/raw/         original CSVs (not tracked by git)
data/processed/   cleaned/aggregated outputs (not tracked)
notebooks/        numbered Jupyter notebooks, run in order
src/              reusable code (config, loading, features, plots)
reports/figures/  saved charts
```

## Findings

_To be filled in._
