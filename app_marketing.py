import streamlit as st
import sqlite3
import pandas as pd
import os
import random

st.set_page_config(
    page_title="Power Baterias - Gerador Infinito de Anúncios",
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
    
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label, .stMultiSelect label { 
        color: #00ff66 !important; 
        font-weight: bold;
    }
    
    .stTab [data-baseweb="tab"] { color: #8b949e; font-weight: bold; font-size: 16px; }
    .stTab [aria-selected="true"] { color: #00ff66 !important; border-bottom-color: #00ff66 !important; }
    
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
    
    # Catálogo Completo Expansível de Baterias (Marcas Principais e Secundárias)
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        catalogo = [
            ("60 Ah Padrao", "Moura 60Ah M60AD", 60, "Moura", 550.00, 20, 24, "Civic, Corolla, Onix, HB20, Fox, Cruze, Astra"),
            ("60 Ah Padrao", "Heliar 60Ah HG60DD", 60, "Heliar", 550.00, 15, 24, "Civic, Corolla, Onix, HB20, Fox, Fit, Gol"),
            ("60 Ah Padrao", "Cral 60Ah CL60D", 60, "Cral", 430.00, 15, 18, "Gol, Palio, Uno, Celta, Voyage, Siena"),
            ("60 Ah Padrao", "América 60Ah AM60D", 60, "América", 410.00, 10, 15, "Gol, Fox, Ka, Palio, Fiesta"),
            ("60 Ah Padrao", "KF 60Ah KF60D", 60, "KF", 380.00, 10, 12, "Uno, Celta, Palio, Gol, Clio"),
            ("60 Ah Padrao", "Super Life 60Ah SL60D", 60, "Super Life", 360.00, 8, 12, "Carros Populares 1.0 e 1.4"),
            ("50 Ah Caixa Alta", "Moura 50Ah M50ED", 50, "Moura", 530.00, 8, 24, "Fiesta, EcoSport, Ka, Fit, City"),
            ("50 Ah Caixa Alta", "Heliar 50Ah HG50ED", 50, "Heliar", 520.00, 8, 24, "Fiesta, EcoSport, Ka, Fit"),
            ("45 Ah", "Cral 45Ah CL45D", 45, "Cral", 390.00, 12, 18, "Celta, Uno, Palio, Ka, March, Clio"),
            ("45 Ah", "Moura 45Ah M45FD", 45, "Moura", 480.00, 10, 24, "Fit, March, Uno, Celta, Picanto"),
            ("70 Ah", "Heliar 70Ah HG70KD", 70, "Heliar", 760.00, 6, 24, "SUVs, Pickups, Compass, Renegade, Hilux"),
            ("70 Ah", "Moura 70Ah M70KD", 70, "Moura", 770.00, 6, 24, "Compass, Renegade, Toro, Hilux, Ranger"),
            ("60 Ah EFB", "Moura 60Ah EFB M60EX", 60, "Moura", 890.00, 5, 24, "Argo, Cronos, Renegade, Toro, Jeep Compass (Start-Stop)"),
            ("150 Ah Pesada", "Moura 150Ah M150BD", 150, "Moura", 1250.00, 4, 15, "Caminhoes, Onibus, Tratores, Micro-onibus")
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
st.sidebar.subheader("Gerador Múltiplo de Anúncios")
st.sidebar.write("---")
st.sidebar.markdown("### Publicação Direta:")
st.sidebar.markdown("- [Facebook Marketplace](https://www.facebook.com/marketplace/create/item)")
st.sidebar.markdown("- [OLX Anunciar](https://www.olx.com.br/anunciar)")
st.sidebar.markdown("- [Google Ads](https://ads.google.com/ups/routing?source=206&subid=xs-ip-gemini-adlt)")

st.title("Power Baterias | Máquina Infinito de Anúncios")

tab_anuncios, tab_albuns = st.tabs([
    "Gerador Infinito de Anuncios Unicos", 
    "Albuns de Fotos por Marca"
])

# -----------------------------------------------------------------------------
# TAB 1: GERADOR INFINITO DE ANÚNCIOS ÚNICOS (VARIABILIDADE TOTAL)
# -----------------------------------------------------------------------------
with tab_anuncios:
    st.subheader("Configurador da Campanha de Vendas")
    
    col_cfg1, col_cfg2 = st.columns([1, 1])
    
    with col_cfg1:
        tipo_selecao = st.radio("Modo de Seleção de Produtos:", [
            "Anúncio de Produto Único",
            "Anúncio por Amperagem (Ex: Todas de 60Ah)",
            "Combo de Várias Marcas (Lista Completa)"
        ])
        
        if tipo_selecao == "Anúncio de Produto Único":
            prods_escolhidos = [st.selectbox("Selecione o Produto:", produtos_df['nome'].unique())]
        elif tipo_selecao == "Anúncio por Amperagem (Ex: Todas de 60Ah)":
            amp_escolhida = st.selectbox("Selecione a Amperagem:", sorted(produtos_df['amperagem'].unique()))
            prods_escolhidos = produtos_df[produtos_df['amperagem'] == amp_escolhida]['nome'].tolist()
        else:
            prods_escolhidos = st.multiselect("Selecione os Produtos da Lista:", produtos_df['nome'].unique(), default=produtos_df['nome'].unique()[:3])

        estrategia_preco = st.selectbox("Estratégia de Exibição de Preço:", [
            "Mostrar Preço Promocional (A Base de Troca)",
            "Mostrar Preço Cheio + Valor na Troca",
            "A partir de R$ (Exibir Menor Valor)",
            "Ocultar Preço (Foco em Chamada no Chat / Mensagem Privada)"
        ])

    with col_cfg2:
        foco_anuncio = st.selectbox("Gancho Principal do Anúncio (Diferencial):", [
            "Foco em Entrega e Instalação Grátis no Local",
            "Foco em Preço Baixo e Cobrir Oferta",
            "Foco em Emergência (Socorro Rápido para Carro Parado)",
            "Foco em Qualidade e Garantia de Fábrica de até 2 Anos",
            "Misturar Tudo (Anúncio Completo de Alta Conversão)"
        ])
        
        canal_venda = st.selectbox("Plataforma de Destino:", [
            "OLX", "Facebook Marketplace", "Instagram / Feed", "WhatsApp Vendas"
        ])
        
        desconto_aplicado = st.number_input("Desconto Promocional na Troca (R$):", min_value=0.0, value=30.0)
        
        qtd_variacoes = st.slider("Quantidade de Opções de Anúncios Diferentes para Gerar:", min_value=1, max_value=10, value=3)

    st.write("---")
    
    if st.button("GERAR VARIAÇÕE$ DE ANÚNCIOS ÚNICOS AGORA"):
        if not prods_escolhidos:
            st.error("Selecione ao menos um produto para gerar o anúncio.")
        else:
            dados_prods = produtos_df[produtos_df['nome'].isin(prods_escolhidos)]
            
            # BANCO DE DADOS DE FRASES E GANCHOS (VARIABILIDADE DINÂMICA)
            TITULOS_EMERGENCIA = [
                "Bateria Pifou? Entrega e Instalacao Rapida no Seu Endereco",
                "Socorro de Bateria Automotiva - Atendimento Imediato no Local",
                "Carro Nao Pega? Baterias Novas com Entrega Expressa",
                "Bateria Entregue e Instalada Onde Voce Estiver Parado"
            ]
            TITULOS_PROMO = [
                "Promocao de Baterias Automotivas com Garantia de Fabrica",
                "Baterias Direto da Distribuidora com Preco de Atacado",
                "Sua Bateria Velha Vale Desconto na Compra da Nova",
                "O Melhor Preco em Baterias Automotivas da Regiao"
            ]
            TITULOS_MARCAS = [
                "Baterias Moura Heliar Cral e Varias Marcas em Promocao",
                "Linha Completa de Baterias 45Ah 50Ah 60Ah e 70Ah Pronta Entrega",
                "Baterias Seladas com Garantia Nacional de ate 24 Meses"
            ]

            GANCHOS_ENTREGA = [
                "Nao passe perrengue na rua. Nossa equipe leva a bateria nova ate voce e faz a instalacao imediata.",
                "Servico completo de entrega expressa e montagem no local onde seu carro estiver parado.",
                "Chegamos rapido ao seu endereco para voce nao perder tempo nem compromisso."
            ]
            GANCHOS_OFERTA = [
                "Cobrimos ofertas da regiao com produto 100% novo, lacrado e com nota.",
                "Precos especiais para pagamento a vista trazendo a sua bateria usada como base de troca.",
                "Compre direto com quem entende e garanta a melhor condicao do mercado."
            ]

            for i in range(qtd_variacoes):
                st.markdown(f"### Opção de Anúncio #{i+1} (Combinação Exclusiva)")
                
                # Seleção aleatória / dinâmica para cada variação
                if foco_anuncio == "Foco em Emergência (Socorro Rápido para Carro Parado)":
                    titulo = random.choice(TITULOS_EMERGENCIA)
                    gancho = random.choice(GANCHOS_ENTREGA)
                elif foco_anuncio == "Foco em Preço Baixo e Cobrir Oferta":
                    titulo = random.choice(TITULOS_PROMO)
                    gancho = random.choice(GANCHOS_OFERTA)
                else:
                    titulo = random.choice(TITULOS_MARCAS + TITULOS_PROMO)
                    gancho = random.choice(GANCHOS_ENTREGA + GANCHOS_OFERTA)

                # Montagem da lista de produtos e preços no texto
                corpo_produtos = ""
                menor_preco = 99999.0
                
                for _, row in dados_prods.iterrows():
                    p_promo = row['preco'] - desconto_aplicado
                    if p_promo < menor_preco:
                        menor_preco = p_promo
                    
                    if estrategia_preco == "Mostrar Preço Promocional (A Base de Troca)":
                        linha_preco = f"R$ {p_promo:.2f} (a base de troca)"
                    elif estrategia_preco == "Mostrar Preço Cheio + Valor na Troca":
                        linha_preco = f"De R$ {row['preco']:.2f} por R$ {p_promo:.2f} na troca"
                    elif estrategia_preco == "A partir de R$ (Exibir Menor Valor)":
                        linha_preco = f"A partir de R$ {p_promo:.2f}"
                    else:
                        linha_preco = "Consulte valor especial no chat"

                    corpo_produtos += f"- Bateria {row['nome']} ({row['amperagem']}Ah) - Garantia: {row['meses_garantia']} Meses | Preco: {linha_preco}\n  Aplicacao: {row['veiculo']}\n\n"

                # Montagem do Texto Final sem Emojis
                texto_anuncio = f"""TITULO: {titulo.upper()}

{gancho}

MODELOS E BATERIAS DISPONIVEIS:
{corpo_produtos}
DIFERENCIAIS POWER BATERIAS:
- Teste do alternador e diagnostico do sistema eletrico gratuitos na entrega.
- Baterias 100% novas, seladas e testadas.
- Parcelamos no cartao de credito em ate 10x.
- Atendimento agil no balcao ou via entrega expressa.

Chame agora mesmo no chat ou WhatsApp para confirmar a entrega imediata."""

                st.code(texto_anuncio, language="text")
                st.write("---")

            st.markdown("#### Links para Publicação Direta:")
            col_l1, col_l2, col_l3 = st.columns(3)
            with col_l1:
                st.markdown('<div class="card-link"><a href="https://www.facebook.com/marketplace/create/item" target="_blank" style="color:#00ff66; text-decoration:none; font-weight:bold;">Anunciar no Facebook</a></div>', unsafe_allow_html=True)
            with col_l2:
                st.markdown('<div class="card-link"><a href="https://www.olx.com.br/anunciar" target="_blank" style="color:#00ff66; text-decoration:none; font-weight:bold;">Anunciar na OLX</a></div>', unsafe_allow_html=True)
            with col_l3:
                st.markdown('<div class="card-link"><a href="https://ads.google.com/ups/routing?source=206&subid=xs-ip-gemini-adlt" target="_blank" style="color:#00ff66; text-decoration:none; font-weight:bold;">Criar Google Ads</a></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: ÁLBUNS DE FOTOS ORGANIZADOS POR MARCA
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
