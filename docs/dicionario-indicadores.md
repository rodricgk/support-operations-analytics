# Dicionário de indicadores — versão 0.1

Status em 11/09/2026: os três indicadores principais foram implementados. Modelo local e Supabase reconciliados; duração conferida na etapa 09 e idade diária na etapa 10 (355 dias, dois cenários). Veja indicadores-duracao.md e idade-fila.md. Modelagem e conexão de leitura do Power BI são a próxima etapa.

## Decisão e público

Coordenador de suporte: acompanhar acúmulo de pendências e identificar segmentos que merecem investigação. Leitura diária, com revisão semanal. Responsável pela definição e validação neste portfólio: Rodrigo Fernandes. Fonte exclusiva: CSV público UCI. Não há metas contratuais, capacidade da equipe ou calendário de SLA disponíveis; não inventar metas.

## Regras comuns

- Uma linha da fonte é um evento; number identifica um chamado.
- Corte diário: eventos com sys_updated_at < meia-noite do dia seguinte, sem converter fuso por suposição.
- Ordem candidata: horário, depois sys_mod_count numérico. Preservar as sinalizações de ambiguidade.
- Pendente de resolução: New, Active e os quatro estados Awaiting (User Info, Vendor, Problem, Evidence).
- Fora da fila de resolução: Resolved e Closed. Resolved não é sinônimo de Closed.
- Outros estados: desconhecidos, em contagem separada. Não presumir encerramento.
- Cenário principal: todos os chamados, com flags visíveis. Comparação: sem os seis sinalizados. Isso não afirma que o principal corresponde à verdade operacional.
- Base histórica estática. Refazer indicadores quando os arquivos ou regras mudarem. Não há atualização operacional em tempo real.
- Campos retrospectivos de resolução não devem determinar o estado passado. Cada indicador declara sua referência temporal.
- Sem média de percentuais, soma de percentis ou soma de estoques diários para produzir total de chamados.

## Três indicadores principais

### 1. Fila observada ao fim do dia (B)

Pergunta: quantos chamados conhecidos ainda dependem de resolução?

Fórmula: contar number distintos cujo último estado conhecido até o corte seja pendente. Unidade: chamados; grão: chamado × data de corte. Fonte: eventos; fotografia diária. Recortes por grupo, prioridade e categoria devem usar os valores desse último evento, não os valores finais do chamado.

No resumo de um período, mostrar a fila do último dia elegível selecionado. Uma média diária é outra medida, explicitamente rotulada. Não somar fotografias para contar chamados únicos. Guardrail: desconhecidos na mesma fotografia e diferença entre cenários de qualidade.

Limites: inclui apenas chamados conhecidos na extração; não reconstrói um estoque inicial não observado. Excluir o dia terminal parcial (18/02/2017) da fotografia de fim de dia não garante cobertura integral dos demais. Diminuir a fila pode resultar de encerramentos prematuros; investigar retornos à pendência como contrapeso.

### 2. P90 do tempo decorrido até a resolução informada

Pergunta: quanto demoram os casos na parte mais lenta da distribuição?

População proposta: um registro por chamado, com resolved_at no período selecionado e último estado do arquivo Resolved ou Closed. Usar os valores não ausentes únicos de opened_at e resolved_at; se houver conflito entre valores, sinalizar em vez de escolher arbitrariamente.

Duração: (resolved_at - opened_at) em horas corridas. Aceitar zero; excluir valores ausentes, inválidos ou negativos apenas desta medida e apresentar suas contagens. Calcular quantil 0,90 com interpolação linear (equivalente ao percentil contínuo), sobre durações individuais elegíveis. Sempre mostrar n elegível; sem casos, retornar vazio, nunca zero.

Mediana é a medida complementar do tempo típico, sobre a mesma população. Recortes usam grupo/prioridade do último registro, rotulados como finais; não atribuir toda a duração como esforço daquele grupo. Quantis devem ser recalculados no recorte, não agregados a partir de quantis de grupos.

Trata-se de análise retrospectiva da data de resolução informada, que não comprova primeira resolução, duração de cada episódio, horas trabalhadas ou cumprimento de SLA. Casos ainda não resolvidos não entram: isso pode favorecer os rápidos. Por isso acompanhar a idade da fila. Comparar também com o cenário sem os sinalizados, sem pressupor que o impacto da fila diária se repita aqui.

