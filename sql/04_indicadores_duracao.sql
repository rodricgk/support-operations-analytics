-- Duração retrospectiva em horas corridas; um registro por chamado.
-- Escopo: toda a extração disponível, sem filtro de mês e sem calendário de fila.
-- Recortes usam a prioridade FINAL, não a prioridade histórica.
with cenarios(cenario, excluir_sinalizados) as (
    values ('todos', false), ('sem_sinalizados', true)
), base as (
    select s.cenario, c.*,
        case
            when opened_at_conflitante or resolved_at_conflitante then 'datas_conflitantes'
            when opened_at_invalida or resolved_at_invalida then 'datas_invalidas'
            when opened_at is null then 'sem_abertura'
            when resolved_at is null then 'sem_resolucao'
            when resolved_at < opened_at then 'duracao_negativa'
            when incident_state_final not in ('Resolved', 'Closed') then 'estado_nao_final'
            else 'elegivel'
        end as motivo
    from cenarios s join analytics.chamados c
        on not s.excluir_sinalizados or not c.sinalizado_temporal
)
select cenario,
    case when grouping(priority_final) = 1 then 'geral' else 'prioridade_final' end as recorte,
    priority_final as prioridade,
    count(*) as n_total,
    count(*) filter (where motivo = 'elegivel') as n_elegivel,
    count(*) filter (where motivo <> 'elegivel') as n_excluido,
    count(*) filter (where motivo = 'datas_conflitantes') as n_datas_conflitantes,
    count(*) filter (where motivo = 'datas_invalidas') as n_datas_invalidas,
    count(*) filter (where motivo = 'sem_abertura') as n_sem_abertura,
    count(*) filter (where motivo = 'sem_resolucao') as n_sem_resolucao,
    count(*) filter (where motivo = 'duracao_negativa') as n_duracao_negativa,
    count(*) filter (where motivo = 'estado_nao_final') as n_estado_nao_final,
    percentile_cont(0.5) within group (
        order by extract(epoch from (resolved_at - opened_at)) / 3600.0
    ) filter (where motivo = 'elegivel') as mediana_horas,
    percentile_cont(0.9) within group (
        order by extract(epoch from (resolved_at - opened_at)) / 3600.0
    ) filter (where motivo = 'elegivel') as p90_horas
from base
group by grouping sets ((cenario), (cenario, priority_final))
order by cenario, recorte, prioridade nulls first;
