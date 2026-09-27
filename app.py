import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO

# Importação para geração do PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

st.set_page_config(
    page_title="Power Baterias+",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização no padrão Dark + Verde Neon da Loja
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
        padding: 10px 20px !important;
    }
    .stButton>button:hover {
        background-color: #39ff14 !important;
        color: #000000 !important;
    }
    [data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-size: 2.2rem !important;
        font-weight: bold !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #16191e !important;
        border-right: 1px solid #28a745;
    }
    .banner-troca {
        background-color: #28a745;
        color: #000000;
        padding: 8px 15px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        font-size: 1.1rem;
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
    
    # Recriar tabela produtos para garantir limpeza e ordenação
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
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
            preco_original REAL NOT NULL,
            desconto REAL NOT NULL,
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
    
    # Popula catálogo exato enviado caso o banco esteja limpo
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        catalogo_exato = [
            ("36/40/45/48 Ah", "Heliar 48Ah", 48, "Heliar", 550.00, 10, 24),
            ("36/40/45/48 Ah", "Moura 48Ah", 48, "Moura", 550.00, 10, 24),
            ("36/40/45/48 Ah", "Cral 45Ah", 45, "Cral", 420.00, 10, 24),
            ("36/40/45/48 Ah", "KF 40Ah", 40, "KF", 250.00, 10, 12),
            ("36/40/45/48 Ah", "Super Life 36Ah", 36, "Super Life", 220.00, 10, 12),

            ("50 Ah Caixa Alta", "Heliar 50Ah Caixa Alta", 50, "Heliar", 550.00, 10, 24),
            ("50 Ah Caixa Alta", "Moura 50Ah Caixa Alta", 50, "Moura", 550.00, 10, 24),
            ("50 Ah Caixa Alta", "América 50Ah Caixa Alta", 50, "América", 470.00, 10, 18),
            ("50 Ah Caixa Alta", "Cral 52Ah Caixa Alta", 52, "Cral", 390.00, 10, 18),
            ("50 Ah Caixa Alta", "KF 52Ah Caixa Alta", 52, "KF", 350.00, 10, 12),
            ("50 Ah Caixa Alta", "Super Life 50Ah Caixa Alta", 50, "Super Life", 330.00, 10, 12),

            ("50 Ah Slim JD/JE", "Heliar 50Ah Slim", 50, "Heliar", 630.00, 10, 24),
            ("50 Ah Slim JD/JE", "Moura 50Ah Slim", 50, "Moura", 590.00, 10, 24),
            ("50 Ah Slim JD/JE", "América 50Ah Slim", 50, "América", 490.00, 10, 18),
            ("50 Ah Slim JD/JE", "Cral 50Ah Slim", 50, "Cral", 450.00, 10, 18),
            ("50 Ah Slim JD/JE", "KF 50Ah Slim", 50, "KF", 390.00, 10, 12),

            ("40 Ah Slim JD", "Heliar 40Ah JD", 40, "Heliar", 590.00, 10, 24),
            ("40 Ah Slim JD", "Moura 40Ah JD", 40, "Moura", 590.00, 10, 24),
            ("40 Ah Slim JD", "Cral 40Ah JD", 40, "Cral", 420.00, 10, 18),
            ("40 Ah Slim JD", "KF 40Ah JD", 40, "KF", 350.00, 10, 12),

            ("60 Ah Padrão", "Heliar 60Ah", 60, "Heliar", 550.00, 10, 24),
            ("60 Ah Padrão", "Moura 60Ah", 60, "Moura", 550.00, 10, 24),
            ("60 Ah Padrão", "América 60Ah", 60, "América", 450.00, 10, 18),
            ("60 Ah Padrão", "Cral 60Ah", 60, "Cral", 430.00, 10, 24),
            ("60 Ah Padrão", "KF 60Ah", 60, "KF", 330.00, 10, 12),
            ("60 Ah Padrão", "Super Life 60Ah", 60, "Super Life", 330.00, 10, 12),

            ("70 Ah", "Heliar 70Ah", 70, "Heliar", 760.00, 10, 24),
            ("70 Ah", "Moura 70Ah", 70, "Moura", 760.00, 10, 24),
            ("70 Ah", "América 70Ah", 70, "América", 590.00, 10, 18),
            ("70 Ah", "Cral 70Ah", 70, "Cral", 580.00, 10, 24),
            ("70 Ah", "Super Life 70Ah", 70, "Super Life", 390.00, 10, 12),

            ("75 Ah", "Heliar 75Ah", 75, "Heliar", 790.00, 10, 24),
            ("75 Ah", "Moura 75Ah", 75, "Moura", 790.00, 10, 24),
            ("75 Ah", "Cral 75Ah", 75, "Cral", 580.00, 10, 24),
            ("75 Ah", "KF 75Ah", 75, "KF", 490.00, 10, 12),

            ("90 Ah Heavy Duty", "Heliar 90Ah", 90, "Heliar", 970.00, 10, 15),
            ("90 Ah Heavy Duty", "Moura 90Ah", 90, "Moura", 970.00, 10, 12),
            ("90 Ah Heavy Duty", "Cral 90Ah", 90, "Cral", 690.00, 10, 15),
            ("90 Ah Heavy Duty", "Biachine 90Ah", 90, "Biachine", 590.00, 10, 12),

            ("Linha EFB / Start Stop", "Heliar 50Ah EFB", 50, "Heliar", 890.00, 10, 24),
            ("Linha EFB / Start Stop", "Moura 50Ah EFB", 50, "Moura", 890.00, 10, 24),
            ("Linha EFB / Start Stop", "Cral 50Ah EFB", 50, "Cral", 690.00, 10, 24),
            ("Linha EFB / Start Stop", "Heliar 60Ah EFB Start Stop", 60, "Heliar", 890.00, 10, 24),
            ("Linha EFB / Start Stop", "Moura 60Ah EFB Start Stop", 60, "Moura", 890.00, 10, 24),
            ("Linha EFB / Start Stop", "Heliar 72Ah Start Stop", 72, "Heliar", 1150.00, 10, 24),
            ("Linha EFB / Start Stop", "Moura 72Ah Start Stop", 72, "Moura", 1150.00, 10, 24),
        ]
        cursor.executemany("""
            INSERT INTO produtos (categoria, nome, amperagem, marca, preco, quantidade, meses_garantia)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, catalogo_exato)
        conn.commit()

    conn.close()

def gerador_pdf_nota(dados):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1b8036'), alignment=1, spaceAfter=5)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.black, alignment=1, spaceAfter=15)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, leading=14)
    
    story.append(Paragraph("<b>POWER BATERIAS+</b>", title_style))
    story.append(Paragraph("DISK BATERIAS: (99) 9519-1090<br/>COMPROVANTE DE VENDA E TERMO DE GARANTIA", sub_style))
    story.append(Spacer(1, 10))
    
    table_info = [
        [Paragraph(f"<b>Nº Venda:</b> {dados['id']}", body_style), Paragraph(f"<b>Data/Hora:</b> {dados['data_hora']}", body_style)],
        [Paragraph(f"<b>Cliente:</b> {dados['cliente_nome']}", body_style), Paragraph(f"<b>CPF/CNPJ:</b> {dados['cliente_cpf']}", body_style)],
        [Paragraph(f"<b>Veículo Placa:</b> {dados['veiculo_placa']}", body_style), Paragraph(f"<b>Nº Série Bateria:</b> {dados['numero_serie']}", body_style)],
        [Paragraph(f"<b>Vendedor:</b> {dados['vendedor']}", body_style), Paragraph(f"<b>Forma Pagamento:</b> {dados['forma_pagamento']} ({dados['parcelas']})", body_style)],
    ]
    
    t_info = Table(table_info, colWidths=[270, 270])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f0f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cccccc')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 15))
    
    table_prod = [
        ["Produto / Modelo", "Amp", "Qtd", "Preço Un.", "Desconto", "Total"],
        [dados['produto_nome'], f"{dados['amperagem']}Ah", str(dados['quantidade']), f"R$ {dados['preco_original']:.2f}", f"R$ {dados['desconto']:.2f}", f"R$ {dados['valor_total']:.2f}"]
    ]
    
    t_prod = Table(table_prod, colWidths=[200, 50, 40, 80, 80, 90])
    t_prod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1b8036')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
    ]))
    story.append(t_prod)
    story.append(Spacer(1, 20))
    
    termos = f"""
    <b>TERMOS DE GARANTIA E CONDIÇÕES:</b><br/>
    1. A garantia deste produto é de <b>{dados['meses_garantia']} meses</b> a contar da data desta venda.<br/>
    2. A garantia cobre defeitos de fabricação. Danos por mau uso, sobrecarga ou caixa quebrada anulam a garantia.<br/>
    3. <b>Observação:</b> Venda realizada com valor à base de troca de carcaça inservível.<br/>
    """
    story.append(Paragraph(termos, body_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("___________________________________________________<br/>Assinatura do Cliente", ParagraphStyle('Sign', alignment=1)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

inicializar_banco()

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = None

if not st.session_state["logado"]:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=320)
    else:
        st.markdown("<h1 style='text-align: center;'>⚡ HELIAR POWER BATERIAS+</h1>", unsafe_allow_html=True)
        
    st.markdown("<p style='text-align: center; color: #39ff14;'>DISK BATERIAS: (99) 9519-1090</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
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
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.markdown("## ⚡ POWER BATERIAS")

st.sidebar.caption("📞 DISK BATERIAS: (99) 9519-1090")
st.sidebar.caption(f"Perfil: **{st.session_state['perfil']}**")
st.sidebar.write("---")

if st.session_state["perfil"] == "ADM":
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque Organizado", "✏️ Editar Baterias", "🛡️ Consultar Garantia", "📄 Histórico", "📊 Painel ADM"])
else:
    menu = st.sidebar.radio("Navegação", ["🛒 Nova Venda", "📦 Estoque Organizado", "🛡️ Consultar Garantia", "📄 Histórico"])

st.sidebar.write("---")
if st.sidebar.button("🚪 Sair"):
    st.session_state["logado"] = False
    st.rerun()

st.markdown('<div class="banner-troca">🔄 VALORES A BASE DE TROCA 🔄</div>', unsafe_allow_html=True)

# --- ABA 1: NOVA VENDA ---
if menu == "🛒 Nova Venda":
    st.header("🛒 Lançamento de Venda")
    
    conn = conectar()
    df_prods = pd.read_sql_query("SELECT id, categoria, nome, amperagem, preco, quantidade, meses_garantia FROM produtos WHERE quantidade > 0", conn)
    conn.close()

    if df_prods.empty:
        st.warning("Nenhuma bateria disponível no estoque!")
    else:
        # Seleção simplificada
        opcoes_prods = [f"ID {row['id']} | {row['nome']} - R$ {row['preco']:.2f} (Estoque: {row['quantidade']})" for _, row in df_prods.iterrows()]
        prod_sel_str = st.selectbox("Selecione a Bateria", opcoes_prods)
        id_prod = int(prod_sel_str.split(" ")[1])
        
        dados_p = df_prods[df_prods['id'] == id_prod].iloc[0]
        
        st.write("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Dados da Venda")
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            preco_base = float(dados_p['preco'])
            
            st.info(f"💰 **Preço Tabela (Unitário):** R$ {preco_base:.2f}")
            desconto = st.number_input("Desconto Total em R$ (Opcional)", min_value=0.0, value=0.0, step=5.0)
            
            valor_final = (preco_base * qtd) - desconto
            st.success(f"🏷️ **Valor Total Final:** R$ {valor_final:.2f}")
            
            vendedor = st.text_input("Nome do Vendedor")
            pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
            parcelas = st.selectbox("Parcelas", [f"{i}x" for i in range(1, 13)]) if pagamento == "Cartão de Crédito" else "1x"
            
        with col2:
            st.subheader("Dados para Nota e Garantia")
            cliente = st.text_input("Nome do Cliente")
            cpf = st.text_input("CPF/CNPJ (Opcional)")
            placa = st.text_input("Placa do Veículo (Opcional)")
            serie = st.text_input("Nº de Série da Bateria (Opcional)")

        if st.button("✅ Concluir Venda e Gerar Nota PDF", use_container_width=True):
            if qtd > dados_p['quantidade']:
                st.error(f"Estoque insuficiente! Restam apenas {dados_p['quantidade']} unidades.")
            else:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (qtd, id_prod))
                
                dt_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
                cursor.execute("""
                    INSERT INTO vendas (data_hora, vendedor, produto_nome, quantidade, preco_original, desconto, valor_total, forma_pagamento, cliente_nome, cliente_cpf, veiculo_placa, numero_serie, parcelas, amperagem, meses_garantia)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (dt_hoje, vendedor or "Atendente", dados_p['nome'], qtd, preco_base, desconto, valor_final, pagamento, cliente or "Não Informado", cpf or "Não Informado", placa.upper() or "Não Informado", serie.upper() or "Não Informado", parcelas, dados_p['amperagem'], dados_p['meses_garantia']))
                
                id_venda = cursor.lastrowid
                conn.commit()
                conn.close()
                
                st.success(f"Venda Nº {id_venda} concluída com sucesso!")
                
                if REPORTLAB_DISPONIVEL:
                    dados_venda_pdf = {
                        'id': id_venda,
                        'data_hora': dt_hoje,
                        'vendedor': vendedor or "Atendente",
                        'cliente_nome': cliente or "Consumidor",
                        'cliente_cpf': cpf or "Não Informado",
                        'veiculo_placa': placa.upper() or "Não Informado",
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
                    pdf_bytes = gerador_pdf_nota(dados_venda_pdf)
                    st.download_button(
                        label="📄 Baixar Comprovante/Nota de Garantia em PDF",
                        data=pdf_bytes,
                        file_name=f"nota_venda_{id_venda}_power_baterias.pdf",
                        mime="application/pdf"
                    )

# --- ABA 2: ESTOQUE ORGANIZADO ---
elif menu == "📦 Estoque Organizado":
    st.header("📦 Estoque Organizado por Categoria")
    
    conn = conectar()
    df_estoque = pd.read_sql_query("SELECT id, categoria, nome, amperagem, marca, preco, quantidade, meses_garantia FROM produtos", conn)
    conn.close()
    
    categorias = df_estoque['categoria'].unique()
    
    for cat in categorias:
        with st.expander(f"🔋 Categorias: {cat}", expanded=True):
            df_sub = df_estoque[df_estoque['categoria'] == cat][['id', 'nome', 'marca', 'amperagem', 'preco', 'quantidade', 'meses_garantia']]
            df_sub.columns = ['ID', 'Modelo', 'Marca', 'Amp (Ah)', 'Preço Troca (R$)', 'Qtd Est.', 'Garantia (Meses)']
            st.dataframe(df_sub, use_container_width=True, hide_index=True)

# --- ABA 3: EDITAR BATERIAS ---
elif menu == "✏️ Editar Baterias":
    st.header("✏️ Alterar ou Excluir Baterias")
    
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
            col1, col2, col3 = st.columns(3)
            with col1:
                e_amp = st.number_input("Amperagem (Ah)", min_value=1, value=int(item['amperagem']))
                e_marca = st.text_input("Marca", value=item['marca'])
            with col2:
                e_preco = st.number_input("Preço R$", min_value=0.0, value=float(item['preco']))
                e_qtd = st.number_input("Estoque", min_value=0, value=int(item['quantidade']))
            with col3:
                e_garantia = st.number_input("Garantia (Meses)", min_value=1, value=int(item['meses_garantia']))
            
            btn_salvar = st.form_submit_button("💾 Salvar Alterações")
            
            if btn_salvar:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE produtos 
                    SET categoria = ?, nome = ?, amperagem = ?, marca = ?, preco = ?, quantidade = ?, meses_garantia = ?
                    WHERE id = ?
                """, (e_cat, e_nome, e_amp, e_marca, e_preco, e_qtd, e_garantia, id_sel))
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
            st.success("Bateria removida!")
            st.rerun()

# --- ABA 4: GARANTIA ---
elif menu == "🛡️ Consultar Garantia":
    st.header("🛡️ Consulta de Garantias")
    termo = st.text_input("🔍 Digite Nome do Cliente, Placa do Veículo ou Nº de Série")
    
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
               quantidade AS 'Qtd', preco_original AS 'Preço Tab.', desconto AS 'Desc.', valor_total AS 'Total', 
               forma_pagamento AS 'Pagamento', cliente_nome AS 'Cliente' 
        FROM vendas ORDER BY id DESC
    """, conn)
    conn.close()
    
    st.dataframe(df_hist, use_container_width=True)

# --- ABA 6: PAINEL ADM ---
elif menu == "📊 Painel ADM":
    st.header("📊 Painel Financeiro e Cadastro")
    
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
        f_cat = st.text_input("Categoria/Família (ex: 60 Ah Padrão)", value="60 Ah Padrão")
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
                INSERT INTO produtos (categoria, nome, amperagem, marca, preco, quantidade, meses_garantia)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f_cat, f_nome, f_amp, f_marca, f_preco, f_qtd, f_garantia))
            conn.commit()
            conn.close()
            st.success("Nova bateria cadastrada!")
            st.rerun()
