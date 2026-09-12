let
    Fonte = Csv.Document(File.Contents(PastaDados & "ResumoDiario.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),
    Tipos = Table.TransformColumnTypes(Nulos, {
        {"data", type date},
        {"chamados_conhecidos", Int64.Type},
        {"fila_todos", Int64.Type},
        {"fila_sem_sinalizados", Int64.Type},
        {"desconhecidos_todos", Int64.Type},
        {"desconhecidos_sem_sinalizados", Int64.Type}
    }, "en-US")
in
    Tipos
