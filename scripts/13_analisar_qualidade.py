"""Audita a qualidade da fonte e do modelo analítico.

O script separa falhas que invalidam a entrega de ressalvas que limitam a
interpretação. Ele não altera o CSV bruto nem as tabelas modeladas.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / "data/raw/incident_event_log.csv"
MODELO = RAIZ / "data/processed/modelo"
PRIORIDADES = {"1 - Critical", "2 - High", "3 - Moderate", "4 - Low"}
ESTADOS_CONHECIDOS = {
    "New", "Active", "Awaiting User Info", "Awaiting Problem",
    "Awaiting Vendor", "Awaiting Evidence", "Resolved", "Closed",
}


def registrar(resultados, nome, valor, esperado, nivel, passou, detalhe):
    resultados.append({
        "checagem": nome,
        "valor": valor,
        "esperado": esperado,
        "nivel": nivel,
        "status": "passou" if passou else ("falhou" if nivel == "bloqueante" else "ressalva"),
        "detalhe": detalhe,
    })


def main() -> None:
    manifest = json.loads((MODELO / "validacao.json").read_text(encoding="utf-8"))
    bruto = pd.read_csv(FONTE, dtype="string", keep_default_na=False)
    chamados = pd.read_csv(
        MODELO / "chamados.csv",
        parse_dates=["opened_at", "resolved_at", "atualizacao_final"],
    )
    eventos = pd.read_csv(MODELO / "eventos.csv", parse_dates=["atualizacao"])
    fotos = pd.read_csv(MODELO / "fotografias.csv", parse_dates=["data", "opened_at", "atualizacao"])
    calendario = pd.read_csv(MODELO / "calendario_fila.csv", parse_dates=["data"])
    resultados = []

    hash_fonte = hashlib.sha256(FONTE.read_bytes()).hexdigest()
    registrar(
        resultados, "fonte_do_modelo", hash_fonte, manifest["sha256_fonte"],
        "bloqueante", hash_fonte == manifest["sha256_fonte"],
        "Impede validar um modelo gerado a partir de outra versão do CSV.",
    )
    chave_evento_repetida = bruto.duplicated(["number", "sys_updated_at", "sys_mod_count"])
    registrar(
        resultados, "chave_evento", int(chave_evento_repetida.sum()),
        0, "bloqueante", not chave_evento_repetida.any(),
        "A combinação identifica cada evento nesta extração.",
    )
    registrar(
        resultados, "chave_chamado", int(chamados.number.duplicated().sum()), 0,
        "bloqueante", chamados.number.is_unique,
        "A tabela de chamados deve ter exatamente uma linha por incidente.",
    )
    registrar(
        resultados, "chave_fotografia", int(fotos.duplicated(["data", "number"]).sum()), 0,
        "bloqueante", not fotos.duplicated(["data", "number"]).any(),
        "Cada chamado aparece no máximo uma vez em cada fotografia diária.",
    )
    integridades = {
        "cobertura_eventos_fonte": (len(eventos), len(bruto)),
        "cobertura_chamados_fonte": (len(chamados), bruto.number.nunique()),
        "eventos_com_chamado": (int(eventos.number.isin(chamados.number).sum()), len(eventos)),
        "fotografias_com_chamado": (int(fotos.number.isin(chamados.number).sum()), len(fotos)),
        "fotografias_no_calendario": (int(fotos.data.isin(calendario.data).sum()), len(fotos)),
    }
    for nome, (valor, esperado) in integridades.items():
        registrar(
            resultados, nome, valor, esperado, "bloqueante", valor == esperado,
            "Confere cobertura e integridade referencial entre fonte e modelo.",
        )

    for coluna in ["number", "sys_updated_at", "sys_mod_count", "opened_at", "incident_state", "priority"]:
        ausentes = int(bruto[coluna].isin(["", "?"]).sum())
        registrar(
            resultados, f"completude_{coluna}", ausentes, 0, "bloqueante", ausentes == 0,
            "Campo obrigatório para identificar, ordenar ou segmentar os eventos.",
        )

    prioridades_invalidas = sorted(set(bruto.priority) - PRIORIDADES)
    registrar(
        resultados, "dominio_prioridade", prioridades_invalidas, [], "bloqueante",
        not prioridades_invalidas, "Evita recortes silenciosamente fora das quatro prioridades documentadas.",
    )
    estados_desconhecidos = sorted(set(bruto.incident_state) - ESTADOS_CONHECIDOS)
    registrar(
        resultados, "dominio_estado", estados_desconhecidos, [], "ressalva",
        not estados_desconhecidos,
        "Valores sem regra de negócio permanecem como desconhecidos e fora da fila calculada.",
    )

    atualizacao = pd.to_datetime(bruto.sys_updated_at, format="%d/%m/%Y %H:%M", errors="coerce")
    abertura = pd.to_datetime(bruto.opened_at, format="%d/%m/%Y %H:%M", errors="coerce")
    datas_invalidas = int(atualizacao.isna().sum() + abertura.isna().sum())
    registrar(
        resultados, "datas_obrigatorias_validas", datas_invalidas, 0, "bloqueante",
        datas_invalidas == 0, "Atualização e abertura sustentam a reconstrução temporal.",
    )
    eventos_antes_abertura = int(atualizacao.lt(abertura).sum())
    registrar(
        resultados, "eventos_antes_abertura", eventos_antes_abertura, 0, "ressalva",
        eventos_antes_abertura == 0,
        "Casos são preservados e sinalizados; a causa não pode ser inferida apenas do CSV.",
    )

    contagens = {
        "eventos": len(eventos), "chamados": len(chamados),
        "fotografias": len(fotos), "datas": len(calendario),
        "elegiveis_duracao": int(chamados.elegivel_duracao.sum()),
    }
    for nome, valor in contagens.items():
        esperado = int(manifest[nome])
        registrar(
            resultados, f"contagem_{nome}", valor, esperado, "bloqueante", valor == esperado,
            "Confere a tabela atual contra o manifesto produzido na modelagem.",
        )

    duracoes_negativas = int(chamados.duracao_negativa.sum())
    registrar(
        resultados, "duracoes_negativas", duracoes_negativas, 0, "bloqueante",
        duracoes_negativas == 0, "Durações negativas não podem entrar nos indicadores.",
    )
    idades_invalidas = int((fotos.classe_estado.eq("pendente") & ~fotos.idade_valida).sum())
    registrar(
        resultados, "idades_pendentes_invalidas", idades_invalidas, 0, "bloqueante",
        idades_invalidas == 0, "Toda idade incluída na mediana diária precisa ser não negativa.",
    )

    sem_resolucao = int(chamados.resolved_at.isna().sum())
    registrar(
        resultados, "chamados_sem_resolucao", sem_resolucao, 0, "ressalva",
        sem_resolucao == 0,
        "Esses chamados são excluídos da duração; a cobertura deve acompanhar a métrica.",
    )
    cobertura_prioridade = {}
    for prioridade, grupo in chamados.groupby("priority_final", dropna=False):
        total = len(grupo)
        elegiveis = int(grupo.elegivel_duracao.sum())
        cobertura_prioridade[str(prioridade)] = {
            "total": total,
            "elegiveis": elegiveis,
            "excluidos": total - elegiveis,
            "cobertura_pct": round(100 * elegiveis / total, 4),
        }
    registrar(
        resultados, "ultimo_dia_parcial_excluido", calendario.data.max().strftime("%Y-%m-%d"),
        (eventos.atualizacao.max().normalize() - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        "bloqueante",
        calendario.data.max() == eventos.atualizacao.max().normalize() - pd.Timedelta(days=1),
        "Evita publicar uma fotografia do último dia incompleto da extração.",
    )

    bloqueantes = [r for r in resultados if r["status"] == "falhou"]
    ressalvas = [r for r in resultados if r["status"] == "ressalva"]
    saida = {
        "status": "falhou" if bloqueantes else "passou_com_ressalvas" if ressalvas else "passou",
        "fonte": str(FONTE.relative_to(RAIZ)),
        "graos": {
            "fonte": "evento por incidente",
            "chamados": "incidente",
            "fotografias": "incidente pendente ou desconhecido por dia",
        },
        "resumo": {
            "checagens": len(resultados),
            "falhas_bloqueantes": len(bloqueantes),
            "ressalvas": len(ressalvas),
            "cobertura_duracao_pct": round(100 * contagens["elegiveis_duracao"] / contagens["chamados"], 4),
        },
        "cobertura_duracao_por_prioridade": cobertura_prioridade,
        "resultados": resultados,
    }
    destino = RAIZ / "data/processed/qualidade"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "validacao.json").write_text(
        json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(saida["resumo"], ensure_ascii=False, indent=2))
    for item in ressalvas:
        print(f"RESSALVA: {item['checagem']} = {item['valor']}")
    if bloqueantes:
        nomes = ", ".join(item["checagem"] for item in bloqueantes)
        raise AssertionError(f"Falhas bloqueantes de qualidade: {nomes}")


if __name__ == "__main__":
    main()
