"""Calcula durações e compara com a consulta SQL executada no Supabase.

Escopo fixo: toda a extração. Não faz junção com eventos nem com calendário.
"""
from pathlib import Path
import json
import math
import hashlib
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
MOTIVOS = [
    "datas_conflitantes", "datas_invalidas", "sem_abertura",
    "sem_resolucao", "duracao_negativa", "estado_nao_final",
]


def carregar():
    caminho = RAIZ / "data/processed/modelo/chamados.csv"
    base = pd.read_csv(caminho, parse_dates=["opened_at", "resolved_at"])
    if not base.number.is_unique:
        raise ValueError("A tabela deve conter um registro por chamado.")
    base["duracao_calculada"] = (base.resolved_at - base.opened_at).dt.total_seconds() / 3600
    # A precedência torna os motivos mutuamente exclusivos; não somar flags sobrepostas.
    condicoes = {
        "datas_conflitantes": base.opened_at_conflitante | base.resolved_at_conflitante,
        "datas_invalidas": base.opened_at_invalida | base.resolved_at_invalida,
        "sem_abertura": base.opened_at.isna(),
        "sem_resolucao": base.resolved_at.isna(),
        "duracao_negativa": base.duracao_calculada.lt(0),
        "estado_nao_final": ~base.incident_state_final.isin(["Resolved", "Closed"]),
    }
    base["motivo"] = "elegivel"
    for motivo, condicao in condicoes.items():
        base.loc[base.motivo.eq("elegivel") & condicao, "motivo"] = motivo
    if not base.motivo.eq("elegivel").eq(base.elegivel_duracao).all():
        raise ValueError("Elegibilidade recalculada difere da etapa 06.")
    return base


def quantil(valores, fracao):
    return None if valores.empty else float(valores.quantile(fracao, interpolation="linear"))


def resumir(base, cenario, recorte, prioridade=None):
    elegiveis = base.loc[base.motivo.eq("elegivel"), "duracao_calculada"]
    resultado = {
        "cenario": cenario, "recorte": recorte, "prioridade": prioridade,
        "n_total": len(base), "n_elegivel": len(elegiveis),
        "n_excluido": len(base) - len(elegiveis),
        **{"n_" + motivo: int(base.motivo.eq(motivo).sum()) for motivo in MOTIVOS},
        "mediana_horas": quantil(elegiveis, 0.5),
        "p90_horas": quantil(elegiveis, 0.9),
    }
    if sum(resultado["n_" + m] for m in MOTIVOS) != resultado["n_excluido"]:
        raise ValueError("Motivos não reconciliam a população excluída.")
    return resultado


def calcular(base):
    resultados = []
    for cenario, dados in [("todos", base), ("sem_sinalizados", base.loc[~base.sinalizado_temporal])]:
        resultados.append(resumir(dados, cenario, "geral"))
        for prioridade, grupo in dados.groupby("priority_final", dropna=False):
            valor = None if pd.isna(prioridade) else str(prioridade)
            resultados.append(resumir(grupo, cenario, "prioridade_final", valor))
    return resultados


def conferir(resultados):
    sql = json.loads((RAIZ / "docs/duracao-sql.json").read_text(encoding="utf-8"))["resultados"]
    def chave(r):
        return r["cenario"], r["recorte"], r["prioridade"]
    esperado = {chave(r): r for r in sql}
    observado = {chave(r): r for r in resultados}
    if len(esperado) != len(sql) or esperado.keys() != observado.keys():
        raise ValueError("Recortes Python e SQL diferem.")
    for chave_grupo, r in observado.items():
        for campo, valor in r.items():
            referencia = esperado[chave_grupo][campo]
            if campo in ("mediana_horas", "p90_horas") and valor is not None and referencia is not None:
                igual = math.isclose(valor, referencia, rel_tol=0, abs_tol=0.000001)
            else:
                igual = valor == referencia
            if not igual:
                raise ValueError(f"Divergência: {chave_grupo}, {campo}.")
    return len(resultados)


def main():
    # Casos que distinguem percentil contínuo, ausência e duração zero.
    assert quantil(pd.Series([0.0, 10.0, 20.0, 100.0]), 0.5) == 15
    assert math.isclose(quantil(pd.Series([0.0, 10.0, 20.0, 100.0]), 0.9), 76)
    assert quantil(pd.Series([], dtype=float), 0.9) is None
    assert quantil(pd.Series([0.0]), 0.9) == 0
    base = carregar()
    resultados = calcular(base)
    n = conferir(resultados)
    destino = RAIZ / "data/processed/duracao"
    destino.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(resultados).to_csv(destino / "indicadores_python.csv", index=False)
    evidencia = {
        "sha256_chamados_csv": hashlib.sha256(
            (RAIZ / "data/processed/modelo/chamados.csv").read_bytes()
        ).hexdigest(),
        "recortes_reconciliados": n, "tolerancia_horas": 0.000001,
        "casos_controlados": "passou: interpolação linear, vazio e zero",
        "comparacao": "SQL recalcula a duração das datas; Python também recalcula, usando pandas.",
        "resultados": resultados,
    }
    (destino / "validacao.json").write_text(
        json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"SQL e Python conferem em {n} recortes.")
    print(pd.DataFrame(resultados).loc[lambda d: d.recorte.eq("geral"),
        ["cenario", "n_total", "n_elegivel", "n_excluido", "mediana_horas", "p90_horas"]].to_string(index=False))


if __name__ == "__main__":
    main()
