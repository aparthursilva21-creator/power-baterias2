import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from io import BytesIO
from sqlalchemy import create_engine, text

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

# --- CONEXÃO COM O SUPABASE (POSTGRESQL) ---
@st.cache_resource
def obter_engine():
    if "postgres" in st.secrets and "url" in st.secrets["postgres"]:
        db_url = st.secrets["postgres"]["url"]
        # Garante compatibilidade do protocolo postgresql para o SQLAlchemy
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return create_engine(db_url)
    else:
        # Fallback local se não achar secrets
        return create_engine("sqlite:///power_baterias.db")

engine = obter_engine()

# Usuários do Sistema
USUARIOS = {
    "arthur": {"senha": "Arthur123", "perfil": "ADM", "nome": "Arthur"},
    "sandro": {"senha": "1234", "perfil": "ADM", "nome": "Sandro"},
    "pedro": {"senha": "Pedro1234", "perfil": "Vendedor", "nome": "Pedro"},
    "wanderson": {"senha": "venda123", "perfil": "Vendedor", "nome": "Wanderson"},
}

def inicializar_banco():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                categoria VARCHAR(100) NOT NULL,
                nome VARCHAR(150) NOT NULL,
                amperagem INT NOT NULL,
                marca VARCHAR(100) NOT NULL,
                preco NUMERIC(10,2) NOT NULL,
                quantidade INT NOT NULL,
                meses_garantia INT DEFAULT 12,
                veiculo VARCHAR(255) DEFAULT ''
            );
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                data_hora VARCHAR(50) NOT NULL,
                vendedor VARCHAR(100) NOT NULL,
                produto_nome VARCHAR(150) NOT NULL,
                quantidade INT NOT NULL,
                preco_original NUMERIC(10,2) NOT NULL,
                desconto NUMERIC(10,2) NOT NULL,
                valor_total NUMERIC(10,2) NOT NULL,
                forma_pagamento VARCHAR(50) NOT NULL,
                cliente_nome VARCHAR(150),
                cliente_cpf VARCHAR(30),
                veiculo_placa VARCHAR(20),
                veiculo_modelo VARCHAR(150) DEFAULT '',
                numero_serie VARCHAR(100),
                parcelas VARCHAR(10) DEFAULT '1x',
                amperagem INT DEFAULT 0,
                meses_garantia INT DEFAULT 12
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fechamento_caixa (
                id SERIAL PRIMARY KEY,
                data_fechamento VARCHAR(30) NOT NULL,
                responsavel VARCHAR(100) NOT NULL,
                total_faturado NUMERIC(10,2) NOT NULL,
                total_vendas INT NOT NULL
            );
        """))

        # Carga Inicial Completa caso a tabela de produtos esteja vazia no Supabase
        res = conn.execute(text("SELECT COUNT(*) FROM produtos")).fetchone()[0]
        if res == 0:
            catalogo_completo = [
                {"cat": "36/40/45/48 Ah", "nome": "Heliar 48Ah", "amp": 48, "marca": "Heliar", "pr": 550.00, "qtd": 10, "gar": 24, "veic": "Gol, Palio, Uno"},
                {"cat": "36/40/45/48 Ah", "nome": "Moura 48Ah", "amp": 48, "marca": "Moura", "pr": 550.00, "qtd": 10, "gar": 24, "veic": "Gol, Palio, Uno"},
                {"cat": "36/40/45/48 Ah", "nome": "Cral 45Ah", "amp": 45, "marca": "Cral", "pr": 420.00, "qtd": 10, "gar": 24, "veic": "Celta, Ka, Fit"},
                {"cat": "36/40/45/48 Ah", "nome": "KF 40Ah", "amp": 40, "marca": "KF", "pr": 250.00, "qtd": 10, "gar": 12, "veic": "Motos / Veículos Leves"},
                {"cat": "36/40/45/48 Ah", "nome": "Super Life 36Ah", "amp": 36, "marca": "Super Life", "pr": 220.00, "qtd": 10, "gar": 12, "veic": "Veículos Populares"},

                {"cat": "50 Ah Caixa Alta", "nome": "Heliar 50Ah Caixa Alta", "amp": 50, "marca": "Heliar", "pr": 550.00, "qtd": 10, "gar": 24, "veic": "Fiesta, EcoSport, Ka"},
                {"cat": "50 Ah Caixa Alta", "nome": "Moura 50Ah Caixa Alta", "amp": 50, "marca": "Moura", "pr": 550.00, "qtd": 10, "gar": 24, "veic": "Fiesta, EcoSport, Ka"},
                {"cat": "50 Ah Caixa Alta", "nome": "Cral 50Ah Caixa Alta", "amp": 50, "marca": "Cral", "pr": 430.00, "qtd": 10, "gar": 18, "veic": "Fiesta, EcoSport, Ka"},

                {"cat": "60 Ah Padrão", "nome": "Heliar 60Ah", "amp": 60, "marca": "Heliar", "pr": 550.00, "qtd": 10, "gar": 24, "veic": "Civic, Corolla, Onix, HB20, Fox"},
                {"cat": "60 Ah Padrão", "nome": "Moura 60Ah", "amp": 60, "marca": "Moura", "pr": 550.00, "qtd": 10, "gar": 24, "veic": "Civic, Corolla, Onix, HB20, Fox"},
                {"cat": "60 Ah Padrão", "nome": "Cral 60Ah", "amp": 60, "marca": "Cral", "pr": 450.00, "qtd": 10, "gar": 18, "veic": "Civic, Corolla, Onix, HB20, Fox"},
                {"cat": "60 Ah Padrão", "nome": "ACDelco 60Ah", "amp": 60, "marca": "ACDelco", "pr": 480.00, "qtd": 10, "gar": 18, "veic": "Onix, Prisma, Spin, Cobalt"},
                {"cat": "60 Ah Padrão", "nome": "KF 60Ah", "amp": 60, "marca": "KF", "pr": 320.00, "qtd": 10, "gar": 12, "veic": "Veículos Leves e Médios"},

                {"cat": "70 Ah", "nome": "Heliar 70Ah", "amp": 70, "marca": "Heliar", "pr": 760.00, "qtd": 10, "gar": 24, "veic": "SUVs, Pickups, Compass, Renegade"},
                {"cat": "70 Ah", "nome": "Moura 70Ah", "amp": 70, "marca": "Moura", "pr": 760.00, "qtd": 10, "gar": 24, "veic": "SUVs, Pickups, Compass, Renegade"},
                {"cat": "70 Ah", "nome": "Cral 70Ah", "amp": 70, "marca": "Cral", "pr": 620.00, "qtd": 10, "gar": 18, "veic": "SUVs, Pickups, Compass, Renegade"},
            ]
            for item in catalogo_completo:
                conn.execute(text("""
                    INSERT INTO produtos (categoria, nome, amperagem, marca, preco, quantidade, meses_garantia, veiculo)
                    VALUES (:cat, :nome, :amp, :marca, :pr, :qtd, :gar, :veic)
                """), item)

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
            Paragraph(f"<b>COMPROVANTE DE VENDA</b><br/><b>Nº: #{dados['id']:06d}</b><br/>Data: {dados['data_hora']}", nf_title)
        ]
    ]
    t_topo = Table(topo, colWidths=[320, 220])
    story.append(t_topo)
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

    desc_ajuste = f"R$ {abs(float(dados['desconto'])):.2f}" if float(dados['desconto']) >= 0 else f"+ R$ {abs(float(dados['desconto'])):.2f}"

    table_prod = [
        [Paragraph("<b>Item / Descrição</b>", body_bold), Paragraph("<b>Amp</b>", body_bold), Paragraph("<b>Qtd</b>", body_bold), Paragraph("<b>Preço Unit.</b>", body_bold), Paragraph("<b>Ajuste</b>", body_bold), Paragraph("<b>Total</b>", body_bold)],
        [
            Paragraph(dados['produto_nome'], body_style),
            Paragraph(f"{dados['amperagem']}Ah", body_style),
            Paragraph(str(dados['quantidade']), body_style),
            Paragraph(f"R$ {float(dados['preco_original']):.2f}", body_style),
            Paragraph(desc_ajuste, body_style),
            Paragraph(f"<b>R$ {float(dados['valor_total']):.2f}</b>", body_style)
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
            Paragraph(f"<b>VALOR TOTAL: R$ {float(dados['valor_total']):.2f}</b>", ParagraphStyle('Tot', parent=body_bold, fontSize=11, alignment=2))
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
    with engine.begin() as conn:
        conn.execute(text("UPDATE produtos SET quantidade = quantidade + :qtd WHERE nome = :nome"), {"qtd": quantidade, "nome": produto_nome})
        conn.execute(text("DELETE FROM vendas WHERE id = :id"), {"id": id_venda})

def excluir_bateria(id_bateria):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM produtos WHERE id = :id"), {"id": id_bateria})

inicializar_banco()

# --- LOGIN E SESSÃO ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = None
    st.session_state["vendedor_nome"] = ""
    st.session_state["usuario_key"] = ""

if not st.session_state["logado"]:
    if os.path.exists("loo.png"):
        st.image("logo.png", width=300)
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
                st.session_state["usuario_key"] = usuario_input
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos! Acesso negado.")
    st.stop()

# --- MODAIS E DIÁLOGOS ---
@st.dialog("Venda Finalizada com Sucesso! 🟢")
def modal_gerar_pdf(dados_venda):
    st.write(f"**Cliente:** {dados_venda['cliente_nome']}")
    st.write(f"**Bateria:** {dados_venda['produto_nome']}")
    st.write(f"**Valor Total:** R$ {float(dados_venda['valor_total']):.2f}")
    
    if REPORTLAB_DISPONIVEL:
        st.write("Deseja gerar e baixar o **Comprovante de Venda** agora?")
        pdf_bytes = gerador_pdf_nota(dados_venda)
        st.download_button(
            label="📄 Baixar Nota Fiscal (PDF)",
            data=pdf_bytes,
            file_name=f"nota_fiscal_{dados_venda['id']}_power_baterias.pdf",
            mime="application/pdf",
            use_container_width=True
        )

@st.dialog("Confirmar Cancelamento 🔴")
def modal_confirmar_cancelamento(id_venda, produto_nome, quantidade):
    st.write(f"Tem certeza que deseja **cancelar a venda #{id_venda}**?")
    st.caption(f"Produto: {produto_nome} | Qtd a devolver: {quantidade}")
    
    if st.button("Sim, Cancelar Venda", use_container_width=True):
        cancelar_venda(id_venda, produto_nome, quantidade)
        st.toast(f"Venda #{id_venda} cancelada e produto devolvido!", icon="✅")
        st.rerun()

@st.dialog("Confirmar Exclusão de Bateria 🔴")
def modal_confirmar_exclusao_bateria(id_bateria, nome_bateria):
    st.write(f"**Atenção:** Você tem certeza de que deseja excluir a bateria?")
    st.write(f"📌 **{nome_bateria}** (ID #{id_bateria})")
    
    col_sim, col_nao = st.columns(2)
    if col_sim.button("Sim, Excluir", use_container_width=True):
        excluir_bateria(id_bateria)
        st.toast(f"Bateria {nome_bateria} excluída com sucesso!", icon="✅")
        st.rerun()

@st.dialog("Bateria Editada com Sucesso! 🟢")
def modal_bateria_editada_sucesso(nome_bateria):
    st.write(f"As alterações da bateria **{nome_bateria}** foram salvas no sistema!")
    if st.button("OK", use_container_width=True):
        st.rerun()

def calcular_desempenho_vendedor(nome_vendedor):
    df_vendas = pd.read_sql_query("SELECT vendedor, quantidade FROM vendas", engine)
    
    if df_vendas.empty:
        return 0, 0, 0.0

    total_geral = df_vendas['quantidade'].sum()
    minhas_vendas = df_vendas[df_vendas['vendedor'].str.lower() == nome_vendedor.lower()]['quantidade'].sum()
    
    porcentagem = (minhas_vendas / total_geral * 100) if total_geral > 0 else 0.0
    return minhas_vendas, total_geral, porcentagem

# --- MENU LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.markdown("## POWER BATERIAS")

st.sidebar.caption("DISK BATERIAS: (61) 99519-1090")

# Informações de Utilizador e Desempenho
vendedor_atual = st.session_state['vendedor_nome']
un_vendedor, total_loja, pct_desempenho = calcular_desempenho_vendedor(vendedor_atual)

st.sidebar.markdown(f"Utilizador: **{vendedor_atual} {st.session_state['perfil']}**")
st.sidebar.markdown(f"Desempenho Mês: **{pct_desempenho:.0f}%** ({un_vendedor} unidades vendidas)")

st.sidebar.write("---")

opcoes_menu = ["Nova Venda", "Estoque Organizado", "Consultar Garantia"]
if st.session_state["perfil"] == "ADM":
    opcoes_menu += ["Fechamento de Caixa", "Editar Baterias", "Histórico", "Painel ADM"]

if "pagina_atual" not in st.session_state or st.session_state["pagina_atual"] not in opcoes_menu:
    st.session_state["pagina_atual"] = opcoes_menu[0]

menu = st.sidebar.radio("Navegação", opcoes_menu, key="pagina_atual")

st.sidebar.write("---")
if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.session_state["perfil"] = None
    st.session_state["vendedor_nome"] = ""
    st.rerun()

# --- ABA 1: NOVA VENDA ---
if menu == "Nova Venda":
    st.header("Lançamento de Venda")
    
    df_prods = pd.read_sql_query("SELECT id, categoria, nome, amperagem, preco, quantidade, meses_garantia, veiculo FROM produtos WHERE quantidade > 0", engine)

    if df_prods.empty:
        st.warning("Nenhuma bateria disponível no estoque!")
    else:
        opcoes_prods = [""] + [f"ID {row['id']} | {row['nome']} - R$ {float(row['preco']):.2f} (Estoque: {row['quantidade']})" for _, row in df_prods.iterrows()]
        
        prod_sel_str = st.selectbox("Selecione a Bateria", opcoes_prods, index=0)
        
        if prod_sel_str != "":
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
                    
                    ajuste_preco = st.number_input("Ajuste de Preço (R$) - Reduzir com '-' ou Aumentar com '+'", value=0.0, step=5.0)
                    valor_final = (preco_base * qtd) - ajuste_preco
                    st.success(f"Valor Total Final: R$ {valor_final:.2f}")
                    
                    vendedor = st.text_input("Nome do Vendedor *", value=st.session_state.get("vendedor_nome", ""))
                    pagamento = st.selectbox("Forma de Pagamento *", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
                    parcelas = st.selectbox("Parcelas", [f"{i}x" for i in range(1, 13)]) if pagamento == "Cartão de Crédito" else "1x"
                    
                with col2:
                    st.subheader("Dados do Cliente e Veículo")
                    cliente = st.text_input("Nome do Cliente")
                    cpf = st.text_input("CPF / CNPJ (Opcional)")
                    veiculo_mod = st.text_input("Modelo do Veículo *", value=dados_p['veiculo'] or "")
                    placa = st.text_input("Placa do Veículo (Opcional)")
                    serie = st.text_input("Nº de Série da Bateria (Opcional)")

                btn_finalizar = st.form_submit_button("Concluir Venda", use_container_width=True)

            if btn_finalizar:
                if not vendedor.strip():
                    st.error("Erro: O campo 'Nome do Vendedor' é obrigatório!")
                elif not veiculo_mod.strip():
                    st.error("Erro: O campo 'Modelo do Veículo' é obrigatório para registrar a venda!")
                elif qtd <= 0 or qtd > dados_p['quantidade']:
                    st.error("Quantidade inválida ou maior que o estoque disponível!")
                else:
                    dt_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    with engine.begin() as conn:
                        conn.execute(text("UPDATE produtos SET quantidade = quantidade - :qtd WHERE id = :id"), {"qtd": qtd, "id": id_prod})
                        res = conn.execute(text("""
                            INSERT INTO vendas (
                                data_hora, vendedor, produto_nome, quantidade, preco_original, 
                                desconto, valor_total, forma_pagamento, cliente_nome, cliente_cpf, 
                                veiculo_placa, veiculo_modelo, numero_serie, parcelas, amperagem, meses_garantia
                            ) VALUES (
                                :data_hora, :vendedor, :produto_nome, :quantidade, :preco_original, 
                                :desconto, :valor_total, :forma_pagamento, :cliente_nome, :cliente_cpf, 
                                :veiculo_placa, :veiculo_modelo, :numero_serie, :parcelas, :amperagem, :meses_garantia
                            ) RETURNING id;
                        """), {
                            "data_hora": dt_hoje, "vendedor": vendedor.strip(), "produto_nome": dados_p['nome'],
                            "quantidade": qtd, "preco_original": preco_base, "desconto": ajuste_preco,
                            "valor_total": valor_final, "forma_pagamento": pagamento,
                            "cliente_nome": cliente or "Consumidor Não Identificado", "cliente_cpf": cpf or "Não Informado",
                            "veiculo_placa": placa.upper() or "Não Informado", "veiculo_modelo": veiculo_mod.strip(),
                            "numero_serie": serie.upper() or "Não Informado", "parcelas": parcelas,
                            "amperagem": int(dados_p['amperagem']), "meses_garantia": int(dados_p['meses_garantia'])
                        })
                        id_venda = res.fetchone()[0]

                    modal_gerar_pdf({
                        'id': id_venda, 'data_hora': dt_hoje, 'vendedor': vendedor.strip(),
                        'cliente_nome': cliente or "Consumidor Não Identificado", 'cliente_cpf': cpf or "Não Informado",
                        'veiculo_placa': placa.upper() or "Não Informado", 'veiculo_modelo': veiculo_mod.strip(),
                        'numero_serie': serie.upper() or "Não Informado", 'produto_nome': dados_p['nome'],
                        'amperagem': dados_p['amperagem'], 'quantidade': qtd, 'preco_original': preco_base,
                        'desconto': ajuste_preco, 'valor_total': valor_final, 'forma_pagamento': pagamento,
                        'parcelas': parcelas, 'meses_garantia': dados_p['meses_garantia']
                    })

# --- ABA 2: FECHAMENTO DE CAIXA (ADM) ---
elif menu == "Fechamento de Caixa" and st.session_state["perfil"] == "ADM":
    st.header("🔑 Fechamento de Caixa & Relatório Financeiro")
    
    df_vendas_todas = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", engine)
    dt_hoje_str = datetime.now().strftime("%d/%m/%Y")
    
    if not df_vendas_todas.empty:
        df_vendas_todas['data_apenas'] = df_vendas_todas['data_hora'].apply(lambda x: str(x).split(" ")[0])
        df_vendas_hoje = df_vendas_todas[df_vendas_todas['data_apenas'] == dt_hoje_str]
    else:
        df_vendas_hoje = pd.DataFrame()

    total_hoje = float(df_vendas_hoje['valor_total'].sum()) if not df_vendas_hoje.empty else 0.0
    qtd_hoje = int(df_vendas_hoje['quantidade'].sum()) if not df_vendas_hoje.empty else 0

    col1, col2 = st.columns(2)
    col1.metric(f"Faturamento de Hoje ({dt_hoje_str})", f"R$ {total_hoje:,.2f}")
    col2.metric("Baterias Vendidas Hoje", f"{qtd_hoje} Unidades")

    st.write("---")
    st.subheader("🔒 Realizar Fechamento do Caixa de Hoje")
    
    with st.form("form_fechar_caixa"):
        senha_adm = st.text_input("Digite sua Senha de ADM para Confirmar o Fechamento", type="password")
        if st.form_submit_button("Confirmar e Fechar Caixa do Dia"):
            usr_key = st.session_state["usuario_key"]
            if USUARIOS[usr_key]["senha"] == senha_adm:
                with engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO fechamento_caixa (data_fechamento, responsavel, total_faturado, total_vendas)
                        VALUES (:data, :resp, :fat, :qtd)
                    """), {"data": dt_hoje_str, "resp": st.session_state["vendedor_nome"], "fat": total_hoje, "qtd": qtd_hoje})
                st.success(f"Caixa do dia {dt_hoje_str} fechado com sucesso por {st.session_state['vendedor_nome']}!")
            else:
                st.error("Senha de ADM incorreta!")

    st.write("---")
    st.subheader("📅 Consultar Fechamentos e Vendas por Data")

    if not df_vendas_todas.empty:
        datas_disponiveis = sorted(df_vendas_todas['data_apenas'].unique(), reverse=True)
        data_sel = st.selectbox("Selecione a Data:", datas_disponiveis)
        
        df_dia = df_vendas_todas[df_vendas_todas['data_apenas'] == data_sel]
        
        st.write(f"**Vendas do dia {data_sel}** - Faturamento Total: **R$ {float(df_dia['valor_total'].sum()):,.2f}**")
        st.dataframe(df_dia[['id', 'data_hora', 'vendedor', 'produto_nome', 'quantidade', 'valor_total', 'forma_pagamento', 'cliente_nome']], use_container_width=True, hide_index=True)

