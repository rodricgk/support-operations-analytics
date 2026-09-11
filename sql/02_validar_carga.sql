-- Conferência da extração atual: todos os resultados devem ter passou = true.
-- Contagens esperadas vêm do manifesto produzido pelo script 06.
with fila_sql as (
    select c.data,
        count(*) filter (where f.classe_estado = 'pendente') as fila_todos,
        count(*) filter (where f.classe_estado = 'pendente' and not f.sinalizado_temporal) as fila_sem_sinalizados,
        count(*) filter (where f.classe_estado = 'desconhecido') as desconhecidos_todos,
        count(*) filter (where f.classe_estado = 'desconhecido' and not f.sinalizado_temporal) as desconhecidos_sem_sinalizados
    from analytics.calendario_fila c
    left join analytics.fotografias f using (data)
    group by c.data
), primeira_observacao as (
    select number, min(atualizacao) as primeira_atualizacao
    from analytics.eventos group by number
), verificacoes as (
    select 'linhas_calendario' as teste, 355::bigint as esperado, count(*) as observado from analytics.calendario_fila
    union all select 'linhas_chamados', 24918, count(*) from analytics.chamados
    union all select 'linhas_eventos', 141712, count(*) from analytics.eventos
    union all select 'linhas_fotografias', 170645, count(*) from analytics.fotografias
    union all select 'linhas_resumo', 355, count(*) from analytics.resumo_diario
    union all select 'chamados_sinalizados', 6, count(*) from analytics.chamados where sinalizado_temporal
    union all select 'elegiveis_duracao', 23362, count(*) from analytics.chamados where elegivel_duracao
    union all select 'dias_divergentes_python_sql', 0, count(*)
        from fila_sql f full join analytics.resumo_diario r using (data)
        where f.data is null or r.data is null
           or (f.fila_todos, f.fila_sem_sinalizados, f.desconhecidos_todos, f.desconhecidos_sem_sinalizados)
              is distinct from
              (r.fila_todos, r.fila_sem_sinalizados, r.desconhecidos_todos, r.desconhecidos_sem_sinalizados)
    union all select 'denominadores_divergentes', 0, count(*)
        from analytics.resumo_diario r
        where r.chamados_conhecidos <> (
            select count(*) from primeira_observacao e
            where e.primeira_atualizacao < r.data + interval '1 day')
    union all select 'fotografias_divergentes_origem', 0, count(*)
        from analytics.fotografias f
        join analytics.eventos e on e.linha_csv = f.linha_csv and e.number = f.number
        where (f.atualizacao, f.incident_state, f.classe_estado, f.category,
               f.subcategory, f.priority, f.assignment_group, f.sinalizado_temporal)
              is distinct from
              (e.atualizacao, e.incident_state, e.classe_estado, e.category,
               e.subcategory, e.priority, e.assignment_group, e.sinalizado_temporal)
    union all select 'fotografias_com_evento_mais_recente_no_corte', 0, count(*)
        from analytics.fotografias f
        join analytics.eventos origem on origem.linha_csv = f.linha_csv
        where exists (
            select 1 from analytics.eventos e
            where e.number = f.number
              and e.atualizacao < f.data + interval '1 day'
              and (e.atualizacao, e.contador) > (origem.atualizacao, origem.contador))
    union all select 'chamados_sem_origem_final_correspondente', 0, count(*)
        from analytics.chamados c
        left join analytics.eventos e on e.linha_csv = c.linha_csv_final and e.number = c.number
        where e.linha_csv is null
            or (c.atualizacao_final, c.incident_state_final, c.category_final, c.subcategory_final,
                c.priority_final, c.assignment_group_final, c.reopen_count_final, c.reassignment_count_final,
                c.sinalizado_temporal)
               is distinct from
               (e.atualizacao, e.incident_state, e.category, e.subcategory,
                e.priority, e.assignment_group, e.reopen_count, e.reassignment_count,
                e.sinalizado_temporal)
    union all select 'duracoes_divergentes', 0, count(*)
        from analytics.chamados
        where elegivel_duracao and abs(duracao_resolucao_horas -
            extract(epoch from (resolved_at - opened_at)) / 3600.0) > 0.000001
    union all select 'idades_divergentes', 0, count(*)
        from analytics.fotografias f join analytics.chamados c using (number)
        where f.opened_at is distinct from c.opened_at
            or (f.idade_valida and abs(f.idade_horas -
                extract(epoch from (f.data + interval '1 day' - f.opened_at)) / 3600.0) > 0.000001)
)
select teste, esperado, observado, esperado = observado as passou
from verificacoes order by teste;
