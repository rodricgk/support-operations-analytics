# Diário de aprendizado

## Sessão inicial — planejamento

- Definido foco em filas e prazos com visão gerencial complementar.
- Escolhida base pública UCI, sujeita a inspeção.
- Escolhidas ferramentas: Python, Supabase/PostgreSQL, Power BI e GitHub.
- Definido aprendizado acompanhado, com atenção especial a Power BI.
- Definido repositório público e projeto separado no Supabase.
- Próxima atividade: inspecionar a granularidade dos eventos.

Nas próximas sessões, registrar: atividade realizada, evidência obtida, aprendizado, dúvida e próximo passo.

## Primeira inspeção — material para discussão

- Ambiente confirmado: Python 3.14.5 e pandas 3.0.5.
- CSV oficial extraído para data/raw, preservado e excluído do Git.
- Conferidas 141.712 linhas, 24.918 chamados distintos e 36 colunas.
- Criado script somente de leitura para comparar eventos e incidentes.
- Exemplo INC0000045: quatro registros, incluindo dois com estado Resolved. As datas resolved_at e closed_at já aparecem preenchidas no registro New.
- Hipótese a investigar: campos de resultado podem ter sido adicionados retrospectivamente no enriquecimento. Não assumir que estavam disponíveis no momento de cada evento.
- Discussão com o autor ainda pendente. Próximo passo: interpretar o exemplo antes de definir regras de consolidação e métricas.
