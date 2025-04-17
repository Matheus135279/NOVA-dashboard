import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button {
        width: 100%;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 0.5rem;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        text-align: left;
        transition: all 0.3s;
    }
    
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"] button:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }
    
    div[data-testid="stVerticalBlock"] div[data-testid="stButton"].active button {
        background-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
    }
    
    /* Cards de métricas */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 1rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h2 {
        color: white;
        font-size: 1.5rem;
        margin: 0;
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

# Botões da sidebar com st.button
col = st.sidebar.container()

if col.button("🖥️ Painel de Campanhas", key="btn_dashboard", 
              help="Visualize KPIs e gráficos das campanhas",
              use_container_width=True):
    st.session_state.page = "dashboard"

if col.button("📥 Upload de Arquivos", key="btn_upload",
              help="Faça upload dos arquivos CSV",
              use_container_width=True):
    st.session_state.page = "upload"

if col.button("📤 Exportar Relatórios", key="btn_export",
              help="Exporte relatórios em Excel ou PDF",
              use_container_width=True):
    st.session_state.page = "export"

if col.button("⚙️ Configurações", key="btn_settings",
              help="Configure as APIs e preferências",
              use_container_width=True):
    st.session_state.page = "settings"

# Filtros globais
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Período")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("De", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("Até", datetime.now())

# Funções auxiliares
def create_distribution_chart(df, value_col, name_col, title):
    """Cria gráfico de pizza para distribuição."""
    fig = px.pie(
        df.groupby(name_col)[value_col].sum().reset_index(),
        values=value_col,
        names=name_col,
        title=title,
        template='plotly_dark'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    return fig

def create_comparison_bar(df, metrics, name_col, title):
    """Cria gráfico de barras para comparação."""
    fig = go.Figure()
    
    for metric in metrics:
        fig.add_trace(go.Bar(
            name=metric.title(),
            x=df[name_col],
            y=df[metric],
        ))
    
    fig.update_layout(
        title=title,
        template='plotly_dark',
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    return fig

# Páginas
if st.session_state.page == "dashboard":
    st.title("📊 Painel de Campanhas")
    
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # KPIs principais
        kpis = calculate_kpis(df)
        cols = st.columns(5)
        
        metrics = [
            ("Investimento Total", format_currency(kpis['Custo Total']), "💰"),
            ("Cliques", format_number(kpis['Cliques']), "🖱️"),
            ("CPC Médio", format_currency(kpis['CPC Médio']), "💵"),
            ("CTR", f"{kpis['CTR']:.2f}%", "📊"),
            ("Conversões", format_number(kpis['Conversões']), "🎯")
        ]
        
        for col, (title, value, icon) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{icon} {title}</h3>
                    <h2>{value}</h2>
                </div>
                """, unsafe_allow_html=True)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Distribuição de Investimento")
            fig_pie = create_distribution_chart(
                df, 'cost', 'campaign',
                'Distribuição de Investimento por Campanha'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Desempenho por Campanha")
            fig_bar = create_comparison_bar(
                df.groupby('campaign').sum().reset_index(),
                ['clicks', 'conversions'],
                'campaign',
                'Cliques e Conversões por Campanha'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Evolução temporal
        st.markdown("### 📈 Evolução Temporal")
        metric = st.selectbox(
            "Métrica",
            ['cost', 'clicks', 'impressions', 'conversions'],
            format_func=lambda x: x.title()
        )
        
        fig_line = create_evolution_chart(
            df.groupby('date')[metric].sum().reset_index(),
            metric,
            f'Evolução de {metric.title()}'
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
    else:
        st.info("Faça upload de dados na aba 'Upload de Arquivos' ou configure as APIs em 'Configurações'")

elif st.session_state.page == "upload":
    st.title("📥 Upload de Arquivos")
    
    uploaded_files = st.file_uploader(
        "Escolha um ou mais arquivos CSV",
        type=['csv'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        all_data = []
        
        for file in uploaded_files:
            df = pd.read_csv(file)
            
            # Verifica colunas necessárias
            required_columns = {
                'date', 'impressions', 'clicks', 'ctr', 'cpc',
                'conversions', 'cost', 'conversion_value', 'campaign'
            }
            
            df = map_csv_columns(df)
            missing_cols = required_columns - set(df.columns)
            
            if missing_cols:
                st.error(f"Arquivo {file.name} não contém as colunas: {', '.join(missing_cols)}")
                continue
            
            st.success(f"Arquivo {file.name} carregado com sucesso!")
            st.write("Preview dos dados:")
            st.dataframe(df.head())
            
            all_data.append(df)
        
        if all_data and st.button("Confirmar Upload"):
            st.session_state.data = pd.concat(all_data, ignore_index=True)
            st.session_state.page = "dashboard"
            st.experimental_rerun()

elif st.session_state.page == "export":
    st.title("📤 Exportar Relatórios")
    
    if st.session_state.data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exportar como Excel", use_container_width=True):
                df = st.session_state.data
                export_to_excel(df, "relatorio_ads.xlsx")
                st.success("Relatório Excel gerado com sucesso!")
        
        with col2:
            if st.button("📄 Exportar como PDF", use_container_width=True):
                df = st.session_state.data
                
                # Gera gráficos para o PDF
                charts = [
                    create_distribution_chart(
                        df, 'cost', 'campaign',
                        'Distribuição de Investimento'
                    ),
                    create_comparison_bar(
                        df.groupby('campaign').sum().reset_index(),
                        ['clicks', 'conversions'],
                        'campaign',
                        'Desempenho por Campanha'
                    )
                ]
                
                export_to_pdf(df, charts, "relatorio_ads.pdf")
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