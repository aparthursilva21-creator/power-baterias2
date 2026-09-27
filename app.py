import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuração da página
st.set_page_config(
    page_title="Power Baterias+",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização no padrão Dark + Verde Neon (Idêntico à Logo)
st.markdown("""
    <style>
    /* Fundo Geral */
    .stApp {
        background-color: #0d0f12;
        color: #e6e6e6;
    }
    
    /* Destaques e Títulos */
    h1, h2, h3 {
        color: #39ff14 !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }
    
    /* Botões Padrão Verde Neon */
    .stButton>button {
        background-color: #28a745 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #39ff14 !important;
        color: #000000 !important;
    }
    
    /* Indicadores Faturamento e Vendas */
    [data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-size: 2.2rem !important;
        font-weight: bold !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #16191e !important;
        border-right: 1px solid #28a745;
    }
    
    /* Tabelas */
    [data-testid="stDataFrame"] {
        background-color: #16191e;
        border-radius: 8px;
    }
    
    </style>
""", unsafe_allow_html=True)

SENHA_ADM = "1234"
SENHA_VENDEDOR = "venda123"

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
        )
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
            numero_serie TEXT,
            parcelas TEXT DEFAULT '1x',
            amperagem INTEGER DEFAULT 0,
            meses_garantia INTEGER DEFAULT 12
        )
    """)
    conn.commit()
    
    # Verificar se o estoque está vazio para popular o catálogo automático
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        catalogo_inicial = [
            # 36 a 48 Ah
            ("Heliar 48Ah", 48, "Heliar", 550.00, 10, 24),
            ("Moura 48Ah", 48, "Moura", 550.00, 10, 24),
            ("Cral 45Ah", 45, "Cral", 420.00, 10, 24),
            ("KF 40Ah", 40, "KF", 250.00, 10, 12),
            ("Super Life 36Ah", 36, "Super Life", 220.00, 10, 12),
            # 70 Ah
            ("Heliar 70Ah", 70, "Heliar", 760.00, 10, 24),
            ("Moura 70Ah", 70, "Moura", 760.00, 10, 24),
            ("América 70Ah", 70, "América", 590.00, 10, 18),
            ("Cral 70Ah", 70, "Cral", 580.00, 10, 24),
            ("Super Life 70Ah", 70, "Super Life", 390.00, 10, 12),
            # 75 Ah
            ("Heliar 75Ah", 75, "Heliar", 790.00, 10, 24),
            ("Moura 75Ah", 75, "Moura", 790.00, 10, 24),
            ("Cral 75Ah", 75, "Cral", 580.00, 10, 24),
            ("KF 75Ah", 75, "KF", 490.00, 10, 12),
            # 40 Slim JD
            ("Heliar 40Ah JD Slim", 40, "Heliar", 590.00, 10, 24),
            ("Moura 40Ah JD Slim", 40, "Moura", 590.00, 10, 24),
            ("Cral 40Ah JD Slim", 40, "Cral", 420.00, 10, 18),
            ("KF 40Ah JD Slim", 40, "KF", 350.00, 10, 12),
            # 72 EFB Start Stop
            ("Heliar 72Ah Start Stop EFB", 72, "Heliar", 1150.00, 10, 24),
            ("Moura 72Ah Start Stop EFB", 72, "Moura", 1150.00, 10, 24),
            # 90 Ah
            ("Heliar 90Ah", 90, "Heliar", 970.00, 10, 15),
            ("Moura 90Ah", 90, "Moura", 970.00, 10, 12),
            ("Cral 90Ah", 90, "Cral", 690.00, 10, 15),
            ("Biachine 90Ah", 90, "Biachine", 590.00, 10, 12),
            # 60 Ah
            ("Heliar 60Ah", 60, "Heliar", 550.00, 10, 24),
            ("Moura 60Ah", 60, "Moura", 550.00, 10, 24),
            ("América 60Ah", 60, "América", 450.00, 10, 18),
            ("Cral 60Ah", 60, "Cral", 430.00, 10, 24),
            ("KF 60Ah", 60, "KF", 330.00, 10, 12),
            ("Super Life 60Ah", 60, "Super Life", 330.00, 10, 12),
            # 50 Slim JD/JE
            ("Heliar 50Ah Slim JD/JE", 50, "Heliar", 630.00, 10, 24),
            ("Moura 50Ah Slim JD/JE", 50, "Moura", 590.00, 10, 24),
            ("América 50Ah Slim JD/JE", 50, "América", 490.00, 10, 18),
            ("Cral 50Ah Slim JD/JE", 50, "Cral", 450.00, 10, 18),
            ("KF 50Ah Slim JD/JE", 50, "KF", 390.00, 10, 12),
            # 50 EFB
            ("Heliar 50Ah EFB", 50, "Heliar", 890.00, 10, 24),
            ("Moura 50Ah EFB", 50, "Moura", 890.00, 10, 24),
            ("Cral 50Ah EFB", 50, "Cral", 690.00, 10, 24),
            # 60 EFB Start Stop
            ("Heliar 60Ah EFB Start Stop", 60, "Heliar", 890.00, 10, 24),
            ("Moura 60Ah EFB Start Stop", 60, "Moura", 890.00, 10, 24),
            # 50 Caixa Alta
            ("Heliar 50Ah Caixa Alta", 50, "Heliar", 550.00, 10, 24),
            ("Moura 50Ah Caixa Alta", 50, "Moura", 550.00, 10, 24),
            ("América 50Ah Caixa Alta", 50, "América", 470.00, 10, 18),
            ("Cral 52Ah Caixa Alta", 52, "Cral", 390.00, 10, 18),
            ("KF 52Ah Caixa Alta", 52, "KF", 350.00, 10, 12),
            ("Super Life 50Ah Caixa Alta", 50, "Super Life", 330.00, 10, 12),
        ]
        cursor.executemany("""
            INSERT INTO produtos (nome, amperagem, marca, preco, quantidade, meses_garantia)
            VALUES (?, ?, ?, ?, ?, ?)
        """, catalogo_inicial)
        conn.commit()

    conn.close()

inicializar_banco()

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = None

if not st.session_state["logado"]:
    if os.path.exists("log"):
        st.image("logo", width=350)
    else:
        st.markdown("<h1 style='text-align: center;'>⚡ HELIAR POWER BATERIAS</h1>", unsafe_allow_html=True)
        
    st.markdown("<p style='text-align: center; color: #39ff14;'>DISK BATERIAS: (61) 99519-1090</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.subheader("🔑 Acesso do Sistema")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Sistema", use_container_width=True):
            if senha == SENHA_ADM:
                st.session_state["logado"] = True
                st.session_state["perfil"] = "ADM"
                st.rerun()
            elif senha == SENHA_VENDEDOR:
                st.session_state["logado"] = True
                st.session_state["perfil"] = "Vendedor"
                st.rerun()
            else:
                st.error("Senha ou usuário incorretos!")
    st.stop()

# --- MENU LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.markdown("## ⚡ POWER BATERIAS")

st.sidebar.caption("📞 DISK BATERIAS: (99) 9519-1090")
st.sidebar.caption(f"Operador: **{st.session_state['perfil']}**")
st.sidebar.write("---")

if st.session_state["perfil"] == "ADM":
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque", "✏️ Editar Baterias", "🛡️ Consultar Garantia", "📄 Histórico", "📊 Painel ADM"])
else:
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque", "🛡️ Consultar Garantia", "📄 Histórico"])

st.sidebar.write("---")
if st.sidebar.button("🚪 Sair"):
    st.session_state["logado"] = False
    st.rerun()

# BANNER DE AVISO
st.markdown('<div class="banner-troca">🔄 VALORES A BASE DE TROCA 🔄</div>', unsafe_allow_html=True)

# --- ABA 1: NOVA VENDA ---
if menu == "🛒 Nova Venda":
    st.header("🛒 Lançamento de Venda")
    
    conn = conectar()
    df_prods = pd.read_sql_query("SELECT id, nome, amperagem, preco, quantidade, meses_garantia FROM produtos WHERE quantidade > 0", conn)
    conn.close()

    if df_prods.empty:
        st.warning("Nenhuma bateria disponível no estoque!")
    else:
        lista_prods = [f"ID {row['id']} - {row['nome']} ({row['amperagem']}Ah) - R$ {row['preco']:.2f} | Est: {row['quantidade']}" for _, row in df_prods.iterrows()]
        prod_selecionado = st.selectbox("Selecione a Bateria", lista_prods)
        id_prod = int(prod_selecionado.split(" ")[1])
        
        col1, col2 = st.columns(2)
        with col1:
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            vendedor = st.text_input("Vendedor")
            pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
            parcelas = st.selectbox("Parcelas", [f"{i}x" for i in range(1, 13)]) if pagamento == "Cartão de Crédito" else "1x"
        
        with col2:
            cliente = st.text_input("Nome do Cliente")
            cpf = st.text_input("CPF/CNPJ (Opcional)")
            placa = st.text_input("Placa do Veículo (Opcional)")
            serie = st.text_input("Nº de Série da Bateria (Opcional)")

        if st.button("✅ Finalizar Venda", use_container_width=True):
            dados_p = df_prods[df_prods['id'] == id_prod].iloc[0]
            
            if qtd > dados_p['quantidade']:
                st.error(f"Estoque insuficiente! Restam apenas {dados_p['quantidade']} unidades.")
            else:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (qtd, id_prod))
                
                total = dados_p['preco'] * qtd
                dt_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
                cursor.execute("""
                    INSERT INTO vendas (data_hora, vendedor, produto_nome, quantidade, valor_total, forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, numero_serie, parcelas, amperagem, meses_garantia)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (dt_hoje, vendedor or "Atendente", dados_p['nome'], qtd, total, pagamento, cliente or "Não Informado", cpf, placa.upper(), serie.upper(), parcelas, dados_p['amperagem'], dados_p['meses_garantia']))
                
                conn.commit()
                conn.close()
                st.success(f"Venda registrada! Total: R$ {total:.2f}")

