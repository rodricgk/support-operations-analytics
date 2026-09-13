"""Executa as conferências finais da entrega analítica e do Power BI.

Pré-requisitos: gerar os artefatos locais pelos scripts 01 a 11. O script não
usa credenciais, não altera a base bruta e não executa consultas no Supabase.
"""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


def executar(nome: str) -> None:
    subprocess.run(
        [sys.executable, str(RAIZ / "scripts" / nome)],
        cwd=RAIZ,
        check=True,
    )


def ler_json(caminho: str) -> dict:
    arquivo = RAIZ / caminho
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Artefato ausente: {caminho}. Execute as etapas anteriores primeiro."
        )
    return json.loads(arquivo.read_text(encoding="utf-8"))


def validar_indicadores() -> None:
    duracao = ler_json("data/processed/duracao/validacao.json")
    geral = next(
        item
        for item in duracao["resultados"]
        if item["cenario"] == "todos" and item["recorte"] == "geral"
    )
    if geral["n_total"] != 24918:
        raise AssertionError("Total de chamados diferente do esperado.")
    if geral["n_elegivel"] != 23362:
        raise AssertionError("Quantidade elegível diferente do esperado.")

    fila = ler_json("data/processed/idade_fila/validacao.json")
    if fila["linhas_conferidas"] != 710 or fila["dias"] != 355:
        raise AssertionError("Cobertura diária da fila diferente do esperado.")
    if fila["primeiro_dia_de_maior_fila"]["n_fila"] != 1869:
        raise AssertionError("Pico da fila diferente do esperado.")


def validar_modelo_power_bi() -> None:
    modelo = ler_json("docs/power-bi-modelo-validacao.json")
    if not all(item["matches"] for item in modelo["measures"]):
        raise AssertionError("Há medida DAX divergente da referência textual.")
    if modelo["pending"]:
        raise AssertionError(f"Há pendências registradas no modelo: {modelo['pending']}")
    if modelo["automatic_date_tables"] != 0:
        raise AssertionError("Ainda existem tabelas de data automáticas.")


def validar_pbix() -> None:
    pbix = RAIZ / "power_bi/support-operations-analytics.pbix"
    definicao = RAIZ / "power_bi/support-operations-analytics.Report/definition"
    if not pbix.exists():
        raise FileNotFoundError("PBIX não encontrado.")

    with zipfile.ZipFile(pbix) as arquivo:
        if arquivo.testzip() is not None:
            raise AssertionError("O contêiner PBIX está corrompido.")
        nomes = [
            nome
            for nome in arquivo.namelist()
            if nome.startswith("Report/definition/") and nome.endswith(".json")
        ]
        for nome in nomes:
            relativo = Path(nome).relative_to("Report/definition")
            local = definicao / relativo
            if not local.exists():
                raise AssertionError(f"Definição ausente no PBIP: {relativo}")
            do_pbix = json.loads(arquivo.read(nome).decode("utf-8"))
            do_pbip = json.loads(local.read_text(encoding="utf-8"))
            if do_pbix != do_pbip:
                raise AssertionError(f"Definição PBIX/PBIP divergente: {relativo}")

        print(f"PBIX íntegro; {len(nomes)} definições do relatório coincidem com o PBIP.")


def main() -> None:
    executar("09_indicadores_duracao.py")
    executar("10_idade_fila_diaria.py")
    executar("11_preparar_power_bi.py")
    validar_indicadores()
    validar_modelo_power_bi()
    validar_pbix()
    print("Validação da entrega concluída com sucesso.")


if __name__ == "__main__":
    main()
