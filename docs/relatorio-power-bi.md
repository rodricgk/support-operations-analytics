# Relatório Power BI — Duração e Fila

## Estado em 12/09/2026

Relatório construído manualmente por Rodrigo Fernandes no Power BI Desktop, com importação local das quatro consultas M e configuração dos relacionamentos descritos em [modelo-power-bi.md](modelo-power-bi.md). As capturas e confirmações da sessão mostram as duas páginas funcionando. O PBIP foi inspecionado: nove fórmulas nativas conferidas por comparação textual, relacionamentos e metadados revisados. Não foram executadas novas consultas DAX por ferramenta nesta etapa.

Arquivo salvo e conferido em `power_bi/support-operations-analytics.pbix` (3.254.315 bytes). Contêiner ZIP íntegro; metadados das duas páginas inspecionados, conforme [evidência do arquivo](power-bi-arquivo-validacao.json). As fórmulas foram conferidas posteriormente no PBIP. A cópia PBIX foi salva novamente pelo autor após os ajustes do modelo; suas definições de relatório coincidem com as do PBIP. PDF de duas páginas e imagens finais salvos e revisados visualmente; veja [evidência da exportação](power-bi-pdf-validacao.json). Data/hora automática desativada e identificadores linha_csv/linha_csv_final ocultos e sem resumo, confirmados no PBIP.

## Medidas para reprodução

- [Duração: quatro medidas](../power_bi/medidas/duracao.dax), tabela inicial Chamados.
- [Fila: cinco medidas](../power_bi/medidas/fila.dax), tabela inicial Fotografias.

Os arquivos registram as fórmulas usadas na orientação da sessão; não são uma exportação do PBIX. Criar cada medida individualmente em Nova medida, preservando os nomes. Renomear para este visual altera apenas o texto exibido. Formatar contagens como inteiros, horas com duas casas e Data Referencia Fila como dd/MM/yyyy. Nos cartões, unidades de exibição Nenhum.

## Página Duração

Filtro: Calendario[ano_mes], rotulado Mês de resolução. Relação ativa com Chamados[data_resolucao]. Sem filtro de mês, Total de chamados inclui os 1.556 registros sem resolução informada; em um mês selecionado esses registros ficam fora. A opção em branco representa esses registros nesta base.

| Rótulo do cartão | Medida |
|---|---|
| Total de chamados | Total de Chamados |
| Chamados com duração válida | Chamados Elegiveis Duracao |
| Duração mediana (h) | Mediana Duracao Horas |
| P90 da duração (h) | P90 Duracao Horas |

Mediana e P90 usam apenas elegivel_duracao = TRUE e são recalculados sobre chamados individuais. O total não é média dos resultados mensais ou das prioridades. População vazia permanece em branco. P90 é o percentil 90 com interpolação linear; não é meta nem prazo de SLA.

Gráfico por mês de resolução em ordem crescente, com Mediana (h) e P90 (h), e quantidade elegível na dica de ferramenta. Tabela por Chamados[priority_final], com total, elegíveis, mediana e P90; total mantido. Prioridade final não representa necessariamente a prioridade durante todo o atendimento.

## Página Fila

Filtro: Calendario[data], intervalo entre datas. O gráfico usa Fila Diaria e a dica de ferramenta Mediana Idade Fila Horas. As medidas diárias exigem uma única data elegível; não somam estoques no total.

| Rótulo do cartão | Medida |
|---|---|
| Pendentes na data de referência | Fila Fim do Periodo |
| Idade mediana dos pendentes (h) | Mediana Idade Fim do Periodo Horas |
| Data da fotografia | Data Referencia Fila |

Data de referência é a última data elegível no contexto selecionado, mesmo se a fila for zero. Cobertura elegível: 29/02/2016 a 17/02/2017. Fora dela, branco significa ausência de cobertura. Em dia elegível sem pendentes, fila zero e idade em branco. Não procurar a última data com fila positiva.

Fila conta linhas pendentes em Fotografias, cujo grão é chamado por data. Idade considera apenas idade_valida e mede horas corridas desde a abertura original até o corte. Reabertura não reinicia essa idade.

