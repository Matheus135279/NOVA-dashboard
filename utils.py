import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st
from fpdf import FPDF
import io

def calculate_metrics(df):
    """Calcula métricas adicionais a partir dos dados brutos"""
    metrics = {
        'total_spend': df['spend'].sum(),
        'total_impressions': df['impressions'].sum(),
        'total_clicks': df['clicks'].sum(),
        'total_conversions': df['conversions'].sum() if 'conversions' in df.columns else 0,
        'avg_ctr': (df['clicks'].sum() / df['impressions'].sum() * 100) if df['impressions'].sum() > 0 else 0,
        'avg_cpc': df['spend'].sum() / df['clicks'].sum() if df['clicks'].sum() > 0 else 0,
        'avg_cpm': df['spend'].sum() / (df['impressions'].sum() / 1000) if df['impressions'].sum() > 0 else 0,
        'conversion_rate': (df['conversions'].sum() / df['clicks'].sum() * 100) if 'conversions' in df.columns and df['clicks'].sum() > 0 else 0,
        'cpa': df['spend'].sum() / df['conversions'].sum() if 'conversions' in df.columns and df['conversions'].sum() > 0 else 0
    }
    return metrics

def create_performance_chart(df, metric):
    """Cria gráfico de linha para métricas ao longo do tempo"""
    fig = px.line(df, x='date', y=metric, color='platform',
                  title=f'Performance de {metric} ao longo do tempo')
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title=metric.capitalize(),
        legend_title="Plataforma",
        template="plotly_white"
    )
    return fig

def create_platform_comparison(df, metric):
    """Cria gráfico de barras comparando plataformas"""
    comparison = df.groupby('platform')[metric].sum().reset_index()
    fig = px.bar(comparison, x='platform', y=metric,
                 title=f'Comparação de {metric} por Plataforma',
                 color='platform')
    fig.update_layout(
        xaxis_title="Plataforma",
        yaxis_title=metric.capitalize(),
        showlegend=False,
        template="plotly_white"
    )
    return fig

def create_campaign_distribution(df):
    """Cria gráfico de pizza mostrando distribuição de investimento por campanha"""
    distribution = df.groupby('campaign_name')['spend'].sum().reset_index()
    fig = px.pie(distribution, values='spend', names='campaign_name',
                 title='Distribuição de Investimento por Campanha')
    fig.update_layout(template="plotly_white")
    return fig

def format_currency(value):
    """Formata valores monetários"""
    return f"R$ {value:,.2f}"

def format_percentage(value):
    """Formata valores percentuais"""
    return f"{value:.2f}%"

def format_number(value):
    """Formata números grandes com separadores de milhar"""
    return f"{int(value):,}"

def export_to_excel(df):
    """Exporta dados para Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    return output.getvalue()

def export_to_pdf(figures, metrics):
    """Exporta dashboard para PDF"""
    pdf = FPDF()
    pdf.add_page()
    
    # Adicionar título
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Relatório de Performance de Anúncios', 0, 1, 'C')
    
    # Adicionar métricas principais
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Período: {metrics['period']}", 0, 1)
    pdf.cell(0, 10, f"Investimento Total: {format_currency(metrics['total_spend'])}", 0, 1)
    pdf.cell(0, 10, f"Total de Cliques: {format_number(metrics['total_clicks'])}", 0, 1)
    pdf.cell(0, 10, f"Total de Conversões: {format_number(metrics['total_conversions'])}", 0, 1)
    
    # Adicionar gráficos
    for fig in figures:
        img_path = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        fig.write_image(img_path)
        pdf.add_page()
        pdf.image(img_path, x=10, y=10, w=190)
        import os
        os.remove(img_path)
    
    output = io.BytesIO()
    pdf.output(output)
    return output.getvalue()

def create_date_filters():
    """Cria filtros de data para o dashboard"""
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Data Inicial",
            datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "Data Final",
            datetime.now()
        )
    return start_date, end_date

def create_platform_filter():
    """Cria filtro de plataforma"""
    return st.multiselect(
        "Plataformas",
        ["Facebook", "Google"],
        ["Facebook", "Google"]
    ) 