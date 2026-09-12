-- Somente leitura. Verifica calendário, projeções e privilégios das quatro views.
with verificacoes as (
    select 'calendario_unico_continuo' as teste,
        count(*) = count(distinct data)
        and count(*) = max(data) - min(data) + 1 as passou
    from analytics.bi_calendario
    union all
    select 'anos_completos', to_char(min(data), 'MM-DD') = '01-01'
        and to_char(max(data), 'MM-DD') = '12-31' from analytics.bi_calendario
    union all
    select 'datas_elegiveis_identicas', not exists (
        (select data from analytics.bi_calendario where data_fotografia_elegivel
         except select data from analytics.calendario_fila)
        union all
        (select data from analytics.calendario_fila
         except select data from analytics.bi_calendario where data_fotografia_elegivel))
    union all
    select 'cobertura_datas', not exists (
        select data from (
            select data_abertura as data from analytics.bi_chamados
            union select data_resolucao from analytics.bi_chamados
            union select data from analytics.bi_fotografias
            union select data from analytics.bi_resumo_diario
        ) d where data is not null and not exists (
            select 1 from analytics.bi_calendario c where c.data = d.data))
    union all
    select 'chamados_preservados',
        (select count(*) from analytics.bi_chamados) = (select count(*) from analytics.chamados)
        and not exists (
            select 1 from analytics.bi_chamados b join analytics.chamados c using(number)
            where (to_jsonb(b) - 'data_abertura' - 'data_resolucao') is distinct from to_jsonb(c)
                or b.data_abertura is distinct from c.opened_at::date
                or b.data_resolucao is distinct from c.resolved_at::date)
    union all
    select 'fotografias_preservadas', not exists (
        (select * from analytics.bi_fotografias except all select * from analytics.fotografias)
        union all
        (select * from analytics.fotografias except all select * from analytics.bi_fotografias))
    union all
    select 'resumo_preservado', not exists (
        (select * from analytics.bi_resumo_diario except all select * from analytics.resumo_diario)
        union all
        (select * from analytics.resumo_diario except all select * from analytics.bi_resumo_diario))
    union all
    select 'quatro_views_security_invoker', count(*) = 4
        and bool_and(coalesce('security_invoker=true' = any(c.reloptions), false))
    from pg_class c join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'analytics' and c.relname in (
        'bi_calendario', 'bi_chamados', 'bi_fotografias', 'bi_resumo_diario') and c.relkind = 'v'
    union all
    select 'sem_acesso_anon_authenticated', not bool_or(
        has_table_privilege(r.papel, 'analytics.' || v.nome, 'select')
        or has_schema_privilege(r.papel, 'analytics', 'usage'))
    from (values ('anon'), ('authenticated')) r(papel)
    cross join (values ('bi_calendario'), ('bi_chamados'), ('bi_fotografias'), ('bi_resumo_diario')) v(nome)
)
select teste, passou from verificacoes order by teste;
