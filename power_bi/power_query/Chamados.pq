let
    Fonte = Csv.Document(File.Contents(PastaDados & "Chamados.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
    Tipos = Table.TransformColumnTypes(Nulos, {
        {"number", type text},
        {"linha_csv_final", Int64.Type},
        {"atualizacao_final", type datetime},
        {"incident_state_final", type text},
        {"category_final", type text},
        {"subcategory_final", type text},
        {"priority_final", type text},
        {"assignment_group_final", type text},
        {"reopen_count_final", Int64.Type},
        {"reassignment_count_final", Int64.Type},
        {"regressao_contador", type logical},
        {"evento_antes_abertura", type logical},
        {"contador_reutilizado", type logical},
        {"sinalizado_temporal", type logical},
        {"opened_at", type datetime},
        {"opened_at_conflitante", type logical},
        {"opened_at_invalida", type logical},
        {"resolved_at", type datetime},
        {"resolved_at_conflitante", type logical},
        {"resolved_at_invalida", type logical},
        {"duracao_negativa", type logical},
        {"elegivel_duracao", type logical},
        {"duracao_resolucao_horas", type number},
        {"data_abertura", type date},
        {"data_resolucao", type date}
    }, "en-US")
in
    Tipos
