# Metrics Dictionary

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
