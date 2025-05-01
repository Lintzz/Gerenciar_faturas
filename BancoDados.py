import sqlite3
import csv
from config import STORAGE_DIR

gasto_bd = STORAGE_DIR / 'gastos.db'


def criar_tabela_gastos(banco=gasto_bd):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        descricao TEXT,
        valor REAL,
        categoria TEXT
    )
    ''')

    conn.commit()
    conn.close()

def importar_csv_para_sqlite(caminho_csv=None, banco=gasto_bd):
    if caminho_csv is None:
        caminho_csv = STORAGE_DIR / 'formatado_limpo.csv'

    criar_tabela_gastos(banco)  # Garante que a tabela existe

    conn = sqlite3.connect(banco)
    cursor = conn.cursor()

    def converter_valor(valor_str):
        return float(valor_str.replace("R$", "").replace(".", "").replace(",", ".").strip())

    with open(caminho_csv, newline='', encoding='utf-8') as arquivo_csv:
        leitor = csv.reader(arquivo_csv)
        for linha in leitor:
            if len(linha) != 4:
                continue
            data, descricao, valor_str, categoria = linha
            valor = converter_valor(valor_str)
            cursor.execute('''
            INSERT INTO gastos (data, descricao, valor, categoria)
            VALUES (?, ?, ?, ?)
            ''', (data, descricao, valor, categoria))

    conn.commit()
    conn.close()