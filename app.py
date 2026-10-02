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

# Estilização Dark + Responsividade Mobile
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
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 18px !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        background-color: #39ff14 !important;
        color: #000000 !important;
    }
    [data-testid="stMetricValue"] {
        color: #39ff14 !important;
        font-size: 1.8rem !important;
        font-weight: bold !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #16191e !important;
        border-right: 1px solid #28a745;
    }
    /* Ajustes Finos para Telas de Celular (Mobile) */
    @media (max-width: 768px) {
        .stApp {
            padding: 5px !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 10px !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
        }
        .stDataFrame {
            font-size: 12px !important;
        }
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

USUARIOS = {
    "arthur": {"senha": "Arthur123", "perfil": "ADM", "nome": "Arthur"},
    "sandro": {"senha": "1234", "perfil": "ADM", "nome": "Sandro"},
    "pedro": {"senha": "Pedro1234", "perfil": "Vendedor", "nome": "Pedro"},
    "wanderson": {"senha": "venda123", "perfil": "Vendedor", "nome": "Wanderson"},
}

CATEGORIAS_BASE = [
    "36Ah 40Ah 45Ah 48Ah",
    "60Ah",
    "70Ah",
    "75Ah",
    "40Ah Slim JD",
    "72Ah EFB Start Stop",
    "90Ah"
]

def obter_todas_categorias():
    try:
        res = supabase.table("produtos").select("categoria").execute()
        cats_banco = [r['categoria'] for r in res.data if r.get('categoria')]
        lista_final = sorted(list(set(CATEGORIAS_BASE + cats_banco)))
        return lista_final
    except Exception:
        return CATEGORIAS_BASE

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

def gerador_pdf_caixa(data_ref, df_vendas, total_faturado):
    if not REPORTLAB_DISPONIVEL:
        return None
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    header_title = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#28a745'), alignment=0)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12)
    body_bold = ParagraphStyle('BodyBold', parent=styles['Normal'], fontSize=9, leading=12, fontName='Helvetica-Bold')

    topo = [
        [
            Paragraph("<b>POWER BATERIAS - FECHAMENTO DE CAIXA</b>", header_title),
            Paragraph(f"<b>Data:</b> {data_ref}<br/><b>Emissão:</b> {datetime.now().strftime('%H:%M:%S')}", body_style)
        ]
    ]
    story.append(Table(topo, colWidths=[340, 200]))
    story.append(Spacer(1, 15))

    story.append(Paragraph(f"<b>FATURAMENTO TOTAL DO DIA: R$ {total_faturado:.2f}</b>", ParagraphStyle('Tot', parent=body_bold, fontSize=12, textColor=colors.HexColor('#28a745'))))
    story.append(Spacer(1, 10))

    table_data = [[Paragraph("<b>ID</b>", body_bold), Paragraph("<b>Vendedor</b>", body_bold), Paragraph("<b>Cliente</b>", body_bold), Paragraph("<b>Produto</b>", body_bold), Paragraph("<b>Pagamento</b>", body_bold), Paragraph("<b>Total</b>", body_bold)]]
    
    for _, r in df_vendas.iterrows():
        table_data.append([
            Paragraph(str(r['id']), body_style),
            Paragraph(str(r['vendedor']), body_style),
            Paragraph(str(r['cliente_nome']), body_style),
            Paragraph(str(r['produto_nome']), body_style),
            Paragraph(str(r['forma_pagamento']), body_style),
            Paragraph(f"R$ {float(r['valor_total']):.2f}", body_style)
        ])

    t_vendas = Table(table_data, colWidths=[30, 80, 110, 140, 100, 80])
    t_vendas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16191e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_vendas)

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

# --- MODAIS DE CONFIRMAÇÃO ---
@st.dialog("Venda Finalizada! 🟢")
def modal_gerar_pdf(dados_venda):
    st.write(f"**Cliente:** {dados_venda['cliente_nome']}")
    st.write(f"**Bateria:** {dados_venda['produto_nome']}")
    st.write(f"**Valor Total:** R$ {dados_venda['valor_total']:.2f}")
    if REPORTLAB_DISPONIVEL:
        pdf_bytes = gerador_pdf_nota(dados_venda)
        st.download_button("📄 Baixar Nota Fiscal (PDF)", data=pdf_bytes, file_name=f"nota_{dados_venda['id']}.pdf", mime="application/pdf", use_container_width=True)