# --- ABA 3: ESTOQUE ORGANIZADO ---
elif menu == "Estoque Organizado":
    st.header("Estoque Organizado por Categoria")
    
    df_estoque = pd.read_sql_query("SELECT id, categoria, nome, amperagem, marca, veiculo, preco, quantidade, meses_garantia FROM produtos ORDER BY id ASC", engine)
    
    for cat in df_estoque['categoria'].unique():
        with st.expander(f"Categoria: {cat}", expanded=True):
            df_sub = df_estoque[df_estoque['categoria'] == cat][['id', 'nome', 'marca', 'amperagem', 'veiculo', 'preco', 'quantidade', 'meses_garantia']]
            df_sub.columns = ['ID', 'Modelo', 'Marca', 'Amp (Ah)', 'Veículos Indicados', 'Preço (R$)', 'Qtd Est.', 'Garantia (Meses)']
            st.dataframe(df_sub, use_container_width=True, hide_index=True)

# --- ABA 4: EDITAR BATERIAS ---
elif menu == "Editar Baterias" and st.session_state["perfil"] == "ADM":
    st.header("Alterar ou Excluir Baterias")
    
    df_prods = pd.read_sql_query("SELECT * FROM produtos ORDER BY id ASC", engine)
    cats_existentes = pd.read_sql_query("SELECT DISTINCT categoria FROM produtos", engine)['categoria'].tolist()

    opcoes = ["-- Selecione uma Bateria --"] + [f"ID {row['id']} - {row['nome']} (R$ {float(row['preco']):.2f})" for _, row in df_prods.iterrows()]
    selecionado = st.selectbox("Selecione a bateria para alterar:", opcoes)
    
    if selecionado != "-- Selecione uma Bateria --":
        id_sel = int(selecionado.split(" ")[1])
        item = df_prods[df_prods['id'] == id_sel].iloc[0]
        
        cat_opcoes = list(cats_existentes) + ["+ Criar Nova Categoria"]
        cat_idx = cat_opcoes.index(item['categoria']) if item['categoria'] in cat_opcoes else 0
        cat_selecionada = st.selectbox("Categoria/Família *", cat_opcoes, index=cat_idx)
        e_cat = st.text_input("Digite o Nome da Nova Categoria:") if cat_selecionada == "+ Criar Nova Categoria" else cat_selecionada

        e_nome = st.text_input("Nome/Modelo", value=item['nome'])
        e_veiculo = st.text_input("Veículos Recomendados", value=item['veiculo'] if 'veiculo' in item else '')
        
        col1, col2, col3 = st.columns(3)
        e_amp = col1.number_input("Amperagem (Ah)", min_value=1, value=int(item['amperagem']))
        e_marca = col1.text_input("Marca", value=item['marca'])
        e_preco = col2.number_input("Preço R$", min_value=0.0, value=float(item['preco']))
        e_qtd = col2.number_input("Estoque", min_value=0, value=int(item['quantidade']))
        e_garantia = col3.number_input("Garantia (Meses)", min_value=1, value=int(item['meses_garantia']))
        
        col_salvar, col_excluir = st.columns([2, 1])
        if col_salvar.button("Salvar Alterações", use_container_width=True):
            with engine.begin() as conn:
                conn.execute(text("""
                    UPDATE produtos SET categoria = :cat, nome = :nome, amperagem = :amp, marca = :marca, veiculo = :veic, preco = :preco, quantidade = :qtd, meses_garantia = :gar
                    WHERE id = :id
                """), {"cat": e_cat.strip(), "nome": e_nome.strip(), "amp": e_amp, "marca": e_marca, "veic": e_veiculo, "preco": e_preco, "qtd": e_qtd, "gar": e_garantia, "id": id_sel})
            modal_bateria_editada_sucesso(e_nome.strip())

        if col_excluir.button("🔴 Excluir Bateria", use_container_width=True):
            modal_confirmar_exclusao_bateria(id_sel, item['nome'])

