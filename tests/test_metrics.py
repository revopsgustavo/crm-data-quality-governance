from __future__ import annotations

from src import metrics


def test_crm_governance_metrics_do_not_error_and_stay_in_range():
    tables = metrics.load_all()
    summary = metrics.executive_summary_metrics(tables)
    assert 0 <= summary["crm_data_quality_score"] <= 100
    assert 0 <= summary["forecast_reliability_score"] <= 100
    assert 0 <= summary["pipeline_hygiene_score"] <= 100
    assert 0 <= summary["duplicate_lead_rate"] <= 1
    assert 0 <= summary["duplicate_account_rate"] <= 1
    assert 0 <= summary["lead_missing_source_rate"] <= 1
    assert summary["revenue_at_risk_from_data_quality"] >= 0
