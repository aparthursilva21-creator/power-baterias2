import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO

# Tenta importar o ReportLab para geração de PDF
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

# Dicionário com dados dos utilizadores restritos
USUARIOS = {
    "arthur": {"senha": "Arthur123", "perfil": "ADM", "nome": "Arthur"},
    "sandro": {"senha": "1234", "perfil": "ADM", "nome": "Sandro"},
    "pedro": {"senha": "Pedro1234", "perfil": "Vendedor", "nome": "Pedro"},
    "wanderson": {"senha": "venda123", "perfil": "Vendedor", "nome": "Wanderson"},
}

def conectar():
    return sqlite3.connect("power_baterias.db", timeout=10)

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT meses_garantia, veiculo FROM produtos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("DROP TABLE IF EXISTS produtos")

    cursor.execute("""
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
    
    cursor.execute("PRAGMA table_info(vendas)")
    colunas_vendas = cursor.fetchall()
    if len(colunas_vendas) != 17:
        cursor.execute("DROP TABLE IF EXISTS vendas")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT NOT NULL,
            vendedor TEXT NOT NULL,
            produto_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_original REAL NOT NULL,
            desconto REAL NOT NULL,
            valor_total REAL NOT NULL,
            forma_pagamento TEXT NOT NULL,
            cliente_nome TEXT,
            cliente_cpf TEXT,
            veiculo_placa TEXT,
            veiculo_modelo TEXT DEFAULT '',
            numero_serie TEXT,
            parcelas TEXT DEFAULT '1x',
            amperagem INTEGER DEFAULT 0,
            meses_garantia INTEGER DEFAULT 12
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        catalogo_exato = [
            ("36/40/45/48 Ah", "Heliar 48Ah", 48, "Heliar", 550.00, 10, 24, "Gol, Palio, Uno"),
            ("36/40/45/48 Ah", "Moura 48Ah", 48, "Moura", 550.00, 10, 24, "Gol, Palio, Uno"),
            ("36/40/45/48 Ah", "Cral 45Ah", 45, "Cral", 420.00, 10, 24, "Celta, Ka, Fit"),
            ("36/40/45/48 Ah", "KF 40Ah", 40, "KF", 250.00, 10, 12, "Motos / Veículos Leves"),
            ("36/40/45/48 Ah", "Super Life 36Ah", 36, "Super Life", 220.00, 10, 12, "Veículos Populares"),

            ("50 Ah Caixa Alta", "Heliar 50Ah Caixa Alta", 50, "Heliar", 550.00, 10, 24, "Fiesta, EcoSport, Ka"),
            ("50 Ah Caixa Alta", "Moura 50Ah Caixa Alta", 50, "Moura", 550.00, 10, 24, "Fiesta, EcoSport, Ka"),
            ("50 Ah Caixa Alta", "América 50Ah Caixa Alta", 50, "América", 470.00, 10, 18, "Ford / Honda"),
            ("50 Ah Caixa Alta", "Cral 52Ah Caixa Alta", 52, "Cral", 390.00, 10, 18, "Ford / Honda"),
            ("50 Ah Caixa Alta", "KF 52Ah Caixa Alta", 52, "KF", 350.00, 10, 12, "Ford / Honda"),
            ("50 Ah Caixa Alta", "Super Life 50Ah Caixa Alta", 50, "Super Life", 330.00, 10, 12, "Ford / Honda"),

            ("60 Ah Padrão", "Heliar 60Ah", 60, "Heliar", 550.00, 10, 24, "Civic, Corolla, Onix, HB20, Fox"),
            ("60 Ah Padrão", "Moura 60Ah", 60, "Moura", 550.00, 10, 24, "Civic, Corolla, Onix, HB20, Fox"),
            ("60 Ah Padrão", "América 60Ah", 60, "América", 450.00, 10, 18, "Carros de Passeio Médios"),
            ("60 Ah Padrão", "Cral 60Ah", 60, "Cral", 430.00, 10, 24, "Carros de Passeio Médios"),
            ("60 Ah Padrão", "KF 60Ah", 60, "KF", 330.00, 10, 12, "Carros de Passeio Médios"),
            ("60 Ah Padrão", "Super Life 60Ah", 60, "Super Life", 330.00, 10, 12, "Carros de Passeio Médios"),

            ("70 Ah", "Heliar 70Ah", 70, "Heliar", 760.00, 10, 24, "SUVs, Pickups, Compass, Renegade"),
            ("70 Ah", "Moura 70Ah", 70, "Moura", 760.00, 10, 24, "SUVs, Pickups, Compass, Renegade"),
            ("70 Ah", "América 70Ah", 70, "América", 590.00, 10, 18, "SUVs e Utilitários"),
            ("70 Ah", "Cral 70Ah", 70, "Cral", 580.00, 10, 24, "SUVs e Utilitários"),
            ("70 Ah", "Super Life 70Ah", 70, "Super Life", 390.00, 10, 12, "SUVs e Utilitários"),

            ("Linha EFB / Start Stop", "Heliar 60Ah EFB Start Stop", 60, "Heliar", 890.00, 10, 24, "Renegade, Argo, Toro, Golf"),
            ("Linha EFB / Start Stop", "Moura 60Ah EFB Start Stop", 60, "Moura", 890.00, 10, 24, "Renegade, Argo, Toro, Golf"),
        ]
        cursor.executemany("""
            INSERT INTO produtos (categoria, nome, amperagem, marca, preco, quantidade, meses_garantia, veiculo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, catalogo_exato)
        conn.commit()

    conn.close()

def gerador_pdf_nota(dados):
    if not REPORTLAB_DISPONIVEL:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    header_title = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#28a745'), alignment=0, spaceAfter=2)
    header_sub = ParagraphStyle('HeaderSub', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#444444'), alignment=0)
    nf_title = ParagraphStyle('NFTitle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#000000'), alignment=2)
    
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Bold')

    topo = [
        [
            Paragraph("<b>POWER BATERIAS</b><br/><font size=8 color='#555555'>AUTOMOTIVAS E UTILITÁRIOS</font>", header_title),
            Paragraph(f"<b>COMPROVANTE DE VENDA</b><br/><b>Nº: #{dados['id']:06d}</b><br/>Data: {dados['data_hora']}", nf_title)
        ]
    ]
    t_topo = Table(topo, colWidths=[320, 220])
    t_topo.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_topo)
    
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>DISK BATERIAS:</b> (61) 99519-1090", header_sub))
    story.append(Spacer(1, 10))

    dados_cliente = [
        [Paragraph("<b>DADOS DO CLIENTE E VEÍCULO</b>", ParagraphStyle('H', parent=body_bold, textColor=colors.white)), ""],
        [Paragraph(f"<b>Cliente:</b> {dados['cliente_nome']}", body_style), Paragraph(f"<b>CPF/CNPJ:</b> {dados['cliente_cpf']}", body_style)],
        [Paragraph(f"<b>Veículo:</b> {dados['veiculo_modelo']}", body_style), Paragraph(f"<b>Placa:</b> {dados['veiculo_placa']}", body_style)],
        [Paragraph(f"<b>Nº Série Bateria:</b> {dados['numero_serie']}", body_style), Paragraph(f"<b>Vendedor:</b> {dados['vendedor']}", body_style)],
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

    table_prod = [
        [Paragraph("<b>Item / Descrição</b>", body_bold), Paragraph("<b>Amp</b>", body_bold), Paragraph("<b>Qtd</b>", body_bold), Paragraph("<b>Preço Unit.</b>", body_bold), Paragraph("<b>Desc.</b>", body_bold), Paragraph("<b>Total</b>", body_bold)],
        [
            Paragraph(dados['produto_nome'], body_style),
            Paragraph(f"{dados['amperagem']}Ah", body_style),
            Paragraph(str(dados['quantidade']), body_style),
            Paragraph(f"R$ {dados['preco_original']:.2f}", body_style),
            Paragraph(f"R$ {dados['desconto']:.2f}", body_style),
            Paragraph(f"<b>R$ {dados['valor_total']:.2f}</b>", body_style)
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
            Paragraph(f"<b>Forma de Pagamento:</b> {dados['forma_pagamento']} ({dados['parcelas']})", body_style),
            Paragraph(f"<b>VALOR TOTAL: R$ {dados['valor_total']:.2f}</b>", ParagraphStyle('Tot', parent=body_bold, fontSize=11, alignment=2))
        ]
    ]
    t_pag = Table(pag_info, colWidths=[300, 240])
    t_pag.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eef9f1')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#28a745')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_pag)
    story.append(Spacer(1, 15))

    termos = f"""
    <b>TERMO DE GARANTIA E CONDIÇÕES GERAIS:</b><br/>
    1. Este produto possui garantia legal e de fábrica de <b>{dados['meses_garantia']} meses</b> contra defeitos de fabricação a partir desta data.<br/>
    2. A garantia cobre exclusivamente falhas internas da bateria. Não cobre mau uso, caixa quebrada, polos danificados, descarga profunda ou sobrecarga (alternador com defeito).<br/>
    3. Obrigatória a apresentação deste comprovante e/ou certificado do fabricante no ato do atendimento.
    """
    story.append(Paragraph(termos, ParagraphStyle('Termos', parent=body_style, fontSize=8, leading=11, textColor=colors.HexColor('#333333'))))
    
    story.append(Spacer(1, 25))
    story.append(Paragraph("___________________________________________________<br/>Assinatura do Cliente / Recebedor", ParagraphStyle('Sign', alignment=1, fontSize=8)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def cancelar_venda(id_venda, produto_nome, quantidade):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE nome = ?", (quantidade, produto_nome))
    cursor.execute("DELETE FROM vendas WHERE id = ?", (id_venda,))
    conn.commit()
    conn.close()

inicializar_banco()

# --- LOGIN E SESSÃO ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = None
    st.session_state["vendedor_nome"] = ""

if not st.session_state["logado"]:
    if os.path.exists("lo"):
        st.image("go.p", width=300)
    else:
        st.markdown("<h1 style='text-align: center;'>HELIAR POWER BATERIAS</h1>", unsafe_allow_html=True)
        
    st.markdown("<p style='text-align: center; color: #39ff14;'>DISK BATERIAS: (61) 99519-1090</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
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
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos! Acesso negado.")
    st.stop()

# --- MODAL DE CONFIRMAÇÃO DE PDF ---
@st.dialog("Venda Finalizada com Sucesso! 🟢")
def modal_gerar_pdf(dados_venda):
    st.write(f"**Cliente:** {dados_venda['cliente_nome']}")
    st.write(f"**Bateria:** {dados_venda['produto_nome']}")
    st.write(f"**Valor Total:** R$ {dados_venda['valor_total']:.2f}")
    
    if REPORTLAB_DISPONIVEL:
        st.write("Deseja gerar e baixar a **Nota Fiscal / Comprovante** agora?")
        pdf_bytes = gerador_pdf_nota(dados_venda)
        st.download_button(
            label="📄 Baixar Nota Fiscal (PDF)",
            data=pdf_bytes,
            file_name=f"nota_fiscal_{dados_venda['id']}_power_baterias.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Biblioteca 'reportlab' não instalada no servidor!")

# --- MODAL DE CONFIRMAÇÃO PARA CANCELAMENTO ---
@st.dialog("Confirmar Cancelamento 🔴")
def modal_confirmar_cancelamento(id_venda, produto_nome, quantidade):
    st.write(f"Tem certeza que deseja **cancelar a venda #{id_venda}**?")
    st.caption(f"Produto: {produto_nome} | Qtd a devolver: {quantidade}")
    
    if st.button("Sim, Cancelar Venda", use_container_width=True):
        cancelar_venda(id_venda, produto_nome, quantidade)
        st.toast(f"Venda #{id_venda} cancelada e produto devolvido!", icon="✅")
        st.rerun()

# --- MENU LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.markdown("## POWER BATERIAS")

st.sidebar.caption("DISK BATERIAS: (61) 99519-1090")
st.sidebar.markdown(f"Utilizador: **{st.session_state['vendedor_nome']}** ({st.session_state['perfil']})")
st.sidebar.write("---")

# Restrições de Menu por Perfil (Histórico apenas para ADM)
if st.session_state["perfil"] == "ADM":
    menu = st.sidebar.radio("Navegação", ["Nova Venda", "Estoque Organizado", "Editar Baterias", "Consultar Garantia", "Histórico", "Painel ADM"])
else:
    menu = st.sidebar.radio("Navegação", ["Nova Venda", "Estoque Organizado", "Consultar Garantia"])

st.sidebar.write("---")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.session_state["perfil"] = None
    st.session_state["vendedor_nome"] = ""
    st.rerun()

# --- ABA 1: NOVA VENDA ---
if menu == "Nova Venda":
    st.header("Lançamento de Venda")
    
    conn = conectar()
    df_prods = pd.read_sql_query("SELECT id, categoria, nome, amperagem, preco, quantidade, meses_garantia, veiculo FROM produtos WHERE quantidade > 0", conn)
    conn.close()

    if df_prods.empty:
        st.warning("Nenhuma bateria disponível no estoque!")
    else:
        busca = st.text_input("🔍 Pesquisar bateria (modelo, marca, veiculo):")
        if busca:
            df_prods = df_prods[
                df_prods['nome'].str.contains(busca, case=False, na=False) |
                df_prods['veiculo'].str.contains(busca, case=False, na=False)
            ]

        if df_prods.empty:
            st.warning("Nenhum produto localizado com esse termo.")
        else:
            opcoes_prods = [f"ID {row['id']} | {row['nome']} - R$ {row['preco']:.2f} (Estoque: {row['quantidade']})" for _, row in df_prods.iterrows()]
            prod_sel_str = st.selectbox("Selecione a Bateria", opcoes_prods)
            id_prod = int(prod_sel_str.split(" ")[1])
            
            dados_p = df_prods[df_prods['id'] == id_prod].iloc[0]
            st.write("---")
            
            with st.form("form_nova_venda", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Dados da Venda")
                    qtd = st.number_input("Quantidade *", min_value=1, value=1)
                    preco_base = float(dados_p['preco'])
                    
                    st.info(f"Preço Tabela (Unitário): R$ {preco_base:.2f}")
                    desconto = st.number_input("Desconto Total em R$ (Opcional)", min_value=0.0, value=0.0, step=5.0)
                    
                    valor_final = (preco_base * qtd) - desconto
                    st.success(f"Valor Total Final: R$ {valor_final:.2f}")
                    
                    # Nome pré-preenchido automaticamente com a sessão logada
                    vendedor = st.text_input("Nome do Vendedor *", value=st.session_state.get("vendedor_nome", ""))
                    pagamento = st.selectbox("Forma de Pagamento *", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
                    parcelas = st.selectbox("Parcelas", [f"{i}x" for i in range(1, 13)]) if pagamento == "Cartão de Crédito" else "1x"
                    
                with col2:
                    st.subheader("Dados do Cliente e Veículo")
                    cliente = st.text_input("Nome do Cliente")
                    cpf = st.text_input("CPF / CNPJ (Opcional)")
                    veiculo_mod = st.text_input("Modelo do Veículo * (ex: Civic, Gol, Corolla)", value=dados_p['veiculo'] or "")
                    placa = st.text_input("Placa do Veículo (Opcional)")
                    serie = st.text_input("Nº de Série da Bateria (Opcional)")

                btn_finalizar = st.form_submit_button("Concluir Venda", use_container_width=True)

            if btn_finalizar:
                # Validação dos campos obrigatórios
                if not vendedor.strip():
                    st.error("Erro: O campo 'Nome do Vendedor' é obrigatório!")
                elif not veiculo_mod.strip():
                    st.error("Erro: O campo 'Modelo do Veículo' é obrigatório para registrar a venda!")
                elif qtd <= 0:
                    st.error("Erro: A quantidade deve ser maior que zero!")
                elif qtd > dados_p['quantidade']:
                    st.error(f"Estoque insuficiente! Restam apenas {dados_p['quantidade']} unidades.")
                else:
                    conn = conectar()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (qtd, id_prod))
                    
                    dt_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    
                    cursor.execute("""
                        INSERT INTO vendas (
                            data_hora, vendedor, produto_nome, quantidade, preco_original, 
                            desconto, valor_total, forma_pagamento, cliente_nome, cliente_cpf, 
                            veiculo_placa, veiculo_modelo, numero_serie, parcelas, amperagem, meses_garantia
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        dt_hoje, 
                        vendedor.strip(), 
                        dados_p['nome'], 
                        qtd, 
                        preco_base, 
                        desconto, 
                        valor_final, 
                        pagamento, 
                        cliente or "Consumidor Não Identificado", 
                        cpf or "Não Informado", 
                        placa.upper() or "Não Informado", 
                        veiculo_mod.strip(), 
                        serie.upper() or "Não Informado", 
                        parcelas, 
                        int(dados_p['amperagem']), 
                        int(dados_p['meses_garantia'])
                    ))
                    
                    id_venda = cursor.lastrowid
                    conn.commit()
                    conn.close()

                    dados_venda_pdf = {
                        'id': id_venda,
                        'data_hora': dt_hoje,
                        'vendedor': vendedor.strip(),
                        'cliente_nome': cliente or "Consumidor Não Identificado",
                        'cliente_cpf': cpf or "Não Informado",
                        'veiculo_placa': placa.upper() or "Não Informado",
                        'veiculo_modelo': veiculo_mod.strip(),
                        'numero_serie': serie.upper() or "Não Informado",
                        'produto_nome': dados_p['nome'],
                        'amperagem': dados_p['amperagem'],
                        'quantidade': qtd,
                        'preco_original': preco_base,
                        'desconto': desconto,
                        'valor_total': valor_final,
                        'forma_pagamento': pagamento,
                        'parcelas': parcelas,
                        'meses_garantia': dados_p['meses_garantia']
                    }

                    modal_gerar_pdf(dados_venda_pdf)

# --- ABA 2: ESTOQUE ORGANIZADO ---
elif menu == "Estoque Organizado":
    st.header("Estoque Organizado por Categoria")
    
    conn = conectar()
    df_estoque = pd.read_sql_query("SELECT id, categoria, nome, amperagem, marca, veiculo, preco, quantidade, meses_garantia FROM produtos", conn)
    conn.close()
    
    categorias = df_estoque['categoria'].unique()
    
    for cat in categorias:
        with st.expander(f"Categoria: {cat}", expanded=True):
            df_sub = df_estoque[df_estoque['categoria'] == cat][['id', 'nome', 'marca', 'amperagem', 'veiculo', 'preco', 'quantidade', 'meses_garantia']]
            df_sub.columns = ['ID', 'Modelo', 'Marca', 'Amp (Ah)', 'Veículos Indicados', 'Preço (R$)', 'Qtd Est.', 'Garantia (Meses)']
            st.dataframe(df_sub, use_container_width=True, hide_index=True)

# --- ABA 3: EDITAR BATERIAS ---
elif menu == "Editar Baterias" and st.session_state["perfil"] == "ADM":
    st.header("Alterar ou Excluir Baterias")
    
    conn = conectar()
    df_prods = pd.read_sql_query("SELECT * FROM produtos ORDER BY id ASC", conn)
    conn.close()
    
    if df_prods.empty:
        st.warning("Nenhuma bateria cadastrada.")
    else:
        opcoes = [f"ID {row['id']} - {row['nome']} (R$ {row['preco']:.2f})" for _, row in df_prods.iterrows()]
        selecionado = st.selectbox("Selecione a bateria para alterar:", opcoes)
        
        id_sel = int(selecionado.split(" ")[1])
        item = df_prods[df_prods['id'] == id_sel].iloc[0]
        
        st.write("---")
        with st.form("form_editar"):
            e_cat = st.text_input("Categoria/Família", value=item['categoria'])
            e_nome = st.text_input("Nome/Modelo", value=item['nome'])
            e_veiculo = st.text_input("Veículos Recomendados", value=item['veiculo'] if 'veiculo' in item else '')
            col1, col2, col3 = st.columns(3)
            with col1:
                e_amp = st.number_input("Amperagem (Ah)", min_value=1, value=int(item['amperagem']))
                e_marca = st.text_input("Marca", value=item['marca'])
            with col2:
                e_preco = st.number_input("Preço R$", min_value=0.0, value=float(item['preco']))
                e_qtd = st.number_input("Estoque", min_value=0, value=int(item['quantidade']))
            with col3:
                e_garantia = st.number_input("Garantia (Meses)", min_value=1, value=int(item['meses_garantia']))
            
            btn_salvar = st.form_submit_button("Salvar Alterações")
            
            if btn_salvar:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE produtos 
                    SET categoria = ?, nome = ?, amperagem = ?, marca = ?, veiculo = ?, preco = ?, quantidade = ?, meses_garantia = ?
                    WHERE id = ?
                """, (e_cat, e_nome, e_amp, e_marca, e_veiculo, e_preco, e_qtd, e_garantia, id_sel))
                conn.commit()
                conn.close()
                st.success("Bateria atualizada com sucesso!")
                st.rerun()

        if st.button("Excluir Bateria do Sistema"):
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produtos WHERE id = ?", (id_sel,))
            conn.commit()
            conn.close()
            st.success("Bateria removida!")
            st.rerun()

# --- ABA 4: GARANTIA ---
elif menu == "Consultar Garantia":
    st.header("Consulta de Garantias")
    
    termo = st.text_input("Pesquisar por Nome do Cliente, CPF, Placa, Veículo ou Nº de Série")
    
    conn = conectar()
    if termo:
        df_garantia = pd.read_sql_query("""
            SELECT id, data_hora, cliente_nome, cliente_cpf, produto_nome, amperagem, veiculo_placa, veiculo_modelo, numero_serie, meses_garantia 
            FROM vendas 
            WHERE cliente_nome LIKE ? OR cliente_cpf LIKE ? OR veiculo_placa LIKE ? OR veiculo_modelo LIKE ? OR numero_serie LIKE ?
            ORDER BY id DESC
        """, conn, params=(f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%", f"%{termo}%"))
    else:
        st.subheader("Últimas Vendas Realizadas")
        df_garantia = pd.read_sql_query("""
            SELECT id, data_hora, cliente_nome, cliente_cpf, produto_nome, amperagem, veiculo_placa, veiculo_modelo, numero_serie, meses_garantia 
            FROM vendas 
            ORDER BY id DESC LIMIT 15
        """, conn)
    conn.close()

    if df_garantia.empty:
        st.warning("Nenhum registo de garantia encontrado.")
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

            status = "🟢 NA GARANTIA" if restantes > 0 else "🔴 VENCIDA"
            tempo_str = f"{restantes} dias restantes" if restantes > 0 else f"Vencida há {abs(restantes)} dias"

            resultados.append({
                "Nº Venda": r['id'],
                "Data": dt_v.strftime("%d/%m/%Y"),
                "Cliente": r['cliente_nome'],
                "CPF / CNPJ": r['cliente_cpf'],
                "Produto": f"{r['produto_nome']} ({r['amperagem']}Ah)",
                "Veículo": r['veiculo_modelo'],
                "Placa": r['veiculo_placa'],
                "Nº Série": r['numero_serie'],
                "Status": status,
                "Prazo": tempo_str
            })

        st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)

# --- ABA 5: HISTÓRICO DE VENDAS (Apenas ADM) ---
elif menu == "Histórico" and st.session_state["perfil"] == "ADM":
    st.header("Histórico Geral de Vendas")
    conn = conectar()
    
    df_hist = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", conn)
    conn.close()
    
    if df_hist.empty:
        st.info("Nenhuma venda registada até ao momento.")
    else:
        for _, row in df_hist.iterrows():
            with st.container():
                col_i, col_d, col_v, col_btn, col_del = st.columns([1, 2.5, 2, 2, 2])
                col_i.write(f"**Nº #{row['id']}**")
                col_d.write(f"**Data:** {row['data_hora']}<br/>**Cliente:** {row['cliente_nome']}<br/>**Vendedor:** {row['vendedor']}", unsafe_allow_html=True)
                col_v.write(f"**Produto:** {row['produto_nome']}<br/>**Total:** R$ {row['valor_total']:.2f}", unsafe_allow_html=True)
                
                dados_v = {
                    'id': row['id'],
                    'data_hora': row['data_hora'],
                    'vendedor': row['vendedor'],
                    'cliente_nome': row['cliente_nome'],
                    'cliente_cpf': row['cliente_cpf'],
                    'veiculo_placa': row['veiculo_placa'],
                    'veiculo_modelo': row['veiculo_modelo'],
                    'numero_serie': row['numero_serie'],
                    'produto_nome': row['produto_nome'],
                    'amperagem': row['amperagem'],
                    'quantidade': row['quantidade'],
                    'preco_original': row['preco_original'],
                    'desconto': row['desconto'],
                    'valor_total': row['valor_total'],
                    'forma_pagamento': row['forma_pagamento'],
                    'parcelas': row['parcelas'],
                    'meses_garantia': row['meses_garantia']
                }
                
                if REPORTLAB_DISPONIVEL:
                    pdf_bytes = gerador_pdf_nota(dados_v)
                    col_btn.download_button(
                        label="📄 Nota Fiscal PDF",
                        data=pdf_bytes,
                        file_name=f"nota_fiscal_{row['id']}_power_baterias.pdf",
                        mime="application/pdf",
                        key=f"btn_pdf_{row['id']}"
                    )
                else:
                    col_btn.caption("⚠️ Requer ReportLab")

                if col_del.button("🔴 Cancelar", key=f"btn_del_{row['id']}"):
                    modal_confirmar_cancelamento(row['id'], row['produto_nome'], row['quantidade'])

                st.write("---")

# --- ABA 6: PAINEL ADM ---
elif menu == "Painel ADM" and st.session_state["perfil"] == "ADM":
    st.header("Painel Financeiro e Cadastro")
    
    conn = conectar()
    totais = pd.read_sql_query("SELECT SUM(valor_total) as faturado, SUM(quantidade) as un_vendidas FROM vendas", conn)
    conn.close()

    fat = totais['faturado'].iloc[0] or 0.0
    qtd_un = totais['un_vendidas'].iloc[0] or 0

    col1, col2 = st.columns(2)
    col1.metric("Faturamento Total", f"R$ {fat:,.2f}")
    col2.metric("Baterias Vendidas", f"{qtd_un} Unidades")

    st.write("---")
    st.subheader("Cadastrar Nova Bateria")
    with st.form("cad_manual"):
        f_cat = st.text_input("Categoria/Família (ex: 60 Ah Padrão)", value="60 Ah Padrão")
        f_nome = st.text_input("Nome do Modelo (ex: Heliar 60Ah)")
        f_veiculo = st.text_input("Veículos Recomendados (ex: Civic, Corolla, Onix)", value="Carros de Passeio")
        f_amp = st.number_input("Amperagem (Ah)", min_value=1, value=60)
        f_marca = st.text_input("Marca", value="Heliar")
        f_preco = st.number_input("Preço (R$)", min_value=0.0, value=400.0)
        f_qtd = st.number_input("Quantidade em Estoque", min_value=1, value=10)
        f_garantia = st.number_input("Garantia (Meses)", min_value=1, value=24)
        
        if st.form_submit_button("Cadastrar Bateria"):
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO produtos (categoria, nome, amperagem, marca, veiculo, preco, quantidade, meses_garantia)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (f_cat, f_nome, f_amp, f_marca, f_veiculo, f_preco, f_qtd, f_garantia))
            conn.commit()
            conn.close()
            st.success("Nova bateria cadastrada!")
            st.rerun()
