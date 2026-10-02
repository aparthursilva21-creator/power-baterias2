import sqlite3
import os

BANCO_NOVO = "power_baterias_novo.db"

def migrar_dados():
    # 1. Cria o novo banco limpo e padronizado
    conn_novo = sqlite3.connect(BANCO_NOVO)
    c_novo = conn_novo.cursor()

    c_novo.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL DEFAULT 'Geral',
            nome TEXT NOT NULL,
            amperagem INTEGER NOT NULL DEFAULT 0,
            marca TEXT NOT NULL DEFAULT '',
            preco REAL NOT NULL DEFAULT 0.0,
            quantidade INTEGER NOT NULL DEFAULT 0,
            meses_garantia INTEGER DEFAULT 12,
            veiculo TEXT DEFAULT ''
        )
    """)

    c_novo.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            vendedor TEXT NOT NULL,
            produto_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_original REAL NOT NULL DEFAULT 0.0,
            desconto REAL NOT NULL DEFAULT 0.0,
            valor_total REAL NOT NULL DEFAULT 0.0,
            forma_pagamento TEXT NOT NULL,
            cliente_nome TEXT DEFAULT 'Consumidor Não Identificado',
            cliente_cpf TEXT DEFAULT 'Não Informado',
            veiculo_placa TEXT DEFAULT 'Não Informado',
            veiculo_modelo TEXT DEFAULT 'Não Informado',
            numero_serie TEXT DEFAULT 'Não Informado',
            parcelas TEXT DEFAULT '1x',
            amperagem INTEGER DEFAULT 0,
            meses_garantia INTEGER DEFAULT 12
        )
    """)

    c_novo.execute("""
        CREATE TABLE IF NOT EXISTS fechamento_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_fechamento TEXT NOT NULL,
            responsavel TEXT NOT NULL,
            total_faturado REAL NOT NULL,
            total_vendas INTEGER NOT NULL
        )
    """)

    conn_novo.commit()

    # 2. Copiar Baterias dos bancos antigos
    bancos_antigos = ["power_baterias_3.db", "power_baterias2.db"]
    
    for db in bancos_antigos:
        if os.path.exists(db):
            print(f"Lendo baterias do banco: {db}...")
            conn_old = sqlite3.connect(db)
            c_old = conn_old.cursor()
            
            try:
                c_old.execute("SELECT nome, amperagem, marca, preco, quantidade, meses_garantia FROM produtos")
                prods = c_old.fetchall()
                for p in prods:
                    # Verifica se já não foi inserida
                    c_novo.execute("SELECT id FROM produtos WHERE nome = ?", (p[0],))
                    if not c_novo.fetchone():
                        c_novo.execute("""
                            INSERT INTO produtos (categoria, nome, amperagem, marca, preco, quantidade, meses_garantia, veiculo)
                            VALUES ('Geral', ?, ?, ?, ?, ?, ?, 'Veículos de Passeio / Utilitários')
                        """, (p[0], p[1], p[2], p[3], p[4], p[5]))
            except Exception as e:
                print(f"Aviso produtos em {db}: {e}")

            # 3. Copiar Histórico de Vendas dos bancos antigos
            try:
                c_old.execute("SELECT data_hora, vendedor, produto_nome, quantidade, valor_total, forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, numero_serie, parcelas, amperagem, meses_garantia FROM vendas")
                vendas = c_old.fetchall()
                for v in vendas:
                    c_novo.execute("""
                        INSERT INTO vendas (data_hora, vendedor, produto_nome, quantidade, preco_original, desconto, valor_total, forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, numero_serie, parcelas, amperagem, meses_garantia)
                        VALUES (?, ?, ?, ?, ?, 0.0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (v[0], v[1], v[2], v[3], v[4], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12]))
            except Exception as e:
                print(f"Aviso vendas em {db}: {e}")

            conn_old.close()

    conn_novo.commit()
    conn_novo.close()
    print("MIGRAÇÃO CONCLUÍDA COM SUCESSO! O arquivo 'power_baterias_novo.db' foi criado.")

if __name__ == "__main__":
    migrar_dados()