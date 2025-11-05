"""Ferramenta de importação para popular o banco SQLite `produtos_bling`.

Este módulo fornece um utilitário de linha de comando que lê uma planilha em
formato CSV ou XLS/XLSX, cria/atualiza a tabela `produtos_bling` e insere os
registros definidos na planilha.
"""
from __future__ import annotations

import argparse
import pathlib
import sqlite3
import sys
from typing import Iterable, List

import pandas as pd


def read_planilha(caminho: pathlib.Path) -> pd.DataFrame:
    """Lê a planilha a partir do `caminho` informado.

    A leitura suporta arquivos com extensões `.csv`, `.xls` ou `.xlsx`.
    """
    sufixo = caminho.suffix.lower()

    if sufixo == ".csv":
        # Usa o engine ``python`` para permitir a detecção automática de delimitadores
        # (por exemplo, ``;``) a partir do conteúdo do arquivo, evitando que todo o
        # cabeçalho seja tratado como uma única coluna.
        dataframe = pd.read_csv(caminho, sep=None, engine="python")
    elif sufixo in {".xls", ".xlsx"}:
        dataframe = pd.read_excel(caminho)
    else:
        raise ValueError(
            "Formato de arquivo não suportado. Utilize arquivos .csv, .xls ou .xlsx."
        )

    if dataframe.empty:
        raise ValueError("A planilha está vazia e não possui dados para importar.")

    return dataframe


def preparar_nomes_colunas(colunas: Iterable[str]) -> List[str]:
    """Garante que os nomes das colunas sejam adequados para uso em SQL."""
    nomes_ajustados: List[str] = []
    colunas_existentes = set()

    for indice, coluna in enumerate(colunas, start=1):
        nome = str(coluna).strip()

        if not nome:
            nome = f"coluna_{indice}"

        nome_original = nome
        contador = 1
        while nome in colunas_existentes:
            contador += 1
            nome = f"{nome_original}_{contador}"

        colunas_existentes.add(nome)
        nomes_ajustados.append(nome)

    return nomes_ajustados


def escapar_identificador(identificador: str) -> str:
    """Escapa um identificador SQL utilizando aspas duplas."""
    return identificador.replace("\"", "\"\"")


def criar_tabela_produtos(cursor: sqlite3.Cursor, colunas: Iterable[str]) -> None:
    """Cria a tabela `produtos_bling` com as colunas especificadas.

    Caso a tabela já exista, ela é removida antes de ser recriada para garantir
    que a estrutura reflita exatamente a planilha fornecida.
    """
    cursor.execute("DROP TABLE IF EXISTS produtos_bling")

    colunas_sql = ", ".join(
        f'"{escapar_identificador(nome)}" TEXT' for nome in colunas
    )
    cursor.execute(f"CREATE TABLE produtos_bling ({colunas_sql})")


def inserir_registros(cursor: sqlite3.Cursor, colunas: List[str], dados: pd.DataFrame) -> None:
    """Insere os registros do `dados` na tabela `produtos_bling`."""
    placeholders = ", ".join(["?"] * len(colunas))
    colunas_sql = ", ".join(
        f'"{escapar_identificador(nome)}"' for nome in colunas
    )
    inserir_sql = f"INSERT INTO produtos_bling ({colunas_sql}) VALUES ({placeholders})"

    valores = [
        [None if pd.isna(valor) else valor for valor in linha]
        for linha in dados.to_numpy()
    ]
    cursor.executemany(inserir_sql, valores)


def importar_planilha(caminho_planilha: pathlib.Path, banco_dados: pathlib.Path) -> None:
    dataframe = read_planilha(caminho_planilha)
    colunas = preparar_nomes_colunas(dataframe.columns)
    dataframe.columns = colunas

    with sqlite3.connect(banco_dados) as conexao:
        cursor = conexao.cursor()
        criar_tabela_produtos(cursor, colunas)
        inserir_registros(cursor, colunas, dataframe)
        conexao.commit()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa uma planilha CSV/XLS para o banco produtos_bling."
    )
    parser.add_argument(
        "caminho_planilha",
        type=pathlib.Path,
        help="Caminho para o arquivo .csv, .xls ou .xlsx que será importado.",
    )
    parser.add_argument(
        "--banco",
        type=pathlib.Path,
        default=pathlib.Path("produtos_bling.db"),
        help="Arquivo de banco de dados SQLite que receberá os dados.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    argumentos = parse_args(argv)

    try:
        importar_planilha(argumentos.caminho_planilha, argumentos.banco)
    except Exception as erro:  # noqa: BLE001 - Erros exibidos ao usuário
        print(f"Erro ao importar planilha: {erro}", file=sys.stderr)
        raise SystemExit(1)

    print(
        "Importação concluída com sucesso!"
        f" Dados gravados em '{argumentos.banco.resolve()}'."
    )


if __name__ == "__main__":
    main()
