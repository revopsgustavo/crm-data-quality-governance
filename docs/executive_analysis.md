# Análise Executiva

## Veredito executivo
Os dados sugerem que o CRM ainda não está plenamente confiável para decisões executivas sem saneamento prévio. O score geral de qualidade está em 65.5/100, o Forecast Reliability Score está em 76.0/100 e o Pipeline Hygiene Score está em 42.8/100. A evidência disponível aponta para R$ 2.414.735,00 em pipeline associado a problemas de qualidade de dados.

## Diagnóstico do período
O risco principal não está apenas na existência de campos incompletos, mas no impacto desses problemas sobre forecast, pipeline hygiene, ownership e confiabilidade da tomada de decisão. CRM Data Quality deve ser tratada como governança de receita, não como checklist técnico.

## Resumo de métricas
- Leads sem source: 13.
- Duplicidade de leads: 3 registros envolvidos.
- Duplicidade de contas: 4 registros envolvidos.
- Contatos sem conta: 4.
- Contas sem owner: 4.
- Oportunidades sem owner: 4.
- Oportunidades sem close_date: 5.
- Oportunidades sem next_step: 5.
- Oportunidades paradas: 37.
- Estágio avançado sem atividade recente: 12.
- Closed Won sem amount: 2.
- Closed Lost sem loss_reason: 9.
- Amount zerado em oportunidade: 6.
- Oportunidades abertas com close_date no passado: 1.
- Forecast category inconsistente: 0.
- Stage/probability incompatível: 14.
- Mudanças manuais de close_date: 49,3%.
- Tarefas de remediação atrasadas: 3.

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
