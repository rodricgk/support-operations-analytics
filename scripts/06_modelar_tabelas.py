"""Constrói tabelas locais de análise e reconcilia a fila com a etapa 05.

Pré-requisitos: executar scripts 04 e 05. O CSV bruto permanece intacto.
"""

from pathlib import Path
import hashlib
import json
import runpy
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
regras = runpy.run_path(str(RAIZ / "scripts/05_comparar_fila.py"))
PENDENTES = regras["PENDENTES"]
FINALIZADOS = regras["FINALIZADOS"]


def data_informada_unica(bruto, coluna):
    """Consolida datas retrospectivas; conflito não vira escolha arbitrária."""
    valores = bruto[coluna].mask(bruto[coluna].isin(["", "?"]))
    datas = pd.to_datetime(valores, format="%d/%m/%Y %H:%M", errors="coerce")
    grupos = bruto["number"]
    quantidade = datas.groupby(grupos).nunique()
    invalida = (valores.notna() & datas.isna()).groupby(grupos).any()
    # first é seguro APENAS após verificar unicidade e validade no grupo.
    resultado = datas.groupby(grupos).first().mask(quantidade.gt(1) | invalida)
    flags = pd.DataFrame({
        f"{coluna}_conflitante": quantidade.gt(1),
        f"{coluna}_invalida": invalida,
    })
    return resultado.rename(coluna), flags


