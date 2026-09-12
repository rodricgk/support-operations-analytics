# Support Operations Analytics

Projeto de portfólio em construção por Rodrigo Fernandes: análise de filas e prazos de incidentes de TI com Python, PostgreSQL no Supabase e Power BI.

## Objetivo

Ajudar um coordenador de suporte a entender a evolução da fila e identificar segmentos que concentram atendimentos demorados. O projeto também serve como percurso de estudo de modelagem e Power BI.

## Fonte

UCI — Incident management process enriched event log.
https://doi.org/10.24432/C57S4H

Amaral, C., Fantinato, M., & Peres, S. (2018). Licença da base: CC BY 4.0. Conferidas no CSV: 141.712 eventos de 24.918 incidentes anonimizados, com 36 colunas.

O projeto utiliza exclusivamente dados públicos; não contém dados do empregador do autor. As transformações serão documentadas. Este projeto não é afiliado à organização de origem da base.

## Estado atual

Histórico público investigado e modelo local implementado. Cinco tabelas preenchidas no Supabase: 141.712 eventos, 24.918 chamados, 170.645 fotografias, 355 datas e 355 resumos diários. Reconciliação Python versus SQL concluída: 14 testes passaram e cinco checksums conferiram. Ainda não há dashboard. A fila segue regras provisórias documentadas; nenhuma meta de SLA foi inventada.

## Executar a primeira inspeção (Windows / PowerShell)

Baixe o ZIP na [página oficial da UCI](https://archive.ics.uci.edu/dataset/498/incident+management+process+enriched+event+log), extraia e coloque `incident_event_log.csv` em `data/raw/`. Preserve o conteúdo original. O CSV não é versionado.

Ambiente usado: Python 3.14.5 e pandas 3.0.5.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/01_inspecionar_base.py
```

Se o ambiente já existe, execute apenas a última linha. A inspeção lê a base sem modificá-la e mostra o histórico de um chamado para discussão.

Segunda inspeção, sobre estados, datas e empates:

```powershell
.\.venv\Scripts\python.exe scripts/02_verificar_historico.py
```

Veja o [diagnóstico inicial](docs/qualidade-historico.md). A versão em notebook está em `notebooks/02_verificar_historico.ipynb`, para leitura e execução em um ambiente Jupyter com pandas instalado.

Terceira inspeção: `.\.venv\Scripts\python.exe scripts/03_validar_contador.py`.
Veja a [validação do contador](docs/validacao-contador.md) e o notebook `notebooks/03_validar_contador.ipynb`.

Quarta inspeção: `.\.venv\Scripts\python.exe scripts/04_investigar_inconsistencias.py`.
Veja a [investigação de inconsistências](docs/investigacao-inconsistencias.md). Extratos diagnósticos são gerados em `data/processed/investigacao_temporal`, fora do Git.

Quinta etapa: `.\.venv\Scripts\python.exe scripts/05_comparar_fila.py` (depende dos extratos do script 04).
Veja a [comparação de cenários da fila](docs/sensibilidade-fila.md), com regras provisórias, resultados e limitações. Trata-se de análise exploratória, não de um indicador final validado da operação.

Próxima fase: [dicionário de indicadores v0.1](docs/dicionario-indicadores.md) e [roteiro de estudo](docs/estudo-fundamentos.md). O dicionário especifica as métricas e os grãos; não implica que todos os cálculos já estejam implementados.

Sexta etapa: `.\.venv\Scripts\python.exe scripts/06_modelar_tabelas.py` (depende das etapas 04 e 05).
Gera eventos, chamados, fotografias e calendário locais, com [regras e validação do modelo](docs/modelo-local.md). A carga no banco foi concluída na etapa Supabase descrita abaixo.

Projeto Supabase separado criado e conexão pelo Codex validada. Veja [estado das conexões](docs/conexao-supabase.md). Python e Power BI ainda não possuem conexão direta configurada.

Etapa Supabase: carga concluída pelo painel e conector autenticados. Fotografias reconstruídas independentemente com `LEAD` em `sql/03_gerar_fotografias.sql`, com resultado equivalente ao Python. Veja [modelo SQL e reprodução](docs/modelo-supabase.md) e [evidência da validação](docs/validacao-supabase.json).

O script `07_carregar_supabase.py` oferece uma alternativa de carga por COPY; sua execução autenticada permanece pendente, por escolha do autor de adiar a senha local. O script `08_preparar_conferencia_integridade.py` gera os checksums dos CSVs para comparação no banco sem precisar de senha.

Primeiros indicadores de duração implementados: mediana 22,10 h e P90 381,55 h, sobre 23.362 chamados elegíveis. Consulte [população, recortes e limites](docs/indicadores-duracao.md), a consulta `sql/04_indicadores_duracao.sql` e o tutorial `notebooks/09_indicadores_duracao.ipynb`. Execute `scripts/09_indicadores_duracao.py` para reproduzir e conferir com a saída SQL salva. A duração é retrospectiva, em horas corridas; não é uma medida de SLA.

Idade da fila implementada em `scripts/10_idade_fila_diaria.py` e `sql/05_idade_fila_diaria.sql`: 710 resultados conferidos, cobrindo 355 dias e dois cenários. Veja [regras, exemplos e uso no Power BI](docs/idade-fila.md) e o tutorial `notebooks/10_idade_fila_diaria.ipynb`. Dias sem pendentes têm mediana em branco.

## Entregas previstas

Modelo de leitura para Power BI preparado: quatro views privadas, calendário de 731 dias e exportação local sem senha. Execute `scripts/11_preparar_power_bi.py` e siga o [guia de importação e relacionamentos](docs/modelo-power-bi.md). Nove verificações SQL passaram; o arquivo Power BI e a execução das consultas M ainda estão pendentes.

- Preparação reproduzível em Python.
- Estrutura e consultas SQL no Supabase.
- Relatório Power BI: visão gerencial e investigação operacional.
- Documentação das métricas, decisões e limitações.
- Imagens e roteiro de vídeo para apresentação no LinkedIn.

## Roteiro

Consulte [o plano](docs/plano.md), [a primeira sessão](docs/primeira-sessao.md) e [o diário de aprendizado](docs/diario.md).
