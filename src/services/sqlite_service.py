import sqlite3
from src.config.settings import DB_FILE

def conectar_sqlite():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RASTREIO (
            codigo_rastreio TEXT PRIMARY KEY,
            data_envio TEXT
        );
    """)
    conn.commit()
    return conn

def buscar_sqlite():
    conn = conectar_sqlite()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo_rastreio, data_envio FROM RASTREIO")
    dados = cursor.fetchall()
    conn.close()
    return dados

def excluir_sqlite(codigo):
    conn = conectar_sqlite()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM RASTREIO WHERE codigo_rastreio = ?", (codigo,))
    conn.commit()
    conn.close()