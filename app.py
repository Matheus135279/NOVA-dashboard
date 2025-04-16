import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from utils import (
    format_currency, format_number, create_evolution_chart,
    create_comparison_chart, export_to_excel, export_to_pdf,
    map_csv_columns, calculate_kpis
)
from api_connectors import FacebookAdsConnector, GoogleAdsConnector

# Configuração inicial
load_dotenv()
st.set_page_config(page_title="Dashboard de Ads", layout="wide")

# CSS personalizado
st.markdown("""
<style>
    /* Fundo gradiente */
    .stApp {
        background: linear-gradient(180deg, #1E1B2E 0%, #2D1A4D 100%);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #2C1A4B;
    }
    
    /* Botões da sidebar */
    .sidebar-button {
        width: 100%;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 0.5rem;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        text-align: left;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .sidebar-button:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    
    .sidebar-button.active {
        background-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
    }
    
    /* Cards de métricas */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 1rem;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Inicialização do estado da sessão
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
if 'data' not in st.session_state:
    st.session_state.data = None

# Sidebar
st.sidebar.markdown("<h2 style='text-align: center'>🎯 Ads Dashboard</h2>", unsafe_allow_html=True)

# Botões da sidebar
pages = {
    "dashboard": "🖥️ Painel de Campanhas",
    "upload": "📥 Upload de Arquivos",
    "export": "📤 Exportar Relatórios",
    "settings": "⚙️ Configurações"
}

for page_id, page_name in pages.items():
    button_class = "sidebar-button active" if st.session_state.page == page_id else "sidebar-button"
    if st.sidebar.markdown(f"""
        <div class="{button_class}" onclick="document.querySelector('section.main').scrollTop=0">
            {page_name}
        </div>
    """, unsafe_allow_html=True):
        st.session_state.page = page_id

# Filtros globais
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Período")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("De", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("Até", datetime.now())

# Páginas
if st.session_state.page == "dashboard":
    st.title("📊 Painel de Campanhas")
    
    # Carrega dados se disponíveis
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # KPIs
        kpis = calculate_kpis(df)
        cols = st.columns(3)
        
        with cols[0]:
            st.markdown("""
            <div class="metric-card">
                <h3>Impressões</h3>
                <h2>{}</h2>
            </div>
            """.format(format_number(kpis['Impressões'])), unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h3>CTR</h3>
                <h2>{:.2f}%</h2>
            </div>
            """.format(kpis['CTR']), unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown("""
            <div class="metric-card">
                <h3>Cliques</h3>
                <h2>{}</h2>
            </div>
            """.format(format_number(kpis['Cliques'])), unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h3>CPC Médio</h3>
                <h2>{}</h2>
            </div>
            """.format(format_currency(kpis['CPC Médio'])), unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown("""
            <div class="metric-card">
                <h3>Conversões</h3>
                <h2>{}</h2>
            </div>
            """.format(format_number(kpis['Conversões'])), unsafe_allow_html=True)
            
            st.markdown("""
            <div class="metric-card">
                <h3>ROAS</h3>
                <h2>{:.2f}x</h2>
            </div>
            """.format(kpis['ROAS']), unsafe_allow_html=True)
        
        # Gráficos
        st.markdown("### 📈 Evolução Temporal")
        evolution_metric = st.selectbox(
            "Métrica",
            ['impressions', 'clicks', 'conversions', 'cost']
        )
        
        fig = create_evolution_chart(
            df,
            evolution_metric,
            f"Evolução de {evolution_metric.title()}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("Faça upload de dados na aba 'Upload de Arquivos' ou configure as APIs em 'Configurações'")

elif st.session_state.page == "upload":
    st.title("📥 Upload de Arquivos")
    
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df = map_csv_columns(df)
        
        st.success("Arquivo carregado com sucesso!")
        st.write("Preview dos dados:")
        st.dataframe(df.head())
        
        if st.button("Confirmar Upload"):
            st.session_state.data = df
            st.session_state.page = "dashboard"
            st.experimental_rerun()

elif st.session_state.page == "export":
    st.title("📤 Exportar Relatórios")
    
    if st.session_state.data is not None:
        export_type = st.radio("Formato de exportação", ["Excel", "PDF"])
        
        if export_type == "Excel":
            if st.button("Exportar para Excel"):
                export_to_excel(st.session_state.data, "relatorio.xlsx")
                st.success("Relatório Excel gerado com sucesso!")
        else:
            if st.button("Exportar para PDF"):
                charts = [
                    create_evolution_chart(
                        st.session_state.data,
                        'impressions',
                        'Evolução de Impressões'
                    ),
                    create_evolution_chart(
                        st.session_state.data,
                        'clicks',
                        'Evolução de Cliques'
                    )
                ]
                export_to_pdf(st.session_state.data, charts, "relatorio.pdf")
                st.success("Relatório PDF gerado com sucesso!")
    else:
        st.info("Carregue dados primeiro na aba 'Upload de Arquivos'")

elif st.session_state.page == "settings":
    st.title("⚙️ Configurações")
    
    st.markdown("### 🔑 APIs")
    
    with st.expander("Facebook Ads"):
        st.text_input("Access Token", value=os.getenv('FB_ACCESS_TOKEN', ''), type="password")
        st.text_input("App ID", value=os.getenv('FB_APP_ID', ''))
        st.text_input("App Secret", value=os.getenv('FB_APP_SECRET', ''), type="password")
        st.text_input("Account ID", value=os.getenv('FB_ACCOUNT_ID', ''))
    
    with st.expander("Google Ads"):
        st.text_input("Client ID", value=os.getenv('GOOGLE_ADS_CLIENT_ID', ''))
        st.text_input("Client Secret", value=os.getenv('GOOGLE_ADS_CLIENT_SECRET', ''), type="password")
        st.text_input("Developer Token", value=os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN', ''), type="password")
        st.text_input("Customer ID", value=os.getenv('GOOGLE_ADS_CUSTOMER_ID', '')) 