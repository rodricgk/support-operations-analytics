-- Camada de leitura privada. Aplicar ao projeto remoto via migration.
-- Não modifica as cinco tabelas nem cria credenciais de conexão.
create view analytics.bi_calendario with (security_invoker = true) as
with datas as (
    select data from analytics.calendario_fila
    union all select opened_at::date from analytics.chamados
    union all select resolved_at::date from analytics.chamados
), limites as (
    select date_trunc('year', min(data)::timestamp) as inicio,
        date_trunc('year', max(data)::timestamp) + interval '1 year - 1 day' as fim
    from datas
), dias as (
    select generate_series(inicio, fim, interval '1 day')::date as data from limites
)
select d.data, extract(year from d.data)::integer as ano,
    extract(month from d.data)::integer as mes,
    to_char(d.data, 'YYYY-MM') as ano_mes,
    exists(select 1 from analytics.calendario_fila f where f.data = d.data)
        as data_fotografia_elegivel
from dias d;

create view analytics.bi_chamados with (security_invoker = true) as
select c.*, c.opened_at::date as data_abertura, c.resolved_at::date as data_resolucao
from analytics.chamados c;

create view analytics.bi_fotografias with (security_invoker = true) as
select f.* from analytics.fotografias f;

create view analytics.bi_resumo_diario with (security_invoker = true) as
select r.* from analytics.resumo_diario r;

comment on view analytics.bi_calendario is 'Anos completos; a flag delimita as datas elegíveis para fotografias. Ausência de cobertura não é fila zero.';
comment on view analytics.bi_chamados is 'Um chamado. Relacionamento principal por data_resolucao; atributos finais, inclusive qualidade retrospectiva.';
comment on view analytics.bi_fotografias is 'Um chamado por data; prioridade e grupo no último estado observado daquele corte. Não relacionar a bi_chamados no modelo BI.';
comment on view analytics.bi_resumo_diario is 'Referência diária sem recortes de prioridade ou grupo; estoque não somável ao longo do tempo.';

revoke all on analytics.bi_calendario, analytics.bi_chamados,
    analytics.bi_fotografias, analytics.bi_resumo_diario from public, anon, authenticated;
