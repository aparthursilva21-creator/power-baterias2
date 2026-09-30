import streamlit as st
import pandas as pd
import sqlite3
import os
import random
from datetime import datetime
from PIL import Image
import io

# Tenta importar a API da OpenAI para o Chatbot com IA
try:
    from openai import OpenAI
    OPENAI_DISPONIVEL = True
except ImportError:
    OPENAI_DISPONIVEL = False

st.set_page_config(
    page_title="Power Marketing & IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ESTILIZAÇÃO VERDE NEON (PADRÃO POWER BATERIAS)
st.markdown("""
    <style>
    .stApp { background-color: #0d0f12; color: #e6e6e6; }
    h1, h2, h3 { color: #39ff14 !important; font-weight: 800 !important; }
    .stButton>button {
        background-color: #28a745 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #39ff14 !important;
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #16191e !important;
        border-right: 1px solid #28a745;
    }
    .copy-box {
        background-color: #16191e;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #28a745;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# BANCO DE DADOS LOCAL PARA MÍDIAS E CHAT
def inicializar_banco_mkt():
    conn = sqlite3.connect("power_baterias.db")
    cursor = conn.cursor()
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

inicializar_banco_mkt()

# CONEXÃO COM BANCO DE DADOS PRINCIPAL PARA PEGAR BATERIAS
def obter_produtos():
    conn = sqlite3.connect("power_baterias.db")
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

# GERADOR DE COPYWRITING (ANÚNCIOS)
def gerar_anuncio(bateria_nome, amperagem, preco, marca, garantia, veiculos, canal):
    horarios = {
        "OLX": "11:30 às 13:30 ou 18:00 às 21:00",
        "Facebook Marketplace": "12:00 às 14:00 ou 19:00 às 22:00",
        "Instagram / WhatsApp": "08:00 às 09:30 ou 18:30 às 20:30",
        "Google Ads": "Campanha Ativa 24h (Foco: 07:00 às 19:00)"
    }
    
    if canal == "OLX":
        titulo = f"Bateria {bateria_nome} {amperagem}Ah - Entregamos e Instalamos Hoje!"
        descricao = f"""⚡ BATERIA {marca.upper()} {amperagem}AH - PRONTA ENTREGA! ⚡

Seu carro não pega? A Power Baterias resolve agora!

✅ Produto Novo com {garantia} Meses de Garantia de Fábrica.
✅ Aplicação Ideal: {veiculos}.
✅ Preço Imbatível: R$ {preco:.2f} à vista (à base de troca).
🚗 ENTREGAMOS E INSTALAMOS ONDE VOCÊ ESTIVER!

📍 Disk Baterias / WhatsApp: (61) 99519-1090
Aceitamos Cartões de Crédito (até 12x), Débito e PIX. Pague somente na entrega!"""

    elif canal == "Facebook Marketplace":
        titulo = f"PROMOÇÃO Bateria {marca} {amperagem}Ah (Entrega Grátis na Região)"
        descricao = f"""🚨 BATERIA PAROU? NÃO FIQUE NA RUA! 🚨

Bateria {bateria_nome} {amperagem}Ah com o melhor preço da região!

• {garantia} Meses de Garantia
• Teste do Alternador Grátis na Instalação
• Indicado para: {veiculos}
• Valor: R$ {preco:.2f}

📲 Chame direto no WhatsApp: (61) 99519-1090
Chegamos rápido até você!"""

    elif canal == "Google Ads":
        titulo = f"Bateria {marca} {amperagem}Ah | Entrega e Troca Rápida | Ligue Já"
        descricao = f"Bateria {bateria_nome} com {garantia} Meses de Garantia. Socorro de Bateria Rápido. Entregamos e Instalamos no Local. Ligue ou Chame no WhatsApp: (61) 99519-1090."

    else: # Instagram
        titulo = f"⚡ Bateria {bateria_nome} {amperagem}Ah em Promoção!"
        descricao = f"""🔋 Seu veículo merece a melhor energia!

Bateria {marca} {amperagem}Ah por apenas R$ {preco:.2f}!
🔒 {garantia} Meses de Garantia
🚘 Servindo com excelência: {veiculos}

🚨 Socorro Rápido de Bateria:
📞 (61) 99519-1090

#PowerBaterias #DiskBaterias #BateriasAutomotivas #{marca} #Mecanica"""

    return titulo, descricao, horarios[canal]

# --- MENU LATERAL ---
st.sidebar.title("POWER MARKETING & IA")
st.sidebar.caption("Central de Anúncios e Assistente Inteligente")

menu = st.sidebar.radio("Navegação", [
    "🚀 Gerador de Anúncios", 
    "🖼️ Galeria de Fotos / Mídia", 
    "🤖 Assistente de Vendas (IA)"
])

# --- ABA 1: GERADOR DE ANÚNCIOS ---
if menu == "🚀 Gerador de Anúncios":
    st.header("📢 Gerador Automático de Anúncios para Redes e Ads")
    st.write("Selecione a bateria e a rede social para gerar a oferta perfeita do dia!")

    df_prods = obter_produtos()
    
    if df_prods.empty:
        st.warning("Cadastre baterias no sistema principal antes de gerar anúncios.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            prod_sel = st.selectbox("Selecione a Bateria:", df_prods['nome'].tolist())
            dados_p = df_prods[df_prods['nome'] == prod_sel].iloc[0]
            
        with col2:
            canal_sel = st.selectbox("Canal de Divulgação:", ["OLX", "Facebook Marketplace", "Google Ads", "Instagram / WhatsApp"])

        if st.button("✨ Gerar Anúncio Agora", use_container_width=True):
            titulo, copy, horario = gerar_anuncio(
                dados_p['nome'], dados_p['amperagem'], dados_p['preco'],
                dados_p['marca'], dados_p['meses_garantia'], dados_p['veiculo'], canal_sel
            )
            
            st.write("---")
            st.success(f"📌 **Melhor Horário para Postar:** {horario}")
            
            st.subheader("1. Título do Anúncio")
            st.code(titulo, language="text")
            
            st.subheader("2. Descrição Completa (Copie e Cole)")
            st.code(copy, language="text")

# --- ABA 2: GALERIA DE FOTOS ---
elif menu == "🖼️ Galeria de Fotos / Mídia":
    st.header("🖼️ Banco de Imagens e Artes da Power Baterias")
    
    tab_ver, tab_envio = st.tabs(["📁 Ver Fotos e Baixar", "⬆️ Enviar Novas Fotos"])
    
    with tab_envio:
        st.subheader("Carregar Nova Imagem")
        cat_foto = st.selectbox("Categoria/Marca", ["Heliar", "Moura", "Cral", "KF", "Super Life", "Promoções", "Gerais"])
        nome_foto = st.text_input("Nome/Descrição da Foto (ex: Heliar 60Ah Foto Real)")
        arq = st.file_uploader("Selecione a Imagem (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
        
        if st.button("Salvar Imagem no Banco"):
            if arq and nome_foto:
                os.makedirs("midias", exist_ok=True)
                caminho = os.path.join("midias", f"{int(datetime.now().timestamp())}_{arq.name}")
                
                with open(caminho, "wb") as f:
                    f.write(arq.getbuffer())
                
                conn = sqlite3.connect("power_baterias.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO galeria_midia (nome, categoria, caminho) VALUES (?, ?, ?)", (nome_foto, cat_foto, caminho))
                conn.commit()
                conn.close()
                st.success("Foto salva com sucesso na galeria!")
                st.rerun()
            else:
                st.error("Preencha o nome e selecione um arquivo!")

    with tab_ver:
        conn = sqlite3.connect("power_baterias.db")
        df_fotos = pd.read_sql_query("SELECT * FROM galeria_midia", conn)
        conn.close()
        
        if df_fotos.empty:
            st.info("Nenhuma foto cadastrada na galeria ainda.")
        else:
            cats = ["Todas"] + df_fotos['categoria'].unique().tolist()
            cat_filtro = st.selectbox("Filtrar por Marca/Categoria:", cats)
            
            if cat_filtro != "Todas":
                df_fotos = df_fotos[df_fotos['categoria'] == cat_filtro]
                
            cols = st.columns(3)
            for idx, row in df_fotos.iterrows():
                with cols[idx % 3]:
                    if os.path.exists(row['caminho']):
                        img = Image.open(row['caminho'])
                        st.image(img, use_column_width=True)
                        st.caption(f"**{row['nome']}** ({row['categoria']})")
                        
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button("📥 Baixar Imagem", data=buf.getvalue(), file_name=f"{row['nome']}.png", mime="image/png", key=f"dl_{row['id']}")

# --- ABA 3: ASSISTENTE DE VENDAS (CHATBOT IA) ---
elif menu == "🤖 Assistente de Vendas (IA)":
    st.header("🤖 Especialista Power Baterias (IA no Balcão)")
    st.write("Pergunte qualquer coisa: aplicações de veículos, quebra de objeções de preço ou dados técnicos de baterias!")

    api_key = st.text_input("Cole sua OpenAI API Key (Caso tenha uma chave OpenAI):", type="password")

    if "mensagens_chat" not in st.session_state:
        st.session_state["mensagens_chat"] = [
            {"role": "assistant", "content": "Fala parceiro! Sou o assistente técnico da Power Baterias. Qual a dúvida de hoje? (Ex: 'Qual bateria vai no Corolla 2021?' ou 'Cliente achou caro, o que falar?')" }
        ]

    for msg in st.session_state["mensagens_chat"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Digite sua dúvida aqui..."):
        st.session_state["mensagens_chat"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Resposta caso não tenha chave API OpenAI cadastrada (Modo Inteligente Offline)
        if not api_key or not OPENAI_DISPONIVEL:
            resposta_offline = f"💡 **Dica de Vendas Power Baterias:**\n\nPara a dúvida '{prompt}', lembre-se:\n- **Garantia & Entrega:** Reforce sempre que entregamos e instalamos no local sem custo extra.\n- **Teste Grátis:** Ofereça o teste do alternador ao cliente para gerar confiança.\n\n*(Instale a biblioteca `openai` e insira a API Key acima para respostas completas com IA em tempo real!)*"
            st.session_state["mensagens_chat"].append({"role": "assistant", "content": resposta_offline})
            st.chat_message("assistant").write(resposta_offline)
        else:
            try:
                client = OpenAI(api_key=api_key)
                system_prompt = "Você é um consultor especialista em baterias automotivas e vendas de balcão da loja Power Baterias. Responda de forma direta, amigável, informal e altamente prática para ajudar o vendedor a fechar a venda rapidamente."
                
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": system_prompt}] + st.session_state["mensagens_chat"]
                )
                
                resp_ia = res.choices[0].message.content
                st.session_state["mensagens_chat"].append({"role": "assistant", "content": resp_ia})
                st.chat_message("assistant").write(resp_ia)
            except Exception as e:
                st.error(f"Erro ao conectar com a IA: {e}")
