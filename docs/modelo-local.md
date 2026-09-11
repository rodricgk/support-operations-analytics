# Modelo analítico local — primeira versão

Implementado em 11/09/2026 pelo script 06. Preparação local para a etapa de SQL e Power BI. Nenhum banco foi criado ou alterado nesta etapa.

## Tabelas e granularidade

| Arquivo em data/processed/modelo | Uma linha representa | Linhas geradas | Uso |
|---|---|---:|---|
| eventos.csv | Um evento original, identificado por linha_csv | 141.712 | Histórico, transições e rastreabilidade |
| chamados.csv | Um chamado (number único) | 24.918 | Datas informadas e atributos finais |
| fotografias.csv | Um chamado pendente ou desconhecido numa data de corte | 170.645 | Fila, idade e segmentação histórica |
| calendario_fila.csv | Uma data de fotografia | 355 | Eixo contínuo, inclusive dias sem fila |
| resumo_diario.csv | Totais e denominador de chamados conhecidos numa data | 355 | Reconciliação e proporção de desconhecidos |

170.645 fotografias não são chamados distintos: o mesmo chamado pode aparecer em vários dias. Não somar fotografias como se fossem incidentes únicos. Fotografias excluem estados finais; o resumo mantém o denominador de todos os chamados já conhecidos, inclusive finalizados.

## Regras implementadas

### Eventos

Todas as linhas da fonte são preservadas, com projeção dos campos necessários à análise. Datas de atualização e contadores são convertidos; textos originais desses dois campos continuam disponíveis. Marcadores '?' e vazios nas categorias, prioridades e grupos viram ausências na cópia analítica, sem inventar nomes. Contadores de reabertura e transferência são acumulados na fonte: não somá-los entre eventos para contar ocorrências.

linha_csv aponta a linha original, com cabeçalho na linha 1. Essa identidade é específica desta versão do arquivo, cujo SHA-256 é gravado em validacao.json. Mudança da extração exige nova identificação da fonte; número de linha não é um identificador global do sistema de origem.

As três flags investigadas são propagadas por chamado: regressao_contador, evento_antes_abertura e contador_reutilizado. sinalizado_temporal é a união delas. Os seis chamados seguem presentes. Flags são conhecimento retrospectivo da qualidade, não atributos que alegamos estarem disponíveis no sistema em cada data histórica.

### Chamados

Atributos do último registro recebem sufixo _final. Por exemplo, assignment_group_final não deve substituir o grupo histórico de uma fotografia.

opened_at e resolved_at são consolidados apenas quando há um único valor de data válido entre os registros não ausentes. Conflitos ou formatos inválidos tornam o campo consolidado ausente e geram flag. Ausência total continua ausente. A função de consolidação foi verificada com exemplos controlados para repetição válida, conflito, ausência e formato inválido.

duracao_resolucao_horas segue o dicionário: tempo corrido de opened_at até resolved_at, apenas quando a duração é não negativa e o estado final é Resolved ou Closed. Encontrados 23.362 chamados elegíveis e 1.556 não elegíveis; zero durações negativas. Ausentes não viram zero. Percentis, recortes por período e comparações de duração ainda não foram publicados como indicadores finais.

### Fotografias

Aplicada a mesma ordem candidata e o mesmo corte da etapa 05, primeiro reduzindo o histórico ao último evento por chamado em cada dia. Isso preserva o resultado do corte diário; não é um novo tratamento dos casos inconsistentes.

Cada fotografia preserva grupo, prioridade, categoria, estado, horário e linha de origem do último evento disponível até o corte. Não usa atributos finais para representar o passado. Idade é a diferença entre a meia-noite seguinte e a abertura informada, apenas para pendentes com idade válida. Idade de estado desconhecido fica ausente. Não houve fotografia pendente com idade inválida nesta execução.

O calendário desta etapa cobre 29/02/2016 a 17/02/2017. 18/02/2017 é parcial no histórico e não recebe fotografia de fim do dia. Para analisar outras datas, como resoluções no último dia, será preciso ampliar o calendário geral e marcar quais datas são elegíveis para fotografia. Não usar implicitamente o limite deste calendário para eliminar chamados ou resoluções.

## Validação realizada

- Fonte bruta preservada, verificada por SHA-256 antes e depois.
- Nenhuma perda ou multiplicação das 141.712 linhas de eventos na junção de flags (many-to-one).
- Unicidade de chamados e de chamado + data nas fotografias.
- Todos os eventos e fotografias referenciam chamados existentes; fotografias apontam linhas de origem existentes.
- Nenhuma fotografia utiliza evento posterior ao corte.
- Quatro contagens diárias (pendentes e desconhecidos, com e sem sinalizados) reconciliadas com a etapa 05 em todas as 355 datas.

Essas verificações confirmam consistência com as regras provisórias. Não comprovam que a fonte retrate todo o histórico real nem removem as ambiguidades já documentadas.

## Reproduzir

Com os resultados das etapas 04 e 05 disponíveis:

```powershell
.\.venv\Scripts\python.exe scripts/06_modelar_tabelas.py
```

Arquivos processados são reproduzíveis e ficam fora do Git. Código, regras e resultados de validação resumidos ficam versionados. A saída validacao.json registra contagens e hash da fonte.

## Próximo passo

Traduzir as tabelas e suas chaves para SQL e preparar a carga no projeto separado do Supabase. No Power BI, evitar relacionar fatos diretamente: calendário e dimensões devem filtrar cada fato segundo a referência temporal apropriada. A comparação Python versus SQL será a próxima verificação de consistência.
