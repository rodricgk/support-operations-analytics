"""Gera conferência de todos os campos importados, sem precisar de senha.

Grava SQL em data/processed/modelo/conferir_integridade.sql para executar no banco.
As duas colunas de ponto flutuante são verificadas com tolerância pelo SQL 02.
MD5 é usado apenas como checksum de transferência, não como proteção criptográfica.
"""
from pathlib import Path
import csv
import hashlib

RAIZ = Path(__file__).resolve().parents[1]
MODELO = RAIZ / 'data/processed/modelo'
CHAVES = {
    'calendario_fila': ['data'], 'chamados': ['number'], 'eventos': ['linha_csv'],
    'fotografias': ['data', 'number'], 'resumo_diario': ['data'],
}
BOOLEANOS = {
    'regressao_contador', 'evento_antes_abertura', 'contador_reutilizado',
    'sinalizado_temporal', 'opened_at_conflitante', 'opened_at_invalida',
    'resolved_at_conflitante', 'resolved_at_invalida', 'duracao_negativa',
    'elegivel_duracao', 'idade_valida',
}
EXCLUIDAS = {'duracao_resolucao_horas', 'idade_horas'}


def main():
    consultas = []
    for tabela, chaves in CHAVES.items():
        with (MODELO / f'{tabela}.csv').open(encoding='utf-8', newline='') as entrada:
            leitor = csv.DictReader(entrada)
            colunas = [c for c in leitor.fieldnames if c not in EXCLUIDAS]
            registros = list(leitor)
        registros.sort(key=lambda r: tuple(int(r[c]) if c == 'linha_csv' else r[c] for c in chaves))
        total = hashlib.md5()
        for r in registros:
            campos = []
            for c in colunas:
                valor = r[c].lower() if c in BOOLEANOS else r[c]
                if valor == '':
                    campos.append(b'-1:')
                else:
                    dados = valor.encode('utf-8')
                    campos.append(str(len(dados)).encode('ascii') + b':' + dados)
            total.update(hashlib.md5(b''.join(campos)).hexdigest().encode('ascii'))
        expressoes = [
            f"case when e.\"{c}\" is null then '-1:' else octet_length(e.\"{c}\"::text)::text || ':' || e.\"{c}\"::text end"
            for c in colunas
        ]
        expressao = ' || '.join('(' + e + ')' for e in expressoes)
        ordem = ', '.join(f'e."{c}"' for c in chaves)
        consultas.append(
            f"select '{tabela}' as tabela, '{total.hexdigest()}' as esperado, "
            f"md5(coalesce(string_agg(md5({expressao}), '' order by {ordem}), '')) as observado, "
            f"{len(registros)}::bigint as linhas_esperadas, count(*) as linhas_observadas "
            f'from analytics."{tabela}" e'
        )
    corpo = '\nunion all\n'.join(consultas)
    consulta = (
        '-- Gerado a partir dos CSVs locais. Não editar os checksums manualmente.\n'
        'with checksums as (\n' + corpo + '\n)\n'
        'select *, esperado = observado and linhas_esperadas = linhas_observadas as passou '
        'from checksums order by tabela;\n'
    )
    destino = MODELO / 'conferir_integridade.sql'
    destino.write_text(consulta, encoding='utf-8')
    print('Conferência SQL gerada para as cinco tabelas, sem credenciais.')


if __name__ == '__main__':
    main()
