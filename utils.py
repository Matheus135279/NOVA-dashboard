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
    try:
        return f"{currency} {float(value):,.2f}"
    except (ValueError, TypeError):
        return f"{currency} 0,00"

def format_number(value, suffix=''):
    """Formata números grandes com K/M/B."""
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.1f}B{suffix}"
        elif value >= 1_000_000:
            return f"{value/1_000_000:.1f}M{suffix}"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K{suffix}"
        return f"{value:.0f}{suffix}"
    except (ValueError, TypeError):
        return f"0{suffix}"

def create_evolution_chart(df, metric, title):
    """Cria gráfico de evolução temporal."""
    # Verifica se as colunas necessárias existem
    if 'date' not in df.columns:
        st.error("❌ A coluna 'date' não foi encontrada no arquivo.")
        return None
        
    if metric not in df.columns:
        st.error(f"❌ A coluna '{metric}' não foi encontrada no arquivo.")
        return None
    
    # Seleciona apenas dados numéricos para o gráfico
    if not pd.api.types.is_numeric_dtype(df[metric]):
        st.error(f"❌ A coluna '{metric}' não contém dados numéricos válidos.")
        return None
    
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
    # Verifica se as colunas necessárias existem
    if dimension not in df.columns:
        st.error(f"❌ A coluna '{dimension}' não foi encontrada no arquivo.")
        return None
        
    if metric not in df.columns:
        st.error(f"❌ A coluna '{metric}' não foi encontrada no arquivo.")
        return None
    
    # Seleciona apenas dados numéricos para o gráfico
    if not pd.api.types.is_numeric_dtype(df[metric]):
        st.error(f"❌ A coluna '{metric}' não contém dados numéricos válidos.")
        return None
    
    # Agrupa os dados
    df_grouped = df.groupby(dimension)[metric].sum().reset_index()
    
    fig = px.bar(
        df_grouped,
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

def safe_dataframe_display(df, linhas=5):
    """
    Exibe DataFrame de forma segura no Streamlit, tratando tipos problemáticos.
    
    Args:
        df (pd.DataFrame): DataFrame a ser exibido
        linhas (int): Número de linhas a mostrar (default: 5)
    """
    try:
        df_copy = df.copy()
        
        # Trata cada coluna baseado em seu tipo
        for col in df_copy.columns:
            # Trata valores nulos primeiro
            df_copy[col] = df_copy[col].fillna('N/A')
            
            # Identifica o tipo da coluna
            dtype = df_copy[col].dtype
            
            # Trata datas
            if pd.api.types.is_datetime64_any_dtype(dtype):
                df_copy[col] = df_copy[col].dt.strftime('%d/%m/%Y')
            
            # Trata números float
            elif pd.api.types.is_float_dtype(dtype):
                df_copy[col] = df_copy[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else 'N/A')
            
            # Trata números inteiros
            elif pd.api.types.is_integer_dtype(dtype):
                df_copy[col] = df_copy[col].apply(lambda x: f"{x:,}" if pd.notnull(x) else 'N/A')
            
            # Trata categorias
            elif dtype.name == 'category':
                df_copy[col] = df_copy[col].astype(str)
            
            # Trata objetos e outros tipos
            else:
                df_copy[col] = df_copy[col].astype(str)
        
        # Exibe o DataFrame
        st.dataframe(df_copy.head(linhas))
        
        # Mostra informações úteis
        st.caption(f"Mostrando {min(linhas, len(df))} de {len(df)} linhas. "
                  f"Total de colunas: {len(df.columns)}")
        
    except Exception as e:
        st.error(f"❌ Erro ao exibir a prévia da tabela: {str(e)}")
        # Log detalhado do erro (opcional)
        st.write("Detalhes do erro:")
        st.write({
            "Tipos das colunas": {col: str(df[col].dtype) for col in df.columns},
            "Erro completo": str(e)
        })

def clean_for_display(df):
    """Limpa o DataFrame para exibição segura no Streamlit."""
    df_clean = df.copy()
    
    for col in df_clean.columns:
        # Trata valores nulos primeiro
        df_clean[col] = df_clean[col].fillna('N/A')
        
        # Converte datas para string no formato brasileiro
        if pd.api.types.is_datetime64_any_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].dt.strftime('%d/%m/%Y')
        
        # Formata números com 2 casas decimais
        elif pd.api.types.is_float_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else 'N/A')
        
        # Formata números inteiros sem decimais
        elif pd.api.types.is_integer_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].apply(lambda x: f"{x:,}" if pd.notnull(x) else 'N/A')
        
        # Converte categorias para string
        elif df_clean[col].dtype.name == 'category':
            df_clean[col] = df_clean[col].astype(str)
        
        # Converte outros tipos para string
        else:
            df_clean[col] = df_clean[col].astype(str)
    
    return df_clean

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
        "início": "start_date",
        "término": "end_date",
        "início dos relatórios": "report_start_date",
        "término dos relatórios": "report_end_date",
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
        "tipo de resultado": "conversion_type",
        "custo por resultado": "cost_per_conversion",
        "valor de conversão": "conversion_value",
        "valor das conversões": "conversion_value",
        "retorno": "conversion_value",
        "impressões": "impressions",
        "visualizações": "impressions",
        "alcance": "impressions",
        "frequência": "frequency",
        "cpm (custo por 1.000 impressões)": "cpm",
        "objetivo": "objective",
        "veiculação da campanha": "campaign_delivery",
        "orçamento da campanha": "campaign_budget",
        "tipo de orçamento da campanha": "campaign_budget_type"
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
    
    # Verifica se as colunas essenciais existem, se não, cria com valores zero
    essential_columns = ['cost', 'clicks', 'impressions', 'conversions', 'conversion_value']
    for col in essential_columns:
        if col not in df_mapped.columns:
            st.warning(f"Arquivo não contém a coluna: {col}")
            df_mapped[col] = 0
    
    def clean_numeric(x):
        """Limpa e converte valores numéricos, tratando casos inválidos de forma segura."""
        try:
            # Verifica valores nulos ou vazios
            if pd.isnull(x) or str(x).strip() in ['', '-', 'nan', 'None']:
                return pd.NA
                
            # Se já for número, converte para float
            if isinstance(x, (int, float)):
                return float(x) if x != float('inf') else pd.NA
                
            # Limpa e formata a string
            value = str(x).strip()
            value = value.replace('R$', '').replace(' ', '')
            
            # Trata formato brasileiro (1.234,56) e outros formatos
            if ',' in value and '.' in value:
                value = value.replace('.', '').replace(',', '.')
            else:
                value = value.replace(',', '.')
            
            # Converte para float
            result = float(value)
            return result if result != float('inf') else pd.NA
            
        except Exception:
            return pd.NA

    def clean_percentage(x):
        """Limpa e converte valores percentuais, tratando casos inválidos."""
        if pd.isna(x) or x == '' or x == '-':
            return pd.NA
        try:
            # Remove % e espaços
            value = str(x).strip().rstrip('%')
            # Converte para decimal
            result = float(value.replace(',', '.')) / 100
            return result if result != float('inf') else pd.NA
        except (ValueError, TypeError):
            return pd.NA
    
    # Trata valores numéricos
    numeric_columns = ['cost', 'clicks', 'impressions', 'conversions', 'conversion_value']
    for col in numeric_columns:
        if col in df_mapped.columns:
            df_mapped[col] = df_mapped[col].apply(clean_numeric)
            # Substitui NA por 0 para cálculos
            df_mapped[col] = df_mapped[col].fillna(0)
    
    # Trata percentuais
    percentage_columns = ['ctr']
    for col in percentage_columns:
        if col in df_mapped.columns:
            df_mapped[col] = df_mapped[col].apply(clean_percentage)
            # Substitui NA por 0 para cálculos
            df_mapped[col] = df_mapped[col].fillna(0)
    
    # Trata datas
    if 'date' in df_mapped.columns:
        try:
            # Primeiro tenta formato padrão
            df_mapped['date'] = pd.to_datetime(df_mapped['date'])
        except:
            try:
                # Tenta formato brasileiro
                df_mapped['date'] = pd.to_datetime(df_mapped['date'].str.strip(), format='%d/%m/%Y')
            except:
                try:
                    # Tenta outros formatos comuns
                    df_mapped['date'] = pd.to_datetime(df_mapped['date'].str.strip(), format='%Y-%m-%d')
                except:
                    st.warning("⚠️ Não foi possível converter a coluna de data automaticamente.")
                    return None
        
        # Converte para date após sucesso na conversão
        df_mapped['date'] = df_mapped['date'].dt.date
    
    # Trata outras colunas de data
    date_columns = ['start_date', 'end_date', 'report_start_date', 'report_end_date']
    for date_col in date_columns:
        if date_col in df_mapped.columns:
            try:
                df_mapped[date_col] = pd.to_datetime(df_mapped[date_col])
            except:
                try:
                    df_mapped[date_col] = pd.to_datetime(df_mapped[date_col].str.strip(), format='%d/%m/%Y')
                except:
                    st.warning(f"⚠️ Não foi possível converter a coluna {date_col} para data.")
    
    return df_mapped

