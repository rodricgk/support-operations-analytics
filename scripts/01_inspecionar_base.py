"""Primeira leitura: eventos, incidentes e o histórico de um chamado.

Somente leitura: o CSV original nunca é alterado.
"""

from pathlib import Path

import pandas as pd


# Resolve o caminho a partir deste script, independentemente do terminal.
raiz = Path(__file__).resolve().parents[1]
arquivo = raiz / "data" / "raw" / "incident_event_log.csv"

# Mantemos os valores como texto nesta inspeção, inclusive o marcador '?'.
# A tipagem definitiva e as regras de ausência serão uma etapa separada.
df = pd.read_csv(arquivo, dtype="string", keep_default_na=False)

print(f"Eventos (linhas): {len(df):,}")
print(f"Chamados distintos: {df['number'].nunique():,}")
print(f"Colunas: {len(df.columns)}")

# Selecionamos um exemplo curto para entender o histórico completo.
chamado = "INC0000045"
historico = df.loc[df["number"].eq(chamado)].copy()

# Texto não deve ser ordenado como se fosse uma data. A conversão é apenas
# uma chave auxiliar; erros de formato interrompem a execução para investigação.
historico["ordem_data"] = pd.to_datetime(
    historico["sys_updated_at"], format="%d/%m/%Y %H:%M", errors="raise"
)
historico = historico.sort_values("ordem_data", kind="stable")

colunas = [
    "number", "incident_state", "sys_updated_at", "sys_mod_count",
    "resolved_at", "closed_at",
]
print(f"\nHistórico de {chamado}:")
print(historico[colunas].to_string(index=False))

print("\nPerguntas para discussão:")
print("1. Por que há dois registros Resolved para o mesmo chamado?")
print("2. O que significa closed_at já estar preenchido na linha New?")
print("3. Contar linhas Resolved mede quantos chamados foram resolvidos?")
