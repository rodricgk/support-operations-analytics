"""Exporta o modelo local para Power BI sem senha; gera consultas M com tipos explícitos."""
from pathlib import Path
import json
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def main():
    origem = RAIZ / "data/processed/modelo"
    destino = RAIZ / "data/processed/power_bi"
    consultas = RAIZ / "power_bi/power_query"
    chamados = pd.read_csv(origem / "chamados.csv", parse_dates=[
        "atualizacao_final", "opened_at", "resolved_at"])
    fotos = pd.read_csv(origem / "fotografias.csv", parse_dates=[
        "data", "atualizacao", "opened_at"])
    resumo = pd.read_csv(origem / "resumo_diario.csv", parse_dates=["data"])
    fila = pd.read_csv(origem / "calendario_fila.csv", parse_dates=["data"])
    chamados["data_abertura"] = chamados.opened_at.dt.normalize()
    chamados["data_resolucao"] = chamados.resolved_at.dt.normalize()
    datas = pd.concat([fila.data, chamados.data_abertura, chamados.data_resolucao]).dropna()
    calendario = pd.DataFrame({"data": pd.date_range(
        f"{datas.min().year}-01-01", f"{datas.max().year}-12-31")})
    calendario["ano"] = calendario.data.dt.year
    calendario["mes"] = calendario.data.dt.month
    calendario["ano_mes"] = calendario.data.dt.strftime("%Y-%m")
    calendario["data_fotografia_elegivel"] = calendario.data.isin(fila.data)
    tabelas = {"Calendario": calendario, "Chamados": chamados,
               "Fotografias": fotos, "ResumoDiario": resumo}

    # Chaves e cobertura: falhar antes de exportar se houver perda ou duplicação.
    for nome, chave in [("Calendario", ["data"]), ("Chamados", ["number"]),
                        ("Fotografias", ["data", "number"]), ("ResumoDiario", ["data"])]:
        tabela = tabelas[nome]
        if tabela[chave].isna().any().any() or tabela.duplicated(chave).any():
            raise ValueError(f"Chave inválida em {nome}.")
    if fila.data.duplicated().any() or set(fila.data) != set(resumo.data):
        raise ValueError("Calendário de fotografias e resumo não reconciliam.")
    for serie in [chamados.data_abertura, chamados.data_resolucao, fotos.data, resumo.data]:
        if not serie.dropna().isin(calendario.data).all():
            raise ValueError("Data fora do calendário BI.")
    if not fotos.data.isin(fila.data).all() or not fotos.number.isin(chamados.number).all():
        raise ValueError("Fotografia sem data elegível ou chamado correspondente.")
    if not calendario.data.diff().dropna().eq(pd.Timedelta(days=1)).all():
        raise ValueError("Calendário com lacunas.")

    destino.mkdir(parents=True, exist_ok=True)
    consultas.mkdir(parents=True, exist_ok=True)
    pasta_m = str(destino).replace('"', '""') + "\\"
    (destino / "PastaDados.pq").write_text(
        '"' + pasta_m + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n',
        encoding="utf-8")
    manifesto = {}
    for nome, tabela in tabelas.items():
        exportacao = tabela.copy()
        tipos = []
        for coluna, serie in tabela.items():
            if pd.api.types.is_datetime64_any_dtype(serie):
                so_data = coluna in {"data", "data_abertura", "data_resolucao"}
                tipo = "type date" if so_data else "type datetime"
                exportacao[coluna] = serie.dt.strftime("%Y-%m-%d" if so_data else "%Y-%m-%d %H:%M:%S")
            elif pd.api.types.is_bool_dtype(serie):
                tipo = "type logical"
                exportacao[coluna] = serie.map({True: "true", False: "false"})
            elif pd.api.types.is_integer_dtype(serie):
                tipo = "Int64.Type"
            elif pd.api.types.is_float_dtype(serie):
                tipo = "type number"
            else:
                tipo = "type text"
            tipos.append('{"' + coluna + '", ' + tipo + '}')
        arquivo = destino / f"{nome}.csv"
        exportacao.to_csv(arquivo, index=False, encoding="utf-8", lineterminator="\n")
        # Round-trip: conferir valores, ordem, nulos e cabeçalhos efetivamente gravados.
        relido = pd.read_csv(arquivo, dtype=str, keep_default_na=False)
        esperado = exportacao.fillna("").astype(str)
        pd.testing.assert_frame_equal(relido, esperado, check_dtype=False)
        # Csv.Document preserva o esquema; vazio vira null antes de converter tipos.
        m = 'let\n    Fonte = Csv.Document(File.Contents(PastaDados & "' + nome + '.csv"),\n'
        m += '        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        m += '    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),\n'
        m += '    Nulos = Table.ReplaceValue(Cabecalhos, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecalhos)),\n'
        m += '    Tipos = Table.TransformColumnTypes(Nulos, {\n        ' + ',\n        '.join(tipos) + '\n    }, "en-US")\nin\n    Tipos\n'
        (consultas / f"{nome}.pq").write_text(m, encoding="utf-8")
        manifesto[nome] = {"linhas": len(tabela), "colunas": list(tabela.columns)}
    manifesto["calendario_inicio"] = calendario.data.min().strftime("%Y-%m-%d")
    manifesto["calendario_fim"] = calendario.data.max().strftime("%Y-%m-%d")
    manifesto["dias_fotografia_elegiveis"] = int(calendario.data_fotografia_elegivel.sum())
    manifesto["resolucao_ausente"] = int(chamados.data_resolucao.isna().sum())
    manifesto["validacao"] = "Chaves, cobertura, continuidade e leitura dos quatro CSVs conferidas."
    manifesto["power_query_executado"] = False
    (destino / "validacao.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifesto, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
