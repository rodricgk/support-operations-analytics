"""Cruza exceções temporais, sem corrigir ou excluir eventos."""

from pathlib import Path
import pandas as pd

raiz = Path(__file__).resolve().parents[1]
df = pd.read_csv(raiz / "data/raw/incident_event_log.csv", dtype="string", keep_default_na=False)
df["linha_csv"] = df.index + 2  # Cabeçalho ocupa a linha 1.
for origem, destino in [
    ("opened_at", "abertura"), ("sys_updated_at", "atualizacao"),
    ("sys_created_at", "criacao"),
]:
    ausente = df[origem].isin(["", "?"])
    df[destino] = pd.to_datetime(
        df[origem].mask(ausente), format="%d/%m/%Y %H:%M", errors="raise"
    )
df["contador"] = pd.to_numeric(df["sys_mod_count"], errors="raise")

minutos = df.groupby(["number", "atualizacao"], sort=True).agg(
    minimo=("contador", "min"), maximo=("contador", "max")
)
minutos["anterior"] = minutos.groupby(level="number")["maximo"].transform(
    lambda s: s.cummax().shift()
)
ids_queda = set(minutos.loc[minutos.minimo.lt(minutos.anterior)].index.get_level_values(0))
antes = df.atualizacao.lt(df.abertura)
ids_antes = set(df.loc[antes, "number"])
reuso = df.groupby(["number", "contador"])["atualizacao"].nunique()
ids_reuso = set(reuso.loc[reuso.gt(1)].index.get_level_values(0))
ids = sorted(ids_queda | ids_antes)

resumo = pd.DataFrame({
    "number": ids,
    "regressao_contador": [n in ids_queda for n in ids],
    "evento_antes_abertura": [n in ids_antes for n in ids],
    "contador_reutilizado": [n in ids_reuso for n in ids],
})
print("CRUZAMENTO POR CHAMADO")
print(resumo.to_string(index=False))
print("Interseção:", len(ids_queda & ids_antes))
print("União:", len(ids))
print("Reuso e regressão atingem o mesmo conjunto:", ids_reuso == ids_queda)

colunas = ["linha_csv", "number", "incident_state", "abertura", "criacao", "atualizacao", "contador", "reopen_count"]
historicos = df.loc[df.number.isin(ids)].sort_values(["number", "atualizacao", "contador"])
print("\nHISTÓRICOS COMPLETOS")
print(historicos[colunas].to_string(index=False))

print("\nCONTEXTO DOS REGISTROS ANTERIORES À ABERTURA")
print("Eventos anteriores também à criação:", int((antes & df.atualizacao.lt(df.criacao)).sum()))
print("Criação ausente nesses eventos:", int(df.loc[antes, "criacao"].isna().sum()))
print("Datas de atualização:", sorted(df.loc[antes, "atualizacao"].dt.strftime("%Y-%m-%d").unique()))
print("Antecedência em minutos:", ((df.loc[antes, "abertura"] - df.loc[antes, "atualizacao"]).dt.total_seconds() / 60).tolist())

# Verificar se abertura e criação variam dentro do histórico extraído.
print("\nATRIBUTOS CONSTANTES NO HISTÓRICO DOS CASOS INVESTIGADOS")
print(historicos.groupby("number")[["opened_at", "sys_created_at"]].nunique().to_string())

destino = raiz / "data/processed/investigacao_temporal"
destino.mkdir(parents=True, exist_ok=True)
resumo.to_csv(destino / "chamados_sinalizados.csv", index=False)
historicos[colunas].to_csv(destino / "historicos.csv", index=False)
print("\nEvidências gravadas em", destino)
print("Os arquivos são diagnósticos; nenhum evento foi corrigido ou excluído.")