@st.dialog("Confirmar Alterações da Bateria ⚠️")
def modal_confirmar_edicao_bateria(id_sel, novos_dados):
    st.warning("Deseja realmente atualizar esta bateria?")
    st.write(f"**Modelo:** {novos_dados['nome']}")
    st.write(f"**Categoria:** {novos_dados['categoria']}")
    st.write(f"**Preço:** R$ {novos_dados['preco']:.2f}")
    st.write(f"**Estoque:** {novos_dados['quantidade']} un")
    
    if st.button("Sim, Confirmar Alteração", use_container_width=True):
        supabase.table("produtos").update(novos_dados).eq("id", id_sel).execute()
        st.toast("Bateria atualizada no Supabase!", icon="✅")
        st.rerun()

@st.dialog("Confirmar Exclusão de Bateria 🔴")
def modal_confirmar_exclusao_bateria(id_sel, nome_bateria):
    st.error(f"Deseja realmente excluir a bateria ID {id_sel} - {nome_bateria}?")
    if st.button("Sim, Excluir Bateria", use_container_width=True):
        supabase.table("produtos").delete().eq("id", id_sel).execute()
        st.toast("Bateria excluída!", icon="🗑️️")
        st.rerun()

@st.dialog("Confirmar Cancelamento de Venda 🔴")
def modal_confirmar_cancelamento_venda(id_venda, produto_nome, quantidade):
    st.error(f"Deseja realmente cancelar a Venda #{id_venda} ({produto_nome})?")
    st.write("O estoque será devolvido automaticamente.")
    if st.button("Sim, Cancelar Venda", use_container_width=True):
        cancelar_venda(id_venda, produto_nome, quantidade)
        st.toast("Venda cancelada!", icon="✅")
        st.rerun()

