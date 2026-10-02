import datetime
from database import conectar
from produtos import listar_estoque

def realizar_venda():
    listar_estoque()
    print("\n--- LANÇAR NOVA VENDA ---")
    
    id_prod = int(input("Digite o ID do produto vendido: "))
    qtd_venda = int(input("Quantidade vendida: "))
    vendedor = input("Nome do vendedor: ").strip().capitalize()
    pagamento = input("Forma de pagamento (PIX / Cartão / Dinheiro): ")

    print("\n--- DADOS DE GARANTIA E CLIENTE (Aperte Enter para pular) ---")
    cliente_nome = input("Nome do Cliente: ").strip().title() or "Não Informado"
    cliente_cpf = input("CPF/CNPJ do Cliente: ").strip() or "Não Informado"
    veiculo_placa = input("Placa do Veículo: ").strip().upper() or "Não Informada"
    numero_serie = input("Número de Série da Bateria (S/N): ").strip().upper() or "S/N"

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, preco, quantidade FROM produtos WHERE id = ?", (id_prod,))
    produto = cursor.fetchone()

    if not produto:
        print("\n❌ Produto não encontrado!")
        conn.close()
        return

    nome, preco, qtd_atual = produto

    if qtd_venda > qtd_atual:
        print(f"\n❌ Estoque insuficiente! Restam apenas {qtd_atual} unidades.")
        conn.close()
        return

    nova_qtd = qtd_atual - qtd_venda
    cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_qtd, id_prod))

    total = preco * qtd_venda
    data_hoje = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
    INSERT INTO vendas (
        data_hora, vendedor, produto_nome, quantidade, valor_total, 
        forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, numero_serie
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data_hoje, vendedor, nome, qtd_venda, total, pagamento, cliente_nome, cliente_cpf, veiculo_placa, numero_serie))

    conn.commit()
    conn.close()

    print("\n" + "="*45)
    print("       COMPROVANTE DE VENDA - POWER BATERIAS       ")
    print("="*45)
    print(f"Data/Hora:  {data_hoje}")
    print(f"Vendedor:   {vendedor}")
    print(f"Cliente:    {cliente_nome} (CPF: {cliente_cpf})")
    print(f"Veículo:    Placa {veiculo_placa}")
    print(f"Nº Série:   {numero_serie}")
    print(f"Produto:    {nome} (x{qtd_venda})")
    print(f"Total:      R$ {total:.2f}")
    print(f"Pagamento:  {pagamento}")
    print("="*45 + "\n")

