import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Meu Analista de Ações", layout="wide")

st.title("📊 Dashboard de Análise de Ações")
st.sidebar.header("Configurações")

# 1. Inputs do Usuário na Barra Lateral
ticket_escolhido = st.sidebar.text_input("Digite o Ticker do Ativo (ex: PETR4.SA, AAPL)", "PETR4.SA")
data_inicio = st.sidebar.date_input("Data de Início", pd.to_datetime("2023-01-01"))
data_fim = st.sidebar.date_input("Data de Fim", pd.to_datetime("today"))

# 2. Carregamento dos Dados
@st.cache_data # Isso faz o app ficar rápido, evitando baixar os dados toda hora
def carregar_dados(ticket, start, end):
    dados = yf.download(ticket, start=start, end=end)
    return dados

try:
    df = carregar_dados(ticket_escolhido, data_inicio, data_fim)

    # 3. Cálculo de Médias Móveis
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()

    # 4. Exibição de Métricas no Topo
    col1, col2, col3 = st.columns(3)
    ultimo_preco = df['Close'].iloc[-1]
    variacao = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
    
    col1.metric("Preço Atual", f"R$ {ultimo_preco:.2f}", f"{variacao:.2f}%")
    col2.metric("Média 20 dias", f"R$ {df['SMA20'].iloc[-1]:.2f}")
    col3.metric("Volume Médio", f"{df['Volume'].mean():.0f}")

    # 5. Gráfico Principal
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                 low=df['Low'], close=df['Close'], name='Preços'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='Média 20d', line=dict(color='orange')))
    fig.update_layout(height=600, template="plotly_dark")
    
    st.plotly_chart(fig, use_container_width=True)

    # 6. Tabela de Dados (opcional)
    if st.checkbox("Mostrar dados brutos"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Erro ao carregar o ativo: {e}")
    