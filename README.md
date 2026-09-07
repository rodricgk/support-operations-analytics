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

Primeira inspeção local implementada. Não há banco provisionado ou dashboard. A viabilidade de fila histórica e SLA depende da inspeção dos registros.

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

## Entregas previstas

- Preparação reproduzível em Python.
- Estrutura e consultas SQL no Supabase.
- Relatório Power BI: visão gerencial e investigação operacional.
- Documentação das métricas, decisões e limitações.
- Imagens e roteiro de vídeo para apresentação no LinkedIn.

## Roteiro

Consulte [o plano](docs/plano.md), [a primeira sessão](docs/primeira-sessao.md) e [o diário de aprendizado](docs/diario.md).
