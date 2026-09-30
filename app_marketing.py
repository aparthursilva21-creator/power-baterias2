import streamlit as st
import sqlite3
import pandas as pd
import os
import re

st.set_page_config(
    page_title="Power Baterias - Maquina de Vendas e IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Tema Dark Matrix / Terminal Profissional (Verde Neon e Preto)
st.markdown("""
<style>
    .main { background-color: #080a0f; color: #00ff66; }
    .stApp { background-color: #080a0f; color: #e6edf3; }
    h1, h2, h3, h4, h5, h6 { color: #00ff66 !important; font-family: 'Trebuchet MS', sans-serif; font-weight: bold; }
    
    .stButton>button {
        background: linear-gradient(135deg, #00ff66 0%, #009933 100%);
        color: #000000;
        font-weight: 900;
        border-radius: 6px;
        border: none;
        padding: 0.8rem 1.5rem;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0px 4px 15px rgba(0, 255, 102, 0.3);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #33ff85 0%, #00cc44 100%);
        color: #000000;
        transform: translateY(-2px);
        box-shadow: 0px 6px 20px rgba(0, 255, 102, 0.5);
    }
    
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label { 
        color: #00ff66 !important; 
        font-weight: bold;
    }
    
    .stTab [data-baseweb="tab"] { color: #8b949e; font-weight: bold; font-size: 16px; }
    .stTab [aria-selected="true"] { color: #00ff66 !important; border-bottom-color: #00ff66 !important; }
    
    .chat-container {
        background-color: #0d1117;
        border: 1px solid #161b22;
        border-radius: 12px;
        padding: 20px;
        max-height: 550px;
        overflow-y: auto;
    }
    .chat-bubble-user {
        background-color: #161b22;
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 15px 15px 2px 15px;
        margin-bottom: 12px;
        margin-left: 20%;
        text-align: right;
        border: 1px solid #30363d;
        font-size: 15px;
    }
    .chat-bubble-bot {
        background-color: #051b11;
        color: #00ff66;
        padding: 14px 20px;
        border-radius: 15px 15px 15px 2px;
        margin-bottom: 12px;
        margin-right: 15%;
        text-align: left;
        border: 1px solid #00ff66;
        font-size: 15px;
        box-shadow: 0px 2px 8px rgba(0, 255, 102, 0.15);
    }
    
    .card-link {
        background-color: #161b22;
        border: 1px solid #00ff66;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

PASTA_UPLOADS = "uploads_baterias"
if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

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
            ("60 Ah Padrao", "Heliar 60Ah HG60DD", 60, "Heliar", 550.00, 15, 24, "Civic, Corolla, Onix, HB20, Fox, Fit, Gol"),
            ("60 Ah Padrao", "Moura 60Ah M60AD", 60, "Moura", 550.00, 12, 24, "Civic, Corolla, Onix, HB20, Fox, Cruze, Astra"),
            ("50 Ah Caixa Alta", "Moura 50Ah M50ED", 50, "Moura", 530.00, 8, 24, "Fiesta, EcoSport, Ka, Fit, City"),
            ("70 Ah", "Heliar 70Ah HG70KD", 70, "Heliar", 760.00, 6, 24, "SUVs, Pickups, Compass, Renegade, Hilux, Ranger"),
            ("36/40/45/48 Ah", "Cral 45Ah CL45D", 45, "Cral", 420.00, 10, 24, "Celta, Uno, Palio, Ka, March, Clio"),
            ("EFB Start Stop", "Moura 60Ah EFB M60EX", 60, "Moura", 890.00, 5, 24, "Argo, Cronos, Renegade, Toro, Jeep Compass"),
            ("Linha Pesada", "Moura 150Ah M150BD", 150, "Moura", 1250.00, 4, 15, "Caminhoes, Onibus, Tratores, Micro-onibus")
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

produtos_df = carregar_produtos()

# BARRA LATERAL
st.sidebar.title("POWER BATERIAS")
st.sidebar.subheader("Central Comercial & Vendas")
st.sidebar.write("---")
st.sidebar.markdown("### Publicacao Rapida:")
st.sidebar.markdown("- [Facebook Marketplace](https://www.facebook.com/marketplace/create/item)")
st.sidebar.markdown("- [OLX Anunciar](https://www.olx.com.br/anunciar)")
st.sidebar.markdown("- [Google Ads](https://ads.google.com/ups/routing?source=206&subid=xs-ip-gemini-adlt)")
st.sidebar.write("---")
st.sidebar.info("Status do Sistema: Online\nBanco de Dados: Ativo")

st.title("Power Baterias | Maquina de Vendas Automatica")

tab_anuncios, tab_albuns, tab_chatbot = st.tabs([
    "Gerador de Anuncios Ultra-Persuasivos", 
    "Albuns de Fotos por Marca", 
    "Chatbot Comercial Humano"
])

# -----------------------------------------------------------------------------
# TAB 1: GERADOR DE ANÚNCIOS PERSUASIVOS
# -----------------------------------------------------------------------------
with tab_anuncios:
    st.subheader("Gerador de Copys de Alta Conversao por Canal")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        produto_sel = st.selectbox("Selecione o produto:", produtos_df['nome'].unique())
        canal = st.selectbox("Canal de Venda:", [
            "OLX (Foco em Entrega Rapida e Preco)",
            "Facebook Marketplace (Foco em Pagamento Facilitado)",
            "Instagram / Facebook Feed (Foco em Autoridade e Engajamento)",
            "WhatsApp Vendas (Atendimento Direto ao Cliente)"
        ])
        desconto = st.number_input("Desconto Promocional (R$):", min_value=0.0, value=30.0)
        
        prod_data = produtos_df[produtos_df['nome'] == produto_sel].iloc[0]
        preco_promo = prod_data['preco'] - desconto
        
        btn_gerar = st.button("GERAR ANUNCIO AGORA")

    with col2:
        if btn_gerar:
            st.markdown(f"### Copy Formatada para {canal.split(' ')[0]}")
            
            if "OLX" in canal:
                texto = f"""BATERIA {prod_data['nome'].upper()} NOVA COM GARANTIA E ENTREGA NO SEU LOCAL

Nao fique na mao com carro sem pegar. A Power Baterias atende voce com agilidade e os melhores preços da regiao.

ESPECIFICACOES DO PRODUTO:
- Modelo: {prod_data['nome']}
- Capacidade: {prod_data['amperagem']} Amperes
- Fabricante: {prod_data['marca']}
- Garantia de fábrica: {prod_data['meses_garantia']} Meses com certificado oficial
- Aplicacao recomendada: {prod_data['veiculo']}

CONDICOES DE PAGAMENTO:
- Preço especial a vista: R$ {preco_promo:.2f} (Entregando a bateria usada como base de troca)
- Preço normal sem troca: R$ {prod_data['preco']:.2f}
- Parcelamento facilitado no cartao de credito em ate 10x.

DIFERENCIAIS EXCLUSIVOS POWER BATERIAS:
- Entrega e instalacao sem custo adicional no raio de atendimento.
- Teste do alternador e diagnostico do sistema eletrico feitos na hora pela nossa equipe.
- Produto 100% novo, selado e testado antes do envio.

Atendimento imediato via chat ou pelo nosso WhatsApp. Mande sua mensagem agora e agende sua entrega."""

            elif "Facebook" in canal:
                texto = f"""Bateria {prod_data['nome']} - Promocao de Estoque Power Baterias

Bateria nova de fabrica, lacrada, com {prod_data['meses_garantia']} meses de garantia comprovada.

Modelos compativeis: {prod_data['veiculo']}

Valor em promocao a vista: R$ {preco_promo:.2f} (Considerando a bateria antiga na troca)

Aceitamos cartao de credito, debito e PIX.

Oferecemos servico completo de entrega e montagem no local onde seu carro esta parado.
Realizamos o teste gratuito do sistema de carga no momento da instalacao.

Chame no Messenger para confirmar o envio imediato para o seu endereco."""

            elif "Instagram" in canal:
                texto = f"""POWER BATERIAS - ENERGIA E CONFIANCA PARA O SEU VEICULO

Evite o transtorno de ficar parado na rua. A Power Baterias oferece linha completa de baterias automotivas com garantia nacional.

Destaque comercial: Bateria {prod_data['nome']}
Garantia: {prod_data['meses_garantia']} meses
Aplicacoes principais: {prod_data['veiculo']}

De R$ {prod_data['preco']:.2f} por apenas R$ {preco_promo:.2f} a vista na troca do seu casco usado.

Servico de entrega expressa e montagem inclusos no atendimento.

Fale diretamente com nossa equipe comercial pelo link da bio ou via mensagem direta."""

            else: # WhatsApp
                texto = f"""Atendimento Comercial Power Baterias.

Aqui esta a cotacao do modelo ideal para o seu veiculo:

Produto: Bateria {prod_data['nome']} ({prod_data['amperagem']}Ah)
Marca: {prod_data['marca']}
Garantia: {prod_data['meses_garantia']} meses de fábrica
Veiculos compativeis: {prod_data['veiculo']}

Valor promocional a vista: R$ {preco_promo:.2f} (Entregando a bateriausada)
Parcelamento: Opcao de pagamento em ate 10x no cartao de credito.

Servicos inclusos: Entrega no local, instalacao e teste completo do alternador.

Podemos agendar a entrega para qual horario?"""

            st.code(texto, language="text")
            
            st.markdown("#### Links para Publicar Imediatamente:")
            col_l1, col_l2, col_l3 = st.columns(3)
            with col_l1:
                st.markdown('<div class="card-link"><a href="https://www.facebook.com/marketplace/create/item" target="_blank" style="color:#00ff66; text-decoration:none; font-weight:bold;">Anunciar no Facebook</a></div>', unsafe_allow_html=True)
            with col_l2:
                st.markdown('<div class="card-link"><a href="https://www.olx.com.br/anunciar" target="_blank" style="color:#00ff66; text-decoration:none; font-weight:bold;">Anunciar na OLX</a></div>', unsafe_allow_html=True)
            with col_l3:
                st.markdown('<div class="card-link"><a href="https://ads.google.com/ups/routing?source=206&subid=xs-ip-gemini-adlt" target="_blank" style="color:#00ff66; text-decoration:none; font-weight:bold;">Criar Google Ads</a></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: ÁLBUNS DE FOTOS POR MARCA
# -----------------------------------------------------------------------------
with tab_albuns:
    st.subheader("Albuns de Fotos dos Produtos por Marca")
    st.write("Organize as fotos dos produtos por pastas de marca para usar nos seus anuncios e mensagens.")
    
    col_up1, col_up2 = st.columns([1, 2])
    
    with col_up1:
        st.markdown("#### Enviar Foto para o Banco Local")
        marca_foto = st.selectbox("Selecione a Marca:", [
            "Moura", "Heliar", "Cral", "América", "KF", "Super Life", "Outras"
        ])
        arquivo_enviado = st.file_uploader("Escolha a imagem da bateria:", type=["jpg", "jpeg", "png"])
        
        if st.button("SALVAR FOTO NO ALBUM"):
            if arquivo_enviado is not None:
                pasta_marca = os.path.join(PASTA_UPLOADS, marca_foto)
                if not os.path.exists(pasta_marca):
                    os.makedirs(pasta_marca)
                
                caminho_final = os.path.join(pasta_marca, arquivo_enviado.name)
                with open(caminho_final, "wb") as f:
                    f.write(arquivo_enviado.getbuffer())
                st.success(f"Foto salva no album {marca_foto} com sucesso.")
            else:
                st.warning("Selecione uma imagem valida primeiro.")

    with col_up2:
        st.markdown("#### Visualizar Albuns")
        marca_filtro = st.selectbox("Escolha o Album:", [
            "Todas", "Moura", "Heliar", "Cral", "América", "KF", "Super Life", "Outras"
        ])
        
        marcas_para_exibir = [marca_filtro] if marca_filtro != "Todas" else ["Moura", "Heliar", "Cral", "América", "KF", "Super Life", "Outras"]
        
        encontrou_foto = False
        for m in marcas_para_exibir:
            pasta_m = os.path.join(PASTA_UPLOADS, m)
            if os.path.exists(pasta_m):
                arquivos = os.listdir(pasta_m)
                if arquivos:
                    encontrou_foto = True
                    st.markdown(f"##### Album da Marca: {m}")
                    cols_img = st.columns(3)
                    for idx, arq in enumerate(arquivos):
                        caminho_img = os.path.join(pasta_m, arq)
                        with cols_img[idx % 3]:
                            st.image(caminho_img, caption=arq, use_container_width=True)
                            with open(caminho_img, "rb") as file:
                                st.download_button(
                                    label="Baixar Imagem",
                                    data=file,
                                    file_name=arq,
                                    mime="image/png",
                                    key=f"dl_{m}_{idx}"
                                )
        if not encontrou_foto:
            st.info("Nenhuma imagem cadastrada neste album. Faça o envio no painel ao lado.")

# -----------------------------------------------------------------------------
# TAB 3: CHATBOT COMERCIAL HUMANIZADO COMPLETO
# -----------------------------------------------------------------------------
with tab_chatbot:
    st.subheader("Atendimento Humano Comercial - Power Baterias")
    
    col_head1, col_head2 = st.columns([1, 6])
    with col_head1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=75)
        else:
            st.markdown("### [POWER]")
    with col_head2:
        st.markdown("### Power Baterias | Atendimento do Balcao")
        st.caption("Atendente Virtual Comercial | Respostas naturais para fechar vendas")

    if "historico_chat" not in st.session_state:
        st.session_state.historico_chat = [
            {"autor": "bot", "texto": "Fala meu amigo, beleza? Aqui e da Power Baterias. Qual e o modelo do seu carro e o ano? Fala pra mim que ja te passo a bateria certa e o melhor preço com entrega na hora."}
        ]

    # Renderizador do chat estilo WhatsApp
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.historico_chat:
        if msg["autor"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>Voce:</b><br>{msg["texto"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-bot"><b>Atendimento Power Baterias:</b><br>{msg["texto"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # MOTOR DE INTELIGENCIA DE CONVERSACAO COMPLETO
    def processar_resposta_humana(pergunta):
        p = pergunta.lower().strip()
        p_clean = re.sub(r'[^\w\s]', '', p)
        
        # 1. Cumprimentos e Saudações Humanas
        if any(w in p_clean for w in ["oi", "ola", "bom dia", "boa tarde", "boa noite", "e ai", "fala", "opa", "salve", "tudo bem", "tudo bom", "tranquilo"]):
            return "Opa, tudo certo por ai? Aqui e do atendimento da Power Baterias. Como posso te ajudar hoje? Ta precisando de bateria pra qual carro?"

        # 2. Localização e Endereço da Loja
        elif any(w in p_clean for w in ["onde fica", "endereco", "localizacao", "onde e a loja", "bairro", "rua", "posso ir ai", "retirar na loja"]):
            return "A gente faz atendimento tanto na loja fisica quanto na entrega rapida onde seu carro estiver parado. Me passa seu bairro ou localizacao que ja te confirmo o tempo de entrega."

        # 3. Entrega e Instalação em Domicílio
        elif any(w in p_clean for w in ["entrega", "instalacao", "montagem", "socorro", "travado", "nao pega", "parado", "rápido", "demora", "taxa"]):
            return "A gente entrega e instala na hora pra voce nao passar perrengue na rua. O nosso tecnico leva a bateria nova, faz a montagem no seu carro e ainda testa seu alternador de graça pra ver se ta carregando certinho. Qual o seu bairro?"

        # 4. Formas de Pagamento, PIX e Cartão
        elif any(w in p_clean for w in ["pix", "cartao", "parcela", "parcelamento", "fiado", "credito", "debito", "desconto", "dinheiro"]):
            return "A gente facilita no pagamento. No PIX ou no dinheiro tem aquele desconto especial na troca da bateria velha. No cartao de credito a gente parcela pra voce em ate 10x sem complicacao. Quer montar uma cotacao?"

        # 5. Entendendo a Base de Troca
        elif any(w in p_clean for w in ["base de troca", "troca", "bateria velha", "casco", "sem a troca", "dar a velha"]):
            return "A base de troca e quando voce entrega a sua bateria antiga pifada pro nosso motoqueiro na hora da instalacao. Com isso o valor da bateria nova cai bastante. Se voce nao tiver a bateria velha pra entregar, me avisa que te passo o valor sem a troca."

        # 6. Como funciona a Garantia
        elif any(w in p_clean for w in ["garantia", "defeito", "pifou", "trocar", "certificado", "durabilidade", "dura quanto"]):
            return "Todas as nossas baterias sao 100% novas e saem com certificado de garantia de fabrica. Linhas top como Moura e Heliar tem 24 meses de garantia nacional. Se der qualquer problema de fabricacao, e so acionar que a troca e garantida."

        # 7. Diagnóstico e Problemas de Alternador
        elif any(w in p_clean for w in ["alternador", "luz da bateria", "painel", "arranque", "estalo", "fuga de corrente", "descarregando"]):
            return "Se o carro ta dando estalo no arranque ou acendeu a luz da bateria no painel, pode ser a bateria fraca ou o alternador que parou de carregar. Fica tranquilo que quando nosso tecnico vai fazer a entrega ele passa o aparelho e testa o alternador na hora pra voce."

        # 8. MAPPING DE CARROS POPULARES (45Ah a 60Ah)
        elif any(w in p_clean for w in ["gol", "palio", "uno", "celta", "ka", "fox", "fiesta", "corsa", "sienna", "voyage", "up", "mobi", "hb20", "march", "clio", "fit"]):
            return "Pra esse modelo a bateria padrao costuma ser de 45Ah ate 60Ah. Temos a Cral 45Ah saindo em promocao ou as linhas premium Moura 60Ah e Heliar 60Ah com 2 anos de garantia. Me fala o ano exato do carro pra te passar o valor fechado com entrega."

        # 9. MAPPING DE SEDANS E HATCHS MEDIOS (60Ah Padrao)
        elif any(w in p_clean for w in ["civic", "corolla", "onix", "cruze", "astra", "vectra", "focus", "jetta", "golf", "cerato", "city", "duster", "sander"]):
            return "Esse carro exige uma bateria de 60Ah com boa corrente de partida (CCA alta). Recomendo a Moura 60Ah M60AD ou Heliar 60Ah HG60DD. Ambas vem com 24 meses de garantia de fabrica e sao as originais das montadoras. Quer que envie a proposta no capricho?"

        # 10. MAPPING DE SUVS, PICKUPS E LINHA DIESEL (70Ah a 90Ah)
        elif any(w in p_clean for w in ["hilux", "ranger", "amarok", "s10", "triton", "frontier", "l200", "pajero", "compass", "renegade", "toro"]):
            return "Pickups e SUVs precisam de bateria reforçada de 70Ah com alto CCA para aguentar o motor. Temos a Heliar 70Ah e Moura 70Ah prontas pra entrega imediata. Qual o ano e motorizacao do seu carro?"

        # 11. SISTEMA START-STOP (EFB / AGM)
        elif any(w in p_clean for w in ["start stop", "startstop", "efb", "agm", "desliga sozinho"]):
            return "Se o seu carro desliga sozinho no sinal (sistema Start-Stop), ele precisa obrigatoriamente de uma bateria EFB ou AGM. Se colocar bateria comum ela pifa em poucos meses. Temos a Moura 60Ah EFB em estoque com valor promocional. Quer cotar essa?"

        # 12. LINHA PESADA (150Ah a 220Ah - Caminhões e Tratores)
        elif any(w in p_clean for w in ["caminhao", "onibus", "trator", "150ah", "180ah", "220ah", "scania", "volvo", "mercedes", "vw delivery"]):
            return "Trabalhamos com a linha pesada reforçada da Moura e Heliar de 150Ah ate 220Ah pra caminhoes, tratores e maquinas. Todas com estrutura resistente a vibracao. Me fala qual e o veiculo que te passo a cotacao da linha pesada."

        # 13. DÚVIDAS SOBRE MARCAS ESPECÍFICAS
        elif "moura" in p_clean:
            return "A Moura e a bateria mais vendida do Brasil, original de montadora e vem com 24 meses de garantia nacional. E colocar no carro e esquecer dor de cabeca. Temos todos os modelos a pronta entrega."

        elif "heliar" in p_clean:
            return "A Heliar tem a tecnologia de placas PowerFrame, garantindo durabilidade extrema e partida rapida ate nos dias frios. Vem com 2 anos de garantia de fabrica e assistencia em todo o pais."

        elif any(w in p_clean for w in ["cral", "america", "kf", "super life"]):
            return "Sao marcas de excelente custo-beneficio, ideais pra quem quer economizar sem abrir mao de uma boa garantia de fabrica. Temos valores muito em conta pra pagamento a vista na troca."

        # 14. HORÁRIO E ATENDIMENTO DE EMERGÊNCIA
        elif any(w in p_clean for w in ["horario", "funciona ate que horas", "domingo", "feriado", "aberto agora", "plantao"]):
            return "Nossa equipe esta sempre apostos para entregas rapidas no horario comercial e plantao de entregas. Mande o endereco de onde voce esta que verificamos o entregador mais proximo."

        # 15. RESPOSTA PADRONIZADA PARA PERGUNTAS FORA DO ESCOPO
        else:
            return "Desculpe, essa informação técnica específica ainda está sendo atualizada no nosso sistema. Por favor, entre em contato com nossa equipe comercial no balcao ou pelo WhatsApp para que possamos te atender com precisao."

    # Campo de entrada e disparo
    st.write("---")
    user_msg = st.text_input("Escreva sua pergunta ou mensagem aqui:", key="input_chat_main")
    
    if st.button("ENVIAR MENSAGEM NO CHAT"):
        if user_msg:
            st.session_state.historico_chat.append({"autor": "user", "texto": user_msg})
            resposta_gerada = processar_resposta_humana(user_msg)
            st.session_state.historico_chat.append({"autor": "bot", "texto": resposta_gerada})
            st.rerun()
