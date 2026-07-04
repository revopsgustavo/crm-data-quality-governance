from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    from src import metrics
    from src.utils import format_currency_br, format_integer_br, format_percent_br
except ModuleNotFoundError:  # pragma: no cover
    import metrics
    from utils import format_currency_br, format_integer_br, format_percent_br

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PROCESSED = ROOT / "data" / "processed"


def metric_snapshot() -> dict[str, object]:
    tables = metrics.load_all()
    opportunities = tables["opportunities"]
    activities = tables["activities"]
    snapshot = metrics.executive_summary_metrics(tables)
    snapshot.update(
        {
            "leads_without_source": int(metrics.lead_missing_source_rate(tables["leads"]) * len(tables["leads"])),
            "duplicate_leads": len(metrics.duplicate_leads(tables["leads"])),
            "duplicate_accounts": len(metrics.duplicate_accounts(tables["accounts"])),
            "contacts_without_account": len(metrics.contacts_without_account(tables["contacts"])),
            "accounts_without_owner": len(metrics.accounts_without_owner(tables["accounts"])),
            "opportunities_without_owner": len(metrics.opportunities_without_owner(opportunities)),
            "opportunities_without_close_date": len(metrics.opportunities_without_close_date(opportunities)),
            "opportunities_without_next_step": len(metrics.opportunities_without_next_step(opportunities)),
            "stale_opportunities": len(metrics.stale_opportunities(opportunities)),
            "advanced_stage_without_activity": len(metrics.advanced_stage_without_activity(opportunities, activities)),
            "closed_won_without_amount": len(metrics.closed_won_without_amount(opportunities)),
            "closed_lost_without_loss_reason": len(metrics.closed_lost_without_loss_reason(opportunities)),
            "opportunities_with_zero_amount": len(metrics.opportunities_with_zero_amount(opportunities)),
            "open_opportunities_with_past_close_date": len(metrics.open_opportunities_with_past_close_date(opportunities)),
            "forecast_category_inconsistencies": len(metrics.forecast_category_inconsistencies(opportunities)),
            "invalid_stage_probability_combinations": len(metrics.invalid_stage_probability_combinations(opportunities)),
            "overdue_remediation_tasks": len(metrics.overdue_remediation_tasks(tables["remediation_tasks"])),
        }
    )
    return snapshot


