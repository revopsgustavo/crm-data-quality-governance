# AI Consultant Analysis

## Veredito executivo
Os dados sugerem que o CRM ainda não deve ser tratado como fonte plenamente confiável para decisões executivas sem uma onda de saneamento prévia. O score geral está em 74.0/100, com 7 gaps críticos, 11 gaps altos e R$ 3.270.414,00 em pipeline associado a problemas de qualidade de dados. A análise é rule-based e gera hipóteses para validação, não confirmação de causa raiz.

## Leitura da operação
A evidência disponível aponta para risco combinado em completude de dados, ownership, higiene de pipeline, forecast governance, stage/probability, close date hygiene e processo de remediação. O ponto central para RevOps é que CRM Data Quality não é um checklist técnico: é fundamento de Revenue Governance, Forecast Reliability e Pipeline Hygiene.

## Principais gaps
### Críticos
- **crm_governance | crm_data_quality_score**: Os dados sugerem score geral de qualidade em 74.0/100. Ação recomendada: Criar war room de CRM hygiene com owners por objeto e foco em campos críticos.
- **ownership | opportunities_without_owner**: Existem 4 oportunidades sem AE owner. Ação recomendada: Atribuir owner antes de qualquer forecast inclusion.
- **forecast_governance | opportunities_without_close_date**: Há 5 oportunidades sem close_date. Ação recomendada: Bloquear forecast de oportunidades abertas sem close_date validada.
- **revenue_integrity | closed_won_without_amount**: Há 2 Closed Won sem amount válido. Ação recomendada: Corrigir amount antes de report executivo.
- **close_date_hygiene | open_opportunities_with_past_close_date**: Há 4 oportunidades abertas com close_date no passado. Ação recomendada: Revisar oportunidades vencidas e exigir reason code.
- **forecast_governance | forecast_category_inconsistencies**: Há 6 forecast categories inconsistentes com stage. Ação recomendada: Criar matriz stage x forecast category.
- **revenue_risk | revenue_at_risk_from_data_quality**: Pipeline associado a problemas de qualidade soma R$ 3,270,414. Ação recomendada: Priorizar correção por valor em risco.

### Altos
- **lead_governance | lead_missing_source_rate**: A evidência disponível aponta para 10.8% dos leads sem source. Ação recomendada: Bloquear criação ou roteamento de lead sem source.
- **deduplication | duplicate_accounts**: Os dados sugerem 4 contas duplicadas por nome e domínio. Ação recomendada: Consolidar contas duplicadas e criar matching por domínio.
- **ownership | accounts_without_owner**: Há 4 contas sem owner. Ação recomendada: Fazer backfill de owner e criar regra diária de atribuição.
- **pipeline_hygiene | opportunities_without_next_step**: Há 5 oportunidades abertas sem next_step. Ação recomendada: Exigir next_step datado em pipeline review.
- **pipeline_hygiene | stale_opportunities**: Há 38 oportunidades paradas há mais de 20 dias. Ação recomendada: Criar limpeza semanal de oportunidades paradas.
- **pipeline_hygiene | advanced_stage_without_activity**: Há 7 oportunidades em estágio avançado sem atividade recente. Ação recomendada: Revisar deals avançados sem atividade.
- **loss_governance | closed_lost_without_loss_reason**: Há 3 Closed Lost sem loss_reason. Ação recomendada: Exigir loss_reason e revisar taxonomia de perdas.
- **revenue_integrity | opportunities_with_zero_amount**: Existem 6 oportunidades com amount zerado. Ação recomendada: Definir stage gate para amount.
- **forecast_governance | invalid_stage_probability_combinations**: Há 7 probabilidades incompatíveis com stage. Ação recomendada: Padronizar probability por stage.
- **close_date_hygiene | manual_close_date_change_rate**: Alterações manuais de close_date representam 84.0% dos eventos. Ação recomendada: Exigir reason code para pushes.
- **remediation_governance | overdue_remediation_tasks**: Há 4 tarefas de remediação atrasadas. Ação recomendada: Criar SLA semanal de remediação.

### Médios
- **deduplication | duplicate_leads**: Há indícios de 5 leads duplicados por email. Ação recomendada: Ativar dedupe por email antes do roteamento.
- **relationship_integrity | contacts_without_account**: Há 4 contatos sem conta associada. Ação recomendada: Associar contatos por domínio e exigir account_id.


## Hipóteses prováveis
- Os dados sugerem que regras de campos obrigatórios podem não estar conectadas ao ciclo comercial real por stage.
- Há indícios de que forecast category e probability podem estar sem controles suficientes.
- A evidência disponível aponta para close date hygiene fraca e necessidade de reason code para pushes.
- Problemas de ownership precisam ser validados com política de território, fila e SLA de aceite.
- Tarefas de remediação atrasadas sugerem oportunidade de fortalecer accountability operacional.

## Evidências observadas
- CRM Data Quality Score: 74.0/100.
- Forecast Reliability Score: 92.8/100.
- Pipeline Hygiene Score: 82.4/100.
- Leads sem source: 10,8%.
- Taxa de duplicidade de leads: 4,2%.
- Taxa de duplicidade de contas: 8,9%.
- Mudanças manuais de close_date no audit log: 84,0%.
- Taxa de conclusão de remediação: 16,7%.

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
