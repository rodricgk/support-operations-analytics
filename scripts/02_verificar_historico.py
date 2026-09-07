"""Diagnóstico inicial do histórico. Não limpa nem altera o CSV original."""

from pathlib import Path
import pandas as pd

raiz = Path(__file__).resolve().parents[1]
df = pd.read_csv(
    raiz / "data/raw/incident_event_log.csv", dtype="string", keep_default_na=False
)

# As contagens por estado são de EVENTOS, não de chamados no estado atual.
print("EVENTOS POR ESTADO")
print(df["incident_state"].value_counts().to_string())

# Separar ausência de falha de conversão evita esconder erros com errors='coerce'.
print("\nDATAS: ausentes, inválidas, mínimo e máximo")
datas = {}
for coluna in ["opened_at", "sys_updated_at", "resolved_at", "closed_at"]:
    ausente = df[coluna].isin(["", "?"])
    convertida = pd.to_datetime(
        df[coluna].mask(ausente), format="%d/%m/%Y %H:%M", errors="coerce"
    )
    datas[coluna] = convertida
    invalidas = (~ausente & convertida.isna()).sum()
    print(coluna, int(ausente.sum()), int(invalidas), convertida.min(), convertida.max())

print("\nLINHAS EXATAMENTE IGUAIS (excedentes à primeira ocorrência)")
print(int(df.duplicated().sum()))

# Uma data com precisão de minuto pode não ordenar todos os eventos.
eventos = df.assign(data_evento=datas["sys_updated_at"])
chave = ["number", "data_evento"]
grupos = eventos.groupby(chave, dropna=False).agg(
    registros=("number", "size"), estados=("incident_state", "nunique")
)
empates = grupos.loc[grupos["registros"].gt(1)]
conflitos = empates.loc[empates["estados"].gt(1)]
print("\nEMPATES POR CHAMADO + HORÁRIO")
print("Grupos com empate:", len(empates))
print("Linhas envolvidas:", int(empates["registros"].sum()))
print("Chamados envolvidos:", empates.index.get_level_values("number").nunique())
print("Grupos com estados distintos:", len(conflitos))

if not conflitos.empty:
    numero, horario = conflitos.index[0]
    exemplo = eventos.loc[
        eventos["number"].eq(numero) & eventos["data_evento"].eq(horario),
        ["number", "sys_updated_at", "sys_mod_count", "incident_state"],
    ]
    print("\nEXEMPLO DE EMPATE COM ESTADOS DISTINTOS")
    print(exemplo.to_string(index=False))

print("\nCHAVE CANDIDATA: chamado + horário + contador de atualização")
chave_com_contador = chave + ["sys_mod_count"]
print("Linhas excedentes:", int(eventos.duplicated(chave_com_contador).sum()))

print("\nATUALIZAÇÕES ANTERIORES À ABERTURA (linhas)")
print(int((datas["sys_updated_at"] < datas["opened_at"]).sum()))
print("\nNão remover registros ou escolher desempates antes de interpretar os achados.")
