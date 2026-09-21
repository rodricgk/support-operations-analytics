# Auditoria de qualidade dos dados e das métricas

## Resultado técnico

As métricas publicadas são reproduzíveis para a extração analisada. A auditoria executou 28 checagens sem falhas bloqueantes: as chaves do modelo são únicas, a fonte corresponde ao hash usado na modelagem, as relações entre as tabelas são íntegras, as contagens reconciliam e não há duração negativa nem idade inválida incluída nos indicadores.

Há três ressalvas de interpretação. A duração cobre 23.362 de 24.918 chamados (93,7555%); 1.556 chamados sem `resolved_at` ficam fora da mediana e do P90. Cinco eventos têm atualização anterior a `opened_at`. O estado `-100`, presente em cinco eventos de dois chamados, não possui significado documentado e permanece fora da contagem de pendentes. Esses casos não foram corrigidos por suposição.

## Evidências principais

| Dimensão | Evidência | Avaliação | Risco para o uso | Tratamento |
|---|---:|---|---|---|
| Identidade da fonte | SHA-256 igual ao manifesto do modelo | Passou | Baixo | Bloquear a validação se o CSV mudar sem remontar o modelo |
| Chave de evento | 0 duplicidades em `number + sys_updated_at + sys_mod_count` | Passou | Baixo nesta extração | Manter teste a cada atualização |
| Chave de chamado | 0 IDs repetidos em 24.918 linhas | Passou | Baixo | Manter teste a cada atualização |
| Chave de fotografia | 0 repetições de chamado por dia | Passou | Baixo | Manter teste a cada atualização |
| Cobertura da duração | 23.362 elegíveis; 1.556 excluídos | Ressalva | Médio: os excluídos podem ter perfil diferente | Exibir cobertura junto da métrica e evitar generalizar para todos os chamados |
| Consistência temporal | 5 eventos antes da abertura; 0 durações negativas incluídas | Ressalva controlada | Baixo no agregado, relevante nos casos afetados | Preservar e sinalizar os registros; comparar cenários com e sem os seis chamados sinalizados |
| Domínio de estado | 5 eventos com `-100` | Ressalva | Classificação da fila desconhecida em seis fotografias diárias | Manter classe `desconhecido`, separada de pendente e finalizado |
| Último dia da fila | Dia parcial excluído automaticamente | Passou | Baixo | Derivar o corte da maior atualização observada |

Não foi incluído gráfico nesta auditoria: as evidências são contagens de validação e relações de integridade, para as quais a tabela permite conferir o valor, a regra e o efeito com mais precisão.

A cobertura varia entre prioridades: 100% em Critical e High, 93,80% em Moderate e 87,08% em Low. Essa diferença não invalida as medianas, mas torna inadequada uma comparação entre prioridades sem informar também total, elegíveis e excluídos de cada grupo.

## Escopo e definições

A fonte contém 141.712 eventos de 24.918 incidentes. O grão esperado do CSV é um evento por combinação de chamado, horário de atualização e contador de modificação. O modelo contém uma linha por chamado e uma linha por chamado pendente ou desconhecido em cada fotografia diária.

A duração é calculada em horas corridas entre `opened_at` e `resolved_at`. Um chamado é elegível quando termina em `Resolved` ou `Closed`, possui datas válidas e únicas e apresenta duração não negativa. A mediana e o P90 descrevem somente essa população elegível; não representam SLA.

A fila diária usa o último evento conhecido até o fim de cada dia. `New`, `Active` e estados `Awaiting ...` entram como pendentes; `Resolved` e `Closed` ficam fora da fila. Estados sem regra confirmada permanecem desconhecidos. O último dia da extração é removido porque sua cobertura é parcial.

## Método de auditoria

O script `scripts/13_analisar_qualidade.py` lê a fonte e os quatro arquivos principais do modelo sem alterá-los. As checagens cobrem:

- completude dos campos usados para identificação, ordenação e recorte;
- unicidade das chaves de evento, chamado e fotografia;
- validade dos domínios de prioridade e estado;
- conversão e ordem das datas usadas nas métricas;
- integridade entre a fonte, o manifesto e as tabelas modeladas;
- elegibilidade das durações e idades da fila;
- exclusão do último dia parcial.

Falhas que podem invalidar a entrega interrompem a execução. Situações conhecidas que limitam a interpretação são registradas como ressalvas e permanecem visíveis no JSON gerado em `data/processed/qualidade/validacao.json`.

## Limitações e robustez

Os scripts 09 e 10 reconciliam os cálculos em Python com resultados SQL armazenados em `docs/duracao-sql.json` e `docs/idade-fila-sql.json`. Isso comprova concordância com a evidência salva, mas não confirma o estado atual do Supabase. Uma auditoria de atualização deve executar novamente as consultas SQL e substituir os arquivos de evidência com data, hash da fonte e identificação da execução.

O modelo deriva o estado diário do histórico disponível. A fonte não comprova que todos os eventos da operação original foram exportados, e os horários não informam fuso. Portanto, a análise é descritiva desta extração; ela não estabelece causalidade nem desempenho contra metas contratuais.

A sensibilidade já implementada compara todos os chamados com um cenário sem os seis casos temporalmente sinalizados. As métricas gerais de duração variam pouco entre os cenários, mas o volume reduzido não explica a causa das anomalias.

## Próximos controles recomendados

1. Registrar nas evidências SQL o hash da fonte e o horário da consulta.
2. Acompanhar a cobertura da duração por prioridade e período, além do total geral.
3. Investigar o significado do estado `-100` antes de reclassificá-lo.
4. Executar `scripts/12_validar_entrega.py` em toda atualização; ele agora chama a auditoria de qualidade e usa o manifesto e as tabelas atuais em vez de números fixos.

## Questões em aberto

- Os chamados sem `resolved_at`, embora terminem como `Closed`, foram resolvidos por outro processo ou perderam essa informação na extração?
- O estado `-100` representa uma etapa operacional, correção técnica ou valor legado?
- Há documentação da origem que explique os cinco eventos anteriores à abertura e o fuso dos horários?

Fonte: UCI, *Incident management process enriched event log*, DOI 10.24432/C57S4H. Resultados reproduzidos localmente sobre o arquivo identificado no manifesto `data/processed/modelo/validacao.json`.