@st.dialog("Editar Venda #{venda_id} ✏️")
def modal_editar_venda(venda_dict):
    venda_id = venda_dict['id']
    st.subheader(f"Editando Venda #{venda_id}")
    
    e_cliente = st.text_input("Cliente", value=str(venda_dict.get('cliente_nome', '')))
    e_cpf = st.text_input("CPF / CNPJ", value=str(venda_dict.get('cliente_cpf', '')))
    e_modelo = st.text_input("Veículo", value=str(venda_dict.get('veiculo_modelo', '')))
    e_placa = st.text_input("Placa", value=str(venda_dict.get('veiculo_placa', '')))
    e_serie = st.text_input("Nº Série", value=str(venda_dict.get('numero_serie', '')))
    
    col_a, col_b = st.columns(2)
    e_total = col_a.number_input("Valor Total (R$)", value=float(venda_dict.get('valor_total', 0.0)))
    e_pag = col_b.selectbox("Pagamento", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"], index=["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"].index(venda_dict.get('forma_pagamento', 'PIX')))
    
    if st.button("Salvar Edição da Venda", use_container_width=True):
        payload = {
            "cliente_nome": e_cliente,
            "cliente_cpf": e_cpf,
            "veiculo_modelo": e_modelo,
            "veiculo_placa": e_placa.upper(),
            "numero_serie": e_serie.upper(),
            "valor_total": float(e_total),
            "forma_pagamento": e_pag
        }
        supabase.table("vendas").update(payload).eq("id", venda_id).execute()
        st.toast("Venda atualizada com sucesso!", icon="✅")
        st.rerun()

# --- MENU LATERAL ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", use_container_width=True)
else:
    st.sidebar.markdown("## POWER BATERIAS")

st.sidebar.caption("DISK BATERIAS: (61) 99519-1090")

opcoes_menu = ["Nova Venda", "Estoque Organizado", "Consultar Garantia"]
if st.session_state["perfil"] == "ADM":
    opcoes_menu += ["Editar Baterias", "Histórico", "Caixa Diário", "Painel ADM"]

if "pagina_atual" not in st.session_state or st.session_state["pagina_atual"] not in opcoes_menu:
    st.session_state["pagina_atual"] = opcoes_menu[0]

menu = st.sidebar.radio("Navegação", opcoes_menu, key="pagina_atual")

st.sidebar.write("---")
st.sidebar.markdown(f"🟢 **Conectado:** {st.session_state['vendedor_nome']} ({st.session_state['perfil']})")
if st.sidebar.button("Sair", use_container_width=True):
    st.session_state["logado"] = False
    st.rerun()

# --- ABA 1: NOVA VENDA ---
if menu == "Nova Venda":
    st.header("Lançamento de Venda")
    res = supabase.table("produtos").select("id, categoria, nome, amperagem, preco, quantidade, meses_garantia, veiculo").execute()
    df_prods = pd.DataFrame(res.data)

    if df_prods.empty:
        st.warning("Nenhuma bateria cadastrada no estoque!")
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
                    preco_tabela_total = preco_base * qtd
                    st.info(f"Preço Tabela (Unidade): R$ {preco_base:.2f}")
                    
                    # Permite digitar o valor final praticado na venda
                    valor_final = st.number_input("Valor Final Praticado (R$) *", value=float(preco_tabela_total), step=5.0)
                    ajuste_desconto = preco_tabela_total - valor_final
                    
                    if ajuste_desconto > 0:
                        st.caption(f"💡 Desconto concedido: R$ {ajuste_desconto:.2f}")
                    elif ajuste_desconto < 0:
                        st.caption(f"💡 Acréscimo aplicado: R$ {abs(ajuste_desconto):.2f}")

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
                            "desconto": float(ajuste_desconto),
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

                        modal_gerar_pdf({'id': id_venda, 'data_hora': dt_hoje, 'vendedor': vendedor.strip(), 'cliente_nome': cliente or "Consumidor Não Identificado", 'cliente_cpf': cpf or "Não Informado", 'veiculo_placa': placa.upper() or "Não Informado", 'veiculo_modelo': veiculo_mod.strip(), 'numero_serie': serie.upper() or "Não Informado", 'produto_nome': dados_p['nome'], 'amperagem': dados_p['amperagem'], 'quantidade': qtd, 'preco_original': preco_base, 'desconto': ajuste_desconto, 'valor_total': valor_final, 'forma_pagamento': pagamento, 'parcelas': parcelas, 'meses_garantia': dados_p['meses_garantia']})

# --- ABA 2: ESTOQUE ORGANIZADO ---
elif menu == "Estoque Organizado":
    st.header("Estoque Geral por Categoria")
    res = supabase.table("produtos").select("id, categoria, nome, marca, amperagem, preco, quantidade, meses_garantia").order("categoria").order("id").execute()
    df_estoque = pd.DataFrame(res.data)
    
    if not df_estoque.empty:
        df_estoque.columns = ['ID', 'Categoria', 'Modelo', 'Marca', 'Amperagem (Ah)', 'Preço (R$)', 'Estoque', 'Garantia (Meses)']
        
        categorias_existentes = sorted(df_estoque['Categoria'].dropna().unique().tolist())
        cat_filtro = st.selectbox("Filtrar por Categoria", ["Todas"] + categorias_existentes)
        
        cats_para_exibir = categorias_existentes if cat_filtro == "Todas" else [cat_filtro]

        for cat in cats_para_exibir:
            st.markdown(f"### 🔋 Categoria: {cat}")
            df_cat = df_estoque[df_estoque['Categoria'] == cat].drop(columns=['Categoria'])
            st.dataframe(df_cat, use_container_width=True, hide_index=True)
            st.write("")
    else:
        st.info("Nenhuma bateria cadastrada no estoque.")

# --- ABA 3: CONSULTAR GARANTIA ---
elif menu == "Consultar Garantia":
    st.header("Consulta de Garantias")
    res_v = supabase.table("vendas").select("*").order("id", desc=True).execute()
    df_v = pd.DataFrame(res_v.data)

    if df_v.empty:
        st.info("Nenhuma venda realizada até o momento.")
    else:
        busca = st.text_input("Digite CPF, Placa, Nº de Série, Modelo do Veículo ou Nome do Cliente:")
        df_exibir = df_v
        
        if busca.strip():
            df_exibir = df_v[
                df_v['cliente_nome'].str.contains(busca, case=False, na=False) |
                df_v['cliente_cpf'].str.contains(busca, case=False, na=False) |
                df_v['veiculo_placa'].str.contains(busca, case=False, na=False) |
                df_v['numero_serie'].str.contains(busca, case=False, na=False) |
                df_v['veiculo_modelo'].str.contains(busca, case=False, na=False)
            ]

        st.subheader("Últimas Vendas / Status da Garantia")
        
        for _, r in df_exibir.iterrows():
            dt_venda_str = r['data_hora']
            meses_gar = int(r.get('meses_garantia', 12) or 12)
            
            try:
                dt_venda = datetime.strptime(dt_venda_str, "%d/%m/%Y %H:%M:%S")
                meses_passados = (datetime.now().year - dt_venda.year) * 12 + (datetime.now().month - dt_venda.month)
                meses_restantes = meses_gar - meses_passados
                
                if meses_restantes > 0:
                    status_garantia = f"🟢 Garantia Válida ({meses_restantes} meses restantes)"
                else:
                    status_garantia = "🔴 Garantia Expirada"
            except Exception:
                status_garantia = f"🟡 Garantia de {meses_gar} meses"

            with st.expander(f"Venda #{r['id']} - {r['cliente_nome']} | {r['produto_nome']} ({status_garantia})"):
                col_a, col_b, col_c = st.columns(3)
                col_a.write(f"**Data da Venda:** {r['data_hora']}")
                col_a.write(f"**Vendedor Responsável:** {r['vendedor']}")
                col_a.write(f"**Cliente:** {r['cliente_nome']}")
                
                col_b.write(f"**CPF / CNPJ:** {r['cliente_cpf']}")
                col_b.write(f"**Veículo / Placa:** {r['veiculo_modelo']} - {r['veiculo_placa']}")
                col_b.write(f"**Nº Série Bateria:** {r['numero_serie']}")

                col_c.write(f"**Bateria:** {r['produto_nome']}")
                col_c.write(f"**Garantia Total:** {meses_gar} meses")
                col_c.write(f"**Status:** {status_garantia}")

# --- ABA 4: EDITAR BATERIAS ---
elif menu == "Editar Baterias" and st.session_state["perfil"] == "ADM":
    st.header("Editar ou Excluir Baterias")
    res = supabase.table("produtos").select("*").order("id").execute()
    df_prods = pd.DataFrame(res.data)

    if df_prods.empty:
        st.info("Nenhuma bateria cadastrada.")
    else:
        opcoes = ["-- Selecione --"] + [f"ID {row['id']} - {row['nome']}" for _, row in df_prods.iterrows()]
        sel = st.selectbox("Escolha a bateria para editar:", opcoes)
        
        if sel != "-- Selecione --":
            id_sel = int(sel.split(" ")[1])
            item = df_prods[df_prods['id'] == id_sel].iloc[0]

            lista_cats = obter_todas_categorias()
            cat_atual = str(item.get('categoria', '60Ah'))
            idx_cat = lista_cats.index(cat_atual) if cat_atual in lista_cats else 0

            col_cat, col_nome = st.columns(2)
            e_categoria_sel = col_cat.selectbox("Categoria", lista_cats + ["+ Criar Nova Categoria"], index=idx_cat)
            
            if e_categoria_sel == "+ Criar Nova Categoria":
                e_categoria = col_cat.text_input("Nome da Nova Categoria")
            else:
                e_categoria = e_categoria_sel

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
                novos_dados = {
                    "categoria": e_categoria.strip(),
                    "nome": e_nome.strip(),
                    "marca": e_marca.strip(),
                    "preco": e_preco,
                    "quantidade": e_qtd,
                    "amperagem": e_amp,
                    "meses_garantia": e_garantia
                }
                modal_confirmar_edicao_bateria(id_sel, novos_dados)
                
            if col_btn2.button("Excluir Bateria 🔴", use_container_width=True):
                modal_confirmar_exclusao_bateria(id_sel, e_nome)

# --- ABA 5: HISTÓRICO COM BOTÃO EDITAR VENDA PARA ADM ---
elif menu == "Histórico" and st.session_state["perfil"] == "ADM":
    st.header("Histórico de Vendas")
    res = supabase.table("vendas").select("*").order("id", desc=True).execute()
    df_hist = pd.DataFrame(res.data)
    
    if df_hist.empty:
        st.info("Nenhuma venda registrada no histórico.")
    else:
        for _, v in df_hist.iterrows():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 2, 1.5, 1.2, 1.2, 1.2])
            c1.write(f"**#{v['id']}**")
            c2.write(f"**{v['cliente_nome']}**<br/>{v['produto_nome']}", unsafe_allow_html=True)
            c3.write(f"Data: {v['data_hora']}<br/>Placa: {v.get('veiculo_placa', 'N/A')}", unsafe_allow_html=True)
            c4.write(f"R$ {float(v['valor_total']):.2f}<br/>{v['forma_pagamento']}", unsafe_allow_html=True)
            
            if c5.button("📄 PDF", key=f"pdf_{v['id']}"):
                modal_gerar_pdf(dict(v))
                
            if c6.button("✏️ Editar", key=f"edit_v_{v['id']}"):
                modal_editar_venda(dict(v))

            if c7.button("🔴 Cancelar", key=f"canc_{v['id']}"):
                modal_confirmar_cancelamento_venda(v['id'], v['produto_nome'], int(v['quantidade']))
            st.divider()

