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

- Criar as tabelas SQL e carregar os dados públicos.
- Configurar a conexão direta de carga em Python e a conexão de leitura no Power BI.
- Para clientes locais IPv4, usar os dados exatos de Session pooler apresentados em Connect no painel. Não adivinhar o host do pooler.
- Configurar credenciais locais fora do Git e validar as conexões antes de declarar a carga pronta. Nenhuma senha foi obtida ou alterada nesta etapa.

Conectar o Codex ao Supabase permite executar SQL pelo conector, mas não autentica automaticamente programas externos. A primeira conexão foi apenas um teste de leitura; os CSVs continuam locais.

Referência: https://supabase.com/docs/guides/database/connecting-to-postgres
