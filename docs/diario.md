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

## Segunda inspeção — ordem dos eventos

- Discutida a distinção entre contar eventos e contar chamados.
- Explicada a fila histórica como último estado conhecido até uma data de corte.
- Executado scripts/02_verificar_historico.py; original preservado.
- Encontrados empates de horário, estado desconhecido e exceções temporais. Evidências em qualidade-historico.md.
- Próximo exercício: interpretar sys_mod_count como candidato a desempate e investigar sua consistência. A regra ainda não foi adotada.

## Terceira inspeção — consistência do contador

- O autor identificou o maior contador como candidato a evento posterior em um empate de horário.
- Script 03 executado: valores válidos, mas 5 chamados apresentam regressões do contador entre horários (11 grupos).
- Chave composta permanece única após conversão numérica.
- Evidências e limites em validacao-contador.md. Nenhuma correção ou exclusão aplicada.
- Próximo passo: confrontar as exceções temporais antes de estabelecer a regra de ordenação do modelo.

## 08/09/2026 — investigação das inconsistências

- Cruzados os conjuntos: quatro chamados em comum; seis na união.
- Todos os cinco eventos anteriores à abertura ocorrem na criação sistêmica ou depois dela.
- INC0000137 mostra Resolved → New com regressão do contador e reopen_count zero; a classificação histórica é ambígua.
- Causa raiz permanece indeterminada. Nenhuma data, contador ou estado corrigido por suposição.
- Geradas evidências locais pelo script 04; resultados documentados em investigacao-inconsistencias.md.

## 08/09/2026 — comparação de cenários da fila diária

- Acordado preservar os valores originais e sinalizar exceções, sem atribuir causa não comprovada à plataforma.
- Implementada fotografia diária provisória por último estado conhecido, com espera como pendência e estados desconhecidos em contagem separada.
- Comparados 355 dias: cinco dias com diferença, máximo de cinco chamados ou 3,07% da fila com todos no primeiro dia.
- Seis fotografias apresentam um chamado em estado desconhecido. Próxima etapa deve incluir essa lacuna na definição dos indicadores.
- Nenhuma correção ou exclusão definitiva aplicada. Resultados não quantificam a fila verdadeira nem impacto intradiário.
- Próximo passo de estudo: formalizar dicionário dos indicadores e a relação entre eventos e tabela de chamados antes de implementar no Supabase.
