"""Verifica o contador antes de adotar uma ordem para os eventos."""

from pathlib import Path
import pandas as pd

raiz = Path(__file__).resolve().parents[1]
df = pd.read_csv(
    raiz / "data/raw/incident_event_log.csv", dtype="string", keep_default_na=False
)

ausente = df["sys_mod_count"].isin(["", "?"])
contador = pd.to_numeric(df["sys_mod_count"].mask(ausente), errors="coerce")
invalido = ~ausente & contador.isna()
negativo = contador.lt(0)
fracionario = contador.mod(1).ne(0) & contador.notna()
data = pd.to_datetime(
    df["sys_updated_at"], format="%d/%m/%Y %H:%M", errors="coerce"
)
print("VALIDADE DO CONTADOR (linhas)")
for nome, mascara in {
    "Ausentes": ausente, "Não numéricos": invalido,
    "Negativos": negativo, "Fracionários": fracionario,
    "Datas inválidas ou ausentes": data.isna(),
}.items():
    print(f"{nome}: {int(mascara.sum())}")

if (ausente | invalido | negativo | fracionario | data.isna()).any():
    raise ValueError("Investigar valores inválidos antes de analisar a sequência.")

eventos = df.assign(data_evento=data, contador=contador)

# Não ordenamos pelo contador para 'provar' que ele cresce: isso seria circular.
# Agrupamos cada minuto e comparamos seu mínimo com o maior contador de
# TODOS os minutos anteriores do mesmo chamado.
minutos = eventos.groupby(["number", "data_evento"], sort=True).agg(
    minimo=("contador", "min"), maximo=("contador", "max")
)
minutos["maior_anterior"] = minutos.groupby(level="number")["maximo"].transform(
    lambda serie: serie.cummax().shift()
)
quedas = minutos.loc[minutos["minimo"].lt(minutos["maior_anterior"])]
print("\nCONTADOR MENOR QUE UM VALOR DE HORÁRIO ANTERIOR")
print("Grupos chamado + horário:", len(quedas))
print("Chamados afetados:", quedas.index.get_level_values("number").nunique())
print(quedas.head(5).to_string())

reusos = eventos.groupby(["number", "contador"]).agg(
    horarios=("data_evento", "nunique")
)
reusos = reusos.loc[reusos["horarios"].gt(1)]
print("\nMESMO CONTADOR EM HORÁRIOS DIFERENTES")
print("Pares chamado + contador:", len(reusos))
print("Chamados afetados:", reusos.index.get_level_values("number").nunique())

chave = ["number", "data_evento", "contador"]
print("\nEMPATES RESTANTES COM CONTADOR NUMÉRICO")
print("Linhas excedentes:", int(eventos.duplicated(chave).sum()))

# Mostra um histórico problemático, caso exista, sem corrigir ou excluir nada.
if not quedas.empty:
    exemplo = quedas.index[0][0]
    print(f"\nHISTÓRICO PARA INVESTIGAÇÃO: {exemplo}")
    print(eventos.loc[eventos["number"].eq(exemplo),
        ["number", "data_evento", "contador", "incident_state"]
    ].sort_values(["data_evento", "contador"]).to_string(index=False))

print("\nUnicidade permite uma ordem determinística, mas não prova a ordem real.")
