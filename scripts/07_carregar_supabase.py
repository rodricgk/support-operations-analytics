"""Carrega os CSVs da etapa 06 por COPY, sem apagar ou substituir registros.

A senha é solicitada no terminal e não é gravada. Execute sem outra importação ativa.
"""
from pathlib import Path
from getpass import getpass
from datetime import datetime, timezone
import argparse
import csv
import hashlib
import json
import sys

RAIZ = Path(__file__).resolve().parents[1]
MODELO = RAIZ / "data/processed/modelo"
TABELAS = {
    "calendario_fila": ("datas", ["data"]),
    "chamados": ("chamados", ["number"]),
    "eventos": ("eventos", ["linha_csv"]),
    "fotografias": ("fotografias", ["data", "number"]),
    "resumo_diario": ("datas", ["data"]),
}


def verificar_arquivos():
    manifesto = json.loads((MODELO / "validacao.json").read_text(encoding="utf-8"))
    fonte = RAIZ / "data/raw/incident_event_log.csv"
    if hashlib.sha256(fonte.read_bytes()).hexdigest() != manifesto["sha256_fonte"]:
        raise ValueError("Fonte bruta difere do manifesto. Refaça e revise a etapa 06.")
    arquivos = {}
    for tabela, (metrica, chaves) in TABELAS.items():
        caminho = MODELO / f"{tabela}.csv"
        with caminho.open(encoding="utf-8", newline="") as entrada:
            leitor = csv.reader(entrada)
            cabecalho = next(leitor)
            indices = [cabecalho.index(chave) for chave in chaves]
            ids = set()
            linhas = 0
            for registro in leitor:
                if len(registro) != len(cabecalho):
                    raise ValueError(f"{tabela}: quantidade inválida de campos.")
                identidade = tuple(registro[i] for i in indices)
                if not all(identidade) or identidade in ids:
                    raise ValueError(f"{tabela}: chave vazia ou repetida.")
                ids.add(identidade)
                linhas += 1
        if linhas != manifesto[metrica]:
            raise ValueError(f"{tabela}: contagem difere do manifesto.")
        arquivos[tabela] = {
            "linhas": linhas,
            "colunas": cabecalho,
            "sha256": hashlib.sha256(caminho.read_bytes()).hexdigest(),
        }
        print(f"{tabela}: {linhas:,} linhas; chaves válidas.", flush=True)
    return arquivos


def carregar(arquivos):
    import psycopg
    from psycopg import sql

    config = json.loads((RAIZ / "config/supabase-project.json").read_text(encoding="utf-8"))
    destino = config["session_pooler"]
    print(f"Destino: {config['name']} / {config['project_id']}", flush=True)
    senha = getpass("Senha do BANCO Supabase (não aparece ao digitar): ")
    if not senha:
        raise ValueError("Senha vazia; nenhuma conexão iniciada.")
    inseridas = {}
    # O contexto confirma tudo no final; uma falha reverte esta execução inteira.
    with psycopg.connect(
        host=destino["host"], port=destino["port"], dbname=destino["database"],
        user=destino["user"], password=senha, sslmode="require",
        connect_timeout=15, application_name="support_operations_carga",
    ) as conexao:
        del senha
        with conexao.cursor() as cursor:
            cursor.execute("set local lock_timeout = '5s'")
            cursor.execute("set local statement_timeout = '5min'")
            alvos = sql.SQL(", ").join(sql.Identifier("analytics", t) for t in TABELAS)
            cursor.execute(sql.SQL("lock table {} in share row exclusive mode").format(alvos))
            for tabela, (_, chaves) in TABELAS.items():
                dados = arquivos[tabela]
                cursor.execute(
                    "select column_name from information_schema.columns "
                    "where table_schema = 'analytics' and table_name = %s "
                    "order by ordinal_position", (tabela,)
                )
                if [linha[0] for linha in cursor.fetchall()] != dados["colunas"]:
                    raise ValueError(f"{tabela}: colunas do banco diferem do CSV.")
                alvo = sql.Identifier("analytics", tabela)
                temporaria = sql.Identifier("carga_" + tabela)
                cursor.execute(sql.SQL(
                    "create temporary table {} (like {} including all) on commit drop"
                ).format(temporaria, alvo))
                colunas = sql.SQL(", ").join(map(sql.Identifier, dados["colunas"]))
                copia = sql.SQL(
                    "copy {} ({}) from stdin with (format csv, header true, encoding 'UTF8')"
                ).format(temporaria, colunas)
                hash_enviado = hashlib.sha256()
                with (MODELO / f"{tabela}.csv").open("rb") as entrada:
                    with cursor.copy(copia) as copy:
                        while bloco := entrada.read(1024 * 1024):
                            hash_enviado.update(bloco)
                            copy.write(bloco)
                if hash_enviado.hexdigest() != dados["sha256"]:
                    raise ValueError(f"{tabela}: arquivo mudou durante a carga.")
                # EXCEPT compara todos os campos, incluindo NULLs.
                # Recusamos dados remotos diferentes; apenas completamos linhas ausentes.
                cursor.execute(sql.SQL(
                    "select exists (select * from {} except select * from {})"
                ).format(alvo, temporaria))
                if cursor.fetchone()[0]:
                    raise ValueError(f"{tabela}: banco contém dados diferentes do CSV; nenhuma substituição feita.")
                chave_sql = sql.SQL(", ").join(map(sql.Identifier, chaves))
                cursor.execute(sql.SQL(
                    "insert into {} ({}) select {} from {} on conflict ({}) do nothing"
                ).format(alvo, colunas, colunas, temporaria, chave_sql))
                inseridas[tabela] = cursor.rowcount
                cursor.execute(sql.SQL("select count(*) from {}").format(alvo))
                if cursor.fetchone()[0] != dados["linhas"]:
                    raise ValueError(f"{tabela}: total após a carga não confere.")
                print(f"{tabela}: {inseridas[tabela]:,} novas linhas preparadas.", flush=True)
            cursor.execute((RAIZ / "sql/02_validar_carga.sql").read_text(encoding="utf-8"))
            verificacoes = [
                dict(zip(("teste", "esperado", "observado", "passou"), linha))
                for linha in cursor.fetchall()
            ]
            falhas = [v["teste"] for v in verificacoes if not v["passou"]]
            if falhas:
                raise ValueError("Reconciliação falhou: " + ", ".join(falhas))
    relatorio = {
        "concluida_em_utc": datetime.now(timezone.utc).isoformat(),
        "project_id": config["project_id"],
        "arquivos": arquivos,
        "linhas_inseridas": inseridas,
        "verificacoes": verificacoes,
    }
    (MODELO / "carga_supabase.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Carga confirmada no Supabase; todas as verificações passaram.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verificar-arquivos", action="store_true",
                        help="Confere arquivos e chaves localmente; não acessa o banco.")
    args = parser.parse_args()
    arquivos = verificar_arquivos()
    if not args.verificar_arquivos:
        carregar(arquivos)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Operação interrompida. Confira o estado no banco antes de retomar.")
    except Exception as erro:
        # Não imprimir argumentos de conexão nem dados de linha retornados pelo servidor.
        if isinstance(erro, (ValueError, FileNotFoundError)):
            print(f"Interrompido: {erro}", file=sys.stderr)
        else:
            codigo = getattr(erro, "sqlstate", None)
            print(f"Falha: {type(erro).__name__}; SQLSTATE={codigo or 'indisponível'}. "
                  "Confira conexão, senha e disponibilidade do banco.", file=sys.stderr)
        sys.exit(1)