# --- ABA 6: FECHAMENTO DE CAIXA DIÁRIO ---
elif menu == "Caixa Diário" and st.session_state["perfil"] == "ADM":
    st.header("Fechamento de Caixa Diário")
    data_filtro = st.date_input("Selecione a Data:", datetime.now())
    data_str = data_filtro.strftime("%d/%m/%Y")

    res = supabase.table("vendas").select("*").execute()
    df_vendas_todas = pd.DataFrame(res.data)

    if not df_vendas_todas.empty:
        df_hoje = df_vendas_todas[df_vendas_todas['data_hora'].str.contains(data_str, na=False)]
    else:
        df_hoje = pd.DataFrame()

    if df_hoje.empty:
        st.warning(f"Nenhuma venda registrada no dia {data_str}.")
    else:
        total_dia = df_hoje['valor_total'].sum()
        qtd_vendas = len(df_hoje)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Faturamento do Dia", f"R$ {total_dia:.2f}")
        col_m2.metric("Total de Vendas", f"{qtd_vendas} vendas")
        col_m3.metric("Ticket Médio", f"R$ {(total_dia/qtd_vendas):.2f}" if qtd_vendas > 0 else "R$ 0.00")

        st.write("---")
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.subheader("Vendas por Forma de Pagamento")
            df_pag = df_hoje.groupby("forma_pagamento")["valor_total"].sum().reset_index()
            df_pag.columns = ["Forma de Pagamento", "Total (R$)"]
            st.dataframe(df_pag, use_container_width=True, hide_index=True)

        with col_p2:
            st.subheader("Vendas por Vendedor")
            df_vend = df_hoje.groupby("vendedor")["valor_total"].sum().reset_index()
            df_vend.columns = ["Vendedor", "Total (R$)"]
            st.dataframe(df_vend, use_container_width=True, hide_index=True)

        st.write("---")
        st.subheader("Detalhamento das Vendas do Dia")
        st.dataframe(df_hoje[['id', 'data_hora', 'vendedor', 'cliente_nome', 'produto_nome', 'forma_pagamento', 'valor_total']], use_container_width=True, hide_index=True)

        if REPORTLAB_DISPONIVEL:
            pdf_caixa = gerador_pdf_caixa(data_str, df_hoje, total_dia)
            st.download_button("📄 Baixar Relatório do Fechamento de Caixa (PDF)", data=pdf_caixa, file_name=f"fechamento_caixa_{data_str.replace('/', '_')}.pdf", mime="application/pdf", use_container_width=True)