def calculate_kpis(df):
    """Calcula KPIs principais."""
    kpis = {}
    
    # Verifica se temos a coluna campaign
    if 'campaign' not in df.columns:
        st.error("❌ A coluna 'campaign' não foi encontrada no arquivo.")
        return kpis
    
    # Seleciona apenas colunas numéricas para agregação
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    metrics_to_sum = [col for col in numeric_columns if col != 'date']
    
    # Agrupa por campanha apenas as métricas numéricas
    if metrics_to_sum:
        df_grouped = df.groupby('campaign')[metrics_to_sum].sum().reset_index()
    else:
        st.warning("⚠️ Nenhuma coluna numérica encontrada para agregação.")
        return kpis
    
    # Calcula KPIs com verificação de existência das colunas
    if 'impressions' in df_grouped.columns:
        kpis['Impressões'] = df_grouped['impressions'].sum()
    else:
        kpis['Impressões'] = 0
        
    if 'clicks' in df_grouped.columns:
        kpis['Cliques'] = df_grouped['clicks'].sum()
    else:
        kpis['Cliques'] = 0
        
    if all(col in df_grouped.columns for col in ['clicks', 'impressions']) and df_grouped['impressions'].sum() > 0:
        kpis['CTR'] = (df_grouped['clicks'].sum() / df_grouped['impressions'].sum() * 100)
    else:
        kpis['CTR'] = 0
        
    if all(col in df_grouped.columns for col in ['cost', 'clicks']) and df_grouped['clicks'].sum() > 0:
        kpis['CPC Médio'] = df_grouped['cost'].sum() / df_grouped['clicks'].sum()
    else:
        kpis['CPC Médio'] = 0
        
    if 'conversions' in df_grouped.columns:
        kpis['Conversões'] = df_grouped['conversions'].sum()
    else:
        kpis['Conversões'] = 0
        
    if 'cost' in df_grouped.columns:
        kpis['Custo Total'] = df_grouped['cost'].sum()
    else:
        kpis['Custo Total'] = 0
        
    if all(col in df_grouped.columns for col in ['conversion_value', 'cost']) and df_grouped['cost'].sum() > 0:
        kpis['ROAS'] = df_grouped['conversion_value'].sum() / df_grouped['cost'].sum()
    else:
        kpis['ROAS'] = 0
        
    # Adiciona métricas adicionais se disponíveis
    if 'frequency' in df_grouped.columns:
        kpis['Frequência Média'] = df_grouped['frequency'].mean()
        
    if 'cpm' in df_grouped.columns:
        kpis['CPM Médio'] = df_grouped['cpm'].mean()
        
    if 'cost_per_conversion' in df_grouped.columns and df_grouped['cost_per_conversion'].sum() > 0:
        kpis['Custo por Conversão Médio'] = df_grouped['cost_per_conversion'].mean()
    
    return kpis 