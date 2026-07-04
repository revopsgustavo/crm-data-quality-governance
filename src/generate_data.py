from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DATABASE = ROOT / "data" / "database"
TODAY = pd.Timestamp("2026-07-04")


def d(days: int) -> str:
    return (TODAY - pd.Timedelta(days=days)).strftime("%Y-%m-%d")


def f(days: int) -> str:
    return (TODAY + pd.Timedelta(days=days)).strftime("%Y-%m-%d")


def main() -> None:
    rng = np.random.default_rng(42)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    DATABASE.mkdir(parents=True, exist_ok=True)

    users = pd.DataFrame(
        [
            ["usr_001", "Ana Souza", "AE", "Enterprise", "active"],
            ["usr_002", "Bruno Lima", "AE", "Mid Market", "active"],
            ["usr_003", "Carla Rocha", "AE", "SMB", "active"],
            ["usr_004", "Diego Martins", "Sales Manager", "Enterprise", "active"],
            ["usr_005", "Fernanda Alves", "RevOps", "Operations", "active"],
            ["usr_006", "Gustavo Pereira", "SDR", "Inbound", "active"],
        ],
        columns=["user_id", "user_name", "role", "team", "status"],
    )
    stages = pd.DataFrame(
        [
            ["Prospecting", 0.10, "Pipeline"],
            ["Discovery", 0.25, "Pipeline"],
            ["Solution", 0.45, "Best Case"],
            ["Proposal", 0.60, "Best Case"],
            ["Negotiation", 0.75, "Best Case"],
            ["Procurement", 0.85, "Commit"],
            ["Contract", 0.95, "Commit"],
            ["Closed Won", 1.00, "Closed"],
            ["Closed Lost", 0.00, "Omitted"],
        ],
        columns=["stage", "default_probability", "default_forecast_category"],
    )
    forecast_categories = pd.DataFrame({"forecast_category": ["Pipeline", "Best Case", "Commit", "Closed", "Omitted"]})

    leads = []
    for i in range(1, 121):
        leads.append(
            {
                "lead_id": f"lead_{i:03d}",
                "lead_name": f"Lead {i:03d}",
                "email": "duplicate@example.com" if i in {18, 19, 20} else f"lead{i:03d}@example.com",
                "company": f"Company {i % 37:02d}",
                "source": "" if i % 9 == 0 else rng.choice(["Inbound", "Outbound", "Partner", "Paid Search", "Event"]),
                "owner_id": rng.choice(["usr_006", "usr_001", "usr_002", "usr_003"]),
                "created_date": d(int(rng.integers(1, 90))),
                "status": rng.choice(["New", "Working", "Qualified", "Disqualified"]),
            }
        )
    leads = pd.DataFrame(leads)

    accounts = []
    for i in range(1, 46):
        name, domain = f"Account {i:02d}", f"account{i:02d}.com"
        if i in {12, 13}:
            name, domain = "Atlas Cloud", "atlascloud.com"
        if i in {27, 28}:
            name, domain = "Nexa SaaS", "nexasaas.com"
        accounts.append(
            {
                "account_id": f"acct_{i:03d}",
                "account_name": name,
                "domain": domain,
                "segment": ["SMB", "Mid Market", "Enterprise"][i % 3],
                "owner_id": "" if i in {8, 21, 35, 42} else ["usr_001", "usr_002", "usr_003"][i % 3],
                "industry": ["Fintech", "Healthtech", "Edtech", "Retail", "Logistics"][i % 5],
                "created_date": d((i * 2) % 90),
            }
        )
    accounts = pd.DataFrame(accounts)

    contacts = pd.DataFrame(
        [
            {
                "contact_id": f"cont_{i:03d}",
                "account_id": "" if i in {9, 31, 62, 77} else accounts.iloc[(i * 3) % len(accounts)]["account_id"],
                "contact_name": f"Contact {i:03d}",
                "email": f"contact{i:03d}@example.com",
                "title": ["CFO", "Head of Sales", "RevOps Manager", "CEO"][i % 4],
                "created_date": d((i * 5) % 90),
            }
            for i in range(1, 91)
        ]
    )

    defaults = {
        "Prospecting": (0.10, "Pipeline"),
        "Discovery": (0.25, "Pipeline"),
        "Solution": (0.45, "Best Case"),
        "Proposal": (0.60, "Best Case"),
        "Negotiation": (0.75, "Best Case"),
        "Procurement": (0.85, "Commit"),
        "Contract": (0.95, "Commit"),
        "Closed Won": (1.00, "Closed"),
        "Closed Lost": (0.00, "Omitted"),
    }
    stages_list = list(defaults)
    opportunities = []
    for i in range(1, 81):
        stage = stages_list[i % len(stages_list)]
        probability, category = defaults[stage]
        amount = float(rng.integers(18000, 240000))
        close_date = f(int(rng.integers(5, 55)))
        if i in {5, 16, 37, 52, 64}:
            close_date = ""
        if i in {6, 17, 29, 47, 68}:
            category = "Commit" if category != "Commit" else "Pipeline"
        if i in {10, 22, 43, 59}:
            probability = 0.98
        if i in {11, 24, 40, 67}:
            amount = 0.0
        if i in {8, 26, 53, 72}:
            close_date = d(int(rng.integers(1, 35)))
        owner = "" if i in {12, 33, 57, 74} else ["usr_001", "usr_002", "usr_003"][i % 3]
        next_step = "" if i in {7, 18, 32, 48, 55, 69} else f"Follow up {i}"
        loss_reason = ""
        if i in {17, 35, 62}:
            stage, category, probability, loss_reason = "Closed Lost", "Omitted", 0.0, ""
        if i in {14, 41}:
            stage, category, probability, amount = "Closed Won", "Closed", 1.0, 0.0
        opportunities.append(
            {
                "opportunity_id": f"opp_{i:03d}",
                "account_id": accounts.iloc[(i * 2) % len(accounts)]["account_id"],
                "owner_id": owner,
                "opportunity_name": f"Opportunity {i:03d}",
                "stage": stage,
                "forecast_category": category,
                "probability": probability,
                "amount": amount,
                "close_date": close_date,
                "created_date": d(int(rng.integers(20, 90))),
                "last_stage_change_date": d(int(rng.integers(1, 45))),
                "next_step": next_step,
                "loss_reason": loss_reason,
            }
        )
    opportunities = pd.DataFrame(opportunities)

    activities = pd.DataFrame(
        [
            {
                "activity_id": f"act_{i:03d}",
                "related_object_type": "opportunity",
                "related_object_id": row["opportunity_id"],
                "activity_type": ["call", "email", "meeting"][i % 3],
                "activity_date": d((i * 3) % 25),
                "owner_id": row["owner_id"],
                "notes_quality": ["high", "medium", "low"][i % 3],
            }
            for i, row in enumerate(opportunities.to_dict("records"), start=1)
        ]
    )
    crm_audit_log = pd.DataFrame(
        [
            {
                "event_id": f"evt_{i:03d}",
                "object_type": "opportunity",
                "object_id": f"opp_{i:03d}",
                "field_changed": "close_date" if i % 2 == 0 else "forecast_category",
                "old_value": f(10),
                "new_value": f(20),
                "changed_by": "usr_005",
                "change_type": "manual",
                "changed_at": d(i % 80),
                "activity_correlated": i % 3 == 0,
            }
            for i in range(1, 70)
        ]
    )
    data_quality_checks = pd.DataFrame(
        [
            ["chk_001", "leads", "source", "required_field", "critical", "active"],
            ["chk_002", "accounts", "owner_id", "required_field", "critical", "active"],
            ["chk_003", "opportunities", "close_date", "forecast_governance", "critical", "active"],
        ],
        columns=["check_id", "object", "field", "check_type", "severity", "status"],
    )
    remediation_tasks = pd.DataFrame(
        [
            ["tsk_001", "lead_source_cleanup", "usr_006", "high", d(4), "in_progress"],
            ["tsk_002", "account_owner_backfill", "usr_005", "critical", d(2), "open"],
            ["tsk_003", "forecast_category_review", "usr_004", "critical", f(3), "open"],
            ["tsk_004", "close_date_push_reason_code", "usr_004", "high", d(1), "open"],
        ],
        columns=["task_id", "task_name", "owner_id", "severity", "due_date", "status"],
    )

    tables = {
        "leads": leads,
        "accounts": accounts,
        "contacts": contacts,
        "opportunities": opportunities,
        "users": users,
        "activities": activities,
        "forecast_categories": forecast_categories,
        "stages": stages,
        "crm_audit_log": crm_audit_log,
        "data_quality_checks": data_quality_checks,
        "remediation_tasks": remediation_tasks,
    }
    for name, table in tables.items():
        table.to_csv(PROCESSED / f"{name}.csv", index=False)
    with sqlite3.connect(DATABASE / "crm_governance_case.sqlite") as conn:
        for name, table in tables.items():
            table.to_sql(name, conn, if_exists="replace", index=False)
    print(f"Synthetic CRM governance data generated in {PROCESSED}")


if __name__ == "__main__":
    main()
