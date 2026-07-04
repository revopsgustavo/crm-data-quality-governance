from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def test_main_crm_governance_files_exist():
    for name in [
        "leads",
        "accounts",
        "contacts",
        "opportunities",
        "users",
        "activities",
        "forecast_categories",
        "stages",
        "crm_audit_log",
        "data_quality_checks",
        "remediation_tasks",
    ]:
        assert (PROCESSED / f"{name}.csv").exists()


def test_required_columns_and_primary_ids_not_null():
    required = {
        "leads": ["lead_id", "source"],
        "accounts": ["account_id", "owner_id"],
        "contacts": ["contact_id", "account_id"],
        "opportunities": ["opportunity_id", "account_id", "owner_id", "amount", "close_date", "stage", "forecast_category", "probability"],
        "users": ["user_id"],
        "activities": ["activity_id", "related_object_id"],
    }
    for table, columns in required.items():
        df = pd.read_csv(PROCESSED / f"{table}.csv")
        for column in columns:
            assert column in df.columns
        assert df[columns[0]].notna().all()
