# Investigação de inconsistências temporais

Data da sessão: 08/09/2026. Base: UCI, 141.712 eventos e 24.918 chamados. Objetivo: investigar se as regressões de contador coincidem com eventos anteriores à abertura. Script 04 executado sobre o CSV original, sem alterá-lo.

## Cruzamento dos conjuntos

| Chamado | Regressão de contador | Evento antes da abertura | Mesmo contador em horários diferentes |
|---|---|---|---|
| INC0000130 | Sim | Sim | Sim |
| INC0000131 | Não | Sim | Não |
| INC0000134 | Sim | Sim | Sim |
| INC0000135 | Sim | Sim | Sim |
| INC0000137 | Sim | Não | Sim |
| INC0000164 | Sim | Sim | Sim |

Interseção: quatro chamados. União: seis (0,024% dos chamados). Reuso de contador e regressão atingem exatamente os mesmos cinco chamados. Esses resultados substituem a incerteza registrada na etapa 03 sobre a identidade dos conjuntos.

## Abertura e criação têm semânticas distintas

Os cinco eventos anteriores à abertura ocorrem em 29/02/2016, primeiro dia observado na base. Eles ocorrem no momento da criação sistêmica ou depois dela, nunca antes. As antecedências em relação à abertura são 134, 147, 109, 18 e 85 minutos: não há um deslocamento uniforme nesses cinco casos.

Por exemplo, INC0000130 tem criação às 07:17, atualização às 07:27 e abertura às 09:41. Isso é uma divergência entre campos temporais, não prova isolada de evento impossível. Abertura e criação permanecem constantes em todas as linhas extraídas de cada um dos seis chamados; isso não comprova que nunca tenham sido alteradas no sistema de origem.

Não substituir opened_at por sys_created_at nem aplicar um ajuste de fuso por suposição. A concentração no primeiro dia é compatível com uma particularidade de extração ou histórico inicial, mas não comprova essa hipótese.

## Caso com impacto na classificação da fila

INC0000137, em ordem de sys_updated_at:

| Horário em 29/02/2016 | Estado | Contador | Reaberturas registradas |
|---|---|---:|---:|
| 09:52 | New | 1 | 0 |
| 11:03 | Resolved | 2 | 0 |
| 11:10 | New | 1 | 0 |

Depois há Closed em 05/03/2016 às 12:00, contador 3. Todas as linhas informam resolução às 11:03 de 29/02/2016.

Se New for pendência e Resolved for saída, a regra puramente cronológica volta a colocar o chamado na fila às 11:10. O contador cai e reopen_count permanece zero. Isso demonstra ambiguidade do histórico; não prova reabertura real nem permite afirmar qual campo está errado. A ordem física do CSV também difere da cronológica nesse caso.

## Decisão e limites

Inconsistências localizadas com confiança alta nas observações e causa ainda desconhecida. Relevância alta para reconstrução temporal desses casos, embora a fração de chamados seja pequena. O pequeno volume não foi usado como prova de impacto desprezível.

Preservados todos os registros. Script 04 produz uma lista por chamado com indicadores separados de anomalia e um extrato dos históricos, em data/processed/investigacao_temporal. São evidências de diagnóstico, não uma base limpa. Não foi definida exclusão definitiva, nem calculado o impacto agregado sobre a fila.

Próximo passo: decidir como apresentar a incerteza na análise histórica, comparando resultados com todos os chamados e com os seis sinalizados separados. Essa decisão deve anteceder a publicação do indicador. Para identificar a causa raiz seria necessária documentação adicional ou acesso à auditoria de origem; não é possível atribuí-la com segurança apenas com o CSV.
