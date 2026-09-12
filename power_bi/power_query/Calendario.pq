let
    Fonte = Csv.Document(File.Contents(PastaDados & "Calendario.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
    Tipos = Table.TransformColumnTypes(Nulos, {
        {"data", type date},
        {"ano", Int64.Type},
        {"mes", Int64.Type},
        {"ano_mes", type text},
        {"data_fotografia_elegivel", type logical}
    }, "en-US")
in
    Tipos
