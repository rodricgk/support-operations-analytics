-- Modelo v1: fonte UCI, uma única extração identificada no manifesto local.
-- Aplicado ao projeto remoto pelo conector; este arquivo registra o SQL exato.
create schema analytics;
revoke all on schema analytics from public, anon, authenticated;

create table analytics.calendario_fila (
    data date primary key,
    ano integer not null,
    mes integer not null check (mes between 1 and 12),
    ano_mes text not null,
    check (ano = extract(year from data)),
    check (mes = extract(month from data)),
    check (ano_mes = to_char(data, 'YYYY-MM'))
);

create table analytics.chamados (
    number text primary key,
    linha_csv_final integer not null check (linha_csv_final >= 2),
    atualizacao_final timestamp without time zone not null,
    incident_state_final text not null,
    category_final text,
    subcategory_final text,
    priority_final text,
    assignment_group_final text,
    reopen_count_final integer not null check (reopen_count_final >= 0),
    reassignment_count_final integer not null check (reassignment_count_final >= 0),
    regressao_contador boolean not null,
    evento_antes_abertura boolean not null,
    contador_reutilizado boolean not null,
    sinalizado_temporal boolean not null,
    opened_at timestamp without time zone,
    opened_at_conflitante boolean not null,
    opened_at_invalida boolean not null,
    resolved_at timestamp without time zone,
    resolved_at_conflitante boolean not null,
    resolved_at_invalida boolean not null,
    duracao_negativa boolean not null,
    elegivel_duracao boolean not null,
    duracao_resolucao_horas double precision,
    check (sinalizado_temporal = (regressao_contador or evento_antes_abertura or contador_reutilizado)),
    check (
        (elegivel_duracao and duracao_resolucao_horas is not null
            and duracao_resolucao_horas >= 0
            and opened_at is not null and resolved_at is not null
            and resolved_at >= opened_at
            and incident_state_final in ('Resolved', 'Closed'))
        or (not elegivel_duracao and duracao_resolucao_horas is null)
    )
);

create table analytics.eventos (
    linha_csv integer primary key check (linha_csv >= 2),
    number text not null references analytics.chamados(number),
    incident_state text not null,
    sys_updated_at text not null,
    sys_mod_count text not null,
    category text,
    subcategory text,
    priority text,
    assignment_group text,
    reopen_count integer not null check (reopen_count >= 0),
    reassignment_count integer not null check (reassignment_count >= 0),
    atualizacao timestamp without time zone not null,
    contador integer not null check (contador >= 0),
    classe_estado text not null check (classe_estado in ('pendente', 'fora_da_fila', 'desconhecido')),
    regressao_contador boolean not null,
    evento_antes_abertura boolean not null,
    contador_reutilizado boolean not null,
    sinalizado_temporal boolean not null,
    unique (number, atualizacao, contador),
    -- A chave composta permite conferir que a fotografia aponta o mesmo chamado.
    unique (linha_csv, number),
    check (sinalizado_temporal = (regressao_contador or evento_antes_abertura or contador_reutilizado))
);

create table analytics.fotografias (
    data date not null references analytics.calendario_fila(data),
    number text not null,
    linha_csv integer not null,
    atualizacao timestamp without time zone not null,
    incident_state text not null,
    classe_estado text not null check (classe_estado in ('pendente', 'desconhecido')),
    category text,
    subcategory text,
    priority text,
    assignment_group text,
    sinalizado_temporal boolean not null,
    opened_at timestamp without time zone,
    idade_valida boolean not null,
    idade_horas double precision,
    primary key (data, number),
    foreign key (linha_csv, number) references analytics.eventos(linha_csv, number),
    check (atualizacao < data + interval '1 day'),
    check (
        (idade_valida and classe_estado = 'pendente' and opened_at is not null
            and opened_at <= data + interval '1 day'
            and idade_horas is not null and idade_horas >= 0)
        or (not idade_valida and idade_horas is null)
    )
);
create index fotografias_evento_idx on analytics.fotografias(linha_csv, number);

create table analytics.resumo_diario (
    data date primary key references analytics.calendario_fila(data),
    chamados_conhecidos integer not null check (chamados_conhecidos >= 0),
    fila_todos integer not null check (fila_todos >= 0),
    fila_sem_sinalizados integer not null check (fila_sem_sinalizados >= 0),
    desconhecidos_todos integer not null check (desconhecidos_todos >= 0),
    desconhecidos_sem_sinalizados integer not null check (desconhecidos_sem_sinalizados >= 0),
    check (fila_sem_sinalizados <= fila_todos),
    check (desconhecidos_sem_sinalizados <= desconhecidos_todos),
    check (fila_todos + desconhecidos_todos <= chamados_conhecidos)
);

comment on schema analytics is 'Modelo analítico UCI; acesso administrativo nesta etapa; sem acesso anônimo.';
comment on table analytics.eventos is 'Um evento por linha original. linha_csv vale apenas para a extração documentada no manifesto.';
comment on table analytics.chamados is 'Um chamado; atributos finais não representam o passado.';
comment on table analytics.fotografias is 'Um chamado pendente/desconhecido por dia, no último estado observado antes da meia-noite seguinte.';
comment on column analytics.chamados.opened_at is 'Data informada sem fuso conhecido; não converter implicitamente para UTC.';
comment on column analytics.chamados.linha_csv_final is 'Origem do registro final; conferida após a carga para evitar dependência circular na importação.';
comment on table analytics.resumo_diario is 'Referência calculada em Python para reconciliação SQL; inclui denominador de chamados já conhecidos.';
comment on table analytics.calendario_fila is 'Datas completas de fotografia; não é calendário geral de todas as medidas.';

-- Sem políticas públicas: postgres carrega; acesso de leitura do BI será definido depois.
alter table analytics.calendario_fila enable row level security;
alter table analytics.chamados enable row level security;
alter table analytics.eventos enable row level security;
alter table analytics.fotografias enable row level security;
alter table analytics.resumo_diario enable row level security;
revoke all on all tables in schema analytics from public, anon, authenticated;
