# Production Flow

Em produção, o fluxo seria conectado a CRM, Sales Engagement, Marketing Automation, Billing e Finance/FP&A.

## Etapas
- Ingestão incremental de objetos, atividades, audit log e snapshots de forecast.
- Modelagem de contas, contatos, oportunidades, atividades, alterações e tarefas.
- Data quality checks por completude, unicidade, validade, integridade referencial e consistência de forecast.
- Alertas para oportunidades sem owner, close_date vencido, Commit sem atividade, Closed Won sem amount e remediações atrasadas.
- Workflow humano com RevOps, CRM Admin, Sales Ops e Sales Managers.
- Segurança com controle de acesso, auditoria e mascaramento de dados sensíveis.

## Limitações
Regras reais, exceções comerciais e validações de manager precisam ser configuradas antes de qualquer uso operacional.
