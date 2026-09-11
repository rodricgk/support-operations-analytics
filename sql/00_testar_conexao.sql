-- Consulta somente de leitura. Executada no projeto separado pelo conector.
select
    current_database() as database_name,
    current_user as connected_role,
    current_setting('server_version') as postgres_version,
    1 as connection_test;
