import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO
from supabase import create_client, Client

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

# --- CONEXÃO COM SUPABASE ---
SUPABASE_URL = "https://pzyxmzhfqzfebzxpgkyy.supabase.co"
SUPABASE_KEY = "sb_publishable_aKrPEl7lz13LDqTSKcRghg_3Wugc8Ul"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- FUNÇÃO PARA POPULAR O ESTOQUE INICIAL COM NOVAS CATEGORIAS ---
def popular_baterias_iniciais():
    try:
        res = supabase.table("produtos").select("id").limit(1).execute()
        if not res.data:
            lista_inicial = [
                # 36Ah a 48Ah
                {"categoria": "36Ah a 48Ah", "nome": "Heliar 48Ah", "marca": "Heliar", "amperagem": 48, "preco": 550.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "36Ah a 48Ah", "nome": "Moura 48Ah", "marca": "Moura", "amperagem": 48, "preco": 550.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "36Ah a 48Ah", "nome": "Cral 45Ah", "marca": "Cral", "amperagem": 45, "preco": 420.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "36Ah a 48Ah", "nome": "KF 40Ah", "marca": "KF", "amperagem": 40, "preco": 250.00, "quantidade": 10, "meses_garantia": 12},
                {"categoria": "36Ah a 48Ah", "nome": "Super Life 36Ah", "marca": "Super Life", "amperagem": 36, "preco": 220.00, "quantidade": 10, "meses_garantia": 12},

                # 60Ah A / B
                {"categoria": "60Ah A", "nome": "Heliar 60Ah", "marca": "Heliar", "amperagem": 60, "preco": 550.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "60Ah A", "nome": "Moura 60Ah", "marca": "Moura", "amperagem": 60, "preco": 550.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "60Ah B", "nome": "América 60Ah", "marca": "América", "amperagem": 60, "preco": 450.00, "quantidade": 10, "meses_garantia": 18},
                {"categoria": "60Ah B", "nome": "Cral 60Ah", "marca": "Cral", "amperagem": 60, "preco": 430.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "60Ah B", "nome": "KF 60Ah", "marca": "KF", "amperagem": 60, "preco": 330.00, "quantidade": 10, "meses_garantia": 12},
                {"categoria": "60Ah B", "nome": "Super Life 60Ah", "marca": "Super Life", "amperagem": 60, "preco": 330.00, "quantidade": 10, "meses_garantia": 12},

                # 70Ah
                {"categoria": "70Ah", "nome": "Heliar 70Ah", "marca": "Heliar", "amperagem": 70, "preco": 760.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "70Ah", "nome": "Moura 70Ah", "marca": "Moura", "amperagem": 70, "preco": 760.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "70Ah", "nome": "América 70Ah", "marca": "América", "amperagem": 70, "preco": 590.00, "quantidade": 10, "meses_garantia": 18},
                {"categoria": "70Ah", "nome": "Cral 70Ah", "marca": "Cral", "amperagem": 70, "preco": 580.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "70Ah", "nome": "Super Life 70Ah", "marca": "Super Life", "amperagem": 70, "preco": 390.00, "quantidade": 10, "meses_garantia": 12},

                # 75Ah
                {"categoria": "75Ah", "nome": "Heliar 75Ah", "marca": "Heliar", "amperagem": 75, "preco": 790.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "75Ah", "nome": "Moura 75Ah", "marca": "Moura", "amperagem": 75, "preco": 790.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "75Ah", "nome": "Cral 75Ah", "marca": "Cral", "amperagem": 75, "preco": 580.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "75Ah", "nome": "KF 75Ah", "marca": "KF", "amperagem": 75, "preco": 490.00, "quantidade": 10, "meses_garantia": 12},

                # 40Ah JD Slim
                {"categoria": "40Ah JD Slim", "nome": "Heliar 40 Slim JD", "marca": "Heliar", "amperagem": 40, "preco": 590.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "40Ah JD Slim", "nome": "Moura 40 Slim JD", "marca": "Moura", "amperagem": 40, "preco": 590.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "40Ah JD Slim", "nome": "Cral 40 Slim JD", "marca": "Cral", "amperagem": 40, "preco": 420.00, "quantidade": 10, "meses_garantia": 18},
                {"categoria": "40Ah JD Slim", "nome": "KF 40 Slim JD", "marca": "KF", "amperagem": 40, "preco": 350.00, "quantidade": 10, "meses_garantia": 12},

                # 72Ah Start Stop
                {"categoria": "72Ah Start Stop", "nome": "Heliar 72Ah Start Stop", "marca": "Heliar", "amperagem": 72, "preco": 1150.00, "quantidade": 10, "meses_garantia": 24},
                {"categoria": "72Ah Start Stop", "nome": "Moura 72Ah Start Stop", "marca": "Moura", "amperagem": 72, "preco": 1150.00, "quantidade": 10, "meses_garantia": 24},

                # 90Ah
                {"categoria": "90Ah", "nome": "Heliar 90Ah", "marca": "Heliar", "amperagem": 90, "preco": 970.00, "quantidade": 10, "meses_garantia": 15},
                {"categoria": "90Ah", "nome": "Moura 90Ah", "marca": "Moura", "amperagem": 90, "preco": 970.00, "quantidade": 10, "meses_garantia": 12},
                {"categoria": "90Ah", "nome": "Cral 90Ah", "marca": "Cral", "amperagem": 90, "preco": 690.00, "quantidade": 10, "meses_garantia": 15},
                {"categoria": "90Ah", "nome": "Biachine 90Ah", "marca": "Biachine", "amperagem": 90, "preco": 590.00, "quantidade": 10, "meses_garantia": 12},
            ]
            supabase.table("produtos").insert(lista_inicial).execute()
    except Exception as e:
        st.error(f"Erro ao inicializar produtos: {e}")

