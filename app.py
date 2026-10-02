import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

st.set_page_config(
    page_title="Power Baterias",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Dark
st.markdown("""
    <style>
    .stApp {
        background-color: #0d0f12;
        color: #e6e6e6;
    }
    h1, h2, h3 {
        color: #39ff14 !important;
        font-weight: 800 !important;
    }
    .stButton>button {
        background-color: #28a745 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 8px 16px !important;
    }
    .stButton>button:hover {
        background-color: #39ff14 !important;
        color: #000000 !important;
    }
    [data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #16191e !important;
        border-right: 1px solid #28a745;
    }
    </style>
""", unsafe_allow_html=True)

DB_NAME = "power_baterias_novo.db"

USUARIOS = {
    "arthur": {"senha": "Arthur123", "perfil": "ADM", "nome": "Arthur"},
    "sandro": {"senha": "1234", "perfil": "ADM", "nome": "Sandro"},
    "pedro": {"senha": "Pedro1234", "perfil": "Vendedor", "nome": "Pedro"},
    "wanderson": {"senha": "venda123", "perfil": "Vendedor", "nome": "Wanderson"},
}

def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS fechamento_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_fechamento TEXT NOT NULL,
            responsavel TEXT NOT NULL,
            total_faturado REAL NOT NULL,
            total_vendas INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def gerador_pdf_nota(dados):
    if not REPORTLAB_DISPONIVEL:
        return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    header_title = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#28a745'), alignment=0)
    nf_title = ParagraphStyle('NFTitle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#000000'), alignment=2)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Bold')

    topo = [
        [
            Paragraph("<b>POWER BATERIAS</b><br/><font size=8 color='#555555'>AUTOMOTIVAS E UTILITÁRIOS</font>", header_title),
            Paragraph(f"<b>COMPROVANTE DE VENDA</b><br/><b>Nº: #{dados.get('id', 0):06d}</b><br/>Data: {dados.get('data_hora', '')}", nf_title)
        ]
    ]
    story.append(Table(topo, colWidths=[320, 220]))
    story.append(Spacer(1, 10))

    dados_cliente = [
        [Paragraph("<b>DADOS DO CLIENTE E VEÍCULO</b>", ParagraphStyle('H', parent=body_bold, textColor=colors.white)), ""],
        [Paragraph(f"<b>Cliente:</b> {dados.get('cliente_nome', '')}", body_style), Paragraph(f"<b>CPF/CNPJ:</b> {dados.get('cliente_cpf', '')}", body_style)],
        [Paragraph(f"<b>Veículo:</b> {dados.get('veiculo_modelo', '')}", body_style), Paragraph(f"<b>Placa:</b> {dados.get('veiculo_placa', '')}", body_style)],
        [Paragraph(f"<b>Nº Série Bateria:</b> {dados.get('numero_serie', '')}", body_style), Paragraph(f"<b>Vendedor:</b> {dados.get('vendedor', '')}", body_style)],
    ]
    t_cli = Table(dados_cliente, colWidths=[270, 270])
    t_cli.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#16191e')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8f9fa')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#28a745')),
        ('INNERGRID', (0,1), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cli)
    story.append(Spacer(1, 12))

    desc_val = dados.get('desconto', 0.0) or 0.0
    desc_ajuste = f"R$ {abs(desc_val):.2f}" if desc_val >= 0 else f"+ R$ {abs(desc_val):.2f}"
    p_orig = dados.get('preco_original', dados.get('valor_total', 0.0)) or 0.0

    table_prod = [
        [Paragraph("<b>Item / Descrição</b>", body_bold), Paragraph("<b>Amp</b>", body_bold), Paragraph("<b>Qtd</b>", body_bold), Paragraph("<b>Preço Unit.</b>", body_bold), Paragraph("<b>Ajuste</b>", body_bold), Paragraph("<b>Total</b>", body_bold)],
        [
            Paragraph(str(dados.get('produto_nome', '')), body_style),
            Paragraph(f"{dados.get('amperagem', 0)}Ah", body_style),
            Paragraph(str(dados.get('quantidade', 1)), body_style),
            Paragraph(f"R$ {p_orig:.2f}", body_style),
            Paragraph(desc_ajuste, body_style),
            Paragraph(f"<b>R$ {dados.get('valor_total', 0.0):.2f}</b>", body_style)
        ]
    ]
    t_prod = Table(table_prod, colWidths=[220, 50, 40, 75, 65, 90])
    t_prod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#28a745')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_prod)
    story.append(Spacer(1, 10))

    pag_info = [
        [
            Paragraph(f"<b>Forma de Pagamento:</b> {dados.get('forma_pagamento', '')} ({dados.get('parcelas', '1x')})", body_style),
            Paragraph(f"<b>VALOR TOTAL: R$ {dados.get('valor_total', 0.0):.2f}</b>", ParagraphStyle('Tot', parent=body_bold, fontSize=11, alignment=2))
        ]
    ]
    t_pag = Table(pag_info, colWidths=[300, 240])
    t_pag.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eef9f1')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#28a745')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_pag)

    doc.build(story)
    buffer.seek(0)
    return buffer

