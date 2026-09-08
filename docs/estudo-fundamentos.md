# Estudo guiado: conceitos usados até aqui

## 1. Granularidade, chaves e contagem

Exemplo: INC0000045 tem quatro eventos, mas é um chamado. Estudar COUNT(*), COUNT(DISTINCT), chaves compostas e cardinalidade de joins. Exercício: explicar por que juntar uma tabela de chamados com eventos pode repetir a duração total do chamado.

## 2. Consultas históricas e funções de janela

Estudar ROW_NUMBER, PARTITION BY, ORDER BY e LAG. Primeiro filtrar eventos anteriores ao corte; depois numerar por chamado, horário decrescente e contador decrescente. Fazer o contrário pode apagar o histórico válido quando o registro atual está no futuro do corte.

Referência primária: https://www.postgresql.org/docs/current/tutorial-window.html

Exercício: escrever o resultado esperado de um chamado aberto segunda, resolvido terça e reaberto quarta para cada fim de dia, antes de escrever SQL.

## 3. Estoque versus fluxo

Fila é estoque numa data. Entradas e saídas são fluxos em um intervalo. Fila de 10 na segunda e 12 na terça não significa 22 chamados distintos. Exercício: fila anterior 10, duas primeiras entradas, uma volta à pendência e quatro saídas conhecidas; sem outros movimentos, fila final 9.

## 4. Qualidade, proveniência e limites de inferência

Separar observação, hipótese e decisão. Observação: contador diminui em cinco chamados. Hipótese: problema no sistema ou extração. Decisão: preservar e sinalizar. Não transformar a hipótese em fato nem unicidade em prova de ordem temporal.

No caso Datarisk, pense no mesmo cuidado com informação futura: a resolução preenchida numa linha antiga não prova que esse valor estava disponível na época.

## 5. Modelagem dimensional para Power BI

Estudar fatos, dimensões, relações um-para-muitos e tabela calendário. Começar definindo o grão de cada tabela. Depois estudar contexto de filtro e medidas DAX. Prioridade e grupo podem variar no histórico: distinguir atributos finais de atributos na data da fotografia.

Referência primária: https://learn.microsoft.com/en-us/power-bi/guidance/star-schema

## Sequência recomendada

Na próxima manhã: estudar funções de janela e desenhar a consulta de último estado por chamado. Na manhã seguinte: estoque versus fluxo e leitura do dicionário de indicadores. Depois: esquema estrela usando as tabelas lógicas deste projeto. Avançar conforme conseguir explicar cada exercício, sem prazo obrigatório.

## Pergunta para entrevista

Como você percebeu que uma query tecnicamente correta poderia produzir um indicador errado? Responder com a diferença entre evento/chamado e com o exemplo de datas empatadas. Descrever a evidência, o risco para o indicador e a decisão tomada.
