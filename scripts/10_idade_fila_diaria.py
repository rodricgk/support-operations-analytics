"""Calcula a idade diária da fila e reconcilia com o SQL e o resumo da etapa 06."""
from pathlib import Path
import json
import math
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def resumir(foto, dia, cenario):
    corte = dia + pd.Timedelta(days=1)
    pendente = foto.classe_estado.eq("pendente")
    idades = (corte - foto.opened_at).dt.total_seconds() / 3600
    elegivel = pendente & idades.notna() & idades.ge(0)
    valores = idades.loc[elegivel]
    return {
        "data": dia.strftime("%Y-%m-%d"), "cenario": cenario,
        "n_fila": int(pendente.sum()),
        "n_elegivel": int(elegivel.sum()),
        "n_idade_invalida": int((pendente & ~elegivel).sum()),
        "n_desconhecido": int(foto.classe_estado.eq("desconhecido").sum()),
        "mediana_idade_horas": None if valores.empty else float(valores.quantile(0.5, interpolation="linear")),
    }


def calcular():
    modelo = RAIZ / "data/processed/modelo"
    fotos = pd.read_csv(modelo / "fotografias.csv", parse_dates=["data", "opened_at"])
    calendario = pd.read_csv(modelo / "calendario_fila.csv", parse_dates=["data"])
    if fotos.duplicated(["data", "number"]).any() or calendario.data.duplicated().any():
        raise ValueError("Chaves repetidas no modelo.")
    if not fotos.data.isin(calendario.data).all():
        raise ValueError("Fotografia fora do calendário.")
    idade = (fotos.data + pd.Timedelta(days=1) - fotos.opened_at).dt.total_seconds() / 3600
    elegivel = fotos.classe_estado.eq("pendente") & idade.notna() & idade.ge(0)
    if not elegivel.eq(fotos.idade_valida).all():
        raise ValueError("Elegibilidade recalculada difere da flag armazenada.")
    resultados = []
    for cenario, dados in [("todos", fotos), ("sem_sinalizados", fotos.loc[~fotos.sinalizado_temporal])]:
        grupos = {dia: grupo for dia, grupo in dados.groupby("data")}
        for dia in calendario.data:
            resultados.append(resumir(grupos.get(dia, dados.iloc[:0]), dia, cenario))
    return resultados


def conferir(resultados):
    sql = json.loads((RAIZ / "docs/idade-fila-sql.json").read_text(encoding="utf-8"))["resultados"]
    chave = lambda r: (r["data"], r["cenario"])
    esperado, observado = ({chave(r): r for r in conjunto} for conjunto in (sql, resultados))
    if len(esperado) != len(sql) or len(observado) != len(resultados) or esperado.keys() != observado.keys():
        raise ValueError("Datas/cenários não reconciliam.")
    for k, r in observado.items():
        if r["n_elegivel"] + r["n_idade_invalida"] != r["n_fila"]:
            raise ValueError("Elegíveis e inválidos não reconciliam a fila.")
        for campo, valor in r.items():
            referencia = esperado[k][campo]
            if campo == "mediana_idade_horas" and valor is not None and referencia is not None:
                igual = math.isclose(valor, referencia, rel_tol=0, abs_tol=0.000001)
            else:
                igual = valor == referencia
            if not igual:
                raise ValueError(f"Divergência em {k}: {campo}.")
    resumo = pd.read_csv(RAIZ / "data/processed/modelo/resumo_diario.csv").set_index("data")
    for r in resultados:
        sufixo = "todos" if r["cenario"] == "todos" else "sem_sinalizados"
        if r["n_fila"] != resumo.loc[r["data"], "fila_" + sufixo]:
            raise ValueError("Fila difere da referência da etapa 06.")
        if r["n_desconhecido"] != resumo.loc[r["data"], "desconhecidos_" + sufixo]:
            raise ValueError("Desconhecidos diferem da referência da etapa 06.")
    return len(resultados)


def testar_limites():
    dia = pd.Timestamp("2020-01-01")
    exemplo = pd.DataFrame({
        "classe_estado": ["pendente"] * 4 + ["desconhecido"],
        "opened_at": pd.to_datetime([
            "2020-01-01 12:00", "2020-01-02 00:00", None,
            "2020-01-02 01:00", "2020-01-01 12:00"
        ]),
    })
    r = resumir(exemplo, dia, "teste")
    assert (r["n_fila"], r["n_elegivel"], r["n_idade_invalida"], r["n_desconhecido"]) == (4, 2, 2, 1)
    assert r["mediana_idade_horas"] == 6
    vazio = resumir(exemplo.iloc[:0], dia, "teste")
    assert vazio["n_fila"] == 0 and vazio["mediana_idade_horas"] is None


def main():
    testar_limites()
    resultados = calcular()
    conferidos = conferir(resultados)
    destino = RAIZ / "data/processed/idade_fila"
    destino.mkdir(parents=True, exist_ok=True)
    tabela = pd.DataFrame(resultados).sort_values(["data", "cenario"])
    tabela.to_csv(destino / "idade_diaria_python.csv", index=False)
    todos = [r for r in resultados if r["cenario"] == "todos"]
    maior_fila = max(todos, key=lambda r: r["n_fila"])
    com_idade = [r for r in todos if r["mediana_idade_horas"] is not None]
    evidencia = {
        "linhas_conferidas": conferidos, "dias": len(todos),
        "dias_sem_fila": sum(r["n_fila"] == 0 for r in todos),
        "dias_com_idade_invalida": sum(r["n_idade_invalida"] > 0 for r in todos),
        "dias_com_desconhecidos": sum(r["n_desconhecido"] > 0 for r in todos),
        "primeiro_dia": todos[0], "ultimo_dia": todos[-1],
        "primeiro_dia_de_maior_fila": maior_fila,
        "primeiro_dia_de_maior_mediana": max(com_idade, key=lambda r: r["mediana_idade_horas"]) if com_idade else None,
        "testes_limites": "passou: vazio, ausência, abertura futura, abertura no corte e desconhecido",
    }
    (destino / "validacao.json").write_text(
        json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(evidencia, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
