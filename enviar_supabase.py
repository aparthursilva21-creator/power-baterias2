import sqlite3
from supabase import create_client, Client

# Credenciais do Supabase
SUPABASE_URL = "https://pzyxmzhfqzfebzxpgkyy.supabase.co"
SUPABASE_KEY = "sb_publishable_aKrPEl7lz13LDqTSKcRghg_3Wugc8Ul"  # <--- Cole aqui a mesma chave do app.py

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Conecta ao banco SQLite local restaurado
conn = sqlite3.connect("power_baterias_novo.db")
c = conn.cursor()

print("Enviando produtos para o Supabase...")
c.execute("SELECT categoria, nome, amperagem, marca, preco, quantidade, meses_garantia, veiculo FROM produtos")
produtos = c.fetchall()

for p in produtos:
    data = {
        "categoria": p[0], 
        "nome": p[1], 
        "amperagem": int(p[2]), 
        "marca": p[3],
        "preco": float(p[4]), 
        "quantidade": int(p[5]), 
        "meses_garantia": int(p[6]), 
        "veiculo": p[7]
    }
    supabase.table("produtos").insert(data).execute()

print("Enviando histórico de vendas para o Supabase...")
c.execute("SELECT data_hora, vendedor, produto_nome, quantidade, preco_original, desconto, valor_total, forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, veiculo_modelo, numero_serie, parcelas, amperagem, meses_garantia FROM vendas")
vendas = c.fetchall()

for v in vendas:
    data = {
        "data_hora": v[0], 
        "vendedor": v[1], 
        "produto_nome": v[2], 
        "quantidade": int(v[3]),
        "preco_original": float(v[4]), 
        "desconto": float(v[5]), 
        "valor_total": float(v[6]), 
        "forma_pagamento": v[7],
        "cliente_nome": v[8], 
        "cliente_cpf": v[9], 
        "veiculo_placa": v[10], 
        "veiculo_modelo": v[11],
        "numero_serie": v[12], 
        "parcelas": v[13], 
        "amperagem": int(v[14]), 
        "meses_garantia": int(v[15])
    }
    supabase.table("vendas").insert(data).execute()

print("--- SUCESSO! Todos os produtos e vendas foram transferidos para a nuvem! ---")   