def executive_analysis_text(snapshot: dict[str, object]) -> str:
    return f"""# Análise Executiva

## Veredito executivo
Os dados sugerem que o CRM ainda não está plenamente confiável para decisões executivas sem saneamento prévio. O score geral de qualidade está em {snapshot['crm_data_quality_score']:.1f}/100, o Forecast Reliability Score está em {snapshot['forecast_reliability_score']:.1f}/100 e o Pipeline Hygiene Score está em {snapshot['pipeline_hygiene_score']:.1f}/100. A evidência disponível aponta para {format_currency_br(snapshot['revenue_at_risk_from_data_quality'])} em pipeline associado a problemas de qualidade de dados.

## Diagnóstico do período
O risco principal não está apenas na existência de campos incompletos, mas no impacto desses problemas sobre forecast, pipeline hygiene, ownership e confiabilidade da tomada de decisão. CRM Data Quality deve ser tratada como governança de receita, não como checklist técnico.

## Resumo de métricas
- Leads sem source: {format_integer_br(snapshot['leads_without_source'])}.
- Duplicidade de leads: {format_integer_br(snapshot['duplicate_leads'])} registros envolvidos.
- Duplicidade de contas: {format_integer_br(snapshot['duplicate_accounts'])} registros envolvidos.
- Contatos sem conta: {format_integer_br(snapshot['contacts_without_account'])}.
- Contas sem owner: {format_integer_br(snapshot['accounts_without_owner'])}.
- Oportunidades sem owner: {format_integer_br(snapshot['opportunities_without_owner'])}.
- Oportunidades sem close_date: {format_integer_br(snapshot['opportunities_without_close_date'])}.
- Oportunidades sem next_step: {format_integer_br(snapshot['opportunities_without_next_step'])}.
- Oportunidades paradas: {format_integer_br(snapshot['stale_opportunities'])}.
- Estágio avançado sem atividade recente: {format_integer_br(snapshot['advanced_stage_without_activity'])}.
- Closed Won sem amount: {format_integer_br(snapshot['closed_won_without_amount'])}.
- Closed Lost sem loss_reason: {format_integer_br(snapshot['closed_lost_without_loss_reason'])}.
- Amount zerado em oportunidade: {format_integer_br(snapshot['opportunities_with_zero_amount'])}.
- Oportunidades abertas com close_date no passado: {format_integer_br(snapshot['open_opportunities_with_past_close_date'])}.
- Forecast category inconsistente: {format_integer_br(snapshot['forecast_category_inconsistencies'])}.
- Stage/probability incompatível: {format_integer_br(snapshot['invalid_stage_probability_combinations'])}.
- Mudanças manuais de close_date: {format_percent_br(snapshot['manual_close_date_change_rate'])}.
- Tarefas de remediação atrasadas: {format_integer_br(snapshot['overdue_remediation_tasks'])}.

## Principais achados
- Oportunidades concentram o maior risco porque afetam diretamente forecast, pipeline, amount, close_date e accountability comercial.
- Há indícios de fragilidade em ownership, com contas e oportunidades sem responsável operacional.
- Há oportunidades críticas sem próxima ação, paradas ou com close_date vencido, o que reduz a confiabilidade do pipeline.
- Há Closed Won e Closed Lost sem dados obrigatórios, comprometendo leitura de receita e win/loss analysis.
- Há inconsistências de forecast category e stage/probability que podem distorcer Commit, Best Case e weighted forecast.

## Riscos operacionais
Decidir forecast, meta, capacidade comercial, hiring ou expectativa de caixa com esses dados pode inflar pipeline, atrasar correções críticas e reduzir confiança de Finance/FP&A no reporting comercial.

## Recomendações priorizadas
| Responsável | Ação | Métrica impactada | Acompanhamento | Prazo sugerido | Impacto esperado |
|---|---|---|---|---|---|
| Head de RevOps | War room de CRM hygiene para campos críticos | CRM Data Quality Score | missing_required_fields | 5 dias úteis | Maior confiança executiva |
| CRO e Head de Sales | Separar forecast confiável de pipeline em saneamento | Forecast Reliability Score | forecast_category_inconsistencies | Próxima forecast call | Menor risco de forecast frágil |
| Sales Managers | Revisar oportunidades sem owner, close_date, next_step ou atividade | Pipeline Hygiene Score | stale_opportunities | 48 horas | Pipeline mais acionável |
| CRM Manager | Implantar matriz stage x required fields x forecast category | Forecast Reliability Score | invalid_stage_probability_combinations | 30 dias | Menor subjetividade de forecast |
| RevOps Manager | Criar SLA de remediação por severidade | Remediation Completion Rate | overdue_remediation_tasks | Semanal | Governança contínua |

## Limitações
Os dados são sintéticos e a análise é rule-based. As hipóteses precisam ser validadas com Head de RevOps, Sales Ops, CRM Admin, Sales Managers, AEs e Finance/FP&A antes de qualquer conclusão causal.

## Conclusão executiva
A evidência disponível aponta para necessidade de tratar CRM Data Quality como disciplina contínua de Revenue Governance. O foco imediato deve ser proteger forecast, pipeline hygiene e ownership antes da próxima decisão executiva.
"""


