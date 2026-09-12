# Primeiros indicadores de duração — 11/09/2026

A mediana do tempo decorrido até a resolução informada é **22,10 horas**; o P90 é **381,55 horas**, aproximadamente **15,90 dias corridos**. Cálculo sobre **23.362 chamados elegíveis**, com um registro por chamado.

A diferença entre a mediana e o P90 evidencia casos na parte mais lenta da distribuição. A próxima investigação deve combinar essa duração com a idade dos chamados ainda pendentes. Não há evidência suficiente para recomendar mudança de equipe, definir SLA ou atribuir causa aos tempos observados.

## População e período

Fonte: [UCI — Incident management process enriched event log](https://doi.org/10.24432/C57S4H), Amaral, Fantinato e Peres (2018), CC BY 4.0. Os dados são públicos e anonimizados; nenhuma informação do empregador foi usada.

Esta leitura cobre toda a extração disponível. Entre os registros com resolução informada, as datas vão de 29/02/2016 às 09:04 até 17/02/2017 às 00:47. Fuso não informado. Não é uma comparação de meses completos nem uma estimativa de desempenho atual.

Dos 24.918 chamados:
- 23.362 entram na medida: **93,76%**.
- 1.556 ficam fora por ausência de resolved_at: **6,24%**.
- Não houve, nesta tabela consolidada, exclusão por ausência de abertura, conflito de datas, formato inválido, duração negativa ou estado final inadequado.

Os 1.556 continuam na base. Estão em estado final, mas a data de resolução não foi informada; não chamá-los automaticamente de pendentes nem substituí-los por duração zero. O percentual de cobertura acima é global, pois chamados sem resolved_at não podem ser distribuídos por mês de resolução sem inventar uma data.

## Cenários de qualidade

| Cenário | Total considerado | Elegíveis | Sem data de resolução | Mediana (h) | P90 (h) |
|---|---:|---:|---:|---:|---:|
| Todos | 24.918 | 23.362 | 1.556 | 22,10 | 381,55 |
| Sem os seis sinalizados | 24.912 | 23.356 | 1.556 | 22,09 | 381,55 |

Sem arredondar, a mediana passa de 22,1 para 22,0916667 horas e o P90 de 381,5483333 para 381,55 horas. Os seis casos têm pouco efeito sobre estes percentis globais; isso não comprova que seu histórico esteja correto nem garante o mesmo efeito em qualquer recorte.

## Primeira segmentação: prioridade final

Cenário com todos os chamados:

| Prioridade final | Total | Elegíveis | Excluídos | Mediana (h) | P90 (h) |
|---|---:|---:|---:|---:|---:|
| 1 - Critical | 270 | 270 | 0 | 80,24 | 616,44 |
| 2 - High | 408 | 408 | 0 | 38,23 | 381,57 |
| 3 - Moderate | 23.466 | 22.010 | 1.456 | 21,55 | 374,61 |
| 4 - Low | 774 | 674 | 100 | 5,02 | 502,30 |

A prioridade baixa combina mediana pequena e P90 elevado. A crítica apresenta mediana maior. Esses números justificam examinar a composição dos chamados, esperas e categorias; não demonstram falha de priorização ou desempenho da equipe. As populações e a cobertura diferem, e a prioridade é a do último registro da extração.

Não calcular o P90 geral pela média dos P90 de prioridades. O percentil deve ser recalculado sobre os chamados individuais do recorte escolhido.

## Como interpretar e reproduzir

Mediana: aproximadamente metade dos chamados elegíveis tem duração até 22,10 horas. P90: aproximadamente 90% têm duração até 381,55 horas; o restante está na parte mais demorada da distribuição.

Usamos percentil contínuo com interpolação linear. No exemplo de durações 0, 10, 20 e 100 horas, a mediana é 15 e o P90 é 76; o percentil não precisa coincidir com uma duração existente. O PostgreSQL implementa essa operação com [percentile_cont](https://www.postgresql.org/docs/17/functions-aggregate.html#FUNCTIONS-ORDEREDSET-TABLE).

SQL principal: sql/04_indicadores_duracao.sql. Usa CASE para classificar motivos exclusivos, FILTER para controlar a população de cada agregação e GROUPING SETS para obter o geral e os recortes de prioridade sem misturá-los.

No terminal do projeto:

```powershell
.\.venv\Scripts\python.exe scripts/09_indicadores_duracao.py
```

O script recalcula as durações a partir das datas, calcula os quantis com pandas e compara com docs/duracao-sql.json, saída salva da consulta executada no Supabase. Resultados locais ficam em data/processed/duracao, fora do Git. Se banco, fonte ou regras mudarem, execute o SQL novamente e atualize a evidência antes de reconciliar.

Tutorial complementar: notebooks/09_indicadores_duracao.ipynb. Suas cinco células Python foram executadas sequencialmente no ambiente do projeto, com saídas capturadas e estrutura JSON conferida. O motor Jupyter não foi executado; suas dependências não estão instaladas.

## Validação e limites

**Avaliação: resultados conferidos, utilizáveis com as ressalvas da fonte.**

- Python e SQL recalcularam a duração pelas datas e conferiram em dez recortes: dois cenários e quatro prioridades em cada um.
- Contagens e motivos coincidiram exatamente; tolerância de 0,000001 hora para percentis.
- A soma dos motivos exclusivos reconcilia os excluídos; nenhum chamado foi multiplicado por eventos.
- Interpolação linear, população vazia (NULL/None) e duração zero foram testadas em ambos os ambientes.
- A elegibilidade recalculada em Python coincidiu com a flag da etapa 06.

São horas corridas, com noites, fins de semana e esperas incluídos. Não medem esforço trabalhado, primeira resolução ou duração de cada episódio de reabertura. Não há contrato ou calendário de SLA para avaliar cumprimento.

Casos sem data de resolução ficam fora; não conhecemos sua distribuição de duração. O recorte retrospectivo de resoluções observadas também não descreve, sozinho, a experiência dos casos ainda em andamento. Não afirmar que estes tempos representam todos os atendimentos reais da operação.

## Próximo exercício

Explicar com as próprias palavras:
1. Por que a mediana é 22,10 h e o P90 pode chegar a 381,55 h?
2. Por que não podemos incluir os 1.556 sem data como zero?
3. Por que prioridade final crítica com mediana maior não prova atendimento pior?

Depois, calcular a mediana da idade dos pendentes por fotografia, para complementar a duração até a resolução.