def cancelar_venda(id_venda, produto_nome, quantidade):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE nome = ?", (quantidade, produto_nome))
    c.execute("DELETE FROM vendas WHERE id = ?", (id_venda,))
    conn.commit()
    conn.close()

def excluir_bateria(id_bateria):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM produtos WHERE id = ?", (id_bateria,))
    conn.commit()
    conn.close()

inicializar_banco()

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = None
    st.session_state["vendedor_nome"] = ""
    st.session_state["usuario_key"] = ""

if not st.session_state["logado"]:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300)
    else:
        st.markdown("<h1 style='text-align: center;'>HELIAR POWER BATERIAS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #39ff14;'>DISK BATERIAS: (61) 99519-1090</p>", unsafe_allow_html=True)
    st.write("---")
    
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.subheader("Acesso ao Sistema")
        usuario_input = st.text_input("Usuário").strip().lower()
        senha_input = st.text_input("Senha", type="password").strip()
        if st.button("Entrar", use_container_width=True):
            if usuario_input in USUARIOS and USUARIOS[usuario_input]["senha"] == senha_input:
                dados_usr = USUARIOS[usuario_input]
                st.session_state["logado"] = True
                st.session_state["perfil"] = dados_usr["perfil"]
                st.session_state["vendedor_nome"] = dados_usr["nome"]
                st.session_state["usuario_key"] = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
    st.stop()

# --- MODAIS ---
@st.dialog("Venda Finalizada! 🟢")
def modal_gerar_pdf(dados_venda):
    st.write(f"**Cliente:** {dados_venda['cliente_nome']}")
    st.write(f"**Bateria:** {dados_venda['produto_nome']}")
    st.write(f"**Valor Total:** R$ {dados_venda['valor_total']:.2f}")
    if REPORTLAB_DISPONIVEL:
        pdf_bytes = gerador_pdf_nota(dados_venda)
        st.download_button("📄 Baixar Nota Fiscal (PDF)", data=pdf_bytes, file_name=f"nota_{dados_venda['id']}.pdf", mime="application/pdf", use_container_width=True)

@st.dialog("Confirmar Cancelamento 🔴")
def modal_confirmar_cancelamento(id_venda, produto_nome, quantidade):
    st.write(f"Deseja cancelar a venda #{id_venda}?")
    if st.button("Sim, Cancelar Venda", use_container_width=True):
        cancelar_venda(id_venda, produto_nome, quantidade)
        st.toast("Venda cancelada com sucesso!", icon="✅")
        st.rerun()

# --- MENU LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.markdown("## POWER BATERIAS")

st.sidebar.caption("DISK BATERIAS: (61) 99519-1090")

