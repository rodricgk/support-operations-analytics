let
    Fonte = Csv.Document(File.Contents(PastaDados & "Fotografias.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
    Tipos = Table.TransformColumnTypes(Nulos, {
        {"data", type date},
        {"number", type text},
        {"linha_csv", Int64.Type},
        {"atualizacao", type datetime},
        {"incident_state", type text},
        {"classe_estado", type text},
        {"category", type text},
        {"subcategory", type text},
        {"priority", type text},
        {"assignment_group", type text},
        {"sinalizado_temporal", type logical},
        {"opened_at", type datetime},
        {"idade_valida", type logical},
        {"idade_horas", type number}
    }, "en-US")
in
    Tipos
