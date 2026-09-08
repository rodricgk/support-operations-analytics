# Sensibilidade da fila diária às exceções temporais

## Objetivo e regra provisória

Comparar a fila observada no histórico publicado, incluindo todos os chamados versus retirando os seis chamados sinalizados na investigação 04. Nenhum registro original foi alterado ou removido. A retirada vale somente para o segundo cenário.

Unidade: chamado no fim do dia. Para cada data, selecionar eventos com sys_updated_at estritamente anterior à meia-noite seguinte, ordenar por chamado, horário e sys_mod_count numérico e escolher o último evento de cada chamado. Não utilizar datas futuras de resolução ou fechamento para inferir estados anteriores. Nenhuma conversão de fuso foi aplicada, pois o fuso de origem não está confirmado.

Classificação operacional provisória:

- Pendência de resolução: New, Active, Awaiting User Info, Awaiting Vendor, Awaiting Problem e Awaiting Evidence.
- Fora da fila de resolução: Resolved e Closed.
- Qualquer outro estado: desconhecido, contabilizado separadamente; não considerado encerrado.

Não usar o booleano active como sinônimo de pendência de resolução. Espera permanece na fila nesta definição, o que não equivale a contar esforço de trabalho nem tempo de SLA.

## Resultados observados

355 datas, de 29/02/2016 a 17/02/2017. O último dia da fonte, 18/02/2017, foi excluído porque o último evento disponível é às 15h. Essa exclusão não comprova completude dos dias anteriores.

| Data | Todos os chamados | Sem os seis sinalizados | Diferença | Diferença / fila com todos |
|---|---:|---:|---:|---:|
| 29/02/2016 | 163 | 158 | 5 | 3,07% |
| 01/03/2016 | 378 | 373 | 5 | 1,32% |
| 02/03/2016 | 644 | 639 | 5 | 0,78% |
| 03/03/2016 | 788 | 787 | 1 | 0,13% |
| 04/03/2016 | 940 | 939 | 1 | 0,11% |

Nos outros 350 dias não há diferença entre os dois cenários para essa métrica. Existem seis fotografias diárias com um chamado em estado desconhecido, nos dois cenários. O máximo observado de desconhecidos no fim do dia é um. Isso impede tratar a contagem de estados conhecidos como classificação completa de todos os chamados.

## Interpretação e decisão

A diferença mede a sensibilidade à exclusão integral dos seis chamados, não a quantidade de registros errados nem uma estimativa da fila verdadeira. Retirar um chamado também retira seus eventos potencialmente válidos. Os 3,07% são uma comparação relativa no primeiro dia, não uma taxa de erro da base.

Manter os registros e as sinalizações é a decisão adotada. O cenário sem sinalizados permanece disponível como comparação. Não foi definida uma correção da fonte, uma exclusão definitiva ou uma validação final do dashboard.

Limites: histórico inicial anterior ao primeiro evento de cada chamado não é reconstruído; recorte da fonte pode não representar toda a operação; a ordenação por contador continua sendo hipótese dentro de horários empatados; a data de abertura não é usada para inventar um evento anterior ao primeiro registro. Esta análise diária não mede efeitos intradiários, sobre SLA, tempos de resolução ou recortes por grupo.

## Verificação e reprodução

Script 05 executado na base inteira. Exemplo controlado confirma corte de meia-noite, ausência de informação futura, reabertura, desempate pelo contador e preservação de estado desconhecido. Checada unicidade da chave composta e diferença diária entre zero e o total de chamados sinalizados.

```powershell
.\.venv\Scripts\python.exe scripts/04_investigar_inconsistencias.py
.\.venv\Scripts\python.exe scripts/05_comparar_fila.py
```

Arquivo gerado: data/processed/sensibilidade_fila/comparacao_diaria.csv. Notebook correspondente: notebooks/05_comparar_fila.ipynb. Artefatos processados permanecem fora do Git, mas são reproduzíveis pelo código versionado.
