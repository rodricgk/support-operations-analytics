# Primeira sessão: entender uma linha

Objetivo: distinguir o registro de um evento do registro de um incidente antes de calcular indicadores.

## Atividade

1. Obter o CSV na página oficial da UCI e preservar o original em data/raw.
2. Conferir dimensões, colunas e quantidade de identificadores number distintos.
3. Escolher um incidente com vários registros e examinar sua sequência de atualizações.
4. Comparar opened_at, sys_created_at, sys_updated_at, resolved_at e closed_at.
5. Identificar como ausências são representadas e quais campos variam no histórico.

## Perguntas para discutir

- O que uma linha representa?
- Quais campos são atributos do incidente e quais representam seu estado em determinado momento?
- Como identificar o último registro quando houver empates?
- Por que contar linhas superestima o volume de chamados?
- Um campo de resolução em um evento antigo descreve o que já era conhecido naquele momento?

## Entrega

Uma inspeção reproduzível e um resumo com evidências, dúvidas e decisões ainda pendentes. Nenhum dashboard é necessário nesta etapa.
