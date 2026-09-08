"""Análise de sensibilidade da fila observada no fim do dia; não corrige dados."""

from pathlib import Path
import pandas as pd

# Hipótese operacional explícita: espera continua sendo pendência de resolução.
PENDENTES = {
    "New", "Active", "Awaiting User Info", "Awaiting Vendor",
    "Awaiting Problem", "Awaiting Evidence",
}
FINALIZADOS = {"Resolved", "Closed"}


def fotografia(eventos_ordenados, dia):
    """Último evento por chamado antes da meia-noite do dia seguinte.

    Entrada já ordenada por chamado, horário e contador numérico.
    Não utiliza opened_at, resolved_at ou closed_at para inventar eventos.
    """
    corte = pd.Timestamp(dia) + pd.Timedelta(days=1)
    ate_o_corte = eventos_ordenados.loc[eventos_ordenados["atualizacao"].lt(corte)]
    return ate_o_corte.drop_duplicates("number", keep="last")


def verificar_regra():
    """Exemplo controlado: reabertura, empate, estado desconhecido e limite diário."""
    exemplo = pd.DataFrame([
        ("A", "2020-01-01 10:00", 0, "New"),
        ("A", "2020-01-02 10:00", 1, "Resolved"),
        ("A", "2020-01-03 10:00", 2, "Active"),
        ("B", "2020-01-01 23:59", 1, "Active"),
        ("B", "2020-01-01 23:59", 2, "Resolved"),
        ("C", "2020-01-02 00:00", 0, "New"),
        ("D", "2020-01-01 12:00", 0, "-100"),
    ], columns=["number", "atualizacao", "contador", "incident_state"])
    exemplo["atualizacao"] = pd.to_datetime(exemplo["atualizacao"])
    exemplo = exemplo.sort_values(["number", "atualizacao", "contador"])
    primeiro = fotografia(exemplo, "2020-01-01").set_index("number")
    assert primeiro["incident_state"].to_dict() == {"A": "New", "B": "Resolved", "D": "-100"}
    assert fotografia(exemplo, "2020-01-02").set_index("number").loc["A", "incident_state"] == "Resolved"
    assert fotografia(exemplo, "2020-01-03").set_index("number").loc["A", "incident_state"] == "Active"


def main():
    verificar_regra()
    raiz = Path(__file__).resolve().parents[1]
    df = pd.read_csv(raiz / "data/raw/incident_event_log.csv", dtype="string", keep_default_na=False)
    sinalizacao = raiz / "data/processed/investigacao_temporal/chamados_sinalizados.csv"
    if not sinalizacao.exists():
        raise FileNotFoundError("Execute primeiro scripts/04_investigar_inconsistencias.py")
    ids_sinalizados = set(pd.read_csv(sinalizacao, dtype="string")["number"])
    df["atualizacao"] = pd.to_datetime(df["sys_updated_at"], format="%d/%m/%Y %H:%M", errors="raise")
    df["contador"] = pd.to_numeric(df["sys_mod_count"], errors="raise")
    df = df.sort_values(["number", "atualizacao", "contador"])
    assert not df.duplicated(["number", "atualizacao", "contador"]).any()

    # O último dia termina às 15h no arquivo: não projetar seu estado até 23h59.
    # Excluir esse dia não é prova de que os dias anteriores estejam completos.
    inicio = df["atualizacao"].min().normalize()
    ultimo_dia = df["atualizacao"].max().normalize()
    resultados = []
    for dia in pd.date_range(inicio, ultimo_dia - pd.Timedelta(days=1), freq="D"):
        foto = fotografia(df, dia)
        pendente = foto["incident_state"].isin(PENDENTES)
        desconhecido = ~foto["incident_state"].isin(PENDENTES | FINALIZADOS)
        sinalizado = foto["number"].isin(ids_sinalizados)
        todos = int(pendente.sum())
        sem_excecoes = int((pendente & ~sinalizado).sum())
        resultados.append({
            "data": dia, "fila_todos": todos, "fila_sem_sinalizados": sem_excecoes,
            "diferenca": todos - sem_excecoes,
            "desconhecidos_todos": int(desconhecido.sum()),
            "desconhecidos_sem_sinalizados": int((desconhecido & ~sinalizado).sum()),
        })
    resultado = pd.DataFrame(resultados)
    resultado["diferenca_pct_fila_todos"] = resultado["diferenca"].div(
        resultado["fila_todos"].replace(0, float("nan"))
    ) * 100
    assert resultado["diferenca"].between(0, len(ids_sinalizados)).all()
    destino = raiz / "data/processed/sensibilidade_fila"
    destino.mkdir(parents=True, exist_ok=True)
    resultado.to_csv(destino / "comparacao_diaria.csv", index=False)
    print("Regra verificada em exemplo controlado.")
    print("Dias comparados:", len(resultado))
    print("Última atualização da fonte:", df["atualizacao"].max())
    print("Chamados sinalizados:", len(ids_sinalizados))
    print("\nDIAS COM DIFERENÇA ENTRE CENÁRIOS")
    print(resultado.loc[resultado["diferenca"].gt(0)].to_string(index=False))
    print("\nMaior diferença absoluta:", resultado["diferenca"].max())
    print("Maior diferença relativa (%):", resultado["diferenca_pct_fila_todos"].max())
    print("Dias com estado desconhecido:", int(resultado["desconhecidos_todos"].gt(0).sum()))
    print("Máximo de chamados em estado desconhecido:", resultado["desconhecidos_todos"].max())
    print("\nComparação de cenários não determina qual seria a fila correta.")


if __name__ == "__main__":
    main()
