from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import metrics
from src.utils import format_currency_br, format_integer_br, format_percent_br, has_columns, select_existing

PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"

st.set_page_config(page_title="CRM Data Quality Revenue Governance", layout="wide")


@st.cache_data
def load_tables() -> dict[str, pd.DataFrame]:
    return metrics.load_all()


def read_table(name: str) -> pd.DataFrame:
    path = PROCESSED / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def markdown_doc(file_name: str) -> None:
    path = DOCS / file_name
    st.markdown(path.read_text(encoding="utf-8") if path.exists() else "Arquivo ainda não gerado. Rode a preparação do projeto.")


def executive_reading(what: str, why: str, decision: str) -> None:
    st.info(f"**O que estamos vendo?** {what}\n\n**Por que importa?** {why}\n\n**Qual decisão isso suporta?** {decision}")


def safe_table(df: pd.DataFrame, columns: list[str] | None = None) -> None:
    if df.empty:
        st.warning("Dados insuficientes para exibir esta tabela.")
        return
    st.dataframe(select_existing(df, columns) if columns else df, use_container_width=True, hide_index=True)


def safe_bar(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if df.empty or not has_columns(df, [x, y]):
        st.warning("Dados insuficientes para exibir este gráfico.")
        return
    st.plotly_chart(px.bar(df, x=x, y=y, title=title), use_container_width=True)


def overview(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Visão Executiva")
    summary = metrics.executive_summary_metrics(tables)
    cols = st.columns(4)
    cols[0].metric("Score geral", f"{summary['crm_data_quality_score']:.1f}/100")
    cols[1].metric("Forecast reliability", f"{summary['forecast_reliability_score']:.1f}/100")
    cols[2].metric("Pipeline hygiene", f"{summary['pipeline_hygiene_score']:.1f}/100")
    cols[3].metric("Receita em risco", format_currency_br(summary["revenue_at_risk_from_data_quality"]))
    executive_reading(
        "Riscos combinados de completude, ownership, forecast governance e pipeline hygiene.",
        "Esses sinais afetam diretamente forecast, pipeline review e reporting executivo.",
        "Priorizar saneamento antes da próxima forecast call e separar pipeline confiável de pipeline em correção.",
    )
    safe_bar(metrics.data_quality_issues_by_object(tables), "object", "issue_count", "Issues por objeto")


def scores(tables: dict[str, pd.DataFrame]) -> None:
    st.title("CRM Data Quality Score")
    frame = pd.DataFrame(
        [{"dimensão": obj, "score": metrics.object_quality_score(obj, tables)} for obj in ["leads", "accounts", "contacts", "opportunities"]]
        + [
            {"dimensão": "forecast", "score": metrics.forecast_reliability_score(tables["opportunities"], tables["activities"])},
            {"dimensão": "pipeline", "score": metrics.pipeline_hygiene_score(tables["opportunities"], tables["activities"])},
        ]
    )
    executive_reading("Scores por objeto e por dimensão de governança.", "Localiza onde o CRM fragiliza decisões.", "Definir foco da primeira onda de remediação.")
    safe_bar(frame, "dimensão", "score", "Score por dimensão")
    safe_table(metrics.missing_required_fields(tables).query("missing_count > 0"))


def leads_quality(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Leads Quality")
    leads = tables["leads"]
    st.metric("Leads sem source", format_percent_br(metrics.lead_missing_source_rate(leads)))
    executive_reading("Leads sem source e duplicidades por email.", "Afeta roteamento, atribuição e leitura de demanda.", "Revisar criação de leads e dedupe antes do handoff.")
    safe_table(metrics.duplicate_leads(leads), ["lead_id", "lead_name", "email", "source", "owner_id", "created_date"])


def accounts_contacts(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Account and Contact Quality")
    cols = st.columns(3)
    cols[0].metric("Contas sem owner", format_integer_br(len(metrics.accounts_without_owner(tables["accounts"]))))
    cols[1].metric("Contas duplicadas", format_integer_br(len(metrics.duplicate_accounts(tables["accounts"]))))
    cols[2].metric("Contatos sem conta", format_integer_br(len(metrics.contacts_without_account(tables["contacts"]))))
    executive_reading("Risco de ownership, duplicidade e integridade de relacionamento.", "Fragmenta visão de conta, histórico e buying committee.", "Corrigir owner e consolidar contas antes de análises executivas.")
    safe_table(metrics.accounts_without_owner(tables["accounts"]), ["account_id", "account_name", "domain", "segment", "owner_id"])
    safe_table(metrics.contacts_without_account(tables["contacts"]), ["contact_id", "contact_name", "account_id", "email", "title"])


def opportunity_hygiene(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Opportunity Hygiene")
    opportunities = tables["opportunities"]
    cols = st.columns(4)
    cols[0].metric("Sem owner", len(metrics.opportunities_without_owner(opportunities)))
    cols[1].metric("Sem next step", len(metrics.opportunities_without_next_step(opportunities)))
    cols[2].metric("Paradas", len(metrics.stale_opportunities(opportunities)))
    cols[3].metric("Close date vencido", len(metrics.open_opportunities_with_past_close_date(opportunities)))
    executive_reading("Oportunidades sem sinais mínimos de execução.", "Deals sem owner, next step ou data válida podem inflar pipeline.", "Limpar pipeline e exigir accountability por deal.")
    safe_table(metrics.stale_opportunities(opportunities), ["opportunity_id", "opportunity_name", "owner_id", "stage", "amount", "close_date", "next_step"])


def forecast_governance(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Forecast Governance")
    opportunities = tables["opportunities"]
    cols = st.columns(4)
    cols[0].metric("Category inconsistente", len(metrics.forecast_category_inconsistencies(opportunities)))
    cols[1].metric("Stage/prob. inválido", len(metrics.invalid_stage_probability_combinations(opportunities)))
    cols[2].metric("Close date manual", format_percent_br(metrics.manual_close_date_change_rate(tables["crm_audit_log"])))
    cols[3].metric("Forecast score", f"{metrics.forecast_reliability_score(opportunities, tables['activities']):.1f}/100")
    executive_reading("Critérios de forecast category, probability e close_date.", "Forecast confiável depende de regras consistentes e auditáveis.", "Revisar Commit, Best Case e Pipeline antes da decisão executiva.")
    safe_table(metrics.forecast_category_inconsistencies(opportunities), ["opportunity_id", "stage", "forecast_category", "probability", "amount", "owner_id"])


def remediation(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Remediation Tasks")
    tasks = tables["remediation_tasks"]
    st.metric("Taxa de conclusão", format_percent_br(metrics.remediation_completion_rate(tasks)))
    executive_reading("Tarefas por status, prazo e severidade.", "Sem SLA, diagnóstico não vira correção operacional.", "Criar cadência de remediação e escalonamento por severidade.")
    safe_table(metrics.overdue_remediation_tasks(tasks))


def revenue_impact(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Impacto na Receita")
    value = metrics.revenue_at_risk_from_data_quality(tables["opportunities"])
    st.metric("Pipeline associado a dados ruins", format_currency_br(value))
    executive_reading("Valor de oportunidades com problemas críticos de qualidade.", "Mostra impacto financeiro potencial de decidir com dados frágeis.", "Priorizar correções pelo valor em risco.")
    safe_bar(metrics.data_quality_issues_by_object(tables), "object", "issue_count", "Issues por objeto")


def gap_consultant() -> None:
    st.title("Consultor de Gaps")
    gaps = read_table("consultant_gap_log")
    if gaps.empty:
        st.warning("Dados insuficientes para exibir esta tabela.")
        return
    cols = st.columns(4)
    for col, severity in zip(cols, ["critical", "high", "medium", "low"]):
        col.metric(severity.title(), int(gaps["severity"].eq(severity).sum()))
    executive_reading("Gaps priorizados por severidade e impacto decisório.", "Ajuda liderança a agir sobre riscos que afetam forecast e pipeline.", "Definir owner, urgência e métrica de acompanhamento.")
    safe_table(gaps[gaps["severity"].isin(["critical", "high"])], ["gap_id", "area", "severity", "evidence", "recommended_action", "owner", "follow_up_metric", "expected_impact"])
    safe_table(gaps)


PAGES = {
    "Visão Executiva": overview,
    "CRM Data Quality Score": scores,
    "Leads Quality": leads_quality,
    "Account and Contact Quality": accounts_contacts,
    "Opportunity Hygiene": opportunity_hygiene,
    "Forecast Governance": forecast_governance,
    "Remediation Tasks": remediation,
    "Impacto na Receita": revenue_impact,
    "Consultor de Gaps": lambda tables: gap_consultant(),
    "IA Consultora": lambda tables: (st.title("IA Consultora"), markdown_doc("ai_consultant_analysis.md")),
    "Análise Executiva": lambda tables: (st.title("Análise Executiva"), markdown_doc("executive_analysis.md")),
    "Qualidade dos Dados": lambda tables: (st.title("Qualidade dos Dados"), safe_table(read_table("data_quality_report"))),
    "Production Flow": lambda tables: (st.title("Production Flow"), markdown_doc("production_flow.md")),
}


def main() -> None:
    tables = load_tables()
    page = st.sidebar.radio("Menu", list(PAGES))
    PAGES[page](tables)


if __name__ == "__main__":
    main()
