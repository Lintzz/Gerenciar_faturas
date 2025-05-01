import sqlite3
import csv
from config import STORAGE_DIR

def criar_db_e_tabela(ano, mes):
    nome_db = STORAGE_DIR / f"fatura_{ano}.db"
    conn = sqlite3.connect(nome_db)
    cursor = conn.cursor()

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {mes} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            descricao TEXT,
            valor REAL,
            categoria TEXT
        )
    ''')

    conn.commit()
    conn.close()

def importar_csv_para_sqlite(ano, mes, caminho_csv=None):
    if caminho_csv is None:
        caminho_csv = STORAGE_DIR / 'formatado_limpo.csv'

    criar_db_e_tabela(ano, mes)

    banco_path = STORAGE_DIR / f"fatura_{ano}.db"
    conn = sqlite3.connect(banco_path)
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
            cursor.execute(f'''
                INSERT INTO "{mes}" (data, descricao, valor, categoria)
                VALUES (?, ?, ?, ?)
            ''', (data, descricao, valor, categoria))

    conn.commit()
    conn.close()