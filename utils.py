import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import streamlit as st
from datetime import datetime
import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import tempfile

def format_currency(value, currency='R$'):
    """Formata valores monetários."""
    return f"{currency} {value:,.2f}"

def format_number(value, suffix=''):
    """Formata números grandes com K/M/B."""
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B{suffix}"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.1f}M{suffix}"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K{suffix}"
    return f"{value:.0f}{suffix}"

def create_evolution_chart(df, metric, title):
    """Cria gráfico de evolução temporal."""
    fig = px.line(
        df,
        x='date',
        y=metric,
        title=title,
        template='plotly_dark'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    
    return fig

def create_comparison_chart(df, metric, dimension, title):
    """Cria gráfico de comparação entre dimensões."""
    fig = px.bar(
        df,
        x=dimension,
        y=metric,
        title=title,
        template='plotly_dark'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    
    return fig

def export_to_excel(df, filename):
    """Exporta dados para Excel com formatação."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Dashboard"
    
    # Adiciona cabeçalho
    headers = list(df.columns)
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)
    
    # Adiciona dados
    for row, data in enumerate(df.values, 2):
        for col, value in enumerate(data, 1):
            ws.cell(row=row, column=col, value=value)
    
    # Salva arquivo
    wb.save(filename)

def export_to_pdf(df, charts, filename):
    """Exporta relatório em PDF com dados e gráficos."""
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Relatório de Performance', 0, 1, 'C')
    pdf.ln(10)
    
    # Dados resumidos
    pdf.set_font('Arial', '', 12)
    for col in df.columns:
        value = df[col].iloc[-1]
        pdf.cell(0, 10, f'{col}: {value}', 0, 1)
    
    # Gráficos
    for chart in charts:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            chart.write_image(tmp.name)
            pdf.add_page()
            pdf.image(tmp.name, x=10, y=10, w=190)
            os.unlink(tmp.name)
    
    pdf.output(filename)

def map_csv_columns(df):
    """Mapeia colunas do CSV para nomes padronizados."""
    column_mapping = {
        # Português
        'data': 'date',
        'impressões': 'impressions',
        'cliques': 'clicks',
        'ctr': 'ctr',
        'cpc': 'cpc',
        'conversões': 'conversions',
        'custo': 'cost',
        'valor_conversão': 'conversion_value',
        
        # Inglês
        'date': 'date',
        'impressions': 'impressions',
        'clicks': 'clicks',
        'ctr': 'ctr',
        'cpc': 'cpc',
        'conversions': 'conversions',
        'cost': 'cost',
        'conversion_value': 'conversion_value'
    }
    
    # Tenta mapear cada coluna
    mapped_columns = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower in column_mapping:
            mapped_columns[col] = column_mapping[col_lower]
    
    return df.rename(columns=mapped_columns)

def calculate_kpis(df):
    """Calcula KPIs principais."""
    kpis = {
        'Impressões': df['impressions'].sum(),
        'Cliques': df['clicks'].sum(),
        'CTR': (df['clicks'].sum() / df['impressions'].sum() * 100),
        'CPC Médio': df['cost'].sum() / df['clicks'].sum(),
        'Conversões': df['conversions'].sum(),
        'Custo Total': df['cost'].sum(),
        'ROAS': df['conversion_value'].sum() / df['cost'].sum()
    }
    return kpis 