# --- ABA 7: PAINEL ADM ---
elif menu == "Painel ADM" and st.session_state["perfil"] == "ADM":
    st.header("Cadastrar Nova Bateria")
    
    lista_cats = obter_todas_categorias()
    
    with st.form("cad_manual"):
        col_cat, col_nome = st.columns(2)
        f_cat_sel = col_cat.selectbox("Categoria", lista_cats + ["+ Criar Nova Categoria"])
        
        if f_cat_sel == "+ Criar Nova Categoria":
            f_cat = col_cat.text_input("Nome da Nova Categoria *")
        else:
            f_cat = f_cat_sel

        f_nome = col_nome.text_input("Nome do Modelo *")
        
        col1, col2, col3 = st.columns(3)
        f_amp = col1.number_input("Amperagem", value=60)
        f_marca = col2.text_input("Marca", value="Heliar")
        f_preco = col3.number_input("Preço (R$)", value=400.0)
        
        col4, col5 = st.columns(2)
        f_qtd = col4.number_input("Estoque Inicial", value=10)
        f_garantia = col5.number_input("Meses de Garantia", value=12)
        
        if st.form_submit_button("Cadastrar Bateria", use_container_width=True):
            if not f_cat.strip() or not f_nome.strip():
                st.error("Preencha Categoria e Nome do Modelo!")
            else:
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
                st.success(f"Bateria '{f_nome}' cadastrada na categoria '{f_cat}' com sucesso!")
                st.rerun()
