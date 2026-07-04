from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from src import metrics
except ModuleNotFoundError:  # pragma: no cover
    import metrics

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "processed" / "consultant_gap_log.csv"


def gap(gap_id: str, area: str, metric: str, actual, expected: str, severity: str, evidence: str, action: str, owner: str, follow: str) -> dict:
    return {
        "gap_id": gap_id,
        "area": area,
        "metric": metric,
        "actual_value": actual,
        "expected_value": expected,
        "severity": severity,
        "evidence": evidence,
        "probable_cause": "Hipótese provável: os dados sugerem fragilidade de regra, processo ou accountability operacional; precisa ser validado antes de confirmar causa raiz.",
        "missing_evidence": "Regras reais do CRM, exceções aprovadas, notas comerciais, motivo de alteração, critérios de forecast e validação dos managers.",
        "validation_questions": "O comportamento observado vem de regra de sistema, disciplina operacional, mix de carteira, exceção aprovada ou ausência de governança?",
        "recommended_action": action,
        "owner": owner,
        "urgency": "immediate" if severity == "critical" else "this_week" if severity == "high" else "this_month",
        "expected_impact": "Melhorar forecast, pipeline hygiene, produtividade comercial, governança e qualidade da decisão executiva.",
        "follow_up_metric": follow,
        "status": "open",
    }


def find_gaps(tables: dict[str, pd.DataFrame] | None = None) -> pd.DataFrame:
    tables = tables or metrics.load_all()
    leads, accounts, contacts = tables["leads"], tables["accounts"], tables["contacts"]
    opportunities, activities = tables["opportunities"], tables["activities"]
    summary = metrics.executive_summary_metrics(tables)
    rows = []
    if summary["crm_data_quality_score"] < 82:
        rows.append(gap("gap_low_crm_data_quality_score", "crm_governance", "crm_data_quality_score", round(summary["crm_data_quality_score"], 1), ">= 82", "critical", f"Os dados sugerem score geral de qualidade em {summary['crm_data_quality_score']:.1f}/100.", "Criar war room de CRM hygiene com owners por objeto e foco em campos críticos.", "Head de RevOps", "crm_data_quality_score"))
    if metrics.lead_missing_source_rate(leads) > 0.05:
        rows.append(gap("gap_leads_without_source", "lead_governance", "lead_missing_source_rate", round(metrics.lead_missing_source_rate(leads), 3), "<= 0.05", "high", f"A evidência disponível aponta para {metrics.lead_missing_source_rate(leads):.1%} dos leads sem source.", "Bloquear criação ou roteamento de lead sem source.", "Marketing Ops", "lead_missing_source_rate"))
    if len(metrics.duplicate_accounts(accounts)) > 0:
        rows.append(gap("gap_duplicate_accounts", "deduplication", "duplicate_accounts", len(metrics.duplicate_accounts(accounts)), "0", "high", f"Os dados sugerem {len(metrics.duplicate_accounts(accounts))} contas duplicadas por nome e domínio.", "Consolidar contas duplicadas e criar matching por domínio.", "CRM Manager", "duplicate_account_rate"))
    if len(metrics.contacts_without_account(contacts)) > 0:
        rows.append(gap("gap_contacts_without_account", "relationship_integrity", "contacts_without_account", len(metrics.contacts_without_account(contacts)), "0", "medium", f"Há {len(metrics.contacts_without_account(contacts))} contatos sem conta associada.", "Associar contatos por domínio e exigir account_id.", "CRM Admin", "contacts_without_account"))
    if len(metrics.opportunities_without_owner(opportunities)) > 0:
        rows.append(gap("gap_opportunities_without_owner", "ownership", "opportunities_without_owner", len(metrics.opportunities_without_owner(opportunities)), "0", "critical", f"Existem {len(metrics.opportunities_without_owner(opportunities))} oportunidades sem AE owner.", "Atribuir owner antes de qualquer forecast inclusion.", "Head de Sales", "opportunities_without_owner"))
    if len(metrics.opportunities_without_close_date(opportunities)) > 0:
        rows.append(gap("gap_opportunities_without_close_date", "forecast_governance", "opportunities_without_close_date", len(metrics.opportunities_without_close_date(opportunities)), "0", "critical", f"Há {len(metrics.opportunities_without_close_date(opportunities))} oportunidades sem close_date.", "Bloquear forecast de oportunidades abertas sem close_date validada.", "RevOps", "opportunities_without_close_date"))
    if len(metrics.opportunities_without_next_step(opportunities)) > 0:
        rows.append(gap("gap_opportunities_without_next_step", "pipeline_hygiene", "opportunities_without_next_step", len(metrics.opportunities_without_next_step(opportunities)), "0", "high", f"Há {len(metrics.opportunities_without_next_step(opportunities))} oportunidades abertas sem next_step.", "Exigir next_step datado em pipeline review.", "Sales Managers", "opportunities_without_next_step"))
    if len(metrics.stale_opportunities(opportunities)) > 0:
        rows.append(gap("gap_stale_opportunities", "pipeline_hygiene", "stale_opportunities", len(metrics.stale_opportunities(opportunities)), "0", "high", f"Há {len(metrics.stale_opportunities(opportunities))} oportunidades paradas há mais de 20 dias.", "Criar limpeza semanal de oportunidades paradas.", "Sales Managers", "stale_opportunities"))
    if len(metrics.forecast_category_inconsistencies(opportunities)) > 0:
        rows.append(gap("gap_forecast_category_inconsistencies", "forecast_governance", "forecast_category_inconsistencies", len(metrics.forecast_category_inconsistencies(opportunities)), "0", "critical", f"Há {len(metrics.forecast_category_inconsistencies(opportunities))} forecast categories inconsistentes com stage.", "Criar matriz stage x forecast category.", "RevOps", "forecast_category_inconsistencies"))
    if summary["revenue_at_risk_from_data_quality"] > 1_000_000:
        rows.append(gap("gap_high_revenue_at_risk", "revenue_risk", "revenue_at_risk_from_data_quality", round(summary["revenue_at_risk_from_data_quality"], 2), "<= 1000000", "critical", f"Pipeline associado a problemas de qualidade soma R$ {summary['revenue_at_risk_from_data_quality']:,.0f}.", "Priorizar correção por valor em risco.", "CRO", "revenue_at_risk_from_data_quality"))
    return pd.DataFrame(rows)


def main() -> None:
    gaps = find_gaps()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    gaps.to_csv(OUTPUT, index=False)
    print(f"Consultant gap log generated at {OUTPUT} with {len(gaps)} gaps")


if __name__ == "__main__":
    main()
