import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from PIL import Image
import io

try:
    from openai import OpenAI
    OPENAI_DISPONIVEL = True
except ImportError:
    OPENAI_DISPONIVEL = False

st.set_page_config(
    page_title="Power Marketing System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# DESIGN PROFISSIONAL - TEMA DARK MODERN (SEM EMOJIS)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e11;
        color: #d1d5db;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #00e676 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    .stButton>button {
        background-color: #00c853 !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #69f0ae !important;
        box-shadow: 0 0 10px rgba(0, 230, 118, 0.4);
    }
    section[data-testid="stSidebar"] {
        background-color: #13171f !important;
        border-right: 1px solid #1e2638;
    }
    .card-info {
        background-color: #13171f;
        padding: 20px;
        border-radius: 6px;
        border: 1px solid #1e2638;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# LIGAÇÃO AO BANCO DE DADOS (GARANTE A TABELA DE PRODUTOS E MÍDIAS)
def conectar_banco():
    caminhos = ["power_baterias.db", "../power_baterias.db", "C:/power_baterias/power_baterias.db"]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return sqlite3.connect(caminho)
    return sqlite3.connect("power_baterias.db")

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS galeria_midia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            caminho TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

inicializar_banco()

def obter_produtos():
    conn = conectar_banco()
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

# GERADOR DE TEXTO TÉCNICO E COMERCIAL
def gerar_anuncio(bateria_nome, amperagem, preco, marca, garantia, veiculos, canal):
    horarios = {
        "OLX": "11:30 às 13:30 / 18:00 às 21:00",
        "Facebook Marketplace": "12:00 às 14:00 / 19:00 às 22:00",
        "Instagram / WhatsApp": "08:00 às 09:30 / 18:30 às 20:30",
        "Google Ads": "Campanha Ativa (Horário Comercial)"
    }
    
    if canal == "OLX":
        titulo = f"Bateria {bateria_nome} {amperagem}Ah - Entrega e Instalação Imediata"
        descricao = f"""BATERIA {marca.upper()} {amperagem}AH - PRONTA ENTREGA

Serviço de socorro e substituição rápida de bateria.

Especificações e Condições:
- Produto Novo com {garantia} Meses de Garantia de Fábrica.
- Aplicação Recomendada: {veiculos}.
- Valor: R$ {preco:.2f} à vista (à base de troca).
- Entrega e instalação no local.

Atendimento e Pedidos via WhatsApp: (61) 99519-1090
Pagamento no ato da entrega (Cartões de Crédito, Débito e PIX)."""

    elif canal == "Facebook Marketplace":
        titulo = f"Bateria {marca} {amperagem}Ah com Garantia e Entrega"
        descricao = f"""OPORTUNIDADE - BATERIA {marca.upper()} {amperagem}AH

Substituição rápida de bateria com teste de sistema elétrico incluso.

- Garantia de {garantia} Meses diretamente pelo fabricante.
- Veículos compatíveis: {veiculos}.
- Preço especial: R$ {preco:.2f}.

Contato direto / WhatsApp: (61) 99519-1090
Atendimento rápido em toda a região."""

    elif canal == "Google Ads":
        titulo = f"Bateria {marca} {amperagem}Ah | Socorro 24h e Instalação"
        descricao = f"Bateria {bateria_nome} com {garantia} Meses de Garantia. Entrega e instalação rápida no local. Fale conosco pelo WhatsApp: (61) 99519-1090."

    else:
        titulo = f"Bateria {bateria_nome} {amperagem}Ah"
        descricao = f"""Linha Baterias Automotivas - Power Baterias

Modelo: {marca} {amperagem}Ah
Valor: R$ {preco:.2f}
Garantia: {garantia} Meses
Aplicações: {veiculos}

Central de Atendimento:
WhatsApp: (61) 99519-1090

#PowerBaterias #BateriasAutomotivas #{marca} #ManutencaoAutomotiva"""

    return titulo, descricao, horarios[canal]

# NAVEGAÇÃO LATERAL
st.sidebar.markdown("<h2 style='margin-bottom: 0px;'>POWER MKT</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #8a99ad; font-size: 13px;'>Módulo de Gestão de Anúncios</p>", unsafe_allow_html=True)
st.sidebar.write("---")

menu = st.sidebar.radio("Menu de Operações", [
    "Gerador de Anúncios", 
    "Banco de Imagens", 
    "Assistente Técnico (IA)"
])

# 1. GERADOR DE ANÚNCIOS
if menu == "Gerador de Anúncios":
    st.markdown("<h2>Gestão e Geração de Campanhas</h2>", unsafe_allow_html=True)
    st.write("Configure os parâmetros abaixo para gerar o texto do anúncio otimizado por plataforma.")

    df_prods = obter_produtos()
    
    if df_prods.empty:
        st.info("Nenhum produto cadastrado no banco de dados. Cadastre produtos no sistema de estoque para gerar anúncios.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            prod_sel = st.selectbox("Selecione o Produto:", df_prods['nome'].tolist())
            dados_p = df_prods[df_prods['nome'] == prod_sel].iloc[0]
            
        with col2:
            canal_sel = st.selectbox("Plataforma de Destino:", ["OLX", "Facebook Marketplace", "Google Ads", "Instagram / WhatsApp"])

        if st.button("Gerar Anúncio", use_container_width=True):
            titulo, copy, horario = gerar_anuncio(
                dados_p['nome'], dados_p['amperagem'], dados_p['preco'],
                dados_p['marca'], dados_p['meses_garantia'], dados_p['veiculo'], canal_sel
            )
            
            st.write("---")
            st.markdown(f"<div class='card-info'><strong>Janela Otimizada de Postagem:</strong> {horario}</div>", unsafe_allow_html=True)
            
            st.markdown("### Título Sugerido")
            st.code(titulo, language="text")
            
            st.markdown("### Texto Descritivo")
            st.code(copy, language="text")

# 2. BANCO DE IMAGENS
elif menu == "Banco de Imagens":
    st.markdown("<h2>Repositório de Mídias e Imagens</h2>", unsafe_allow_html=True)
    
    tab_ver, tab_envio = st.tabs(["Consultar Imagens", "Upload de Mídia"])
    
    with tab_envio:
        st.markdown("### Registrar Nova Foto")
        cat_foto = st.selectbox("Categoria", ["Heliar", "Moura", "Cral", "KF", "Super Life", "Institucional"])
        nome_foto = st.text_input("Identificação da Imagem")
        arq = st.file_uploader("Arquivo de Imagem (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
        
        if st.button("Salvar Imagem"):
            if arq and nome_foto:
                os.makedirs("midias", exist_ok=True)
                caminho = os.path.join("midias", f"{int(datetime.now().timestamp())}_{arq.name}")
                
                with open(caminho, "wb") as f:
                    f.write(arq.getbuffer())
                
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO galeria_midia (nome, categoria, caminho) VALUES (?, ?, ?)", (nome_foto, cat_foto, caminho))
                conn.commit()
                conn.close()
                st.success("Imagem registrada no sistema.")
                st.rerun()
            else:
                st.error("Preencha todos os campos e selecione o arquivo.")

    with tab_ver:
        conn = conectar_banco()
        df_fotos = pd.read_sql_query("SELECT * FROM galeria_midia", conn)
        conn.close()
        
        if df_fotos.empty:
            st.info("Nenhuma imagem cadastrada no repositório.")
        else:
            cats = ["Todas"] + df_fotos['categoria'].unique().tolist()
            cat_filtro = st.selectbox("Filtrar Categoria:", cats)
            
            if cat_filtro != "Todas":
                df_fotos = df_fotos[df_fotos['categoria'] == cat_filtro]
                
            cols = st.columns(3)
            for idx, row in df_fotos.iterrows():
                with cols[idx % 3]:
                    if os.path.exists(row['caminho']):
                        img = Image.open(row['caminho'])
                        st.image(img, use_column_width=True)
                        st.caption(f"{row['nome']} - {row['categoria']}")
                        
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button("Download", data=buf.getvalue(), file_name=f"{row['nome']}.png", mime="image/png", key=f"dl_{row['id']}")

# 3. ASSISTENTE TÉCNICO (IA)
elif menu == "Assistente Técnico (IA)":
    st.markdown("<h2>Assistente Consultivo de Vendas</h2>", unsafe_allow_html=True)
    st.write("Consulta técnica de aplicação de baterias e suporte de atendimento.")

    api_key = st.text_input("OpenAI API Key:", type="password")

    if "mensagens_chat" not in st.session_state:
        st.session_state["mensagens_chat"] = [
            {"role": "assistant", "content": "Sistema pronto para consultas técnicas. Digite o modelo do veículo ou a dúvida comercial."}
        ]

    for msg in st.session_state["mensagens_chat"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Digite sua consulta..."):
        st.session_state["mensagens_chat"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if not api_key or not OPENAI_DISPONIVEL:
            resposta_offline = f"Consulta registrada: '{prompt}'. Insira a chave da API OpenAI para habilitar respostas do modelo em tempo real."
            st.session_state["mensagens_chat"].append({"role": "assistant", "content": resposta_offline})
            st.chat_message("assistant").write(resposta_offline)
        else:
            try:
                client = OpenAI(api_key=api_key)
                system_prompt = "Você é um assistente técnico especialista em baterias automotivas e aplicação veicular. Responda de forma profissional, direta e técnica."
                
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": system_prompt}] + st.session_state["mensagens_chat"]
                )
                
                resp_ia = res.choices[0].message.content
                st.session_state["mensagens_chat"].append({"role": "assistant", "content": resp_ia})
                st.chat_message("assistant").write(resp_ia)
            except Exception as e:
                st.error(f"Erro na conexão com o serviço: {e}")
