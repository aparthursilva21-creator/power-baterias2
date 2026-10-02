import sqlite3

def conectar():
    return sqlite3.connect("power_baterias.db")

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        amperagem INTEGER NOT NULL,
        marca TEXT NOT NULL,
        preco REAL NOT NULL,
        quantidade INTEGER NOT NULL,
        meses_garantia INTEGER DEFAULT 12
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_hora TEXT NOT NULL,
        vendedor TEXT NOT NULL,
        produto_nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor_total REAL NOT NULL,
        forma_pagamento TEXT NOT NULL,
        cliente_nome TEXT,
        cliente_cpf TEXT,
        veiculo_placa TEXT,
        numero_serie TEXT
    );
    """)

    conn.commit()
    conn.close()