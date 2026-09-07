# Plano de construção e estudo

## Público e pergunta

Público: coordenação de suporte. Pergunta: como a fila evolui e quais segmentos concentram atendimentos mais demorados?

## Etapas

1. Inspecionar a base: granularidade, tipos, ausências, datas, estados e cobertura temporal.
2. Definir métricas: população, fórmula, calendário, exceções e limitações.
3. Preparar dados em Python e modelar o histórico no PostgreSQL/Supabase.
4. Investigar com SQL e produzir resultados de referência.
5. Construir duas páginas no Power BI, aprendendo Power Query, relacionamentos, calendário e DAX.
6. Reconciliar números e preparar a apresentação pública.

## Indicadores candidatos

Entradas, resoluções, pendências históricas, idade da fila, mediana e percentil 90 do tempo de resolução, reaberturas e reatribuições. SLA depende de validação do significado de made_sla.

Não assumir que linhas são incidentes, que reatribuição equivale a erro ou que duração representa esforço trabalhado. Não inventar horários úteis, metas de SLA ou nomes para categorias anonimizadas. Não descartar linhas idênticas sem investigar sua origem. O recorte da base pode limitar a reconstrução da fila e a generalização dos achados.

## Forma de trabalho

Construção acompanhada, por marcos, sem prazo fixo. A cada etapa: explicar a pergunta, discutir opções, realizar uma atividade prática, revisar o resultado e registrar o aprendizado. Decisões delegadas também devem ser explicadas. Priorizar o aprendizado de Power BI, aproveitando o domínio intermediário/avançado declarado em Python e SQL.

## Controle de versão

Repositório público previsto: support-operations-analytics. Fazer commits de avanços reais e push ao concluir sessões, quando houver autenticação. Não alterar datas para simular atividade. Verificar a identidade do autor antes do primeiro commit. Não versionar credenciais ou ambientes locais.

## Conclusão da primeira versão

- SQL e Power BI apresentam números reconciliados.
- Processo reproduzível a partir das instruções.
- Fonte, transformações e limitações documentadas.
- Autor consegue explicar uma métrica, uma decisão de modelagem e um achado.

## Fora da primeira versão

Machine learning, aplicação web, automações de produção e atualização agendada. Revisitar apenas se houver uma necessidade demonstrada.
