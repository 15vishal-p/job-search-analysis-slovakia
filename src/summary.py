"""Recompute the headline numbers from data/applications.csv.

Run: python src/summary.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data" / "applications.csv"


def main() -> None:
    df = pd.read_csv(DATA)
    n = len(df)
    status = df["final_status"]
    interview = (df["interview"] == "Yes").sum()
    test_or_interview = ((df["interview"] == "Yes") | (df["assessment"] == "Yes")).sum()
    days = df["days_to_first_reply"].dropna()

    print(f"Applications:                 {n}")
    print(f"Ghosted (no reply 30+ days):  {status.str.startswith('Ghosted').sum()}")
    print(f"Rejected (any stage):         {status.str.startswith('Rejected').sum()}")
    print(f"Reached a test or interview:  {test_or_interview}")
    print(f"Interviews:                   {interview} (1 in {round(n / interview)})")
    print(f"Instant rejections (0-1 day): {(df['instant_rejection'] == 'Yes').sum()}")
    print(f"Median days to first reply:   {days.median():.0f}")
    print("\nFinal status:")
    print(status.value_counts().to_string())
    print("\nWho sent the first reply:")
    print(df["first_reply_sender"].value_counts().to_string())
    print("\nInterviews per 100 applications by channel:")
    ch = df.groupby("applied_via").agg(n=("company", "size"), iv=("interview", lambda s: (s == "Yes").sum()))
    ch = ch[ch.n >= 10].assign(per_100=lambda x: (x.iv / x.n * 100).round(1))
    print(ch.sort_values("n", ascending=False).to_string())


if __name__ == "__main__":
    main()