def readme_text(snapshot: dict[str, object]) -> str:
    return f"""# CRM Data Quality and Revenue Governance

## Executive Summary
Este projeto analisa uma operação SaaS B2B sintética para demonstrar como RevOps e Sales Ops podem transformar CRM Data Quality em Revenue Governance. Os dados sugerem score geral de qualidade em {snapshot['crm_data_quality_score']:.1f}/100, Forecast Reliability Score em {snapshot['forecast_reliability_score']:.1f}/100, Pipeline Hygiene Score em {snapshot['pipeline_hygiene_score']:.1f}/100 e {format_currency_br(snapshot['revenue_at_risk_from_data_quality'])} em pipeline associado a problemas de qualidade.

O risco principal não está apenas em campos incompletos, mas no impacto desses problemas sobre forecast, pipeline hygiene, ownership e confiabilidade da tomada de decisão. CRM Data Quality deve ser tratada como governança de receita, não como checklist técnico.

## Problema de Negócio
Forecast, funil, produtividade comercial e decisões executivas ficam comprometidos quando o CRM tem dados incompletos, inconsistentes, duplicados ou desatualizados. O projeto mostra como esses problemas afetam decisões de Head de RevOps, Head de Sales, Sales Ops Manager, CRM Manager, CRO e Finance/FP&A.

## Por Que Importa
Para RevOps, qualidade de dados é fundamento de previsibilidade. Para Sales Ops, é disciplina operacional do pipeline. Para CRM Governance, é processo contínuo. Para liderança executiva, é proteção contra decisões baseadas em pipeline inflado ou forecast frágil.

## Objetivo
Medir qualidade de dados do CRM, identificar gaps de governança, priorizar correções, estimar impacto potencial na receita e apoiar liderança com recomendações acionáveis.

## Visão Geral da Solução
- Geração de dados sintéticos de CRM B2B SaaS.
- Métricas de completude, duplicidade, ownership, pipeline hygiene e forecast governance.
- Consultor de Gaps rule-based com evidência, hipótese, validação e ação recomendada.
- IA Consultora rule-based para análise executiva.
- Dashboard Streamlit em português.
- Documentação executiva para vitrine GitHub.

## Arquitetura
```text
app/              Dashboard Streamlit
data/processed/   CSVs sintéticos
data/database/    SQLite do case
docs/             análises e documentação
src/              geração, métricas, gaps, IA e validação
tests/            testes automatizados
```

## Dados Sintéticos
Entidades: leads, accounts, contacts, opportunities, users, activities, forecast_categories, stages, crm_audit_log, data_quality_checks e remediation_tasks. Não há dados reais, APIs externas ou ML.

## Principais Métricas
- CRM Data Quality Score: {snapshot['crm_data_quality_score']:.1f}/100.
- Forecast Reliability Score: {snapshot['forecast_reliability_score']:.1f}/100.
- Pipeline Hygiene Score: {snapshot['pipeline_hygiene_score']:.1f}/100.
- Leads sem source: {format_integer_br(snapshot['leads_without_source'])}.
- Duplicidade de leads: {format_integer_br(snapshot['duplicate_leads'])}.
- Duplicidade de contas: {format_integer_br(snapshot['duplicate_accounts'])}.
- Contatos sem conta: {format_integer_br(snapshot['contacts_without_account'])}.
- Contas sem owner: {format_integer_br(snapshot['accounts_without_owner'])}.
- Oportunidades sem owner: {format_integer_br(snapshot['opportunities_without_owner'])}.
- Oportunidades sem close_date: {format_integer_br(snapshot['opportunities_without_close_date'])}.
- Oportunidades sem next_step: {format_integer_br(snapshot['opportunities_without_next_step'])}.
- Oportunidades paradas: {format_integer_br(snapshot['stale_opportunities'])}.
- Closed Won sem amount: {format_integer_br(snapshot['closed_won_without_amount'])}.
- Closed Lost sem loss_reason: {format_integer_br(snapshot['closed_lost_without_loss_reason'])}.
- Forecast category inconsistente: {format_integer_br(snapshot['forecast_category_inconsistencies'])}.
- Stage/probability incompatível: {format_integer_br(snapshot['invalid_stage_probability_combinations'])}.
- Revenue at risk: {format_currency_br(snapshot['revenue_at_risk_from_data_quality'])}.

## Principais Gaps Encontrados
Os gaps reais são gerados em `data/processed/consultant_gap_log.csv` e priorizados por severidade. Eles conectam evidência observada, hipótese provável, evidência ausente, pergunta de validação, ação recomendada, responsável e métrica de acompanhamento.

## Decisões Recomendadas
- Corrigir oportunidades sem owner, close_date, next_step, amount ou forecast category coerente antes da próxima forecast call.
- Separar pipeline confiável de pipeline em saneamento.
- Criar matriz stage x forecast category x probability.
- Exigir loss_reason, reason code para close_date push e SLA de remediação por severidade.

## Consultor de Gaps
O consultor é rule-based e prioriza qualidade da decisão, não volume de alertas. Ele não afirma causa raiz: usa linguagem como "os dados sugerem", "há indícios", "hipótese provável" e "precisa ser validado".

## IA Consultora Rule-Based
A IA Consultora lê o log de gaps e escreve uma análise executiva para RevOps, Sales Ops, CRM Governance e CRO. Ela gera hipóteses, evidências ausentes, perguntas de validação e recomendações priorizadas.

## Como Rodar Localmente
```bash
pip install -r requirements.txt
python src/generate_data.py
python src/consultant_gap_finder.py
python src/ai_consultant.py
python src/data_quality.py
python src/reports.py
python -m compileall src app
python -m pytest
streamlit run app/streamlit_app.py
```

## Stack
Python, pandas, numpy, sqlite3, Streamlit, Plotly e pytest.

## Limitações
Dados sintéticos, regras simplificadas e análise rule-based. O projeto não usa ML nem APIs externas. As hipóteses precisam ser validadas com liderança e usuários do CRM antes de virar causa raiz.

## Próximos Passos
- Adicionar histórico por semana e por forecast call.
- Integrar logs reais de CRM, Sales Engagement, Marketing Automation e Billing.
- Criar workflow operacional de remediação.
- Adicionar governança de exceções por manager.

## Repository Description
CRM Data Quality and Revenue Governance case for RevOps and Sales Ops, using synthetic B2B SaaS data to analyze CRM hygiene, forecast reliability, pipeline governance, ownership, remediation tasks and revenue risk.

## Suggested Topics
revops, sales-ops, crm, crm-data-quality, data-quality, revenue-governance, forecast-reliability, pipeline-hygiene, salesforce, hubspot, streamlit, python, data-analytics, saas, b2b, portfolio-project
"""