### 3. Mediana da idade total dos chamados pendentes

Pergunta: há quanto tempo os chamados que continuam na fila foram abertos?

População: chamados pendentes na fotografia diária, com opened_at válido e anterior ou igual ao corte. Fórmula individual: (corte - opened_at) em horas corridas. Mediana sobre chamados elegíveis, acompanhada de n elegível e n com idade inválida/ausente. Abertura posterior ao corte torna a idade inválida; não retirar silenciosamente o chamado da contagem de fila.

Grão: chamado × data. Recortes usam os atributos da fotografia. No resumo de um período, mostrar a mediana na última fotografia elegível, não a mediana de medianas diárias. Em reabertura, a idade continua desde a abertura original; não representa tempo desde a última reabertura. Duração de espera permanece incluída. P90 de idade pode ser adicionado se a mediana ocultar casos antigos relevantes.

## Fluxos para explicar variações

Não usar o termo ambíguo 'abertos' tanto para entrada quanto para estoque.

| Medida | Definição proposta | Referência temporal |
|---|---|---|
| Chamados abertos no período | number distintos por opened_at, uma vez por chamado; ausências/conflitos sinalizados | Data de abertura informada |
| Chamados com resolução informada no período | Contagem da população elegível do indicador 2, não contagem de linhas Resolved | resolved_at |
| Entrada observada em pendência | Transição de fora da pendência para pendência; primeiro evento pendente é entrada observada com histórico anterior desconhecido | sys_updated_at |
| Saída observada de pendência | Transição de pendente para Resolved/Closed; pendente → desconhecido é movimento separado | sys_updated_at |

As duas primeiras medidas são mais fáceis de comunicar, mas NÃO reconciliam automaticamente a fila. Datas informadas, reaberturas e cobertura da extração podem divergir dos eventos observados.

Para reconciliar fotografias, usar os movimentos do mesmo histórico:

B(d) = B(d-1) + entradas observadas em pendência - saídas conhecidas - movimentos de pendência para desconhecido.

Entradas incluem desconhecido → pendente, primeira observação pendente e retornos à pendência. Primeiro registro não pendente não causa saída, pois não havia pendência observada anterior. Repetições do mesmo estado pendente têm delta zero. O estoque anterior ao início da extração é zero apenas para esta construção observada, não para a operação real. Ao filtrar grupos, incluir transferências de grupo na reconciliação; essa fórmula sem transferências aplica-se ao total da base.

Não denominar automaticamente um retorno à pendência como reabertura real: o caso INC0000137 demonstra a ambiguidade. Confrontar com reopen_count e flags antes dessa interpretação.

## Controles de qualidade visíveis

1. Chamados em estado desconhecido: quantidade e proporção dos chamados conhecidos na fotografia, com denominador explícito; vazio quando denominador zero. Não significa taxa de erro.
2. Sensibilidade aos sinalizados: diferença absoluta e relativa (dividida pelo cenário com todos; vazio quando zero) por indicador e recorte. Informar elegíveis/excluídos para as medidas de duração.

## Métricas adiadas

- SLA: sem semântica confirmada de made_sla, contrato e calendário, não publicar taxa ou meta.
- Produtividade individual: não há esforço e capacidade suficientes para sustentá-la.
- Taxa de reabertura: validar transições e contador, definir denominador e janela de observação antes de comparar grupos.

## Estrutura conceitual para o próximo passo

| Tabela lógica | O que uma linha representa | Finalidade |
|---|---|---|
| Eventos | Um registro de atualização da fonte | Histórico, transições e rastreabilidade |
| Chamados | Um number, com atributos finais explicitamente identificados | Aberturas e durações retrospectivas |
| Fotografias | Um chamado pendente ou desconhecido em uma data de corte | Fila e idade com atributos conhecidos no corte |
| Calendário | Uma data | Filtros e eixos temporais |

As fotografias implementadas preservam o grão chamado por data e os atributos históricos. As tabelas já estão no Supabase; os relacionamentos do Power BI ainda serão construídos. Não ligar fatos diretamente e depois somar colunas de chamados repetidas pelos eventos.
