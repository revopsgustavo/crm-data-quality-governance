# Business Rules

## Campos obrigatórios
Leads precisam de `lead_id` e `source`. Accounts precisam de `account_id` e `owner_id`. Contacts precisam de `contact_id` e `account_id`. Opportunities precisam de `opportunity_id`, `account_id`, `owner_id`, `amount`, `close_date`, `stage`, `forecast_category` e `probability`.

## Forecast Governance
Forecast category deve ser coerente com stage. Probability usa escala 0-1 e deve respeitar faixas esperadas por stage. Exceções precisam de validação de manager.

## Pipeline Hygiene
Oportunidades abertas devem ter owner, close_date, next_step e atividade recente. Oportunidades com close_date no passado exigem revisão imediata ou reason code de push.

## Remediação
Gaps críticos devem ser tratados imediatamente; gaps altos entram na semana; gaps médios entram na cadência mensal.
