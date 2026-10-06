"""Build the Slovakia job market dashboard and the README snapshot table.

Reads data/market_indicators.csv (hand-collected, with sources) and, when present,
data/eurostat_sk.csv (from src/fetch_eurostat.py). Writes
charts/dashboard_slovakia_market.png and refreshes the table between the
SNAPSHOT markers in README.md.

Run: python src/market_report.py
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib
import matplotlib.dates

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
INDICATORS = ROOT / "data" / "market_indicators.csv"
EUROSTAT = ROOT / "data" / "eurostat_sk.csv"
CHART = ROOT / "charts" / "dashboard_slovakia_market.png"
README = ROOT / "README.md"

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

# indicator -> (label, formatter) for the README snapshot, in display order
SNAPSHOT = {
    "registered_unemployment_rate": ("Registered unemployment rate", "{:.1f}%"),
    "registered_unemployment_pdu": ("Available jobseekers (PDU)", "{:.2f}%"),
    "lfs_unemployment_rate": ("Unemployment rate (Labour Force Survey)", "{:.1f}%"),
    "average_wage": ("Average gross monthly wage", "€{:,.0f}"),
    "average_wage_real_yoy": ("Real wage growth, year on year", "{:+.1f}%"),
    "job_postings_profesia": ("Job postings on Profesia.sk", "{:,.0f}"),
    "job_postings_profesia_yoy": ("Profesia postings, year on year", "{:+.0f}%"),
    "applicants_per_posting": ("Applicants per posting", "{:.0f}"),
    "gdp_growth_forecast_nbs": ("GDP growth forecast (NBS)", "{:.1f}%"),
}
EUROSTAT_SNAPSHOT = {
    "unemployment_rate": ("Unemployment rate, seasonally adj. (Eurostat)", "{:.1f}%"),
    "youth_unemployment_rate": ("Youth unemployment, under 25 (Eurostat)", "{:.1f}%"),
    "inflation_hicp": ("Inflation, HICP year on year (Eurostat)", "{:.1f}%"),
    "job_vacancy_rate": ("Job vacancy rate (Eurostat)", "{:.1f}%"),
}


def latest(df: pd.DataFrame, key: str, col: str) -> pd.Series | None:
    rows = df[df[col] == key].sort_values("period")
    return None if rows.empty else rows.iloc[-1]


def snapshot_rows(ind: pd.DataFrame, euro: pd.DataFrame | None) -> list[str]:
    rows = []
    if euro is not None:
        for key, (label, fmt) in EUROSTAT_SNAPSHOT.items():
            r = latest(euro, key, "series")
            if r is not None:
                rows.append(f"| {label} | {fmt.format(r.value)} | {r.period} | Eurostat |")
    for key, (label, fmt) in SNAPSHOT.items():
        r = latest(ind, key, "indicator")
        if r is not None:
            rows.append(f"| {label} | {fmt.format(float(r.value))} | {r.period} | [{r.source}]({r.url}) |")
    return rows


def style(ax, title: str) -> None:
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10)
    ax.set_facecolor("#fcfcfb")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def bars(ax, labels, values, fmt, colors) -> None:
    ax.bar(labels, values, color=colors, width=0.55)
    for x, v in zip(labels, values):
        ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=10, color=INK)
    ax.set_ylim(0, max(values) * 1.18)


def draw(ind: pd.DataFrame, euro: pd.DataFrame | None) -> None:
    v = ind.set_index(["indicator", "period"])["value"].astype(float)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), dpi=150)
    fig.patch.set_facecolor("#fcfcfb")

    # 1. Fewer postings: H1 2026 vs H1 2025 (H1 2025 backed out from the -14% change)
    h1_26 = v["job_postings_profesia", "2026-H1"]
    h1_25 = h1_26 / (1 + v["job_postings_profesia_yoy", "2026-H1"] / 100)
    ax = axes[0, 0]
    bars(ax, ["H1 2025 (implied)", "H1 2026"], [h1_25, h1_26], "{:,.0f}", [MUTED, BLUE])
    style(ax, "Job postings on Profesia.sk fell 14%")
    ax.yaxis.set_major_formatter(lambda x, _: f"{x/1000:.0f}k")

    # 2. More competition per posting
    ax = axes[0, 1]
    bars(ax, ["H1 2025", "H1 2026"],
         [v["applicants_per_posting", "2025-H1"], v["applicants_per_posting", "2026-H1"]], "{:.0f}", [MUTED, ORANGE])
    style(ax, "Applicants per posting rose from 28 to 36")

    # 3. Unemployment: Eurostat monthly series if downloaded, else registered PDU points
    ax = axes[1, 0]
    if euro is not None and (euro.series == "unemployment_rate").any():
        s = euro[euro.series == "unemployment_rate"]
        ax.plot(pd.to_datetime(s.period), s.value, color=BLUE, linewidth=2)
        last = s.iloc[-1]
        ax.annotate(f"{last.value:.1f}% ({last.period})", (pd.to_datetime(last.period), last.value),
                    xytext=(-10, 10), textcoords="offset points", ha="right", fontsize=9, color=INK)
        style(ax, "Unemployment rate, seasonally adjusted (Eurostat)")
    else:
        s = ind[ind.indicator == "registered_unemployment_pdu"].sort_values("period")
        dates = pd.to_datetime(s.period)
        ax.plot(dates, s.value.astype(float), color=BLUE, linewidth=2, marker="o", markersize=6)
        for d, val in zip(dates, s.value.astype(float)):
            ax.text(d, val + 0.03, f"{val:.2f}%", ha="center", va="bottom", fontsize=9, color=INK)
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
        ax.set_ylim(3.6, 4.7)
        style(ax, "Available jobseekers (PDU), % of working-age")
    ax.yaxis.set_major_formatter(lambda x, _: f"{x:.1f}%")

    # 4. Wages: nominal level with real growth labelled
    ax = axes[1, 1]
    q = ["2026-Q1", "2026-Q2"]
    bars(ax, ["Q1 2026", "Q2 2026"], [v["average_wage", p] for p in q], "€{:,.0f}", [MUTED, BLUE])
    for x, p in zip(["Q1 2026", "Q2 2026"], q):
        ax.text(x, 120, f"real {v['average_wage_real_yoy', p]:+.1f}% y/y", ha="center", fontsize=9, color="white")
    style(ax, "Average wage rose, but real pay turned negative")

    fig.suptitle("Slovakia job market, latest data", x=0.06, ha="left", fontsize=15, color=INK, fontweight="bold")
    fig.text(0.06, 0.015, "Sources: Profesia.sk, ŠÚ SR, ÚPSVaR, Eurostat. See data/market_indicators.csv.",
             fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0.03, 0.03, 1, 0.95), h_pad=3, w_pad=3)
    CHART.parent.mkdir(exist_ok=True)
    fig.savefig(CHART, facecolor=fig.get_facecolor())
    print(f"Saved {CHART.relative_to(ROOT)}")


def update_readme(rows: list[str]) -> None:
    table = "\n".join(["| Indicator | Latest | Period | Source |", "|---|---|---|---|", *rows])
    text = README.read_text()
    new = re.sub(r"(<!-- SNAPSHOT:START -->\n).*?(\n<!-- SNAPSHOT:END -->)", rf"\g<1>{table}\g<2>", text, flags=re.S)
    if new != text:
        README.write_text(new)
        print("Updated README snapshot")


def main() -> None:
    ind = pd.read_csv(INDICATORS, dtype={"period": str})
    euro = pd.read_csv(EUROSTAT, dtype={"period": str}) if EUROSTAT.exists() else None
    rows = snapshot_rows(ind, euro)
    print("\n".join(rows))
    draw(ind, euro)
    update_readme(rows)


if __name__ == "__main__":
    main()
