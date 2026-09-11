# Projeto Supabase e estado das conexões

Criado em 11/09/2026, com autorização do autor.

- Nome: support-operations-analytics.
- Organização confirmada: rodricgk's Org (plano Free).
- Região: São Paulo, sa-east-1.
- Referência: cgvfubhikahizyydpmst.
- Painel: https://supabase.com/dashboard/project/cgvfubhikahizyydpmst
- Custo informado pelo conector na criação: 0 por mês. Não é uma garantia de custo zero para alterações futuras de plano ou recursos.
- Status verificado: ACTIVE_HEALTHY.

## O que já está conectado

O Codex acessou o novo projeto pelo conector autenticado do Supabase e executou sql/00_testar_conexao.sql. Retorno: database_name=postgres, connected_role=postgres, postgres_version=17.6, connection_test=1.

config/supabase-project.json identifica o destino deste repositório e não contém credenciais. Ele documenta o vínculo; não configura sozinho uma conexão direta do Python ou do Power BI, nem equivale a executar supabase link na CLI.

## O que ainda falta

- A carga já foi concluída nas cinco tabelas e reconciliada. Veja modelo-supabase.md e validacao-supabase.json.
- Configurar a conexão direta de carga em Python e a conexão de leitura no Power BI.
- Session pooler conferido em Connect: aws-0-sa-east-1.pooler.supabase.com, porta 5432, banco postgres, usuário postgres.cgvfubhikahizyydpmst. Parâmetros salvos sem senha; script 07 preparado, mas conexão Python autenticada ainda pendente.
- Configurar credenciais locais fora do Git e validar as conexões antes de declarar a carga pronta. Nenhuma senha foi obtida ou alterada nesta etapa.

Conectar o Codex ao Supabase permite executar SQL pelo conector, mas não autentica automaticamente programas externos. O modelo foi preenchido pelo painel e pelo conector. As fotografias foram reconstruídas em SQL e comparadas com o Python. Os CSVs originais continuam locais; nenhuma senha foi criada, obtida ou alterada por esta automação.

Referência: https://supabase.com/docs/guides/database/connecting-to-postgres
