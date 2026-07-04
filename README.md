# CRM Data Quality and Revenue Governance

## Executive Summary
Este projeto analisa uma operação SaaS B2B sintética para demonstrar como RevOps e Sales Ops podem transformar CRM Data Quality em Revenue Governance. Os dados sugerem score geral de qualidade em 74.0/100, Forecast Reliability Score em 92.8/100, Pipeline Hygiene Score em 82.4/100 e R$ 3.270.414,00 em pipeline associado a problemas de qualidade.

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
- CRM Data Quality Score: 74.0/100.
- Forecast Reliability Score: 92.8/100.
- Pipeline Hygiene Score: 82.4/100.
- Leads sem source: 13.
- Duplicidade de leads: 5.
- Duplicidade de contas: 4.
- Contatos sem conta: 4.
- Contas sem owner: 4.
- Oportunidades sem owner: 4.
- Oportunidades sem close_date: 5.
- Oportunidades sem next_step: 5.
- Oportunidades paradas: 38.
- Closed Won sem amount: 2.
- Closed Lost sem loss_reason: 3.
- Forecast category inconsistente: 6.
- Stage/probability incompatível: 7.
- Revenue at risk: R$ 3.270.414,00.

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