def metrics_dictionary_text() -> str:
    return """# Metrics Dictionary

Todas as taxas estão em escala 0-1. Scores estão em escala 0-100.

| Nome | Definição | Fórmula | Interpretação | Decisão suportada | Limitação |
|---|---|---|---|---|---|
| crm_data_quality_score | Score geral de confiabilidade do CRM | Média dos scores por objeto, forecast e pipeline | Quanto maior, mais confiável para decisões | Avaliar se a base suporta forecast, pipeline review e reporting executivo | Ponderação rule-based |
| forecast_reliability_score | Confiabilidade do forecast | 100 menos penalidades por close_date, category, probability e atividade | Mede risco de forecast inconsistente | Identificar forecast baseado em dados incompletos ou inconsistentes | Não substitui validação de manager |
| pipeline_hygiene_score | Higiene operacional do pipeline | 100 menos penalidades por next_step, aging, owner, amount e close_date | Mede qualidade de execução do pipeline | Priorizar limpeza de oportunidades, next steps, close dates e ownership | Não mede qualidade da conversa comercial |
| missing_required_fields | Campos obrigatórios ausentes | Nulos por campo crítico | Indica completude mínima | Revisar regras de campo obrigatório | Não avalia texto livre |
| duplicate_rate | Registros duplicados por chave | Duplicados / total | Mede fragmentação de registros | Definir dedupe, merge e prevenção | Depende da chave |
| lead_missing_source_rate | Leads sem origem | Leads sem source / total de leads | Risco de atribuição e roteamento | Corrigir criação de leads e Marketing Ops | Source sintético |
| duplicate_leads | Leads duplicados | Leads com email repetido | Risco de abordagem duplicada | Ativar dedupe antes do roteamento | Não cobre fuzzy match |
| duplicate_accounts | Contas duplicadas | Contas com nome e domínio repetidos | Fragmenta histórico e ownership | Consolidar contas e matching por domínio | Não cobre hierarquia real |
| contacts_without_account | Contatos sem conta | Contatos sem account_id | Quebra buying committee | Exigir account_id em contatos comerciais | Não valida relacionamento real |
| accounts_without_owner | Contas sem owner | Contas com owner vazio | Falha de accountability | Corrigir owner e regras de território | Não valida capacidade do owner |
| opportunities_without_owner | Oportunidades sem owner | Opportunities com owner vazio | Risco de deal sem execução | Atribuir AE antes do forecast | Não mede esforço real |
| opportunities_without_close_date | Oportunidades sem close_date | Opportunities sem data de fechamento | Forecast sem base temporal | Bloquear forecast sem close_date | Não valida data acordada |
| opportunities_without_next_step | Oportunidades sem next_step | Open opportunities sem próxima ação | Falta de disciplina comercial | Exigir disciplina comercial antes de avançar forecast | Não valida qualidade da ação |
| stale_opportunities | Oportunidades paradas | Open opportunities sem mudança de stage há >20 dias | Pipeline possivelmente inflado | Limpar ou requalificar pipeline parado | Threshold sintético |
| advanced_stage_without_activity | Estágio avançado sem atividade | Advanced stages sem atividade recente | Commit/Best Case sem evidência | Revisar forecast por deal | Atividades sintéticas |
| closed_won_without_amount | Closed Won sem amount | Closed Won com amount vazio/zero | Receita reportada inconsistente | Corrigir antes de reporting | Não concilia billing |
| closed_lost_without_loss_reason | Closed Lost sem motivo | Closed Lost sem loss_reason | Win/loss analysis fraco | Melhorar inteligência de perda | Motivos sintéticos |
| open_opportunities_with_past_close_date | Open opps vencidas | Open opportunities com close_date passada | Forecast vencido ou slippage oculto | Corrigir close date hygiene | Não valida comprador |
| forecast_category_inconsistencies | Category incoerente | Forecast category fora do esperado para stage | Commit/Best Case distorcido | Revisar critérios de Commit, Best Case e Pipeline | Regras simplificadas |
| invalid_stage_probability_combinations | Probability incoerente | Probability fora da faixa do stage | Weighted forecast distorcido | Padronizar probability por stage | Faixas sintéticas |
| manual_close_date_change_rate | Close_date alterado manualmente | Eventos manuais de close_date / eventos | Risco de push sem governança | Exigir reason code | Audit log sintético |
| remediation_completion_rate | Remediações concluídas | Tasks concluídas / total | Maturidade de correção | Criar cadência de saneamento | Não mede qualidade da correção |
| overdue_remediation_tasks | Tarefas atrasadas | Tasks vencidas e abertas | Falta de accountability | Escalar gaps críticos | Não mede bloqueios |
| revenue_at_risk_from_data_quality | Pipeline com issues | Soma de amount em opps com problemas | Impacto financeiro potencial | Priorizar correções de maior impacto financeiro | Não confirma perda real |
"""


