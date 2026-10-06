"""Download the latest official Slovak labour market series from Eurostat.

Writes data/eurostat_sk.csv (series, period, value). Run monthly:
    python src/fetch_eurostat.py

No API key is needed. If a series fails to download, the others are still saved.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
OUT = Path(__file__).resolve().parent.parent / "data" / "eurostat_sk.csv"
SINCE = "2019-01"

# name -> (dataset, filters). Every filter must pin one value so that only time varies.
SERIES = {
    "unemployment_rate": ("une_rt_m", {"geo": "SK", "s_adj": "SA", "age": "TOTAL", "sex": "T", "unit": "PC_ACT"}),
    "youth_unemployment_rate": ("une_rt_m", {"geo": "SK", "s_adj": "SA", "age": "Y_LT25", "sex": "T", "unit": "PC_ACT"}),
    "inflation_hicp": ("prc_hicp_manr", {"geo": "SK", "coicop": "CP00", "unit": "RCH_A"}),
    "job_vacancy_rate": ("jvs_q_nace2", {"geo": "SK", "nace_r2": "B-S", "sizeclas": "TOTAL", "s_adj": "NSA", "indic_em": "JOBRATE"}),
}


def parse_jsonstat(doc: dict) -> pd.Series:
    """Turn a Eurostat JSON-stat 2.0 response into a Series indexed by time period."""
    ids, sizes = doc["id"], doc["size"]
    if any(s != 1 for d, s in zip(ids, sizes) if d != "time"):
        raise ValueError(f"expected one value per non-time dimension, got sizes {dict(zip(ids, sizes))}")
    # With every other dimension fixed to one value, the flat index equals the time index.
    time_index = doc["dimension"]["time"]["category"]["index"]
    by_pos = {pos: period for period, pos in time_index.items()}
    values = {by_pos[int(k)]: v for k, v in doc["value"].items() if v is not None}
    return pd.Series(values, dtype=float).sort_index()


def fetch(dataset: str, filters: dict) -> pd.Series:
    params = {**filters, "format": "JSON", "lang": "EN", "sinceTimePeriod": SINCE}
    url = API + dataset + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        return parse_jsonstat(json.load(resp))


def main() -> int:
    frames, failed = [], []
    for name, (dataset, filters) in SERIES.items():
        try:
            s = fetch(dataset, filters)
        except Exception as exc:  # keep going so one broken series does not block the rest
            print(f"  {name}: failed ({exc})", file=sys.stderr)
            failed.append(name)
            continue
        print(f"  {name}: {len(s)} points, latest {s.index[-1]} = {s.iloc[-1]}")
        frames.append(pd.DataFrame({"series": name, "period": s.index, "value": s.values}))
    if not frames:
        print("Nothing downloaded; existing file left unchanged.", file=sys.stderr)
        return 1
    new = pd.concat(frames)
    if OUT.exists() and failed:  # keep the last good copy of series that failed this time
        old = pd.read_csv(OUT)
        new = pd.concat([old[old.series.isin(failed)], new])
    new.to_csv(OUT, index=False)
    print(f"Saved {OUT.relative_to(OUT.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