popular_baterias_iniciais()

USUARIOS = {
    "arthur": {"senha": "Arthur123", "perfil": "ADM", "nome": "Arthur"},
    "sandro": {"senha": "1234", "perfil": "ADM", "nome": "Sandro"},
    "pedro": {"senha": "Pedro1234", "perfil": "Vendedor", "nome": "Pedro"},
    "wanderson": {"senha": "venda123", "perfil": "Vendedor", "nome": "Wanderson"},
}

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
    prod = supabase.table("produtos").select("quantidade").eq("nome", produto_nome).execute()
    if prod.data:
        nova_qtd = prod.data[0]["quantidade"] + quantidade
        supabase.table("produtos").update({"quantidade": nova_qtd}).eq("nome", produto_nome).execute()
    supabase.table("vendas").delete().eq("id", id_venda).execute()

# --- LOGIN ---
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

# --- MENU LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.markdown("## POWER BATERIAS")

st.sidebar.caption("DISK BATERIAS: (61) 99519-1090")

opcoes_menu = ["Nova Venda", "Estoque Organizado", "Consultar Garantia"]
if st.session_state["perfil"] == "ADM":
    opcoes_menu += ["Editar Baterias", "Histórico", "Painel ADM"]

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
    res = supabase.table("produtos").select("id, categoria, nome, amperagem, preco, quantidade, meses_garantia, veiculo").execute()
    df_prods = pd.DataFrame(res.data)

    if df_prods.empty:
        st.warning("Nenhuma bateria no estoque!")
    else:
        opcoes_prods = [""] + [f"ID {row['id']} | [{row.get('categoria', 'Geral')}] {row['nome']} - R$ {float(row['preco']):.2f} (Estoque: {int(row['quantidade'])})" for _, row in df_prods.iterrows()]
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
                    veiculo_mod = st.text_input("Modelo do Veículo *", value=str(dados_p.get('veiculo') or ''))
                    placa = st.text_input("Placa")
                    serie = st.text_input("Nº Série Bateria")

                if st.form_submit_button("Concluir Venda", use_container_width=True):
                    if not vendedor.strip() or not veiculo_mod.strip():
                        st.error("Preencha Vendedor e Veículo!")
                    else:
                        dt_hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        
                        nova_qtd = int(dados_p['quantidade']) - qtd
                        supabase.table("produtos").update({"quantidade": nova_qtd}).eq("id", id_prod).execute()
                        
                        venda_payload = {
                            "data_hora": dt_hoje,
                            "vendedor": vendedor.strip(),
                            "produto_nome": dados_p['nome'],
                            "quantidade": int(qtd),
                            "preco_original": float(preco_base),
                            "desconto": float(ajuste_preco),
                            "valor_total": float(valor_final),
                            "forma_pagamento": pagamento,
                            "cliente_nome": cliente or "Consumidor Não Identificado",
                            "cliente_cpf": cpf or "Não Informado",
                            "veiculo_placa": placa.upper() or "Não Informado",
                            "veiculo_modelo": veiculo_mod.strip(),
                            "numero_serie": serie.upper() or "Não Informado",
                            "parcelas": parcelas,
                            "amperagem": int(dados_p['amperagem']),
                            "meses_garantia": int(dados_p['meses_garantia'])
                        }
                        insert_res = supabase.table("vendas").insert(venda_payload).execute()
                        id_venda = insert_res.data[0]['id'] if insert_res.data else 0

                        modal_gerar_pdf({'id': id_venda, 'data_hora': dt_hoje, 'vendedor': vendedor.strip(), 'cliente_nome': cliente or "Consumidor Não Identificado", 'cliente_cpf': cpf or "Não Informado", 'veiculo_placa': placa.upper() or "Não Informado", 'veiculo_modelo': veiculo_mod.strip(), 'numero_serie': serie.upper() or "Não Informado", 'produto_nome': dados_p['nome'], 'amperagem': dados_p['amperagem'], 'quantidade': qtd, 'preco_original': preco_base, 'desconto': ajuste_preco, 'valor_total': valor_final, 'forma_pagamento': pagamento, 'parcelas': parcelas, 'meses_garantia': dados_p['meses_garantia']})

