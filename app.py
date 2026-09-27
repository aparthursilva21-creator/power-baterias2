import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página e tema
st.set_page_config(
    page_title="Power Baterias+",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização no padrão visual da fachada da Power Baterias (Verde Heliar + Clean)
st.markdown("""
    <style>
    /* Estilo Geral */
    .stApp {
        background-color: #f8f9fa;
        color: #1e1e1e;
    }
    
    /* Topo e Cabeçalhos Verde Heliar */
    h1, h2, h3 {
        color: #1b8036 !important;
        font-weight: 700 !important;
    }
    
    /* Botões Verde Heliar */
    .stButton>button {
        background-color: #1b8036 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #146329 !important;
        color: #ffffff !important;
    }
    
    /* Indicadores de Métricas */
    [data-testid="stMetricValue"] {
        color: #1b8036 !important;
        font-size: 2.2rem !important;
        font-weight: bold !important;
    }
    
    /* Menu Lateral */
    section[data-testid="stSidebar"] {
        background-color: #1e2229 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Caixas de Alerta e Expander */
    .stAlert {
        border-radius: 8px !important;
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

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = None

if not st.session_state["logado"]:
    st.markdown("<h1 style='text-align: center; font-size: 2.8rem;'>⚡ POWER BATERIAS+</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>DISK BATERIAS: (99) 9519-1090</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔑 Acesso ao Sistema")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar", use_container_width=True):
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
st.sidebar.markdown("## ⚡ POWER BATERIAS+")
st.sidebar.caption("📞 DISK BATERIAS: (99) 9519-1090")
st.sidebar.caption(f"Perfil: **{st.session_state['perfil']}**")
st.sidebar.write("---")

if st.session_state["perfil"] == "ADM":
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque", "🛡️ Consultar Garantia", "📄 Histórico", "📊 Relatório & Carga ADM"])
else:
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque", "🛡️ Consultar Garantia", "📄 Histórico"])

st.sidebar.write("---")
if st.sidebar.button("🚪 Sair"):
    st.session_state["logado"] = False
    st.rerun()

# --- ABA 1: NOVA VENDA ---
if menu == "🛒 Nova Venda":
    st.header("🛒 Lançamento de Venda")
    
    conn = conectar()
    df_prods = pd.read_sql_query("SELECT id, nome, amperagem, preco, quantidade, meses_garantia FROM produtos", conn)
    conn.close()

    if df_prods.empty:
        st.warning("Nenhuma bateria cadastrada no estoque! Vá na aba ADM para cadastrar ou carregar a lista de baterias.")
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
                st.success(f"Venda registrada com sucesso! Total: R$ {total:.2f}")

# --- ABA 2: ESTOQUE ---
elif menu == "📦 Estoque":
    st.header("📦 Estoque Atual")
    conn = conectar()
    df_estoque = pd.read_sql_query("SELECT id AS 'ID', nome AS 'Modelo/Nome', amperagem AS 'Amp (Ah)', marca AS 'Marca', preco AS 'Preço (R$)', quantidade AS 'Qtd Est.', meses_garantia AS 'Garantia (Meses)' FROM produtos", conn)
    conn.close()
    
    st.dataframe(df_estoque, use_container_width=True)

# --- ABA 3: GARANTIA ---
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

# --- ABA 5: RELATÓRIO E CARGA EM MASSA ADM ---
elif menu == "📊 Relatório & Carga ADM":
    st.header("📊 Painel ADM & Gerenciamento de Estoque")
    
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
    st.subheader("📥 Adicionar Baterias em Massa")

    tab1, tab2, tab3 = st.tabs(["🚀 Carga Automática Padrão", "📁 Importar Planilha (Excel/CSV)", "➕ Cadastrar Unidade"])

    with tab1:
        st.write("Clique no botão abaixo para cadastrar automaticamente os modelos mais vendidos (Heliar, Moura, Cral, etc.):")
        if st.button("⚡ Inserir Modelos Padrão no Estoque"):
            modelos_padrao = [
                ("Heliar HG60DD", 60, "Heliar", 450.00, 15, 24),
                ("Heliar HG50ED", 50, "Heliar", 380.00, 10, 24),
                ("Heliar HG70ND", 70, "Heliar", 520.00, 8, 24),
                ("Moura M60AD", 60, "Moura", 440.00, 15, 18),
                ("Moura M50ED", 50, "Moura", 370.00, 10, 18),
                ("Cral CL60DD", 60, "Cral", 320.00, 20, 15),
                ("Bateria Moto 6Ah", 6, "Heliar", 180.00, 12, 12),
            ]
            conn = conectar()
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO produtos (nome, amperagem, marca, preco, quantidade, meses_garantia)
                VALUES (?, ?, ?, ?, ?, ?)
            """, modelos_padrao)
            conn.commit()
            conn.close()
            st.success("Baterias inseridas com sucesso!")
            st.rerun()

    with tab2:
        st.write("Envie um arquivo Excel (.xlsx) ou CSV com as colunas: `nome`, `amperagem`, `marca`, `preco`, `quantidade`, `meses_garantia`")
        arquivo = st.file_uploader("Escolha a planilha", type=["csv", "xlsx"])
        if arquivo is not None:
            try:
                if arquivo.name.endswith(".csv"):
                    df_upload = pd.read_csv(arquivo)
                else:
                    df_upload = pd.read_excel(arquivo)
                
                st.dataframe(df_upload.head(), use_container_width=True)
                
                if st.button("Confirmar Importação da Planilha"):
                    conn = conectar()
                    df_upload.to_sql("produtos", conn, if_exists="append", index=False)
                    conn.close()
                    st.success("Todas as baterias da planilha foram importadas com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao processar planilha: {e}")

    with tab3:
        with st.form("cad_manual"):
            f_nome = st.text_input("Modelo/Nome (ex: Heliar 60Ah)")
            f_amp = st.number_input("Amperagem (Ah)", min_value=1, value=60)
            f_marca = st.text_input("Marca", value="Heliar")
            f_preco = st.number_input("Preço (R$)", min_value=0.0, value=400.0)
            f_qtd = st.number_input("Quantidade", min_value=1, value=10)
            f_garantia = st.number_input("Garantia (Meses)", min_value=1, value=24)
            if st.form_submit_button("Salvar Bateria"):
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO produtos (nome, amperagem, marca, preco, quantidade, meses_garantia)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (f_nome, f_amp, f_marca, f_preco, f_qtd, f_garantia))
                conn.commit()
                conn.close()
                st.success("Bateria cadastrada!")
                st.rerun()

    st.write("---")
    st.subheader("Histórico Completo de Vendas")
    st.dataframe(df_vendas, use_container_width=True)
