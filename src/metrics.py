from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from src.utils import safe_divide
except ModuleNotFoundError:  # pragma: no cover
    from utils import safe_divide

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
TODAY = pd.Timestamp("2026-07-04")
OPEN_STAGES = {"Prospecting", "Discovery", "Solution", "Proposal", "Negotiation", "Procurement", "Contract"}
ADVANCED_STAGES = {"Negotiation", "Procurement", "Contract"}
VALID_FORECAST_BY_STAGE = {
    "Prospecting": {"Pipeline"},
    "Discovery": {"Pipeline"},
    "Solution": {"Pipeline", "Best Case"},
    "Proposal": {"Best Case"},
    "Negotiation": {"Best Case", "Commit"},
    "Procurement": {"Commit"},
    "Contract": {"Commit"},
    "Closed Won": {"Closed"},
    "Closed Lost": {"Omitted"},
}
EXPECTED_PROBABILITY = {
    "Prospecting": (0.0, 0.20),
    "Discovery": (0.15, 0.35),
    "Solution": (0.30, 0.55),
    "Proposal": (0.45, 0.70),
    "Negotiation": (0.60, 0.85),
    "Procurement": (0.75, 0.95),
    "Contract": (0.85, 0.99),
    "Closed Won": (1.0, 1.0),
    "Closed Lost": (0.0, 0.0),
}


def load_table(name: str, base_path: Path = PROCESSED) -> pd.DataFrame:
    path = base_path / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def load_all(base_path: Path = PROCESSED) -> dict[str, pd.DataFrame]:
    names = [
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
    ]
    return {name: load_table(name, base_path) for name in names}