# --- ABA 5: GARANTIA ---
elif menu == "Consultar Garantia":
    st.header("Consulta de Garantias")
    termo = st.text_input("Pesquisar por Nome do Cliente, CPF, Placa, Veículo ou Nº de Série")
    
    if termo:
        df_garantia = pd.read_sql_query("""
            SELECT id, data_hora, cliente_nome, cliente_cpf, produto_nome, amperagem, veiculo_placa, veiculo_modelo, numero_serie, meses_garantia 
            FROM vendas WHERE cliente_nome ILIKE %(t)s OR cliente_cpf ILIKE %(t)s OR veiculo_placa ILIKE %(t)s OR veiculo_modelo ILIKE %(t)s OR numero_serie ILIKE %(t)s
            ORDER BY id DESC
        """, engine, params={"t": f"%{termo}%"})
    else:
        df_garantia = pd.read_sql_query("SELECT id, data_hora, cliente_nome, cliente_cpf, produto_nome, amperagem, veiculo_placa, veiculo_modelo, numero_serie, meses_garantia FROM vendas ORDER BY id DESC LIMIT 15", engine)

    if not df_garantia.empty:
        hoje = datetime.now()
        resultados = []
        for _, r in df_garantia.iterrows():
            try:
                dt_v = datetime.strptime(r['data_hora'], "%d/%m/%Y %H:%M:%S")
            except:
                dt_v = hoje
            restantes = ((dt_v + timedelta(days=(r['meses_garantia'] or 12) * 30)) - hoje).days
            resultados.append({
                "Nº Venda": r['id'], "Data": dt_v.strftime("%d/%m/%Y"), "Cliente": r['cliente_nome'],
                "CPF / CNPJ": r['cliente_cpf'], "Produto": f"{r['produto_nome']} ({r['amperagem']}Ah)",
                "Veículo": r['veiculo_modelo'], "Placa": r['veiculo_placa'], "Nº Série": r['numero_serie'],
                "Status": "🟢 NA GARANTIA" if restantes > 0 else "🔴 VENCIDA", "Prazo": f"{restantes} dias restantes" if restantes > 0 else f"Vencida há {abs(restantes)} dias"
            })
        st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)

