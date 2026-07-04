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

st.set_page_config(page_title="CRM Data Quality and Revenue Governance", layout="wide")


@st.cache_data
def load_tables() -> dict[str, pd.DataFrame]:
    return metrics.load_all()


def read_table(name: str) -> pd.DataFrame:
    path = PROCESSED / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def markdown_doc(file_name: str) -> None:
    path = DOCS / file_name
    st.markdown(path.read_text(encoding="utf-8") if path.exists() else "Arquivo ainda nao gerado. Rode a preparacao do projeto.")


def safe_table(df: pd.DataFrame, columns: list[str] | None = None) -> None:
    if df.empty:
        st.warning("Dados insuficientes para exibir esta tabela.")
        return
    st.dataframe(select_existing(df, columns) if columns else df, use_container_width=True, hide_index=True)


def safe_bar(df: pd.DataFrame, x: str, y: str, title: str) -> None:
    if df.empty or not has_columns(df, [x, y]):
        st.warning("Dados insuficientes para exibir este grafico.")
        return
    st.plotly_chart(px.bar(df, x=x, y=y, title=title), use_container_width=True)


def executive_reading(what: str, why: str, decision: str) -> None:
    st.info(f"**O que estamos vendo?** {what}\n\n**Por que importa?** {why}\n\n**Qual decisao isso suporta?** {decision}")


def overview(tables: dict[str, pd.DataFrame]) -> None:
    st.title("CRM Data Quality and Revenue Governance")
    st.caption("Case RevOps SaaS B2B: CRM hygiene, forecast reliability, pipeline hygiene, ownership e revenue risk.")
    summary = metrics.executive_summary_metrics(tables)
    cols = st.columns(4)
    cols[0].metric("CRM Data Quality", f"{summary['crm_data_quality_score']:.1f}/100")
    cols[1].metric("Forecast Reliability", f"{summary['forecast_reliability_score']:.1f}/100")
    cols[2].metric("Pipeline Hygiene", f"{summary['pipeline_hygiene_score']:.1f}/100")
    cols[3].metric("Receita em risco", format_currency_br(summary["revenue_at_risk_from_data_quality"]))
    executive_reading(
        "Riscos combinados de completude, ownership, forecast governance e pipeline hygiene.",
        "Esses sinais afetam forecast, pipeline review e reporting executivo.",
        "Priorizar saneamento antes da proxima forecast call e separar pipeline confiavel de pipeline em correcao.",
    )
    safe_bar(metrics.data_quality_issues_by_object(tables), "object", "issue_count", "Issues por objeto")


def scores(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Scores de Governanca")
    frame = pd.DataFrame(
        [{"dimensao": obj, "score": metrics.object_quality_score(obj, tables)} for obj in ["leads", "accounts", "contacts", "opportunities"]]
        + [
            {"dimensao": "forecast", "score": metrics.forecast_reliability_score(tables["opportunities"], tables["activities"])},
            {"dimensao": "pipeline", "score": metrics.pipeline_hygiene_score(tables["opportunities"], tables["activities"])},
        ]
    )
    safe_bar(frame, "dimensao", "score", "Score por dimensao")
    safe_table(metrics.missing_required_fields(tables).query("missing_count > 0"))


def lead_account_quality(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Lead, Account e Contact Quality")
    cols = st.columns(4)
    cols[0].metric("Leads sem source", format_percent_br(metrics.lead_missing_source_rate(tables["leads"])))
    cols[1].metric("Leads duplicados", format_integer_br(len(metrics.duplicate_leads(tables["leads"]))))
    cols[2].metric("Contas sem owner", format_integer_br(len(metrics.accounts_without_owner(tables["accounts"]))))
    cols[3].metric("Contatos sem conta", format_integer_br(len(metrics.contacts_without_account(tables["contacts"]))))
    executive_reading(
        "Source, dedupe, ownership e relacionamento conta-contato sustentam roteamento e atribuição.",
        "Dados frágeis no topo do funil distorcem produtividade e leitura de demanda.",
        "Corrigir regras de criação, dedupe e owner antes de análises executivas.",
    )
    safe_table(metrics.duplicate_leads(tables["leads"]))
    safe_table(metrics.accounts_without_owner(tables["accounts"]))
    safe_table(metrics.contacts_without_account(tables["contacts"]))


def opportunity_hygiene(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Pipeline Hygiene")
    opportunities = tables["opportunities"]
    cols = st.columns(4)
    cols[0].metric("Sem owner", format_integer_br(len(metrics.opportunities_without_owner(opportunities))))
    cols[1].metric("Sem next step", format_integer_br(len(metrics.opportunities_without_next_step(opportunities))))
    cols[2].metric("Paradas", format_integer_br(len(metrics.stale_opportunities(opportunities))))
    cols[3].metric("Close date vencido", format_integer_br(len(metrics.open_opportunities_with_past_close_date(opportunities))))
    executive_reading(
        "Oportunidades sem sinais minimos de execucao podem inflar pipeline.",
        "Deals sem owner, next step ou data valida reduzem confiabilidade do forecast.",
        "Limpar pipeline e exigir accountability por deal.",
    )
    safe_table(metrics.stale_opportunities(opportunities), ["opportunity_id", "opportunity_name", "owner_id", "stage", "amount", "close_date", "next_step"])


def forecast_governance(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Forecast Governance")
    opportunities = tables["opportunities"]
    cols = st.columns(4)
    cols[0].metric("Category inconsistente", format_integer_br(len(metrics.forecast_category_inconsistencies(opportunities))))
    cols[1].metric("Stage/prob. invalido", format_integer_br(len(metrics.invalid_stage_probability_combinations(opportunities))))
    cols[2].metric("Close date manual", format_percent_br(metrics.manual_close_date_change_rate(tables["crm_audit_log"])))
    cols[3].metric("Forecast score", f"{metrics.forecast_reliability_score(opportunities, tables['activities']):.1f}/100")
    safe_table(metrics.forecast_category_inconsistencies(opportunities), ["opportunity_id", "stage", "forecast_category", "probability", "amount", "owner_id"])


def remediation(tables: dict[str, pd.DataFrame]) -> None:
    st.title("Remediation Governance")
    tasks = tables["remediation_tasks"]
    st.metric("Taxa de conclusao", format_percent_br(metrics.remediation_completion_rate(tasks)))
    safe_table(metrics.overdue_remediation_tasks(tasks))


PAGES = {
    "Visao Executiva": overview,
    "Scores de Governanca": scores,
    "Lead, Account e Contact Quality": lead_account_quality,
    "Pipeline Hygiene": opportunity_hygiene,
    "Forecast Governance": forecast_governance,
    "Remediation Governance": remediation,
    "Consultor de Gaps": lambda tables: (st.title("Consultor de Gaps"), safe_table(read_table("consultant_gap_log"))),
    "IA Consultora": lambda tables: (st.title("IA Consultora"), markdown_doc("ai_consultant_analysis.md")),
    "Analise Executiva": lambda tables: (st.title("Analise Executiva"), markdown_doc("executive_analysis.md")),
    "Executive Memo": lambda tables: (st.title("Executive Memo"), markdown_doc("executive_memo.md")),
}


def main() -> None:
    tables = load_tables()
    page = st.sidebar.radio("Menu", list(PAGES))
    PAGES[page](tables)


if __name__ == "__main__":
    main()
