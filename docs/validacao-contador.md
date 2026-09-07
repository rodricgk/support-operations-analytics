# Validação do contador de atualizações

## Pergunta

sys_mod_count pode desempatar eventos com o mesmo horário? Inspeção da base inteira: 141.712 eventos, 24.918 chamados. Original preservado.

## Método

Converter contador para número e horário para datetime. Para cada chamado e minuto, comparar o menor contador daquele minuto com o maior observado em todos os minutos anteriores. Não ordenar pelo contador e usar essa própria ordenação como evidência de crescimento.

## Resultados

- Contadores ausentes, não numéricos, negativos ou fracionários: zero.
- Datas de atualização ausentes ou inválidas: zero.
- 11 grupos chamado + horário apresentam contador menor que um valor de horário anterior, envolvendo 5 chamados (aproximadamente 0,020% dos chamados).
- 5 pares chamado + contador aparecem em horários distintos, envolvendo 5 chamados. Não presumir que são o mesmo conjunto sem confrontar os identificadores.
- Chamado + horário + contador numérico: zero combinações repetidas.

Exemplo INC0000130: em 29/02/2016 às 07:27 o contador é 2; às 09:59 é 1; em 01/03/2016 às 14:13 volta a ser 2. Os dois primeiros eventos têm estado New. A causa não foi determinada.

## Interpretação

Confiança alta nas contagens observadas. A chave composta permite ordenação determinística, mas isso não comprova a ordem real de eventos dentro de um minuto. A monotonicidade global do contador falha em casos localizados. Há risco para reconstrução histórica; não corrigir horários ou contadores por suposição.

Próxima decisão a discutir: manter todos os registros e sinalizar os chamados com inconsistências temporais. Antes do indicador de fila, confrontar essas exceções com atualizações anteriores à abertura e analisar o efeito da regra candidata. Nenhuma exclusão ou regra definitiva foi aplicada.

Reprodução: scripts/03_validar_contador.py ou notebooks/03_validar_contador.ipynb. Notebook sem resultados embutidos; o script foi executado na base completa.
