from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from src import metrics
    from src.utils import format_currency_br, format_percent_br
except ModuleNotFoundError:  # pragma: no cover
    import metrics
    from utils import format_currency_br, format_percent_br

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
OUTPUT = DOCS / "ai_consultant_analysis.md"


def severity_block(gaps: pd.DataFrame, severity: str) -> str:
    subset = gaps[gaps["severity"].eq(severity)] if "severity" in gaps else pd.DataFrame()
    if subset.empty:
        return "- Nenhum gap nesta severidade.\n"
    return "\n".join(f"- **{row.area} | {row.metric}**: {row.evidence} Ação recomendada: {row.recommended_action}" for row in subset.itertuples()) + "\n"


def build_analysis(gaps: pd.DataFrame, summary: dict[str, float]) -> str:
    critical = int(gaps.get("severity", pd.Series(dtype=str)).eq("critical").sum())
    high = int(gaps.get("severity", pd.Series(dtype=str)).eq("high").sum())
    return f"""# AI Consultant Analysis

## Veredito executivo
Os dados sugerem que o CRM ainda não deve ser tratado como fonte plenamente confiável para decisões executivas sem uma onda de saneamento prévia. O score geral está em {summary['crm_data_quality_score']:.1f}/100, com {critical} gaps críticos, {high} gaps altos e {format_currency_br(summary['revenue_at_risk_from_data_quality'])} em pipeline associado a problemas de qualidade de dados. A análise é rule-based e gera hipóteses para validação, não confirmação de causa raiz.

## Leitura da operação
A evidência disponível aponta para risco combinado em completude de dados, ownership, higiene de pipeline, forecast governance, stage/probability, close date hygiene e processo de remediação. O ponto central para RevOps é que CRM Data Quality não é um checklist técnico: é fundamento de Revenue Governance, Forecast Reliability e Pipeline Hygiene.

## Principais gaps
### Críticos
{severity_block(gaps, "critical")}
### Altos
{severity_block(gaps, "high")}
### Médios
{severity_block(gaps, "medium")}

## Hipóteses prováveis
- Os dados sugerem que regras de campos obrigatórios podem não estar conectadas ao ciclo comercial real por stage.
- Há indícios de que forecast category e probability podem estar sem controles suficientes.
- A evidência disponível aponta para close date hygiene fraca e necessidade de reason code para pushes.
- Problemas de ownership precisam ser validados com política de território, fila e SLA de aceite.
- Tarefas de remediação atrasadas sugerem oportunidade de fortalecer accountability operacional.

## Evidências observadas
- CRM Data Quality Score: {summary['crm_data_quality_score']:.1f}/100.
- Forecast Reliability Score: {summary['forecast_reliability_score']:.1f}/100.
- Pipeline Hygiene Score: {summary['pipeline_hygiene_score']:.1f}/100.
- Leads sem source: {format_percent_br(summary['lead_missing_source_rate'])}.
- Taxa de duplicidade de leads: {format_percent_br(summary['duplicate_lead_rate'])}.
- Taxa de duplicidade de contas: {format_percent_br(summary['duplicate_account_rate'])}.
- Mudanças manuais de close_date no audit log: {format_percent_br(summary['manual_close_date_change_rate'])}.
- Taxa de conclusão de remediação: {format_percent_br(summary['remediation_completion_rate'])}.

## Evidências ausentes
- Regras reais do CRM e obrigatoriedade por stage.
- Logs completos de alteração e motivo de alteração de close_date.
- Política de ownership e exceções aprovadas.
- Critérios formais de Forecast Category e avanço de stage.
- Qualidade das notas comerciais e validação dos managers.
- Conciliação com Finance/FP&A para Closed Won e amount.

## Perguntas de validação
- Head de RevOps: quais campos devem bloquear forecast inclusion?
- Sales Ops: quais SLAs existem para owner, close_date, next_step e loss_reason?
- CRM Admin: quais validações estão ativas por perfil e stage?
- Sales Managers: quais deals críticos permanecem no forecast sem evidência operacional?
- AEs: close_date representa compromisso do comprador ou expectativa interna?
- Finance/FP&A: Closed Won sem amount já foi conciliado com contrato ou billing?

## Recomendações priorizadas
### Fazer agora
- Responsável: Head de RevOps. Ação: war room de CRM hygiene para campos críticos. Métrica impactada: CRM Data Quality Score. Acompanhamento: missing_required_fields. Prazo: 5 dias úteis. Impacto esperado: maior confiança executiva.
- Responsável: CRO e Head de Sales. Ação: separar forecast confiável de pipeline em saneamento. Métrica impactada: Forecast Reliability Score. Acompanhamento: forecast_category_inconsistencies. Prazo: antes da próxima forecast call. Impacto esperado: menor risco de decisão com forecast frágil.
- Responsável: Sales Managers. Ação: revisar oportunidades sem owner, close_date, next_step ou atividade recente. Métrica impactada: Pipeline Hygiene Score. Acompanhamento: stale_opportunities. Prazo: 48 horas. Impacto esperado: pipeline mais acionável.

### Fazer depois
- Responsável: CRM Manager. Ação: implementar matriz stage x required fields x forecast category. Métrica impactada: Forecast Reliability Score. Acompanhamento: invalid_stage_probability_combinations. Prazo: 30 dias. Impacto esperado: menor subjetividade no forecast.
- Responsável: Marketing Ops e Sales Ops. Ação: dedupe e regra de source obrigatória. Métrica impactada: lead_missing_source_rate. Acompanhamento: duplicate_rate. Prazo: 30 dias. Impacto esperado: melhor roteamento e atribuição.

### Monitorar
- Responsável: RevOps Analytics. Ação: painel semanal de gaps por owner, objeto e severidade. Métrica impactada: remediation_completion_rate. Acompanhamento: overdue_remediation_tasks. Prazo: semanal. Impacto esperado: governança contínua.

## Riscos de decisão
Decidir forecast, capacidade comercial, meta, hiring ou expectativa de caixa com dados incompletos pode inflar pipeline, esconder slippage, distorcer win/loss analysis e reduzir accountability por owner. O risco principal não é apenas campo vazio; é tratar registros frágeis como evidência comercial confiável.

## Conclusão executiva
A recomendação é tratar CRM Data Quality como disciplina de Revenue Governance. O projeto mostra onde os dados sugerem risco, quais evidências faltam e quais decisões devem ser protegidas antes da próxima forecast call.
"""


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    gaps_path = PROCESSED / "consultant_gap_log.csv"
    gaps = pd.read_csv(gaps_path) if gaps_path.exists() else pd.DataFrame()
    OUTPUT.write_text(build_analysis(gaps, metrics.executive_summary_metrics(metrics.load_all())), encoding="utf-8")
    print(f"AI consultant analysis generated at {OUTPUT}")


if __name__ == "__main__":
    main()
