# Apresentação do projeto — roteiro de 2 a 3 minutos

## Mensagem central

Transformei um histórico público de eventos de suporte em um modelo que separa duração dos chamados e evolução diária da fila. Usei Python para investigar e preparar os dados, PostgreSQL no Supabase para reconstruir e conferir resultados, e Power BI para explorar os indicadores.

## 1. Problema — mostrar as duas páginas (20 segundos)

“Este projeto responde a duas perguntas: quanto tempo os chamados levaram até a resolução informada e quantos continuavam pendentes em cada dia. Trabalhei com uma base pública da UCI, com 141.712 eventos referentes a 24.918 chamados.”

## 2. Decisão de modelagem — mostrar o modelo (30 segundos)

“A parte central foi distinguir evento, chamado e fotografia diária. Um chamado pode aparecer em muitos eventos e em vários dias da fila. Por isso, contar todas as linhas como chamados daria uma resposta errada. Separei uma tabela com um registro por chamado e outra com um registro por chamado e data. Na análise da fila, usei os atributos observados naquele dia; na duração, os atributos finais.”

## 3. Duração — mostrar a página sem filtro mensal (35 segundos)

“Dos 24.918 chamados, 23.362 têm duração elegível para o cálculo. Nesse conjunto, a mediana é 22,10 horas e o percentil 90 é 381,55 horas. A diferença entre esses indicadores mostra por que apenas uma medida central não descreve bem a distribuição. São horas corridas, e não horas de esforço nem cumprimento de SLA.”

Passe o mouse em dezembro/2016 para mostrar também a quantidade elegível: 54. Explique: “O mês agrupa chamados pela resolução informada. Comparações entre meses precisam considerar o volume e quais casos foram resolvidos; a curva sozinha não prova piora no atendimento.”

## 4. Fila — mostrar o intervalo até 16/03/2016 (35 segundos)

“Na fotografia de 16 de março de 2016, havia 1.869 chamados pendentes, com idade mediana de 157,45 horas desde a abertura. Ao selecionar uma prioridade, os indicadores mostram aquele segmento. O cartão usa a última data elegível do período, não a soma dos estoques diários.”

Selecione Low na tabela: 98 pendentes, idade mediana 321,36 horas. Limpe a seleção ao terminar. Não descreva a diferença como descumprimento de prioridade: não há meta nem controle de complexidade neste recorte.

## 5. Validação e limite — mostrar o repositório (25 segundos)

“Reconstruí e comparei resultados em Python e SQL, documentei as regras e conferi as nove medidas do Power BI no projeto textual. Também distingui fila zero de ausência de cobertura. É um estudo retrospectivo com dados públicos: não é uma operação em tempo real e não mede um ganho de negócio causado pelo dashboard.”

## O que destacar em entrevista

- Contar chamados exige respeitar o grão; não somar fotografias para obter chamados únicos.
- Mediana e P90 são recalculados sobre registros elegíveis, inclusive nos totais.
- Ausência de data não vira duração zero; ausência de cobertura não vira fila zero.
- Separar atributos históricos e finais evita atribuir o passado à situação final do chamado.
- A revisão textual das fórmulas complementa as conferências de resultados; não equivale a executar testes automáticos no motor DAX.

## Preparação da demonstração

1. Duração: Mês de resolução = Todos; nenhuma linha ou ponto selecionado.
2. Fila: 01/01/2016 a 16/03/2016; nenhuma prioridade selecionada; detalhe diário decrescente.
3. PDF serve como prévia estática e mostra apenas as linhas visíveis. Use o Power BI para demonstrar filtros e dicas de ferramenta.
4. O Power BI importa CSVs locais. PostgreSQL foi usado na modelagem e validação; não apresentar como conexão direta do Power BI ao Supabase.

## Referências e materiais

- [Fonte pública UCI](https://doi.org/10.24432/C57S4H), Amaral, Fantinato e Peres (2018), CC BY 4.0.
- [Regras e conferências do relatório](relatorio-power-bi.md).
- [Duração: população e validação](indicadores-duracao.md).
- [Fila e idade: regras e validação](idade-fila.md).
- [Relatório em PDF](../power_bi/support-operations-analytics.pdf).
- [Repositório](https://github.com/rodricgk/support-operations-analytics).
