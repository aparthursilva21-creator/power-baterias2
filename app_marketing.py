import streamlit as st
import sqlite3
import pandas as pd
import os

try:
    import openai
    OPENAI_DISPONIVEL = True
except ImportError:
    OPENAI_DISPONIVEL = False

st.set_page_config(
    page_title="Power Baterias - Marketing IA & Suporte",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Profissional / Custom CSS (Tema Power Baterias - Dark & Neon)
st.markdown("""
<style>
    .main { background-color: #0d1117; }
    .stApp { color: #f0f6fc; }
    .stButton>button {
        background: linear-gradient(90deg, #ffb703 0%, #fb8500 100%);
        color: #000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 0px 12px rgba(255, 183, 3, 0.6);
    }
    .card-plat {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #ffb703;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

def conectar():
    return sqlite3.connect("power_baterias.db", timeout=10)

def inicializar_banco():
    conn = conectar()
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
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        catalogo = [
            ("60 Ah Padrão", "Heliar 60Ah", 60, "Heliar", 550.00, 15, 24, "Civic, Corolla, Onix, HB20, Fox"),
            ("60 Ah Padrão", "Moura 60Ah", 60, "Moura", 550.00, 12, 24, "Civic, Corolla, Onix, HB20, Fox"),
            ("50 Ah Caixa Alta", "Moura 50Ah CA", 50, "Moura", 530.00, 8, 24, "Fiesta, EcoSport, Ka, Fit"),
            ("70 Ah", "Heliar 70Ah", 70, "Heliar", 760.00, 6, 24, "SUVs, Pickups, Compass, Renegade"),
            ("36/40/45/48 Ah", "Cral 45Ah", 45, "Cral", 420.00, 10, 24, "Celta, Uno, Palio, Ka")
        ]
        cursor.executemany("INSERT INTO produtos (categoria, nome, amperagem, marca, preco, quantidade, meses_garantia, veiculo) VALUES (?,?,?,?,?,?,?,?)", catalogo)
        conn.commit()
    conn.close()

inicializar_banco()

def carregar_produtos():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

# BARRA LATERAL - CONFIGURAÇÕES & CHAVE IA
st.sidebar.image("logo.png" if os.path.exists("logo.png") else "https://via.placeholder.com/200x80?text=POWER+BATERIAS", use_container_width=True)
st.sidebar.title("⚡ Painel de Controle")
st.sidebar.markdown("---")

api_key = st.sidebar.text_input("🔑 Sua Chave API OpenAI (sk-...):", type="password", help="Insira sua chave para ativar a IA avançada")
if api_key and OPENAI_DISPONIVEL:
    openai.api_key = api_key
    st.sidebar.success("IA Conectada com Sucesso!")
else:
    st.sidebar.warning("Modo IA Padrão Ativo (Sem Chave)")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Dica de Anúncios:**\n- **OLX:** Foco em preço à vista e entrega rápida local.\n- **Facebook:** Foco em garantia e facilidade de cartão.\n- **WhatsApp:** Mensagem direta e atendimento humanizado.")

# CABEÇALHO PRINCIPAL
st.title("⚡ Power Baterias | Hub de Vendas & IA")
st.caption("Gerador de Campanhas Multicanal, Galeria de Mídias e Assistente Inteligente")

produtos_df = carregar_produtos()

# ABAS DO SISTEMA
tab_anuncios, tab_galeria, tab_bot = st.tabs([
    "📢 Anúncios por Plataforma (OLX / FB / Insta / Zap)", 
    "🖼️ Galeria de Fotos dos Modelos", 
    "🤖 Chatbot Suporte & Tira-Dúvidas"
])

# -----------------------------------------------------------------------------
# ABA 1: GERADOR DE ANÚNCIOS ESPECÍFICOS POR CANAL
# -----------------------------------------------------------------------------
with tab_anuncios:
    st.subheader("🎯 Criador de Anúncios Direcionados por Canal")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 1. Escolha o Produto e Canal")
        prod_selecionado = st.selectbox("Bateria para Anunciar:", produtos_df['nome'].unique())
        canal = st.selectbox("Canal de Venda / Rede Social:", [
            "OLX (Desconto + Entrega Rápida)",
            "Facebook Marketplace (Condições de Pagamento + Aplicação)",
            "Instagram / TikTok (Legenda Engajadora + Hashtags)",
            "WhatsApp (Prospecção Direta para Cliente)"
        ])
        
        desconto_aplicado = st.number_input("Desconto de Promoção (R$):", min_value=0.0, value=30.0)
        prod_data = produtos_df[produtos_df['nome'] == prod_selecionado].iloc[0]
        preco_final = prod_data['preco'] - desconto_aplicado
        
        btn_gerar = st.button("🚀 Gerar Anúncio Profissional")

    with col2:
        st.markdown("#### 2. Resultado do Anúncio Formatado")
        if btn_gerar:
            if api_key and OPENAI_DISPONIVEL:
                prompt = f"""
                Escreva um anúncio de alta conversão para a loja 'Power Baterias' vender no {canal}.
                Produto: Bateria {prod_data['nome']} ({prod_data['amperagem']}Ah).
                Marca: {prod_data['marca']}.
                Garantia: {prod_data['meses_garantia']} meses.
                Veículos Compatíveis: {prod_data['veiculo']}.
                Preço Promocional: R$ {preco_final:.2f} (Preço normal R$ {prod_data['preco']:.2f}).
                Instalação e Entrega: Teste do alternador grátis + entrega grátis no raio de atendimento.
                Adapte o tom especificamente para o público do {canal}. Use formatação adequada e emojis.
                """
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    texto_anuncio = res.choices[0].message.content
                except Exception as e:
                    st.error(f"Erro na API da OpenAI: {e}")
                    texto_anuncio = None
            else:
                # Textos pré-configurados sob medida para cada canal
                if "OLX" in canal:
                    texto_anuncio = f"""🔥 **BATERIA {prod_data['nome'].upper()} - NOVA C/ GARANTIA + ENTREGA RÁPIDA** 🔥

Sua bateria pifou? Entregamos e instalamos onde você estiver!

🔋 **Modelo:** {prod_data['nome']} ({prod_data['amperagem']} Amperes)
🛡️ **Garantia:** {prod_data['meses_garantia']} Meses de fábrica
🚗 **Ideal para:** {prod_data['veiculo']}

💰 **Preço Imbatível à Vista:** R$ {preco_final:.2f} (A base de troca)
💳 Parcelamos em até 10x no cartão!

✅ Teste de alternador e fuga de corrente GRÁTIS na entrega.
📍 Atendimento Rápido na Região.

📲 Chama no chat da OLX ou no WhatsApp da Power Baterias!"""

                elif "Facebook" in canal:
                    texto_anuncio = f"""⚡ **POWER BATERIAS - A MELHOR OPÇÃO PARA O SEU CARRO** ⚡

Não fique na mão! Bateria {prod_data['nome']} com desconto exclusivo essa semana!

🚗 Compatível com: {prod_data['veiculo']}
🛡️ Garantia Total de {prod_data['meses_garantia']} Meses
⚡ Amperagem: {prod_data['amperagem']}Ah

De: ~R$ {prod_data['preco']:.2f}~
Por apenas: **R$ {preco_final:.2f}** à vista!

💳 Aceitamos Cartões de Crédito / Débito / PIX.
🛠️ Entrega e Instalação Grátis na sua garagem!

📩 Mande uma mensagem agora no Messenger para garantir o seu desconto!"""

                elif "Instagram" in canal:
                    texto_anuncio = f"""🚗⚡ **SEU CARRO MERECE A MELHOR ENERGIA!**

Carro custando a pegar de manhã? Pode ser a bateria! 🔋

Aproveite nossa super oferta da **{prod_data['nome']}**:
✅ {prod_data['meses_garantia']} Meses de Garantia
✅ Instalação e Teste Grátis no seu veículo
✅ Aplicação perfeita em: {prod_data['veiculo']}

🏷️ De R$ {prod_data['preco']:.2f} por **R$ {preco_final:.2f}**!

📲 Clique no link da bio e fale direto com nossos especialistas no WhatsApp!

---
#PowerBaterias #BateriaDeCarro #Bateria{prod_data['marca']} #AutoEletrica #ManutencaoAutomotiva #Carros"""

                else: # WhatsApp
                    texto_anuncio = f"""Olá! Tudo bem? ⚡ **Power Baterias** informando:

Sua Bateria está fraquejando? Garantimos a troca rápida sem você sair de casa!

🔋 **Bateria {prod_data['nome']}**
• Garantia: {prod_data['meses_garantia']} meses
• Recomendada para: {prod_data['veiculo']}
• Valor Promocional: **R$ {preco_final:.2f}** à vista (base de troca).

🛵 Levemos, testamos o alternador e instalamos na hora!
Quer agendar a sua entrega agora?"""

            if texto_anuncio:
                st.code(texto_anuncio, language="markdown")
                st.info("💡 Basta clicar no ícone no canto superior direito do bloco de código para copiar!")

# -----------------------------------------------------------------------------
# ABA 2: GALERIA DE FOTOS DOS MODELOS (PRONTAS PARA COPIAR E POSTAR)
# -----------------------------------------------------------------------------
with tab_galeria:
    st.subheader("🖼️ Banco de Imagens & Fotos dos Modelos")
    st.markdown("Guarde ou selecione as fotos das baterias para anexar nos posts da OLX, Facebook e WhatsApp.")
    
    cols = st.columns(3)
    modelos_fotos = [
        {"nome": "Linha Moura (48Ah / 60Ah / 70Ah)", "url": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=500&auto=format&fit=crop&q=60", "tag": "Moura Profissional"},
        {"nome": "Linha Heliar Premium", "url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&auto=format&fit=crop&q=60", "tag": "Heliar 24 Meses"},
        {"nome": "Linha Cral / América / KF", "url": "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=500&auto=format&fit=crop&q=60", "tag": "Econômicas"}
    ]
    
    for idx, item in enumerate(modelos_fotos):
        with cols[idx % 3]:
            st.image(item["url"], caption=item["nome"], use_container_width=True)
            st.caption(f"**Selo:** {item['tag']}")
            st.text_input(f"Link da Foto {idx+1}:", value=item["url"], key=f"img_{idx}")

# -----------------------------------------------------------------------------
# ABA 3: CHATBOT DE SUPORTE & TIRA-DÚVIDAS (TÉCNICO E VENDAS)
# -----------------------------------------------------------------------------
with tab_bot:
    st.subheader("🤖 Chatbot Auxiliar - Dúvidas Técnicas e de Vendas")
    st.markdown("Consulte aplicações de baterias, amperagens corretas e dicas de atendimento ao cliente.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Olá! Sou o assistente da **Power Baterias**. Pode me perguntar sobre qual bateria usar em determinado carro, problemas de alternador ou como responder clientes no WhatsApp!"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ex: Qual bateria vai no Civic 2018? Ou: Como dar desconto no PIX?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            if api_key and OPENAI_DISPONIVEL:
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Você é o especialista técnico e comercial da Power Baterias. Seja direto, prático e prestativo."},
                            *st.session_state.messages
                        ]
                    )
                    resposta = res.choices[0].message.content
                except Exception as e:
                    resposta = f"Erro no servidor da IA: {e}"
            else:
                # Respostas pré-programadas para dúvidas comuns
                txt_lower = user_input.lower()
                if "civic" in txt_lower or "corolla" in txt_lower:
                    resposta = "🚗 Para Civic / Corolla modernos, o recomendado é a bateria de **60Ah** (Moura M60AD / Heliar HG60DD) com polo positivo no lado correto da caixa."
                elif "desconto" in txt_lower or "pix" in txt_lower:
                    resposta = "💡 **Dica de Venda:** No PIX você pode oferecer de R$ 20,00 a R$ 30,00 de desconto se o cliente entregar a bateria velha (à base de troca)."
                elif "garantia" in txt_lower:
                    resposta = "🛡️ A garantia das marcas Moura/Heliar é de 24 meses. Linhas intermediárias (Cral, América) costumam ter de 12 a 18 meses."
                else:
                    resposta = f"Entendi sua dúvida sobre '{user_input}'. Para consultas avançadas com inteligência artificial ilimitada, adicione sua chave API na barra lateral esquerda!"

            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})