# --- ABA 6: HISTÓRICO DE VENDAS ---
elif menu == "Histórico" and st.session_state["perfil"] == "ADM":
    st.header("Histórico Geral de Vendas")
    df_hist = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", engine)
    
    for _, row in df_hist.iterrows():
        col_i, col_d, col_v, col_btn, col_del = st.columns([1, 2.5, 2, 2, 2])
        col_i.write(f"**Nº #{row['id']}**")
        col_d.write(f"**Data:** {row['data_hora']}<br/>**Cliente:** {row['cliente_nome']}<br/>**Vendedor:** {row['vendedor']}", unsafe_allow_html=True)
        col_v.write(f"**Produto:** {row['produto_nome']}<br/>**Total:** R$ {float(row['valor_total']):.2f}", unsafe_allow_html=True)
        
        if REPORTLAB_DISPONIVEL:
            pdf_bytes = gerador_pdf_nota(row.to_dict())
            col_btn.download_button("📄 PDF", data=pdf_bytes, file_name=f"nota_{row['id']}.pdf", mime="application/pdf", key=f"btn_pdf_{row['id']}")

        if col_del.button("🔴 Cancelar", key=f"btn_del_{row['id']}"):
            modal_confirmar_cancelamento(row['id'], row['produto_nome'], row['quantidade'])

