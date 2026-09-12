# Idade da fila diária — 11/09/2026

A idade mediana dos pendentes foi calculada e conferida em **355 datas e dois cenários de qualidade: 710 resultados SQL versus Python**.

A maior fila observada ocorreu em **16/03/2016**, com **1.869 chamados** e idade mediana de **157,45 horas (6,56 dias corridos)**. Volume e idade contam aspectos diferentes: a maior mediana ocorreu em 15/12/2016, com apenas 33 chamados na fila.

## Pergunta, população e fórmula

Pergunta para a coordenação de suporte: há quanto tempo estão abertos os chamados que continuam pendentes na fotografia do dia?

Uma linha de fotografia representa um chamado numa data. Entram no cálculo da mediana os estados classificados como pendentes, com abertura conhecida e anterior ou igual à meia-noite seguinte. A idade é:

`meia-noite do dia seguinte - opened_at`, convertido para horas corridas.

Usamos a abertura original informada, inclusive se houve retorno à pendência. A idade não é tempo desde a última reabertura, esforço de trabalho ou SLA. As flags de qualidade são retrospectivas.

Fonte: [UCI — Incident management process enriched event log](https://doi.org/10.24432/C57S4H), Amaral, Fantinato e Peres (2018), CC BY 4.0. Mesma extração pública já documentada no modelo. Cobertura das fotografias: 29/02/2016 a 17/02/2017; 18/02/2017 é terminal parcial e não entra no corte de fim de dia. Fuso não informado.

## Leitura de algumas datas

Cenário com todos os chamados:

| Data de corte | Pendentes | Elegíveis para idade | Idade mediana (h) | Idade mediana (dias) |
|---|---:|---:|---:|---:|
| 29/02/2016 | 163 | 163 | 11,13 | 0,46 |
| 16/03/2016 | 1.869 | 1.869 | 157,45 | 6,56 |
| 15/12/2016 | 33 | 33 | 5.365,77 | 223,57 |
| 17/02/2017 | 0 | 0 | Sem pendentes | Sem pendentes |

As datas de extremos são selecionadas para explicar a diferença entre volume e idade, não para representar o dia típico. Não concluir melhora ou piora operacional apenas por essa comparação: composição e cobertura da extração variam.

A idade elevada de dezembro foi inspecionada. No grupo de 33 pendentes, o chamado central na ordenação, INC0026758, tem abertura em 06/05/2016 às 10:14 e último evento observado até o corte em 13/10/2016 às 19:09, estado New. Até 16/12/2016 às 00:00, isso produz 5.365,7667 horas. A regra prolonga o último estado conhecido; não comprova que o histórico disponibilizado contenha todas as mudanças reais.

## Ausências, desconhecidos e sensibilidade

- Dois dias têm fila observada zero: 14/02/2017 e 17/02/2017. A mediana é NULL/None, nunca zero.
- Nenhum dia teve pendentes com idade inválida ou ausente nesta execução.
- Seis fotografias diárias contêm um chamado em estado desconhecido, contado separadamente. Ele não entra na mediana dos pendentes.
- A comparação sem os seis chamados sinalizados altera a mediana em quatro datas: 29/02, 01/03, 02/03 e 04/03 de 2016. Em 03/03 a quantidade da fila muda, mas a mediana não muda.
- Em 29/02, por exemplo, a fila passa de 163 para 158 e a mediana de 11,1333 para 10,7333 horas. Isso é sensibilidade ao cenário, não comprovação de qual fila retrata a operação real.

Fila vazia no fim de uma extração histórica não comprova que toda a operação ficou sem pendências. O indicador descreve os chamados e eventos disponíveis.

## Como usar no Power BI

Em uma linha do tempo, mostrar cada data com sua própria fila e mediana. Manter o calendário completo, inclusive os dias sem pendência.

Em um cartão referente a um período, usar a **última data elegível selecionada**. Se essa data tiver fila zero, mostrar fila 0 e idade em branco ou “Sem pendentes”. Não voltar silenciosamente ao último dia com uma mediana preenchida.

Não somar estoques diários, não tomar média das medianas e não juntar todas as fotografias para obter a idade do período. Isso daria pesos diferentes aos chamados que aparecem em mais dias.

Recortes futuros por grupo, prioridade ou categoria devem usar os atributos da fotografia, e a mediana deve ser recalculada sobre os chamados do recorte.

## Código e reprodução

Consulta: sql/05_idade_fila_diaria.sql. O calendário é cruzado com os cenários e recebe as fotografias por LEFT JOIN. O filtro dos sinalizados fica na condição da junção para não remover datas vazias. COUNT(number) e FILTER evitam contar a linha vazia gerada pela junção como um chamado.

No terminal do repositório:

```powershell
.\.venv\Scripts\python.exe scripts/10_idade_fila_diaria.py
```

O Python recalcula a idade pelas datas, confere a elegibilidade e compara com a saída SQL salva em docs/idade-fila-sql.json. Também reconcilia as quantidades de fila e desconhecidos com o resumo da etapa 06. Saídas locais: data/processed/idade_fila, fora do Git.

Tutorial complementar: notebooks/10_idade_fila_diaria.ipynb. Células executadas sequencialmente no Python do projeto, com estrutura JSON e saídas conferidas. O motor Jupyter não foi executado, pois suas dependências não estão instaladas.

## Validação

Avaliação: resultados conferidos e utilizáveis com as ressalvas da fonte.

- Contagens coincidiram exatamente em 710 combinações de data e cenário.
- Medianas coincidiram com tolerância absoluta de 0,000001 hora.
- Elegíveis mais pendentes com idade inválida reconciliam a fila.
- Idade recalculada elegível coincidiu com a flag armazenada.
- Vazio, ausência de abertura, abertura futura, abertura exatamente no corte e estado desconhecido foram testados em exemplos controlados. Em SQL e Python, quatro pendentes (dois elegíveis, dois inválidos) e um desconhecido produzem mediana de 6 horas.
- Nenhuma tabela do banco foi alterada nesta etapa.

## Próximo passo

Com os três indicadores principais implementados, preparar o modelo de leitura para Power BI: calendário, relacionamentos e campos que serão usados nos cartões e gráficos. A conexão de leitura do Power BI ainda não foi configurada.