def blank(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().eq("")


def open_opportunities(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or "stage" not in opportunities:
        return opportunities.iloc[0:0].copy()
    return opportunities[opportunities["stage"].isin(OPEN_STAGES)].copy()


def duplicate_rate(df: pd.DataFrame, subset: list[str] | str) -> float:
    if df.empty:
        return 0.0
    subset = [subset] if isinstance(subset, str) else subset
    if not set(subset).issubset(df.columns):
        return 0.0
    return safe_divide(int(df.duplicated(subset=subset, keep=False).sum()), len(df))


def lead_missing_source_rate(leads: pd.DataFrame) -> float:
    return safe_divide(int(blank(leads["source"]).sum()), len(leads)) if not leads.empty and "source" in leads else 0.0


def duplicate_leads(leads: pd.DataFrame) -> pd.DataFrame:
    return leads[leads.duplicated(["email"], keep=False)].copy() if not leads.empty and "email" in leads else pd.DataFrame()


def duplicate_accounts(accounts: pd.DataFrame) -> pd.DataFrame:
    if accounts.empty or not {"account_name", "domain"}.issubset(accounts.columns):
        return pd.DataFrame()
    return accounts[accounts.duplicated(["account_name", "domain"], keep=False)].copy()


def contacts_without_account(contacts: pd.DataFrame) -> pd.DataFrame:
    return contacts[blank(contacts["account_id"])].copy() if not contacts.empty and "account_id" in contacts else pd.DataFrame()


def accounts_without_owner(accounts: pd.DataFrame) -> pd.DataFrame:
    return accounts[blank(accounts["owner_id"])].copy() if not accounts.empty and "owner_id" in accounts else pd.DataFrame()


def opportunities_without_owner(opportunities: pd.DataFrame) -> pd.DataFrame:
    return opportunities[blank(opportunities["owner_id"])].copy() if not opportunities.empty and "owner_id" in opportunities else pd.DataFrame()


def opportunities_without_close_date(opportunities: pd.DataFrame) -> pd.DataFrame:
    return opportunities[blank(opportunities["close_date"])].copy() if not opportunities.empty and "close_date" in opportunities else pd.DataFrame()


def opportunities_without_next_step(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or "next_step" not in opportunities:
        return pd.DataFrame()
    opened = open_opportunities(opportunities)
    return opened[blank(opened["next_step"])].copy()


def stale_opportunities(opportunities: pd.DataFrame, days: int = 20) -> pd.DataFrame:
    if opportunities.empty or "last_stage_change_date" not in opportunities:
        return pd.DataFrame()
    opened = open_opportunities(opportunities)
    last_change = pd.to_datetime(opened["last_stage_change_date"], errors="coerce")
    return opened[(TODAY - last_change).dt.days > days].copy()


def advanced_stage_without_activity(opportunities: pd.DataFrame, activities: pd.DataFrame, days: int = 14) -> pd.DataFrame:
    if opportunities.empty or activities.empty or "related_object_id" not in activities:
        return pd.DataFrame()
    last_activity = activities.groupby("related_object_id", as_index=False).agg(last_activity_date=("activity_date", "max"))
    merged = opportunities.merge(last_activity, left_on="opportunity_id", right_on="related_object_id", how="left")
    dates = pd.to_datetime(merged["last_activity_date"], errors="coerce")
    return merged[merged["stage"].isin(ADVANCED_STAGES) & (dates.isna() | ((TODAY - dates).dt.days > days))].copy()


def closed_won_without_amount(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or not {"stage", "amount"}.issubset(opportunities.columns):
        return pd.DataFrame()
    amount = pd.to_numeric(opportunities["amount"], errors="coerce")
    return opportunities[opportunities["stage"].eq("Closed Won") & (amount.isna() | (amount <= 0))].copy()


def closed_lost_without_loss_reason(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or not {"stage", "loss_reason"}.issubset(opportunities.columns):
        return pd.DataFrame()
    return opportunities[opportunities["stage"].eq("Closed Lost") & blank(opportunities["loss_reason"])].copy()


def opportunities_with_zero_amount(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or "amount" not in opportunities:
        return pd.DataFrame()
    amount = pd.to_numeric(opportunities["amount"], errors="coerce").fillna(0)
    return opportunities[amount <= 0].copy()


def open_opportunities_with_past_close_date(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or "close_date" not in opportunities:
        return pd.DataFrame()
    opened = open_opportunities(opportunities)
    return opened[pd.to_datetime(opened["close_date"], errors="coerce") < TODAY].copy()


def forecast_category_inconsistencies(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or not {"stage", "forecast_category"}.issubset(opportunities.columns):
        return pd.DataFrame()
    invalid = [idx for idx, row in opportunities.iterrows() if row["forecast_category"] not in VALID_FORECAST_BY_STAGE.get(row["stage"], set())]
    return opportunities.loc[invalid].copy()


def invalid_stage_probability_combinations(opportunities: pd.DataFrame) -> pd.DataFrame:
    if opportunities.empty or not {"stage", "probability"}.issubset(opportunities.columns):
        return pd.DataFrame()
    df = opportunities.copy()
    df["probability"] = pd.to_numeric(df["probability"], errors="coerce")
    invalid = []
    for idx, row in df.iterrows():
        low, high = EXPECTED_PROBABILITY.get(row["stage"], (0.0, 1.0))
        if pd.isna(row["probability"]) or row["probability"] < low or row["probability"] > high:
            invalid.append(idx)
    return df.loc[invalid].copy()


def manual_close_date_change_rate(audit_log: pd.DataFrame) -> float:
    if audit_log.empty or "field_changed" not in audit_log:
        return 0.0
    manual = audit_log[audit_log["change_type"].eq("manual")] if "change_type" in audit_log else audit_log
    return safe_divide(int(manual["field_changed"].eq("close_date").sum()), len(audit_log))


def remediation_completion_rate(tasks: pd.DataFrame) -> float:
    return safe_divide(int(tasks["status"].eq("completed").sum()), len(tasks)) if not tasks.empty and "status" in tasks else 0.0


def overdue_remediation_tasks(tasks: pd.DataFrame) -> pd.DataFrame:
    if tasks.empty or not {"due_date", "status"}.issubset(tasks.columns):
        return pd.DataFrame()
    return tasks[(pd.to_datetime(tasks["due_date"], errors="coerce") < TODAY) & ~tasks["status"].eq("completed")].copy()


def data_quality_issues_by_owner(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    opportunities = tables.get("opportunities", pd.DataFrame())
    if not opportunities.empty and "owner_id" in opportunities:
        for owner, group in opportunities.fillna({"owner_id": "missing_owner"}).groupby("owner_id"):
            rows.append(
                {
                    "owner_id": owner or "missing_owner",
                    "object": "opportunities",
                    "issue_count": len(opportunities_without_owner(group))
                    + len(opportunities_without_close_date(group))
                    + len(opportunities_without_next_step(group))
                    + len(opportunities_with_zero_amount(group))
                    + len(forecast_category_inconsistencies(group)),
                }
            )
    return pd.DataFrame(rows)


def data_quality_issues_by_object(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    leads = tables.get("leads", pd.DataFrame())
    accounts = tables.get("accounts", pd.DataFrame())
    contacts = tables.get("contacts", pd.DataFrame())
    opportunities = tables.get("opportunities", pd.DataFrame())
    return pd.DataFrame(
        [
            {"object": "leads", "issue_count": len(duplicate_leads(leads)) + int(lead_missing_source_rate(leads) * len(leads))},
            {"object": "accounts", "issue_count": len(duplicate_accounts(accounts)) + len(accounts_without_owner(accounts))},
            {"object": "contacts", "issue_count": len(contacts_without_account(contacts))},
            {
                "object": "opportunities",
                "issue_count": len(opportunities_without_owner(opportunities))
                + len(opportunities_without_close_date(opportunities))
                + len(opportunities_without_next_step(opportunities))
                + len(stale_opportunities(opportunities))
                + len(opportunities_with_zero_amount(opportunities))
                + len(open_opportunities_with_past_close_date(opportunities))
                + len(invalid_stage_probability_combinations(opportunities))
                + len(forecast_category_inconsistencies(opportunities)),
            },
        ]
    )


def revenue_at_risk_from_data_quality(opportunities: pd.DataFrame) -> float:
    if opportunities.empty or "amount" not in opportunities:
        return 0.0
    risky_ids: set[str] = set()
    for frame in [
        opportunities_without_owner(opportunities),
        opportunities_without_close_date(opportunities),
        opportunities_without_next_step(opportunities),
        opportunities_with_zero_amount(opportunities),
        open_opportunities_with_past_close_date(opportunities),
        invalid_stage_probability_combinations(opportunities),
        forecast_category_inconsistencies(opportunities),
    ]:
        if "opportunity_id" in frame:
            risky_ids.update(frame["opportunity_id"].astype(str))
    amount = pd.to_numeric(opportunities["amount"], errors="coerce").fillna(0)
    return float(opportunities[opportunities["opportunity_id"].astype(str).isin(risky_ids)].assign(_amount=amount)["_amount"].clip(lower=0).sum())


def forecast_reliability_score(opportunities: pd.DataFrame, activities: pd.DataFrame | None = None) -> float:
    if opportunities.empty:
        return 100.0
    penalties = (
        safe_divide(len(opportunities_without_close_date(opportunities)), len(opportunities)) * 22
        + safe_divide(len(forecast_category_inconsistencies(opportunities)), len(opportunities)) * 28
        + safe_divide(len(invalid_stage_probability_combinations(opportunities)), len(opportunities)) * 22
        + safe_divide(len(open_opportunities_with_past_close_date(opportunities)), len(opportunities)) * 18
    )
    if activities is not None:
        penalties += safe_divide(len(advanced_stage_without_activity(opportunities, activities)), len(opportunities)) * 10
    return max(0.0, min(100.0, 100.0 - penalties))


def pipeline_hygiene_score(opportunities: pd.DataFrame, activities: pd.DataFrame | None = None) -> float:
    if opportunities.empty:
        return 100.0
    penalties = (
        safe_divide(len(opportunities_without_next_step(opportunities)), len(opportunities)) * 25
        + safe_divide(len(stale_opportunities(opportunities)), len(opportunities)) * 25
        + safe_divide(len(opportunities_with_zero_amount(opportunities)), len(opportunities)) * 15
        + safe_divide(len(opportunities_without_owner(opportunities)), len(opportunities)) * 20
        + safe_divide(len(open_opportunities_with_past_close_date(opportunities)), len(opportunities)) * 15
    )
    if activities is not None:
        penalties += safe_divide(len(advanced_stage_without_activity(opportunities, activities)), len(opportunities)) * 15
    return max(0.0, min(100.0, 100.0 - penalties))


def object_quality_score(object_name: str, tables: dict[str, pd.DataFrame]) -> float:
    df = tables.get(object_name, pd.DataFrame())
    if df.empty:
        return 0.0
    issue_count = data_quality_issues_by_object(tables).set_index("object").loc[object_name, "issue_count"]
    return max(0.0, min(100.0, 100.0 - safe_divide(issue_count, len(df)) * 100))


def crm_data_quality_score(tables: dict[str, pd.DataFrame]) -> float:
    opportunities = tables.get("opportunities", pd.DataFrame())
    activities = tables.get("activities", pd.DataFrame())
    scores = [object_quality_score(name, tables) for name in ["leads", "accounts", "contacts", "opportunities"]]
    scores += [forecast_reliability_score(opportunities, activities), pipeline_hygiene_score(opportunities, activities)]
    return round(sum(scores) / len(scores), 2)


def missing_required_fields(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    required = {
        "leads": ["lead_id", "source"],
        "accounts": ["account_id", "owner_id"],
        "contacts": ["contact_id", "account_id"],
        "opportunities": ["opportunity_id", "account_id", "owner_id", "amount", "close_date", "stage", "forecast_category", "probability"],
        "users": ["user_id"],
        "activities": ["activity_id", "related_object_id"],
        "forecast_categories": ["forecast_category"],
        "stages": ["stage"],
        "crm_audit_log": ["event_id"],
        "data_quality_checks": ["check_id"],
        "remediation_tasks": ["task_id"],
    }
    rows = []
    for table, columns in required.items():
        df = tables.get(table, pd.DataFrame())
        for column in columns:
            missing = len(df) if column not in df else int(blank(df[column]).sum())
            rows.append({"object": table, "field": column, "missing_count": missing, "missing_rate": safe_divide(missing, len(df))})
    return pd.DataFrame(rows)


def critical_issue_count(gaps: pd.DataFrame) -> int:
    return int(gaps.get("severity", pd.Series(dtype=str)).eq("critical").sum())


def high_issue_count(gaps: pd.DataFrame) -> int:
    return int(gaps.get("severity", pd.Series(dtype=str)).eq("high").sum())


def executive_summary_metrics(tables: dict[str, pd.DataFrame]) -> dict[str, float]:
    opportunities = tables.get("opportunities", pd.DataFrame())
    activities = tables.get("activities", pd.DataFrame())
    return {
        "crm_data_quality_score": crm_data_quality_score(tables),
        "forecast_reliability_score": forecast_reliability_score(opportunities, activities),
        "pipeline_hygiene_score": pipeline_hygiene_score(opportunities, activities),
        "revenue_at_risk_from_data_quality": revenue_at_risk_from_data_quality(opportunities),
        "lead_missing_source_rate": lead_missing_source_rate(tables.get("leads", pd.DataFrame())),
        "duplicate_lead_rate": duplicate_rate(tables.get("leads", pd.DataFrame()), "email"),
        "duplicate_account_rate": duplicate_rate(tables.get("accounts", pd.DataFrame()), ["account_name", "domain"]),
        "manual_close_date_change_rate": manual_close_date_change_rate(tables.get("crm_audit_log", pd.DataFrame())),
        "remediation_completion_rate": remediation_completion_rate(tables.get("remediation_tasks", pd.DataFrame())),
    }