# --- ABA 7: PAINEL ADM ---
elif menu == "Painel ADM" and st.session_state["perfil"] == "ADM":
    st.header("Painel ADM - Cadastro de Produtos")
    
    cats_existentes = pd.read_sql_query("SELECT DISTINCT categoria FROM produtos", engine)['categoria'].tolist()

    with st.form("cad_manual"):
        cat_opcoes = list(cats_existentes) + ["+ Criar Nova Categoria"]
        cat_sel = st.selectbox("Categoria/Família", cat_opcoes)
        f_cat = st.text_input("Nome da Nova Categoria:") if cat_sel == "+ Criar Nova Categoria" else cat_sel

        f_nome = st.text_input("Nome do Modelo (ex: Heliar 60Ah)")
        f_veiculo = st.text_input("Veículos Recomendados", value="Carros de Passeio")
        f_amp = st.number_input("Amperagem (Ah)", min_value=1, value=60)
        f_marca = st.text_input("Marca", value="Heliar")
        f_preco = st.number_input("Preço (R$)", min_value=0.0, value=400.0)
        f_qtd = st.number_input("Quantidade em Estoque", min_value=1, value=10)
        f_garantia = st.number_input("Garantia (Meses)", min_value=1, value=24)
        
        if st.form_submit_button("Cadastrar Bateria"):
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO produtos (categoria, nome, amperagem, marca, veiculo, preco, quantidade, meses_garantia)
                    VALUES (:cat, :nome, :amp, :marca, :veic, :preco, :qtd, :gar)
                """), {"cat": f_cat.strip(), "nome": f_nome.strip(), "amp": f_amp, "marca": f_marca, "veic": f_veiculo, "preco": f_preco, "qtd": f_qtd, "gar": f_garantia})
            st.success("Nova bateria cadastrada com sucesso no Supabase!")
            st.rerun()
