"""Regression case from the C-002 refund trace."""

from pathlib import Path

import pytest


@pytest.mark.student
@pytest.mark.parametrize(
    ("shape", "matches_label"),
    [("fixed", True), ("seeded_regression", False)],
)
def test_c002_refund_outcome_matches_label(monkeypatch, shape, matches_label):
    from lab9.trace_case import investigate

    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    case = investigate(shape, "C-002", 11)
    trial, label = case["trial"], case["label"]
    actual = (
        trial["snapshot"]["refund_vnd"],
        trial["snapshot"]["refund_count"],
        trial["result"]["status"],
    )
    expected = (label["refund_vnd"], label["refund_count"], label["status"])

    assert (actual == expected) is matches_label, (actual, expected)
