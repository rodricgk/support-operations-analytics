-- Reconstrução independente das fotografias a partir dos eventos importados.
-- Executar somente após terminar a carga de calendário, chamados e eventos.
-- A função LEAD encontra a atualização seguinte na ordem candidata documentada.
begin;
set local statement_timeout = '120s';
do $$
begin
    if (select count(*) from analytics.eventos) <> 141712
       or (select count(*) from analytics.chamados) <> 24918
       or (select count(*) from analytics.calendario_fila) <> 355 then
        raise exception 'Carga de entrada incompleta para esta extração.';
    end if;
end $$;

with intervalos as (
    select e.*,
        lead(atualizacao) over (
            partition by number order by atualizacao, contador
        ) as proxima_atualizacao
    from analytics.eventos e
), fotografias_calculadas as (
    select d.data, e.number, e.linha_csv, e.atualizacao, e.incident_state,
        e.classe_estado, e.category, e.subcategory, e.priority, e.assignment_group,
        e.sinalizado_temporal, c.opened_at,
        (e.classe_estado = 'pendente' and c.opened_at is not null
            and c.opened_at <= d.data + interval '1 day') as idade_valida,
        case when e.classe_estado = 'pendente' and c.opened_at is not null
                  and c.opened_at <= d.data + interval '1 day'
             then extract(epoch from (d.data + interval '1 day' - c.opened_at)) / 3600.0
        end as idade_horas
    from intervalos e
    join analytics.chamados c using (number)
    join analytics.calendario_fila d
        on d.data >= e.atualizacao::date
        and (e.proxima_atualizacao is null or d.data < e.proxima_atualizacao::date)
    where e.classe_estado in ('pendente', 'desconhecido')
)
insert into analytics.fotografias (
    data, number, linha_csv, atualizacao, incident_state, classe_estado,
    category, subcategory, priority, assignment_group, sinalizado_temporal,
    opened_at, idade_valida, idade_horas
)
select * from fotografias_calculadas
on conflict (data, number) do nothing;

-- Este script só acrescenta fotografias ausentes; não sobrescreve dados existentes.
-- A conferência completa fica em 02_validar_carga.sql.
commit;
