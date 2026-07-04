from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GAP_LOG = ROOT / "data" / "processed" / "consultant_gap_log.csv"


def test_consultant_gap_log_generated_with_required_columns():
    assert GAP_LOG.exists()
    gaps = pd.read_csv(GAP_LOG)
    assert len(gaps) >= 1
    for column in ["severity", "recommended_action", "missing_evidence", "validation_questions"]:
        assert column in gaps.columns
        assert gaps[column].notna().all()


def test_gap_log_does_not_assert_root_cause_as_fact():
    text = " ".join(pd.read_csv(GAP_LOG).astype(str).stack().tolist()).lower()
    assert not any(term in text for term in ["a causa é", "foi comprovado", "garantidamente", "com certeza"])
