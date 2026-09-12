-- Um resultado por data e cenário, inclusive quando não há pendentes.
-- Horas corridas desde a abertura original até a meia-noite seguinte.
with cenarios(cenario, excluir_sinalizados) as (
    values ('todos', false), ('sem_sinalizados', true)
), base as (
    select d.data, s.cenario, f.number, f.classe_estado,
        f.opened_at,
        (f.classe_estado = 'pendente' and f.opened_at is not null
            and f.opened_at <= d.data + interval '1 day') as elegivel,
        extract(epoch from (d.data + interval '1 day' - f.opened_at)) / 3600.0 as idade_calculada
    from analytics.calendario_fila d
    cross join cenarios s
    left join analytics.fotografias f
        on f.data = d.data
        and (not s.excluir_sinalizados or not f.sinalizado_temporal)
)
select data::text as data, cenario,
    count(number) filter(where classe_estado = 'pendente') as n_fila,
    count(number) filter(where elegivel) as n_elegivel,
    count(number) filter(where classe_estado = 'pendente' and not elegivel) as n_idade_invalida,
    count(number) filter(where classe_estado = 'desconhecido') as n_desconhecido,
    percentile_cont(0.5) within group(order by idade_calculada)
        filter(where elegivel) as mediana_idade_horas
from base
group by data, cenario
order by data, cenario;