Tabela de prioridades usa Fotografias[priority], atributo histórico, com as medidas de fim do período. Detalhamento diário usa data, fila e idade; datas curtas em ordem decrescente, sem total. Selecionar uma linha pode filtrar os demais visuais, inclusive a data dos cartões; limpar a seleção para retornar ao intervalo completo.

## Conferências registradas na sessão

Valores abaixo foram observados em capturas ou confirmados pelo autor. As referências gerais de duração e fila já haviam sido reconciliadas em Python/SQL; isto não substitui uma auditoria automática do PBIX.

| Recorte | Resultado observado |
|---|---|
| Duração, todos | 24.918 total; 23.362 elegíveis; mediana 22,10 h; P90 381,55 h |
| Resolução março/2016 | 6.878 elegíveis; mediana 44,13 h; P90 306,97 h |
| Resolução dezembro/2016 | 54 elegíveis; mediana 3.087,97 h; P90 6.282,02 h |
| Mês em branco | 1.556 total; elegíveis e durações em branco |
| Fila em 16/03/2016 | 1.869 pendentes; mediana 157,45 h |
| Fila, prioridade Low em 16/03/2016 | 98 pendentes; mediana 321,36 h; data preservada |
| Fila em 14/02 e 17/02/2017 | Zero; idade em branco |
| Fila em 18/02/2017 | Branco, fora da cobertura elegível |
| Intervalo até 31/12/2017 | Referência 17/02/2017; fila zero; idade em branco |

O recorte Low foi conferido visualmente, sem nova reconciliação independente específica. Na página Duração, as quatro prioridades e o total aparecem integralmente na captura final, após redução do preenchimento das linhas.

## Apresentação e limites

Duas páginas 1280 × 720, título e filtro no topo, cartões com números em fonte 32, fundos claros e linhas azuis. Fila apresenta evolução e prioridades lado a lado, detalhe abaixo; Duração apresenta gráfico mensal e tabela abaixo. Os rótulos dos visuais foram simplificados, preservando os nomes das medidas.

Base pública histórica e estática: não representa monitoramento atual. A queda final da fila e o aumento das durações em meses com poucos casos não demonstram melhora ou piora operacional. Há limitações de cobertura e seleção dos chamados resolvidos. Não existem metas contratuais ou calendário de horas úteis nesta análise. Consulte [duração](indicadores-duracao.md), [idade da fila](idade-fila.md) e [dicionário](dicionario-indicadores.md).

## Pendências de entrega

1. PBIX atualizado a partir do projeto revisado; integridade e definições do relatório conferidas.
2. Exportação visual concluída: [PDF](../power_bi/support-operations-analytics.pdf), [Duração](imagens/duracao.png) e [Fila](imagens/fila.png). Duração usa todos os meses; Fila usa 01/01/2016 a 16/03/2016. O PDF mostra somente as linhas visíveis do detalhamento, não o histórico completo.
3. Fórmulas, calendário e os dois identificadores técnicos conferidos no PBIP; evidência em power-bi-modelo-validacao.json.
4. Preparar a apresentação do portfólio após incorporar esses artefatos. Conexão direta ao Supabase permanece uma etapa separada.

## Atualização: calendário automático removido

Conferido no PBIP salvo: Data/hora automática desativada, somente Calendario, Chamados, Fotografias e ResumoDiario, com os quatro relacionamentos planejados. As nove fórmulas nativas foram comparadas com a referência textual e coincidem, ignorando espaços. Esta conferência estática resolve as pendências anteriores de leitura das fórmulas e calendário automático; não executa novos cálculos DAX. Evidência em power-bi-modelo-validacao.json. Os identificadores Chamados[linha_csv_final] e Fotografias[linha_csv] também foram conferidos: ocultos e com summarizeBy: none.

## Abrir e reproduzir o projeto PBIP

Abra `power_bi/support-operations-analytics.pbip` no Power BI Desktop. As pastas Report e SemanticModel precisam permanecer ao lado desse arquivo. O parâmetro PastaDados contém o caminho desta máquina: ajuste-o no Power Query para sua pasta data/processed/power_bi após gerar os CSVs pelo script 11. Em um clone sem cache local, será necessário atualizar os dados. Os caches e preferências locais .pbi são ignorados no Git. Para visualizar os dados já incorporados, use a cópia PBIX.
