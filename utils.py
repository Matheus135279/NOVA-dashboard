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
        # Mapeamento Facebook Ads
        "nome da campanha": "campaign",
        "nome do conjunto de anúncios": "campaign",
        "campanha": "campaign",
        "valor usado (brl)": "cost",
        "custo": "cost",
        "valor gasto": "cost",
        "dia": "date",
        "data": "date",
        "data do relatório": "date",
        "cliques no link": "clicks",
        "cliques": "clicks",
        "cliques totais": "clicks",
        "cpc (custo por clique no link)": "cpc",
        "cpc": "cpc",
        "custo por clique": "cpc",
        "ctr (taxa de cliques no link)": "ctr",
        "ctr": "ctr",
        "taxa de cliques": "ctr",
        "resultados": "conversions",
        "conversões": "conversions",
        "ações": "conversions",
        "valor de conversão": "conversion_value",
        "valor das conversões": "conversion_value",
        "retorno": "conversion_value",
        "impressões": "impressions",
        "visualizações": "impressions",
        "alcance": "impressions"
    }
    
    # Tenta mapear cada coluna
    mapped_columns = {}
    missing_columns = []
    
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower in column_mapping:
            mapped_columns[col] = column_mapping[col_lower]
        else:
            missing_columns.append(col)
    
    # Se encontrou colunas não mapeadas, exibe aviso
    if missing_columns:
        st.warning(f"⚠️ As seguintes colunas não foram mapeadas e serão mantidas como estão: {', '.join(missing_columns)}")
    
    # Aplica o mapeamento
    df_mapped = df.rename(columns=mapped_columns)
    
    # Função auxiliar para limpar e converter valores numéricos
    def clean_numeric(value):
        if pd.isna(value):
            return 0
        if isinstance(value, (int, float)):
            return value
        try:
            # Remove caracteres não numéricos exceto ponto e vírgula
            value_str = str(value).strip()
            value_str = value_str.replace('R$', '').replace(' ', '')
            if ',' in value_str and '.' in value_str:
                # Caso brasileiro: 1.234,56
                value_str = value_str.replace('.', '').replace(',', '.')
            else:
                # Caso americano ou vírgula como separador
                value_str = value_str.replace(',', '.')
            return float(value_str)
        except:
            return 0

    # Trata valores numéricos
    numeric_columns = ['cost', 'clicks', 'impressions', 'conversions', 'conversion_value']
    for col in numeric_columns:
        if col in df_mapped.columns:
            df_mapped[col] = df_mapped[col].apply(clean_numeric)
    
    # Trata percentuais
    def clean_percentage(value):
        if pd.isna(value):
            return 0
        try:
            value_str = str(value).strip().rstrip('%')
            return float(value_str.replace(',', '.')) / 100
        except:
            return 0
    
    percentage_columns = ['ctr']
    for col in percentage_columns:
        if col in df_mapped.columns:
            df_mapped[col] = df_mapped[col].apply(clean_percentage)
    
    # Trata datas
    if 'date' in df_mapped.columns:
        try:
            df_mapped['date'] = pd.to_datetime(df_mapped['date']).dt.date
        except:
            try:
                # Tenta formato brasileiro
                df_mapped['date'] = pd.to_datetime(df_mapped['date'], format='%d/%m/%Y').dt.date
            except:
                st.warning("⚠️ Não foi possível converter a coluna de data automaticamente.")
    
    return df_mapped

def calculate_kpis(df):
    """Calcula KPIs principais."""
    kpis = {}
    
    # Verifica cada métrica antes de calcular
    if 'impressions' in df.columns:
        kpis['Impressões'] = df['impressions'].sum()
    else:
        kpis['Impressões'] = 0
        
    if 'clicks' in df.columns:
        kpis['Cliques'] = df['clicks'].sum()
    else:
        kpis['Cliques'] = 0
        
    if 'clicks' in df.columns and 'impressions' in df.columns and df['impressions'].sum() > 0:
        kpis['CTR'] = (df['clicks'].sum() / df['impressions'].sum() * 100)
    else:
        kpis['CTR'] = 0
        
    if 'cost' in df.columns and 'clicks' in df.columns and df['clicks'].sum() > 0:
        kpis['CPC Médio'] = df['cost'].sum() / df['clicks'].sum()
    else:
        kpis['CPC Médio'] = 0
        
    if 'conversions' in df.columns:
        kpis['Conversões'] = df['conversions'].sum()
    else:
        kpis['Conversões'] = 0
        
    if 'cost' in df.columns:
        kpis['Custo Total'] = df['cost'].sum()
    else:
        kpis['Custo Total'] = 0
        
    if 'conversion_value' in df.columns and 'cost' in df.columns and df['cost'].sum() > 0:
        kpis['ROAS'] = df['conversion_value'].sum() / df['cost'].sum()
    else:
        kpis['ROAS'] = 0
        
    return kpis 