opcoes_menu = ["Nova Venda", "Estoque Organizado", "Consultar Garantia"]
if st.session_state["perfil"] == "ADM":
    opcoes_menu += ["Fechamento de Caixa", "Editar Baterias", "Histórico", "Painel ADM"]

if "pagina_atual" not in st.session_state or st.session_state["pagina_atual"] not in opcoes_menu:
    st.session_state["pagina_atual"] = opcoes_menu[0]

menu = st.sidebar.radio("Navegação", opcoes_menu, key="pagina_atual")

st.sidebar.write("---")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

# --- ABA 1: NOVA VENDA ---
if menu == "Nova Venda":
    st.header("Lançamento de Venda")
    conn = sqlite3.connect(DB_NAME)
    df_prods = pd.read_sql_query("SELECT id, nome, amperagem, preco, quantidade, meses_garantia, veiculo FROM produtos", conn)
    conn.close()

    if df_prods.empty:
        st.warning("Nenhuma bateria no estoque!")
    else:
        opcoes_prods = [""] + [f"ID {row['id']} | {row['nome']} - R$ {float(row['preco']):.2f} (Estoque: {int(row['quantidade'])})" for _, row in df_prods.iterrows()]
        prod_sel_str = st.selectbox("Selecione a Bateria", opcoes_prods, index=0)
        
        if prod_sel_str != "":
            id_prod = int(prod_sel_str.split(" ")[1])
            dados_p = df_prods[df_prods['id'] == id_prod].iloc[0]
            st.write("---")
            
            with st.form("form_nova_venda", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    qtd = st.number_input("Quantidade *", min_value=1, value=1)
                    preco_base = float(dados_p['preco'])
                    st.info(f"Preço Tabela: R$ {preco_base:.2f}")
                    ajuste_preco = st.number_input("Ajuste de Preço (R$)", value=0.0, step=5.0)
                    valor_final = (preco_base * qtd) - ajuste_preco
                    st.success(f"Valor Total Final: R$ {valor_final:.2f}")
                    vendedor = st.text_input("Vendedor *", value=st.session_state.get("vendedor_nome", ""))
                    pagamento = st.selectbox("Pagamento *", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
                    parcelas = st.selectbox("Parcelas", [f"{i}x" for i in range(1, 13)]) if pagamento == "Cartão de Crédito" else "1x"
                with col2:
                    cliente = st.text_input("Cliente")
                    cpf = st.text_input("CPF / CNPJ")
                    veiculo_mod = st.text_input("Modelo do Veículo *", value=str(dados_p['veiculo'] or ''))
                    placa = st.text_input("Placa")
                    serie = st.text_input("Nº Série Bateria")

                if st.form_submit_button("Concluir Venda", use_container_width=True):
                    if not vendedor.strip() or not veiculo_mod.strip():
                        st.error("Preencha Vendedor e Veículo!")
                    else:
                        dt_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        conn = sqlite3.connect(DB_NAME)
                        c = conn.cursor()
                        c.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (qtd, id_prod))
                        c.execute("""
                            INSERT INTO vendas (data_hora, vendedor, produto_nome, quantidade, preco_original, desconto, valor_total, forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, veiculo_modelo, numero_serie, parcelas, amperagem, meses_garantia)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (dt_hoje, vendedor.strip(), dados_p['nome'], qtd, preco_base, ajuste_preco, valor_final, pagamento, cliente or "Consumidor Não Identificado", cpf or "Não Informado", placa.upper() or "Não Informado", veiculo_mod.strip(), serie.upper() or "Não Informado", parcelas, dados_p['amperagem'], dados_p['meses_garantia']))
                        id_venda = c.lastrowid
                        conn.commit()
                        conn.close()

                        modal_gerar_pdf({'id': id_venda, 'data_hora': dt_hoje, 'vendedor': vendedor.strip(), 'cliente_nome': cliente or "Consumidor Não Identificado", 'cliente_cpf': cpf or "Não Informado", 'veiculo_placa': placa.upper() or "Não Informado", 'veiculo_modelo': veiculo_mod.strip(), 'numero_serie': serie.upper() or "Não Informado", 'produto_nome': dados_p['nome'], 'amperagem': dados_p['amperagem'], 'quantidade': qtd, 'preco_original': preco_base, 'desconto': ajuste_preco, 'valor_total': valor_final, 'forma_pagamento': pagamento, 'parcelas': parcelas, 'meses_garantia': dados_p['meses_garantia']})

# --- ABA 2: ESTOQUE ORGANIZADO ---
elif menu == "Estoque Organizado":
    st.header("Estoque Geral")
    conn = sqlite3.connect(DB_NAME)
    df_estoque = pd.read_sql_query("SELECT id, categoria as Categoria, nome as Modelo, marca as Marca, amperagem as Amperagem, preco as Preço, quantidade as Estoque, meses_garantia as Garantia FROM produtos ORDER BY id ASC", conn)
    conn.close()
    st.dataframe(df_estoque, use_container_width=True, hide_index=True)

# --- ABA 3: EDITAR BATERIAS ---
elif menu == "Editar Baterias" and st.session_state["perfil"] == "ADM":
    st.header("Editar ou Excluir Baterias")
    conn = sqlite3.connect(DB_NAME)
    df_prods = pd.read_sql_query("SELECT * FROM produtos ORDER BY id ASC", conn)
    conn.close()

    opcoes = ["-- Selecione --"] + [f"ID {row['id']} - {row['nome']}" for _, row in df_prods.iterrows()]
    sel = st.selectbox("Escolha a bateria:", opcoes)
    
    if sel != "-- Selecione --":
        id_sel = int(sel.split(" ")[1])
        item = df_prods[df_prods['id'] == id_sel].iloc[0]

        e_nome = st.text_input("Nome", value=item['nome'])
        col1, col2 = st.columns(2)
        e_preco = col1.number_input("Preço R$", value=float(item['preco']))
        e_qtd = col2.number_input("Estoque", value=int(item['quantidade']))
        
        if st.button("Salvar Alterações"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("UPDATE produtos SET nome = ?, preco = ?, quantidade = ? WHERE id = ?", (e_nome, e_preco, e_qtd, id_sel))
            conn.commit()
            conn.close()
            st.success("Bateria atualizada!")
            st.rerun()

# --- ABA 4: HISTÓRICO ---
elif menu == "Histórico" and st.session_state["perfil"] == "ADM":
    st.header("Histórico de Vendas")
    conn = sqlite3.connect(DB_NAME)
    df_hist = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", conn)
    conn.close()
    
    if df_hist.empty:
        st.info("Nenhuma venda registrada.")
    else:
        st.dataframe(df_hist[['id', 'data_hora', 'vendedor', 'produto_nome', 'quantidade', 'valor_total', 'forma_pagamento', 'cliente_nome']], use_container_width=True, hide_index=True)

# --- ABA 5: PAINEL ADM ---
elif menu == "Painel ADM" and st.session_state["perfil"] == "ADM":
    st.header("Cadastrar Nova Bateria")
    with st.form("cad_manual"):
        f_nome = st.text_input("Nome do Modelo")
        f_amp = st.number_input("Amperagem", value=60)
        f_marca = st.text_input("Marca", value="Heliar")
        f_preco = st.number_input("Preço (R$)", value=400.0)
        f_qtd = st.number_input("Estoque Inicial", value=10)
        
        if st.form_submit_button("Cadastrar"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO produtos (nome, amperagem, marca, preco, quantidade) VALUES (?, ?, ?, ?, ?)", (f_nome, f_amp, f_marca, f_preco, f_qtd))
            conn.commit()
            conn.close()
            st.success("Cadastrado com sucesso!")
            st.rerun()
