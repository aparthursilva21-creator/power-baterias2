from database import conectar

def cadastrar_bateria():
    print("\n--- CADASTRO DE NOVA BATERIA ---")
    nome = input("Nome do modelo (ex: Moura M60AD): ")
    amperagem = int(input("Amperagem (Ah): "))
    marca = input("Marca: ")
    preco = float(input("Preço de venda (R$): "))
    quantidade = int(input("Quantidade em estoque: "))
    garantia = int(input("Garantia (meses): "))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO produtos (nome, amperagem, marca, preco, quantidade, meses_garantia)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, amperagem, marca, preco, quantidade, garantia))
    
    conn.commit()
    conn.close()
    print(f"\n✅ Bateria '{nome}' cadastrada com sucesso!")

def listar_estoque():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, amperagem, marca, preco, quantidade FROM produtos")
    baterias = cursor.fetchall()
    conn.close()

    print("\n" + "="*58)
    print("           POWER BATERIAS - ESTOQUE ATUAL           ")
    print("="*58)
    print(f"{'ID':<4} | {'Nome':<22} | {'Amp':<5} | {'Preço':<10} | {'Qtd':<4}")
    print("-" * 58)
    for b in baterias:
        print(f"{b[0]:<4} | {b[1]:<22} | {b[2]:<5} | R$ {b[4]:<7.2f} | {b[5]:<4}")
    print("="*58)
def editar_bateria():
    listar_estoque()
    print("\n--- EDITAR / AJUSTAR BATERIA (ÁREA ADM) ---")
    try:
        id_prod = int(input("Digite o ID da bateria que deseja editar: "))
    except ValueError:
        print("\n❌ ID inválido!")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, amperagem, marca, preco, quantidade, meses_garantia FROM produtos WHERE id = ?", (id_prod,))
    prod = cursor.fetchone()

    if not prod:
        print("\n❌ Bateria não encontrada!")
        conn.close()
        return

    print(f"\nEditando: {prod[0]} (Atual: {prod[4]} un | R$ {prod[3]:.2f})")
    print("👉 Pressione ENTER para manter o valor atual.")

    novo_nome = input(f"Novo nome [{prod[0]}]: ").strip() or prod[0]
    
    amp_in = input(f"Nova amperagem [{prod[1]} Ah]: ").strip()
    nova_amperagem = int(amp_in) if amp_in else prod[1]

    nova_marca = input(f"Nova marca [{prod[2]}]: ").strip() or prod[2]

    preco_in = input(f"Novo preço [R$ {prod[3]:.2f}]: ").strip()
    novo_preco = float(preco_in) if preco_in else prod[3]

    qtd_in = input(f"Nova quantidade no estoque [{prod[4]}]: ").strip()
    nova_quantidade = int(qtd_in) if qtd_in else prod[4]

    garantia_in = input(f"Nova garantia [{prod[5]} meses]: ").strip()
    nova_garantia = int(garantia_in) if garantia_in else prod[5]

    cursor.execute("""
    UPDATE produtos 
    SET nome = ?, amperagem = ?, marca = ?, preco = ?, quantidade = ?, meses_garantia = ?
    WHERE id = ?
    """, (novo_nome, nova_amperagem, nova_marca, novo_preco, nova_quantidade, nova_garantia, id_prod))

    conn.commit()
    conn.close()
    print(f"\n✅ Bateria ID {id_prod} atualizada com sucesso!")