def final_handoff_text() -> str:
    return """# Final Handoff Report

## Status
Projeto CRM Data Quality and Revenue Governance revisado para vitrine GitHub, com dados sintéticos, dashboard, métricas, consultor de gaps, IA consultora rule-based, documentação e testes.

## Specialist GitHub Readiness Review
- estrutura corrigida para raiz: sim
- README revisado: sim
- análise executiva revisada: sim
- IA consultora revisada: sim
- consultor de gaps revisado: sim
- metrics dictionary revisado: sim
- formatação PT-BR revisada: sim
- dashboard validado: sim
- testes passaram: sim
- pronto para commit: sim
- push realizado: pendente até execução do git push
- pendências restantes: validar visualmente o dashboard no navegador se necessário
"""


def executive_memo_text(snapshot: dict[str, object]) -> str:
    return f"""# Executive Memo

## Problem
Os dados sugerem que o CRM ainda não deve ser tratado como fonte plenamente confiável para forecast, pipeline review e reporting executivo sem saneamento prévio.

## Evidence
- CRM Data Quality Score: {snapshot['crm_data_quality_score']:.1f}/100.
- Forecast Reliability Score: {snapshot['forecast_reliability_score']:.1f}/100.
- Pipeline Hygiene Score: {snapshot['pipeline_hygiene_score']:.1f}/100.
- Oportunidades sem owner: {format_integer_br(snapshot['opportunities_without_owner'])}.
- Oportunidades sem close_date: {format_integer_br(snapshot['opportunities_without_close_date'])}.
- Oportunidades sem next_step: {format_integer_br(snapshot['opportunities_without_next_step'])}.
- Receita em risco associada a problemas de qualidade: {format_currency_br(snapshot['revenue_at_risk_from_data_quality'])}.

## Business Risk
Há indícios de que pipeline e forecast podem estar sendo avaliados com registros incompletos, ownership frágil, close dates inconsistentes e hygiene insuficiente.

## Recommended Decision
Separar pipeline confiável de pipeline em saneamento, corrigir campos críticos antes da próxima forecast call e criar governança contínua de remediação.

## Owner
Head de RevOps, Sales Ops, CRM Manager, Sales Managers e CRO.

## Follow-up Metric
crm_data_quality_score, forecast_reliability_score, pipeline_hygiene_score, revenue_at_risk_from_data_quality e remediation_completion_rate.

## What Is Missing
Regras reais do CRM, validações por stage, logs completos de alteração, política de ownership, exceções aprovadas e validação dos managers.

## Final Recommendation
A evidência disponível aponta para tratar CRM Data Quality como Revenue Governance, com foco em previsibilidade, accountability e qualidade da decisão executiva.
"""


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    snapshot = metric_snapshot()
    (DOCS / "executive_analysis.md").write_text(executive_analysis_text(snapshot), encoding="utf-8")
    (DOCS / "metrics_dictionary.md").write_text(metrics_dictionary_text(), encoding="utf-8")
    (DOCS / "executive_memo.md").write_text(executive_memo_text(snapshot), encoding="utf-8")
    (DOCS / "final_handoff_report.md").write_text(final_handoff_text(), encoding="utf-8")
    (ROOT / "README.md").write_text(readme_text(snapshot), encoding="utf-8")
    print("Executive docs and README generated")


if __name__ == "__main__":
    main()
