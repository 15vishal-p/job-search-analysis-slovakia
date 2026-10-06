import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from fetch_eurostat import parse_jsonstat  # noqa: E402


def doc(values, sizes=(1, 1, 3)):
    return {
        "id": ["freq", "geo", "time"],
        "size": list(sizes),
        "dimension": {"time": {"category": {"index": {"2026-06": 0, "2026-07": 1, "2026-08": 2}}}},
        "value": values,
    }


def test_parses_and_sorts_by_period():
    s = parse_jsonstat(doc({"2": 5.4, "0": 5.6, "1": 5.5}))
    assert list(s.index) == ["2026-06", "2026-07", "2026-08"]
    assert list(s.values) == [5.6, 5.5, 5.4]


def test_missing_values_are_skipped():
    s = parse_jsonstat(doc({"0": 5.6, "2": 5.4}))
    assert list(s.index) == ["2026-06", "2026-08"]


def test_rejects_unpinned_dimensions():
    with pytest.raises(ValueError):
        parse_jsonstat(doc({"0": 1.0}, sizes=(1, 2, 3)))