# --- ABA 2: ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque Atual")
    conn = conectar()
    df_estoque = pd.read_sql_query("SELECT id AS 'ID', nome AS 'Modelo/Nome', amperagem AS 'Amp (Ah)', marca AS 'Marca', preco AS 'Preço (R$)', quantidade AS 'Qtd Est.', meses_garantia AS 'Garantia (Meses)' FROM produtos ORDER BY amperagem ASC", conn)
    conn.close()
    
    st.dataframe(df_estoque, use_container_width=True)

# --- ABA 3: EDITAR BATERIAS (ADM) ---
elif menu == "✏️ Editar Baterias":
    st.header("✏️ Alterar ou Excluir Baterias")
    
    conn = conectar()
    df_prods = pd.read_sql_query("SELECT * FROM produtos ORDER BY id ASC", conn)
    conn.close()
    
    if df_prods.empty:
        st.warning("Nenhuma bateria cadastrada.")
    else:
        opcoes = [f"ID {row['id']} - {row['nome']} (R$ {row['preco']:.2f})" for _, row in df_prods.iterrows()]
        selecionado = st.selectbox("Selecione a bateria que deseja alterar:", opcoes)
        
        id_sel = int(selecionado.split(" ")[1])
        item = df_prods[df_prods['id'] == id_sel].iloc[0]
        
        st.write("---")
        with st.form("form_editar"):
            e_nome = st.text_input("Nome/Modelo", value=item['nome'])
            col1, col2, col3 = st.columns(3)
            with col1:
                e_amp = st.number_input("Amperagem (Ah)", min_value=1, value=int(item['amperagem']))
                e_marca = st.text_input("Marca", value=item['marca'])
            with col2:
                e_preco = st.number_input("Preço (R$)", min_value=0.0, value=float(item['preco']))
                e_qtd = st.number_input("Quantidade em Estoque", min_value=0, value=int(item['quantidade']))
            with col3:
                e_garantia = st.number_input("Garantia (Meses)", min_value=1, value=int(item['meses_garantia']))
            
            c_salvar, c_deletar = st.columns(2)
            btn_salvar = st.form_submit_button("💾 Salvar Alterações")
            
            if btn_salvar:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE produtos 
                    SET nome = ?, amperagem = ?, marca = ?, preco = ?, quantidade = ?, meses_garantia = ?
                    WHERE id = ?
                """, (e_nome, e_amp, e_marca, e_preco, e_qtd, e_garantia, id_sel))
                conn.commit()
                conn.close()
                st.success("Bateria atualizada com sucesso!")
                st.rerun()

        if st.button("❌ Excluir Bateria do Sistema"):
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (id_sel,))
            conn.commit()
            conn.close()
            st.success("Bateria removida do sistema!")
            st.rerun()

# --- ABA 4: GARANTIA ---
elif menu == "🛡️ Consultar Garantia":
    st.header("🛡️ Consulta de Garantias")
    termo = st.text_input("🔍 Digite o Nome do Cliente, Placa do Veículo ou Nº de Série")
    
    if termo:
        conn = conectar()
        df_garantia = pd.read_sql_query("""
            SELECT id, data_hora, cliente_nome, produto_nome, amperagem, veiculo_placa, numero_serie, meses_garantia 
            FROM vendas 
            WHERE cliente_nome LIKE ? OR veiculo_placa LIKE ? OR numero_serie LIKE ?
        """, conn, params=(f"%{termo}%", f"%{termo}%", f"%{termo}%"))
        conn.close()

        if df_garantia.empty:
            st.warning("Nenhum registro encontrado.")
        else:
            hoje = datetime.now()
            resultados = []

            for _, r in df_garantia.iterrows():
                try:
                    dt_v = datetime.strptime(r['data_hora'], "%d/%m/%Y %H:%M:%S")
                except:
                    dt_v = hoje
                
                m_garantia = r['meses_garantia'] if r['meses_garantia'] else 12
                dt_venc = dt_v + timedelta(days=m_garantia * 30)
                restantes = (dt_venc - hoje).days

                status = "✅ NA GARANTIA" if restantes > 0 else "❌ VENCIDA"
                tempo_str = f"{restantes} dias restantes" if restantes > 0 else f"Vencida há {abs(restantes)} dias"

                resultados.append({
                    "ID Venda": r['id'],
                    "Data": dt_v.strftime("%d/%m/%Y"),
                    "Cliente": r['cliente_nome'],
                    "Produto": f"{r['produto_nome']} ({r['amperagem']}Ah)",
                    "Placa": r['veiculo_placa'],
                    "Nº Série": r['numero_serie'],
                    "Status": status,
                    "Prazo Garantia": tempo_str
                })

            st.dataframe(pd.DataFrame(resultados), use_container_width=True)

# --- ABA 5: HISTÓRICO ---
elif menu == "📄 Histórico":
    st.header("📄 Histórico Geral de Vendas")
    conn = conectar()
    df_hist = pd.read_sql_query("""
        SELECT id AS 'ID', data_hora AS 'Data/Hora', vendedor AS 'Vendedor', produto_nome AS 'Produto', 
               amperagem AS 'Amp (Ah)', quantidade AS 'Qtd', valor_total AS 'Total (R$)', 
               forma_pagamento AS 'Pagamento', parcelas AS 'Parc.', cliente_nome AS 'Cliente' 
        FROM vendas ORDER BY id DESC
    """, conn)
    conn.close()
    
    st.dataframe(df_hist, use_container_width=True)

# --- ABA 6: PAINEL ADM ---
elif menu == "📊 Painel ADM":
    st.header("📊 Painel ADM e Adicionar Novas Baterias")
    
    conn = conectar()
    totais = pd.read_sql_query("SELECT SUM(valor_total) as faturado, SUM(quantidade) as un_vendidas FROM vendas", conn)
    df_vendas = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", conn)
    conn.close()

    fat = totais['faturado'].iloc[0] or 0.0
    qtd_un = totais['un_vendidas'].iloc[0] or 0

    col1, col2 = st.columns(2)
    col1.metric("💰 Faturamento Total", f"R$ {fat:,.2f}")
    col2.metric("📦 Baterias Vendidas", f"{qtd_un} Unidades")

    st.write("---")
    st.subheader("➕ Cadastrar Nova Bateria")
    with st.form("cad_manual"):
        f_nome = st.text_input("Nome do Modelo (ex: Heliar 60Ah)")
        f_amp = st.number_input("Amperagem (Ah)", min_value=1, value=60)
        f_marca = st.text_input("Marca", value="Heliar")
        f_preco = st.number_input("Preço a Base de Troca (R$)", min_value=0.0, value=400.0)
        f_qtd = st.number_input("Quantidade em Estoque", min_value=1, value=10)
        f_garantia = st.number_input("Garantia (Meses)", min_value=1, value=24)
        
        if st.form_submit_button("Cadastrar Bateria"):
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produtos (nome, amperagem, marca, preco, quantidade, meses_garantia)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f_nome, f_amp, f_marca, f_preco, f_qtd, f_garantia))
            conn.commit()
            conn.close()
            st.success("Nova bateria cadastrada!")
            st.rerun()

    st.write("---")
    st.subheader("Relatório Completo de Vendas")
    st.dataframe(df_vendas, use_container_width=True)