def consultar_garantia():
    busca = input("\nDigite a PLACA do veículo ou o NÚMERO DE SÉRIE: ").strip().upper()
    
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, data_hora, cliente_nome, produto_nome, veiculo_placa, numero_serie, vendedor
        FROM vendas
        WHERE veiculo_placa = ? OR numero_serie = ?
    """, (busca, busca))
    
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("\n❌ Nenhuma garantia ou venda encontrada para esse termo!")
        return

    print("\n" + "="*60)
    print("           🛡️ CERTIFICADO DE GARANTIA ENCONTRADO          ")
    print("="*60)
    for r in resultados:
        print(f"ID Venda:    {r[0]}")
        print(f"Data Venda:  {r[1]}")
        print(f"Cliente:     {r[2]}")
        print(f"Modelo:      {r[3]}")
        print(f"Placa Carro: {r[4]}")
        print(f"Nº Série:    {r[5]}")
        print(f"Vendedor:    {r[6]}")
        print("-" * 60)
    print("="*60 + "\n")

def relatorio_vendas():
    conn = conectar()
    cursor = conn.cursor()

    print("\n" + "="*50)
    print("        📊 FATURAMENTO E VENDEDORES       ")
    print("="*50)

    cursor.execute("SELECT SUM(valor_total), SUM(quantidade) FROM vendas")
    total_rs, total_qtd = cursor.fetchone()
    
    total_rs = total_rs if total_rs else 0.0
    total_qtd = total_qtd if total_qtd else 0

    print(f"💰 Total Faturado: R$ {total_rs:.2f}")
    print(f"📦 Baterias Vendidas: {total_qtd} unidades")
    print("-" * 50)

    print("🏆 DESEMPENHO POR VENDEDOR:")
    cursor.execute("""
        SELECT 
            vendedor, 
            SUM(quantidade) as total_qtd, 
            SUM(valor_total) as total_rs,
            GROUP_CONCAT(produto_nome, ', ') as itens
        FROM vendas 
        GROUP BY LOWER(vendedor) 
        ORDER BY total_rs DESC
    """)
    vendedores = cursor.fetchall()

    for v in vendedores:
        nome_vendedor = v[0].capitalize()
        qtd = v[1]
        valor = v[2]
        produtos = v[3]
        print(f"• {nome_vendedor}: {qtd} bateria(s) | Total: R$ {valor:.2f}")
        print(f"  └─ Itens vendidos: {produtos}\n")

    print("="*50 + "\n")
    conn.close()

def listar_vendas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, data_hora, vendedor, produto_nome, quantidade, valor_total, forma_pagamento FROM vendas")
    vendas = cursor.fetchall()
    conn.close()

    print("\n" + "="*70)
    print("                POWER BATERIAS - HISTÓRICO DE VENDAS                ")
    print("="*70)
    print(f"{'ID':<4} | {'Data/Hora':<19} | {'Vendedor':<10} | {'Produto':<15} | {'Total':<9} | {'Pgto'}")
    print("-" * 70)
    for v in vendas:
        print(f"{v[0]:<4} | {v[1]:<19} | {v[2]:<10} | {v[3]:<15} | R$ {v[5]:<6.2f} | {v[6]}")
    print("="*70)

def gerenciar_vendas_adm():
    listar_vendas()
    print("\n--- EDICÃO / CANCELAMENTO DE VENDA (ADM) ---")
    try:
        id_venda = int(input("Digite o ID da venda que deseja alterar/cancelar: "))
    except ValueError:
        print("\n❌ ID inválido!")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, produto_nome, quantidade, valor_total, vendedor, veiculo_placa 
        FROM vendas WHERE id = ?
    """, (id_venda,))
    venda = cursor.fetchone()

    if not venda:
        print("\n❌ Venda não encontrada!")
        conn.close()
        return

    print(f"\nVenda selecionada: ID {venda[0]} | Produto: {venda[1]} (x{venda[2]}) | Total: R$ {venda[3]:.2f}")
    print("1. Cancelar/Excluir Venda (Devolve item ao estoque)")
    print("2. Alterar Valor Total da Venda")
    print("3. Voltar")
    
    opcao = input("\nEscolha o que deseja fazer: ").strip()

    if opcao == "1":
        confirmar = input(f"Tem certeza que deseja CANCELAR a venda ID {id_venda}? (S/N): ").strip().upper()
        if confirmar == "S":
            # 1. Devolve a quantidade para o estoque
            cursor.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE nome = ?", (venda[2], venda[1]))
            # 2. Apaga o registro da venda
            cursor.execute("DELETE FROM vendas WHERE id = ?", (id_venda,))
            conn.commit()
            print(f"\n✅ Venda ID {id_venda} cancelada e {venda[2]} unidade(s) devolvida(s) ao estoque!")

    elif opcao == "2":
        try:
            novo_valor = float(input(f"Digite o novo valor total (Atual R$ {venda[3]:.2f}): R$ "))
            cursor.execute("UPDATE vendas SET valor_total = ? WHERE id = ?", (novo_valor, id_venda))
            conn.commit()
            print(f"\n✅ Valor da venda ID {id_venda} atualizado para R$ {novo_valor:.2f}!")
        except ValueError:
            print("\n❌ Valor inválido!")

    conn.close()