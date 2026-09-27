import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página e tema
st.set_page_config(
    page_title="Power Baterias - Gestão Oficial",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Personalizada (CSS da Power Baterias)
st.markdown("""
    <style>
    /* Estilo do fundo e cores principais */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Botões da marca */
    .stButton>button {
        background-color: #ffcc00 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
    }
    .stButton>button:hover {
        background-color: #e6b800 !important;
        color: #000000 !important;
    }
    
    /* Destaques e Caixas do Dashboard */
    [data-testid="stMetricValue"] {
        color: #ffcc00 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    
    /* Menus laterais */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #ffcc00 !important;
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
    conn.close()

inicializar_banco()

# --- SISTEMA DE LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = None

if not st.session_state["logado"]:
    st.markdown("<h1 style='text-align: center;'>⚡ POWER BATERIAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Portal de Gestão & Vendas</h3>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("🔐 Acessar o Sistema", use_container_width=True):
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

# --- MENU LATERAL PERSONALIZADO ---
st.sidebar.markdown("## ⚡ Power Baterias")
st.sidebar.caption(f"Operador: **{st.session_state['perfil']}**")
st.sidebar.write("---")

if st.session_state["perfil"] == "ADM":
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque", "🛡️ Consultar Garantia", "📄 Histórico", "📊 Relatório ADM"])
else:
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque", "🛡️ Consultar Garantia", "📄 Histórico"])

st.sidebar.write("---")
if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state["logado"] = False
    st.rerun()

# --- ABA 1: NOVA VENDA ---
if menu == "🛒 Nova Venda":
    st.header("🛒 Lançamento de Venda")
    
    conn = conectar()
    df_prods = pd.read_sql_query("SELECT id, nome, amperagem, preco, quantidade, meses_garantia FROM produtos", conn)
    conn.close()

    if df_prods.empty:
        st.warning("Nenhum produto cadastrado no estoque!")
    else:
        lista_prods = [f"ID {row['id']} - {row['nome']} ({row['amperagem']}Ah) - R$ {row['preco']:.2f} | Est: {row['quantidade']}" for _, row in df_prods.iterrows()]
        prod_selecionado = st.selectbox("Selecione a Bateria", lista_prods)
        id_prod = int(prod_selecionado.split(" ")[1])
        
        col1, col2 = st.columns(2)
        with col1:
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            vendedor = st.text_input("Nome do Vendedor")
            pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
            parcelas = st.selectbox("Parcelas", [f"{i}x" for i in range(1, 13)]) if pagamento == "Cartão de Crédito" else "1x"
        
        with col2:
            cliente = st.text_input("Nome do Cliente (Para Garantia)")
            cpf = st.text_input("CPF/CNPJ (Opcional)")
            placa = st.text_input("Placa do Veículo (Opcional)")
            serie = st.text_input("Nº de Série da Bateria (Opcional)")

        if st.button("✅ Finalizar Venda e Emitir Garantia", use_container_width=True):
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
                st.success(f"Venda registrada com sucesso! Total: R$ {total:.2f}")

# --- ABA 2: ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque de Baterias")
    conn = conectar()
    df_estoque = pd.read_sql_query("SELECT id AS 'ID', nome AS 'Modelo/Nome', amperagem AS 'Amp (Ah)', marca AS 'Marca', preco AS 'Preço (R$)', quantidade AS 'Qtd Est.', meses_garantia AS 'Garantia (Meses)' FROM produtos", conn)
    conn.close()
    
    st.dataframe(df_estoque, use_container_width=True)

# --- ABA 3: GARANTIA ---
elif menu == "🛡️ Consultar Garantia":
    st.header("🛡️ Consulta de Garantias e Clientes")
    termo = st.text_input("🔍 Digite o Nome do Cliente, Placa do Carro ou Nº de Série")
    
    if termo:
        conn = conectar()
        df_garantia = pd.read_sql_query("""
            SELECT id, data_hora, cliente_nome, produto_nome, amperagem, veiculo_placa, numero_serie, meses_garantia 
            FROM vendas 
            WHERE cliente_nome LIKE ? OR veiculo_placa LIKE ? OR numero_serie LIKE ?
        """, conn, params=(f"%{termo}%", f"%{termo}%", f"%{termo}%"))
        conn.close()

        if df_garantia.empty:
            st.warning("Nenhum registro encontrado para a busca realizada.")
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
                    "Status Garantia": status,
                    "Prazo Restante": tempo_str
                })

            st.dataframe(pd.DataFrame(resultados), use_container_width=True)

# --- ABA 4: HISTÓRICO ---
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

# --- ABA 5: RELATÓRIO ADM ---
elif menu == "📊 Relatório ADM":
    st.header("📊 Painel de Controle - Power Baterias")
    
    conn = conectar()
    totais = pd.read_sql_query("SELECT SUM(valor_total) as faturado, SUM(quantidade) as un_vendidas FROM vendas", conn)
    df_vendas = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", conn)
    conn.close()

    fat = totais['faturado'].iloc[0] or 0.0
    qtd_un = totais['un_vendidas'].iloc[0] or 0

    col1, col2 = st.columns(2)
    col1.metric("💰 Faturamento Total", f"R$ {fat:,.2f}")
    col2.metric("🔋 Baterias Vendidas", f"{qtd_un} Unidades")

    st.write("---")
    st.subheader("Gerenciamento do Estoque")
    with st.expander("➕ Cadastrar Nova Bateria no Estoque"):
        with st.form("cad_prod"):
            f_nome = st.text_input("Nome do Modelo (ex: Moura M60AD)")
            f_amp = st.number_input("Amperagem (Ah)", min_value=1, value=60)
            f_marca = st.text_input("Marca")
            f_preco = st.number_input("Preço de Venda (R$)", min_value=0.0, value=350.0)
            f_qtd = st.number_input("Estoque Inicial", min_value=0, value=10)
            f_garantia = st.number_input("Garantia (Meses)", min_value=1, value=18)
            
            if st.form_submit_button("Salvar no Banco de Dados"):
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO produtos (nome, amperagem, marca, preco, quantidade, meses_garantia) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (f_nome, f_amp, f_marca, f_preco, f_qtd, f_garantia))
                conn.commit()
                conn.close()
                st.success("Nova bateria salva com sucesso!")
                st.rerun()

    st.subheader("Relatório Completo")
    st.dataframe(df_vendas, use_container_width=True)