def main():
    fonte = RAIZ / "data/raw/incident_event_log.csv"
    hash_antes = hashlib.sha256(fonte.read_bytes()).hexdigest()
    bruto = pd.read_csv(fonte, dtype="string", keep_default_na=False)
    flags = pd.read_csv(
        RAIZ / "data/processed/investigacao_temporal/chamados_sinalizados.csv"
    )
    referencia = pd.read_csv(
        RAIZ / "data/processed/sensibilidade_fila/comparacao_diaria.csv", parse_dates=["data"]
    ).set_index("data")
    if referencia.empty:
        raise ValueError("Referência da etapa 05 vazia.")

    # 1. Eventos: preserva todas as linhas, selecionando os campos analíticos.
    campos = ["number", "incident_state", "sys_updated_at", "sys_mod_count",
              "category", "subcategory", "priority", "assignment_group",
              "reopen_count", "reassignment_count"]
    eventos = bruto[campos].copy()
    eventos.insert(0, "linha_csv", bruto.index + 2)
    eventos["atualizacao"] = pd.to_datetime(
        eventos["sys_updated_at"], format="%d/%m/%Y %H:%M", errors="raise"
    )
    eventos["contador"] = pd.to_numeric(eventos["sys_mod_count"], errors="raise")
    for coluna in ["category", "subcategory", "priority", "assignment_group"]:
        eventos[coluna] = eventos[coluna].mask(eventos[coluna].isin(["", "?"]))
    for coluna in ["reopen_count", "reassignment_count"]:
        eventos[coluna] = pd.to_numeric(eventos[coluna], errors="raise")
    eventos["classe_estado"] = "desconhecido"
    eventos.loc[eventos.incident_state.isin(PENDENTES), "classe_estado"] = "pendente"
    eventos.loc[eventos.incident_state.isin(FINALIZADOS), "classe_estado"] = "fora_da_fila"
    flags_colunas = list(flags.columns.drop("number"))
    eventos = eventos.merge(flags, on="number", how="left", validate="many_to_one")
    for coluna in flags_colunas:
        eventos[coluna] = eventos[coluna].fillna(False).astype(bool)
    eventos["sinalizado_temporal"] = eventos[flags_colunas].any(axis=1)
    eventos = eventos.sort_values(["number", "atualizacao", "contador"])
    assert len(eventos) == len(bruto)
    assert eventos.linha_csv.is_unique
    assert not eventos.duplicated(["number", "atualizacao", "contador"]).any()

    # 2. Chamados: um registro por ID, com atributos finais rotulados.
    finais = eventos.drop_duplicates("number", keep="last").set_index("number")
    colunas_finais = ["linha_csv", "atualizacao", "incident_state", "category",
                     "subcategory", "priority", "assignment_group", "reopen_count",
                     "reassignment_count"]
    chamados = finais[colunas_finais].rename(columns=lambda c: f"{c}_final")
    chamados = chamados.join(finais[flags_colunas + ["sinalizado_temporal"]])
    for coluna in ["opened_at", "resolved_at"]:
        consolidada, qualidade = data_informada_unica(bruto, coluna)
        chamados = chamados.join(consolidada).join(qualidade)
    duracao = (chamados.resolved_at - chamados.opened_at).dt.total_seconds() / 3600
    chamados["duracao_negativa"] = duracao.lt(0)
    chamados["elegivel_duracao"] = (
        chamados.incident_state_final.isin(FINALIZADOS) & duracao.notna() & duracao.ge(0)
    )
    chamados["duracao_resolucao_horas"] = duracao.where(chamados.elegivel_duracao)
    assert chamados.index.is_unique
    assert len(chamados) == bruto.number.nunique()
    assert eventos.number.isin(chamados.index).all()

    # 3. Fotografias: um chamado pendente/desconhecido por dia.
    # Reduzimos primeiro a um evento por chamado e dia. Mantém o mesmo corte
    # histórico e evita varrer todos os eventos em cada fotografia.
    eventos["dia_evento"] = eventos.atualizacao.dt.normalize()
    diarios = eventos.drop_duplicates(["number", "dia_evento"], keep="last")
    inicio = eventos.atualizacao.min().normalize()
    fim = eventos.atualizacao.max().normalize() - pd.Timedelta(days=1)
    calendario = pd.DataFrame({"data": pd.date_range(inicio, fim, freq="D")})
    fatias = []
    totais = []
    for dia in calendario["data"]:
        foto = diarios.loc[diarios.dia_evento.le(dia)].drop_duplicates("number", keep="last")
        totais.append({"data": dia, "chamados_conhecidos": len(foto)})
        foto = foto.loc[foto.classe_estado.ne("fora_da_fila"), [
            "number", "linha_csv", "atualizacao", "incident_state", "classe_estado",
            "category", "subcategory", "priority", "assignment_group", "sinalizado_temporal",
        ]].copy()
        foto.insert(0, "data", dia)
        foto["opened_at"] = foto.number.map(chamados.opened_at)
        idade = ((dia + pd.Timedelta(days=1)) - foto.opened_at).dt.total_seconds() / 3600
        foto["idade_valida"] = idade.notna() & idade.ge(0) & foto.classe_estado.eq("pendente")
        foto["idade_horas"] = idade.where(foto.idade_valida)
        fatias.append(foto)
    fotografias = pd.concat(fatias, ignore_index=True)
    assert not fotografias.duplicated(["data", "number"]).any()
    assert fotografias.number.isin(chamados.index).all()
    assert fotografias.linha_csv.isin(eventos.linha_csv).all()
    assert fotografias.atualizacao.lt(fotografias.data + pd.Timedelta(days=1)).all()

    # Reconciliação independente com o CSV do algoritmo da etapa 05.
    resumo = pd.DataFrame(totais).set_index("data")
    for coluna, condicao in {
        "fila_todos": fotografias.classe_estado.eq("pendente"),
        "fila_sem_sinalizados": fotografias.classe_estado.eq("pendente") & ~fotografias.sinalizado_temporal,
        "desconhecidos_todos": fotografias.classe_estado.eq("desconhecido"),
        "desconhecidos_sem_sinalizados": fotografias.classe_estado.eq("desconhecido") & ~fotografias.sinalizado_temporal,
    }.items():
        resumo[coluna] = fotografias.loc[condicao].groupby("data").size().reindex(resumo.index, fill_value=0)
        pd.testing.assert_series_equal(resumo[coluna], referencia[coluna], check_dtype=False, check_freq=False)

    # Calendário contínuo, inclusive datas com fila zero. Seu domínio diário
    # exclui o último dia parcial; datas de outras medidas exigirão calendário maior.
    calendario["ano"] = calendario.data.dt.year
    calendario["mes"] = calendario.data.dt.month
    calendario["ano_mes"] = calendario.data.dt.strftime("%Y-%m")
    assert hashlib.sha256(fonte.read_bytes()).hexdigest() == hash_antes
    destino = RAIZ / "data/processed/modelo"
    destino.mkdir(parents=True, exist_ok=True)
    eventos.drop(columns="dia_evento").to_csv(destino / "eventos.csv", index=False)
    chamados.reset_index().to_csv(destino / "chamados.csv", index=False)
    fotografias.to_csv(destino / "fotografias.csv", index=False)
    calendario.to_csv(destino / "calendario_fila.csv", index=False)
    resumo.to_csv(destino / "resumo_diario.csv")
    manifest = {
        "sha256_fonte": hash_antes, "eventos": len(eventos), "chamados": len(chamados),
        "fotografias": len(fotografias), "datas": len(calendario),
        "chamados_sinalizados": int(chamados.sinalizado_temporal.sum()),
        "elegiveis_duracao": int(chamados.elegivel_duracao.sum()),
        "duracoes_negativas": int(chamados.duracao_negativa.sum()),
        "fotografias_idade_pendente_invalida": int((fotografias.classe_estado.eq("pendente") & ~fotografias.idade_valida).sum()),
        "reconciliacao_05": "passou: quatro contagens diárias em todas as datas",
        "observacao": "Modelo local provisório. Fonte original preservada; não carregado em banco.",
    }
    (destino / "validacao.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
