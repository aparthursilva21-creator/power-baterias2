import sqlite3

# Conecta ao novo banco local
conn = sqlite3.connect("power_baterias_novo.db")
c = conn.cursor()

# 1. Cria tabela de produtos
c.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT NOT NULL,
        nome TEXT NOT NULL,
        amperagem INTEGER NOT NULL,
        marca TEXT NOT NULL,
        preco REAL NOT NULL,
        quantidade INTEGER NOT NULL,
        meses_garantia INTEGER DEFAULT 12,
        veiculo TEXT DEFAULT ''
    )
""")

# 2. Cria tabela de vendas
c.execute("""
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

# Catalogo completo resgatado
produtos_resgatados = [
    ("36/40/45/48 Ah", "Super Life 36Ah", 36, "Super Life", 0.0, 10, 12, "Veículos Populares"),
    ("36/40/45/48 Ah", "KF 40Ah", 40, "KF", 0.0, 10, 12, "Motos / Veículos Leves"),
    ("36/40/45/48 Ah", "Cral 45Ah", 45, "Cral", 0.0, 10, 12, "Celta, Ka, Fit"),
    ("36/40/45/48 Ah", "Moura 48Ah", 48, "Moura", 0.0, 10, 12, "Gol, Palio, Uno"),
    ("36/40/45/48 Ah", "Heliar 48Ah", 48, "Heliar", 0.0, 10, 12, "Gol, Palio, Uno"),
    ("50 Ah Caixa Alta", "Super Life 50Ah Caixa Alta", 50, "Super Life", 0.0, 10, 12, "Ford / Honda"),
    ("50 Ah Caixa Alta", "KF 52Ah Caixa Alta", 52, "KF", 0.0, 10, 12, "Ford / Honda"),
    ("50 Ah Caixa Alta", "Cral 52Ah Caixa Alta", 52, "Cral", 0.0, 10, 12, "Ford / Honda"),
    ("50 Ah Caixa Alta", "América 50Ah Caixa Alta", 50, "América", 0.0, 10, 12, "Ford / Honda"),
    ("50 Ah Caixa Alta", "Moura 50Ah Caixa Alta", 50, "Moura", 0.0, 10, 12, "Fiesta, EcoSport, Ka"),
    ("50 Ah Caixa Alta", "Heliar 50Ah Caixa Alta", 50, "Heliar", 0.0, 10, 12, "Fiesta, EcoSport, Ka"),
    ("60 Ah Padrão", "Super Life 60Ah", 60, "Super Life", 0.0, 10, 12, "Carros de Passeio Médios"),
    ("60 Ah Padrão", "KF 60Ah", 60, "KF", 0.0, 10, 12, "Carros de Passeio Médios"),
    ("60 Ah Padrão", "Cral 60Ah", 60, "Cral", 0.0, 10, 12, "Carros de Passeio Médios"),
    ("60 Ah Padrão", "América 60Ah", 60, "América", 0.0, 10, 12, "Carros de Passeio Médios"),
    ("60 Ah Padrão", "Moura 60Ah", 60, "Moura", 0.0, 10, 12, "Civic, Corolla, Onix, HB20, Fox"),
    ("60 Ah Padrão", "Heliar 60Ah", 60, "Heliar", 0.0, 10, 12, "Civic, Corolla, Onix, HB20, Fox"),
    ("70 Ah", "Super Life 70Ah", 70, "Super Life", 0.0, 10, 12, "SUVs e Utilitários"),
    ("70 Ah", "Cral 70Ah", 70, "Cral", 0.0, 10, 12, "SUVs e Utilitários"),
    ("70 Ah", "América 70Ah", 70, "América", 0.0, 10, 12, "SUVs e Utilitários"),
    ("70 Ah", "Moura 70Ah", 70, "Moura", 0.0, 10, 12, "SUVs, Pickups, Compass, Renegade"),
    ("70 Ah", "Heliar 70Ah", 70, "Heliar", 0.0, 10, 12, "SUVs, Pickups, Compass, Renegade"),
    ("Linha EFB / Start Stop", "Moura 60Ah EFB Start Stop", 60, "Moura", 0.0, 10, 12, "Renegade, Argo, Toro, Golf"),
    ("Linha EFB / Start Stop", "Heliar 60Ah EFB Start Stop", 60, "Heliar", 0.0, 10, 12, "Renegade, Argo, Toro, Golf")
]

# Insere produtos sem duplicar
for p in produtos_resgatados:
    c.execute("SELECT id FROM produtos WHERE nome = ?", (p[1],))
    if not c.fetchone():
        c.execute("""
            INSERT INTO produtos (categoria, nome, amperagem, marca, preco, quantidade, meses_garantia, veiculo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

# Restaura o histórico de vendas recuperado
c.execute("SELECT id FROM vendas WHERE produto_nome = 'Heliar 48Ah'")
if not c.fetchone():
    c.execute("""
        INSERT INTO vendas (data_hora, vendedor, produto_nome, quantidade, preco_original, desconto, valor_total, forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, veiculo_modelo, numero_serie, parcelas, amperagem, meses_garantia)
        VALUES ('27/09/2026 10:20:17', 'Atendente', 'Heliar 48Ah', 1, 0.0, 0.0, 0.0, 'PIX', 'Consumidor Não Identificado', 'Não Informado', 'Não Informado', 'Gol, Palio, Uno', 'Não Informado', '1x', 48, 12)
    """)

conn.commit()
conn.close()
print("Restauração local concluída com sucesso!")