# --- ABA 2: ESTOQUE ORGANIZADO POR CATEGORIA ---
elif menu == "Estoque Organizado":
    st.header("Estoque Geral por Categoria")
    res = supabase.table("produtos").select("id, categoria, nome, marca, amperagem, preco, quantidade, meses_garantia").order("categoria").order("id").execute()
    df_estoque = pd.DataFrame(res.data)
    
    if not df_estoque.empty:
        df_estoque.columns = ['ID', 'Categoria', 'Modelo', 'Marca', 'Amperagem (Ah)', 'Preço (R$)', 'Estoque', 'Garantia (Meses)']
        
        cats = ["Todas"] + sorted(df_estoque['Categoria'].unique().tolist())
        cat_filtro = st.selectbox("Filtrar por Categoria", cats)
        
        if cat_filtro != "Todas":
            df_exibir = df_estoque[df_estoque['Categoria'] == cat_filtro]
        else:
            df_exibir = df_estoque

        st.dataframe(df_exibir, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma bateria cadastrada.")

# --- ABA 3: CONSULTAR GARANTIA ---
elif menu == "Consultar Garantia":
    st.header("Consulta de Garantias")
    busca = st.text_input("Digite o CPF, Placa, Série ou Nome do Cliente:")
    if busca:
        res = supabase.table("vendas").select("*").execute()
        df_v = pd.DataFrame(res.data)
        if not df_v.empty:
            df_fil = df_v[
                df_v['cliente_nome'].str.contains(busca, case=False, na=False) |
                df_v['cliente_cpf'].str.contains(busca, case=False, na=False) |
                df_v['veiculo_placa'].str.contains(busca, case=False, na=False) |
                df_v['numero_serie'].str.contains(busca, case=False, na=False)
            ]
            st.dataframe(df_fil, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro encontrado.")

# --- ABA 4: EDITAR BATERIAS (COM EDIÇÃO DE CATEGORIA) ---
elif menu == "Editar Baterias" and st.session_state["perfil"] == "ADM":
    st.header("Editar ou Excluir Baterias")
    res = supabase.table("produtos").select("*").order("id").execute()
    df_prods = pd.DataFrame(res.data)

    if df_prods.empty:
        st.info("Nenhuma bateria cadastrada.")
    else:
        opcoes = ["-- Selecione --"] + [f"ID {row['id']} - [{row.get('categoria', 'Geral')}] {row['nome']}" for _, row in df_prods.iterrows()]
        sel = st.selectbox("Escolha a bateria para editar:", opcoes)
        
        if sel != "-- Selecione --":
            id_sel = int(sel.split(" ")[1])
            item = df_prods[df_prods['id'] == id_sel].iloc[0]

            col_cat, col_nome = st.columns(2)
            e_categoria = col_cat.text_input("Categoria (ex: 60Ah A, 60Ah B, 70Ah)", value=str(item.get('categoria', 'Geral')))
            e_nome = col_nome.text_input("Nome do Modelo", value=item['nome'])

            col1, col2, col3 = st.columns(3)
            e_marca = col1.text_input("Marca", value=str(item.get('marca', '')))
            e_preco = col2.number_input("Preço R$", value=float(item['preco']))
            e_qtd = col3.number_input("Estoque", value=int(item['quantidade']))
            
            col4, col5 = st.columns(2)
            e_amp = col4.number_input("Amperagem", value=int(item.get('amperagem', 60)))
            e_garantia = col5.number_input("Meses de Garantia", value=int(item.get('meses_garantia', 12)))

            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("Salvar Alterações", use_container_width=True):
                supabase.table("produtos").update({
                    "categoria": e_categoria.strip(),
                    "nome": e_nome.strip(),
                    "marca": e_marca.strip(),
                    "preco": e_preco,
                    "quantidade": e_qtd,
                    "amperagem": e_amp,
                    "meses_garantia": e_garantia
                }).eq("id", id_sel).execute()
                st.success("Bateria atualizada com sucesso!")
                st.rerun()
                
            if col_btn2.button("Excluir Bateria 🔴", use_container_width=True):
                supabase.table("produtos").delete().eq("id", id_sel).execute()
                st.toast("Bateria excluída!", icon="🗑️")
                st.rerun()

# --- ABA 5: HISTÓRICO ---
elif menu == "Histórico" and st.session_state["perfil"] == "ADM":
    st.header("Histórico de Vendas")
    res = supabase.table("vendas").select("*").order("id", desc=True).execute()
    df_hist = pd.DataFrame(res.data)
    
    if df_hist.empty:
        st.info("Nenhuma venda registrada.")
    else:
        st.dataframe(df_hist[['id', 'data_hora', 'vendedor', 'produto_nome', 'quantidade', 'valor_total', 'forma_pagamento', 'cliente_nome']], use_container_width=True, hide_index=True)

# --- ABA 6: PAINEL ADM ---
elif menu == "Painel ADM" and st.session_state["perfil"] == "ADM":
    st.header("Cadastrar Nova Bateria")
    with st.form("cad_manual"):
        f_cat = st.text_input("Categoria (ex: 60Ah A, 60Ah B, 70Ah, 80Ah...)", value="60Ah A")
        f_nome = st.text_input("Nome do Modelo")
        f_amp = st.number_input("Amperagem", value=60)
        f_marca = st.text_input("Marca", value="Heliar")
        f_preco = st.number_input("Preço (R$)", value=400.0)
        f_qtd = st.number_input("Estoque Inicial", value=10)
        f_garantia = st.number_input("Meses de Garantia", value=12)
        
        if st.form_submit_button("Cadastrar"):
            novo_prod = {
                "categoria": f_cat.strip(),
                "nome": f_nome.strip(),
                "amperagem": int(f_amp),
                "marca": f_marca.strip(),
                "preco": float(f_preco),
                "quantidade": int(f_qtd),
                "meses_garantia": int(f_garantia)
            }
            supabase.table("produtos").insert(novo_prod).execute()
            st.success("Cadastrado com sucesso no Supabase!")
            st.rerun()
