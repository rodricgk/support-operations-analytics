# Diagnóstico inicial do histórico

Escopo: verificar se é possível identificar o último evento por chamado em uma data de corte. Unidade: evento registrado no CSV. Inspeção de 141.712 linhas e 24.918 chamados; nenhuma transformação foi aplicada ao original.

## Evidências

| Checagem | Resultado | Implicação |
|---|---|---|
| Abertura e atualização | Sem ausências ou falhas de conversão | Permitem iniciar a análise temporal; completude não prova consistência |
| Intervalo de atualizações | 29/02/2016 01:23 a 18/02/2017 15:00 | Recorte observado; não prova cobertura integral da operação |
| Resolução ausente | 3.141 linhas (2,22%) | Investigar por chamado antes de calcular duração |
| Linhas exatamente iguais | Nenhuma | A repetição do identificador não é duplicidade integral |
| Chamado + horário com empate | 13.627 grupos, 27.745 linhas (19,58%), 9.318 chamados (37,39%) | Alta relevância: apenas o horário não determina o último evento |
| Empates com estados diferentes | 7.556 grupos | Podem alterar a classificação de pendência |
| Chamado + horário + sys_mod_count | Nenhuma combinação repetida | Chave candidata única nesta extração; ordem temporal ainda não validada |
| Estado -100 | 5 linhas | Sem interpretação confirmada; não mapear automaticamente para aberto ou fechado |
| Atualização anterior à abertura | 5 linhas | Exceções temporais a investigar; causa desconhecida |

Contagens e taxas calculadas pelo script 02. Taxas de linhas usam 141.712; taxa de chamados usa 24.918. As duas ocorrências de cinco linhas não foram verificadas como sendo os mesmos registros.

## Exemplo para estudo

INC0000047 em 01/03/2016 09:14: Active com sys_mod_count=5 e Awaiting User Info com sys_mod_count=6. A precisão de minuto pode contribuir para empates, mas não confirma sua causa em toda a base.

## Decisões e pendências

- Não eliminar eventos só porque number se repete.
- Não usar a ordem física do CSV como regra de desempate.
- Investigar a consistência do contador antes de usar o maior valor como evento posterior.
- Confirmar os estados que representam fila; o código -100 permanece desconhecido.
- Horários sem fuso informado: não converter para horário de Brasília por suposição.
- Não produzir ainda um indicador de fila histórica: unicidade da chave não comprova histórico completo ou semanticamente consistente.

Confiança alta nas contagens observadas; causas e regras de negócio ainda em investigação. Material de estudo, não uma auditoria concluída.
