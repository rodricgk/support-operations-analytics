# Modelo SQL e carga no Supabase

## Estado verificado em 11/09/2026

Projeto: support-operations-analytics (cgvfubhikahizyydpmst), esquema analytics.

As cinco tabelas foram criadas pela migração remota criar_modelo_analitico.
sql/01_criar_modelo.sql registra o SQL aplicado; não é um arquivo gerado pela CLI.
Não executar novamente em um banco que já contém esse esquema.

| Tabela | Chave primária | Esperado no modelo | Verificado no banco |
|---|---|---:|---:|
| calendario_fila | data | 355 | 355 |
| chamados | number | 24.918 | 24.918 |
| eventos | linha_csv | 141.712 | 141.712 |
| fotografias | data + number | 170.645 | 170.645 |
| resumo_diario | data | 355 | 355 |

Carga completa e reconciliação concluídas. Os 14 testes em sql/02_validar_carga.sql passaram e os checksums das cinco tabelas coincidiram com os CSVs. Evidência detalhada em validacao-supabase.json.
Os totais desta tabela são o registro desta etapa, não um monitor em tempo real.

## O que as chaves garantem

Uma chave primária impede duplicação no grão escolhido. Em fotografias, um chamado pode aparecer em vários dias, mas só uma vez na mesma data.

A chave estrangeira liga cada evento a um chamado existente. Uma fotografia referencia simultaneamente a linha original e o número do chamado, impedindo que use um evento de outro chamado. Datas de fotografia e resumo precisam existir no calendário.

linha_csv continua sendo identidade desta extração, não um identificador universal de evento. O arquivo bruto e seu hash continuam sendo a referência de origem.

linha_csv_final é conferida pela consulta de reconciliação após a carga. Não criamos uma chave estrangeira circular que exigisse importar eventos antes de chamados e chamados antes de eventos.

CHECKs validam regras locais, como mês entre 1 e 12, duração elegível não negativa e fotografia anterior à meia-noite seguinte. Eles não corrigem a história: as seis exceções temporais continuam sinalizadas e preservadas.

Datas usam timestamp without time zone, pois a fonte não informa o fuso. Medidas em horas usam double precision; a conferência aceita diferença de até 0,000001 hora para arredondamento numérico.

## Como esta carga foi realizada

Calendário e chamados foram importados pelo painel. A carga de eventos começou pelo painel e foi completada em lotes pelo conector SQL autenticado, preservando chaves existentes. O resumo diário foi importado do CSV de referência por um lote SQL.

As fotografias foram reconstruídas no próprio banco por sql/03_gerar_fotografias.sql. A função LEAD encontra a próxima atualização de cada chamado. Para a fotografia de fim do dia, um evento vale a partir de sua data até antes da data da próxima atualização. Eventos substituídos no mesmo dia não aparecem no corte diário. O último evento de um chamado continua válido até o fim do calendário.

Essa formulação também trata o limite da meia-noite: uma atualização exatamente à meia-noite seguinte não altera a fotografia do dia anterior. Foram verificados exemplos controlados desse limite e de dois eventos no mesmo horário com contadores diferentes.

O resultado foi conferido com a fotografia já calculada em Python. Não foram criadas senhas nem configurado acesso direto do Python. O autor preferiu adiar essa configuração.

## Alternativa: carregar por Python

O script abaixo está preparado e teve os arquivos e a sintaxe verificados localmente, mas sua execução autenticada ainda não foi testada. Não é necessário executá-lo para usar a carga já concluída.

Driver instalado no ambiente virtual: psycopg[binary] 3.3.5. Os parâmetros do Session pooler foram lidos em Connect no painel e estão em config/supabase-project.json, sem senha.

1. Defina e guarde a senha do banco no painel do Supabase. Ela é diferente do login via GitHub.
2. Espere qualquer importação do painel terminar. Não execute duas cargas ao mesmo tempo.
3. No terminal do VS Code, aberto na raiz do repositório, execute:

```powershell
.\.venv\Scripts\python.exe scripts/07_carregar_supabase.py
```

Digite a senha apenas quando o terminal solicitar. Não aparecem caracteres enquanto você digita; a senha não é gravada no projeto.

Em outro ambiente, instale antes as dependências de requirements.txt. Para conferir apenas os arquivos, sem conexão:

```powershell
.\.venv\Scripts\python.exe scripts/07_carregar_supabase.py --verificar-arquivos
```

## Como o script funciona

- Confere o hash da fonte, as contagens e a unicidade das chaves dos cinco CSVs.
- Abre conexão com SSL e bloqueia alterações concorrentes nas tabelas durante a transação.
- Usa COPY para carregar cada CSV numa tabela temporária com os mesmos tipos.
- Compara todos os campos das linhas já existentes com o CSV. Se houver divergência, interrompe sem substituir os dados.
- Insere somente linhas ausentes, na ordem calendário, chamados, eventos, fotografias e resumo.
- Executa sql/02_validar_carga.sql e confirma a transação apenas se todos os testes passarem.

Isso permite retomar a carga já iniciada pelo painel. Executar de novo com os mesmos arquivos não deve duplicar linhas. Uma falha dentro da transação reverte as inserções daquela execução; os dados que já existiam permanecem.

O relatório local data/processed/modelo/carga_supabase.json é escrito após a confirmação da transação. Contém hashes, contagens, novas linhas e resultados, sem credenciais. Fica fora do Git.

## Verificações e limites

Já executados:
- Criação das cinco tabelas e conferência de RLS e privilégios.
- Testes controlados de duplicação de chave, CHECK de mês e chave estrangeira: os três erros foram rejeitados e a transação foi revertida.
- Conferência local dos cinco arquivos pelo script 07: contagens e chaves passaram, fonte preservada.
- Reconciliação integral de filas, denominadores, atributos históricos, durações e idades: 14 testes passaram.
- Checksums de calendário, chamados, eventos, fotografias e resumo coincidiram com os CSVs. O script 08 gera a consulta a partir dos arquivos locais; MD5 serve apenas como checksum de transferência. As colunas duracao_resolucao_horas e idade_horas são verificadas separadamente com tolerância de 0,000001 hora.
- Teste transacional de repetição da inserção do calendário não gerou novas linhas; teste revertido.

Ainda pendentes:
- Execução do COPY pelo Python autenticado e teste completo de repetição desse script, caso o autor escolha essa alternativa.
- Conexão de leitura para o Power BI.

Os verificadores do Supabase retornaram informações de RLS sem políticas nas cinco tabelas e de índice ainda sem uso. Nesta etapa, o acesso é administrativo: não há políticas públicas nem privilégios de uso do esquema para anon/authenticated. A política de leitura do Power BI será definida quando criarmos seu usuário de leitura.

Referências:
- [Importar dados no Supabase](https://supabase.com/docs/guides/database/import-data).
- [Conexões PostgreSQL](https://supabase.com/docs/guides/database/connecting-to-postgres).
- [COPY com Psycopg](https://www.psycopg.org/psycopg3/docs/basic/copy.html).
- [Aviso de RLS sem políticas](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).
- [Aviso de índice sem uso](https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index).
