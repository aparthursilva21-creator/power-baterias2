import streamlit as st
import sqlite3
import pandas as pd
import os

# Tenta importar a biblioteca da OpenAI para recursos de IA
try:
    import openai
    OPENAI_DISPONIVEL = True
except ImportError:
    OPENAI_DISPONIVEL = False

st.set_page_config(page_title="Marketing IA - Power Baterias", layout="wide")

def conectar():
    return sqlite3.connect("power_baterias.db", timeout=10)

def carregar_produtos():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

st.title("🤖 Central de Marketing IA - Power Baterias")
st.markdown("Crie campanhas, ofertas para WhatsApp e posts para redes sociais automaticamente.")

# Configuração da chave de API da OpenAI
api_key = st.sidebar.text_input("Chave API OpenAI (opcional)", type="password")
if api_key and OPENAI_DISPONIVEL:
    openai.api_key = api_key

produtos_df = carregar_produtos()

tab1, tab2, tab3 = st.tabs(["📲 Ofertas WhatsApp", "📸 Posts Redes Sociais", "🎯 Promoções por Estoque"])

with tab1:
    st.subheader("Gerador de Mensagens para WhatsApp")
    
    if not produtos_df.empty:
        produto_sel = st.selectbox("Selecione o produto em promoção:", produtos_df['nome'].unique())
        prod_data = produtos_df[produtos_df['nome'] == produto_sel].iloc[0]
        
        tom = st.selectbox("Tom da conversa:", ["Urgente / Promoção Relâmpago", "Amigável e Direto", "Profissional"])
        desconto = st.number_input("Desconto em R$ (opcional):", min_value=0.0, value=20.0)
        
        if st.button("Gerar Mensagem"):
            preco_promo = prod_data['preco'] - desconto
            
            if api_key and OPENAI_DISPONIVEL:
                prompt = f"Crie uma mensagem curta e persuasiva de WhatsApp para a loja Power Baterias vendendo a bateria {prod_data['nome']} por R${preco_promo:.2f} (Preço original R${prod_data['preco']:.2f}). Compatível com {prod_data['veiculo']}. Tom: {tom}. Use emojis."
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    mensagem = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Erro na API: {e}")
                    mensagem = None
            else:
                # Gerador padrão de texto sem API
                mensagem = f"⚡ *OFERTA ESPECIAL POWER BATERIAS!* ⚡\n\nSua bateria falhou? Não fique na mão!\n\n🔋 *{prod_data['nome']}*\n🚗 Ideal para: {prod_data['veiculo']}\n🛡️ Garantia: {prod_data['meses_garantia']} meses\n\n💰 De R$ {prod_data['preco']:.2f} por apenas *R$ {preco_promo:.2f}* à vista!\n\nEntregamos e instalamos na sua casa! Responda essa mensagem e garanta a sua."
            
            if mensagem:
                st.success("Mensagem gerada com sucesso!")
                st.code(mensagem, language="markdown")

with tab2:
    st.subheader("Gerador de Legendas para Instagram e Facebook")
    
    foco = st.text_input("Qual o foco do post?", "Troca de bateria com instalação grátis em domicílio")
    
    if st.button("Criar Post"):
        if api_key and OPENAI_DISPONIVEL:
            prompt = f"Escreva uma legenda engajadora para o Instagram da loja 'Power Baterias'. Foco: {foco}. Inclua hashtags relevantes sobre carros, manutenção preventiva e baterias."
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                legenda = response.choices[0].message.content
                st.markdown(legenda)
            except Exception as e:
                st.error(f"Erro ao gerar post via IA: {e}")
        else:
            st.info("Adicione sua chave API da OpenAI na barra lateral para gerar legendas personalizadas com Inteligência Artificial.")
            st.markdown(f"**Sugestão Padrão:**\n\n🚗⚡ Seu carro merece a energia certa! Na Power Baterias você encontra as melhores marcas com garantia e instalação rápida.\n\n📍 Foco de hoje: {foco}\n\n📲 Chame no WhatsApp e solicite seu orçamento sem compromisso!\n\n#PowerBaterias #ManutencaoAutomotiva #BateriaDeCarro #AutoEletrica")

with tab3:
    st.subheader("Análise do Estoque para Campanhas")
    if not produtos_df.empty:
        st.write("Produtos com maior quantidade em estoque (ideais para liquidação):")
        estoque_alto = produtos_df.sort_values(by="quantidade", ascending=False).head(5)
        st.dataframe(estoque_alto[['nome', 'marca', 'quantidade', 'preco']])
