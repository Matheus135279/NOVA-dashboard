import os
from datetime import datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class FacebookAdsConnector:
    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.ad_account_id = os.getenv('FACEBOOK_AD_ACCOUNT_ID')
        
        FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
        self.account = AdAccount(self.ad_account_id)
    
    def get_campaigns_data(self, start_date, end_date):
        try:
            fields = [
                'campaign_name',
                'spend',
                'impressions',
                'clicks',
                'ctr',
                'cpc',
                'cpm',
                'actions',
                'reach',
                'video_p25_watched_actions',
                'video_p50_watched_actions',
                'video_p75_watched_actions',
                'video_p100_watched_actions'
            ]
            
            params = {
                'time_range': {
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                'level': 'campaign'
            }
            
            insights = self.account.get_insights(fields=fields, params=params)
            data = []
            
            for insight in insights:
                campaign_data = {
                    'platform': 'Facebook',
                    'campaign_name': insight['campaign_name'],
                    'spend': float(insight.get('spend', 0)),
                    'impressions': int(insight.get('impressions', 0)),
                    'clicks': int(insight.get('clicks', 0)),
                    'ctr': float(insight.get('ctr', 0)),
                    'cpc': float(insight.get('cpc', 0)),
                    'cpm': float(insight.get('cpm', 0)),
                    'reach': int(insight.get('reach', 0)),
                }
                
                # Processar conversões e ações
                if 'actions' in insight:
                    for action in insight['actions']:
                        if action['action_type'] == 'lead':
                            campaign_data['conversions'] = int(action['value'])
                            break
                
                data.append(campaign_data)
            
            return pd.DataFrame(data)
            
        except Exception as e:
            print(f"Erro ao obter dados do Facebook Ads: {str(e)}")
            return pd.DataFrame()

class GoogleAdsConnector:
    def __init__(self):
        # Configuração específica para resolver o erro do use_proto_plus
        client_config = {
            'use_proto_plus': True,  # Adicionando a configuração necessária
            'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
            'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
            'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
            'login_customer_id': os.getenv('GOOGLE_ADS_CUSTOMER_ID')
        }
        self.client = GoogleAdsClient.load_from_dict(client_config)
        self.customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
    
    def get_campaigns_data(self, start_date, end_date):
        try:
            query = """
                SELECT
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.average_cpc,
                    metrics.ctr,
                    metrics.average_cpm
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            """.format(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=self.customer_id, query=query)
            
            data = []
            for row in response:
                campaign_data = {
                    'platform': 'Google',
                    'campaign_name': row.campaign.name,
                    'spend': row.metrics.cost_micros / 1000000,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'ctr': row.metrics.ctr,
                    'cpc': row.metrics.average_cpc / 1000000,
                    'cpm': row.metrics.average_cpm / 1000000,
                    'conversions': row.metrics.conversions
                }
                data.append(campaign_data)
            
            return pd.DataFrame(data)
            
        except GoogleAdsException as e:
            print(f"Erro ao obter dados do Google Ads: {str(e)}")
            return pd.DataFrame()

def load_csv_data(file_path, platform):
    try:
        df = pd.read_csv(file_path)
        df['platform'] = platform
        return df
    except Exception as e:
        print(f"Erro ao carregar arquivo CSV: {str(e)}")
        return pd.DataFrame()

def process_facebook_csv(file):
    """Processa arquivo CSV do Facebook Ads"""
    try:
        df = pd.read_csv(file)
        required_columns = ['campaign_name', 'spend', 'impressions', 'clicks', 'ctr', 'cpc', 'cpm', 'reach']
        
        # Verifica se as colunas necessárias existem
        if not all(col in df.columns for col in required_columns):
            raise ValueError("O arquivo CSV do Facebook não contém todas as colunas necessárias")
        
        # Adiciona a coluna de plataforma
        df['platform'] = 'Facebook'
        
        # Garante que os tipos de dados estão corretos
        df['spend'] = pd.to_numeric(df['spend'], errors='coerce')
        df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
        df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
        df['ctr'] = pd.to_numeric(df['ctr'], errors='coerce')
        df['cpc'] = pd.to_numeric(df['cpc'], errors='coerce')
        df['cpm'] = pd.to_numeric(df['cpm'], errors='coerce')
        df['reach'] = pd.to_numeric(df['reach'], errors='coerce')
        
        # Adiciona coluna de conversões se existir
        if 'conversions' in df.columns:
            df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce')
        else:
            df['conversions'] = 0
            
        return df
        
    except Exception as e:
        print(f"Erro ao processar arquivo CSV do Facebook: {str(e)}")
        return pd.DataFrame()

def process_google_csv(file):
    """Processa arquivo CSV do Google Ads"""
    try:
        df = pd.read_csv(file)
        required_columns = ['campaign_name', 'cost', 'impressions', 'clicks', 'ctr', 'avg_cpc', 'avg_cpm']
        
        # Verifica se as colunas necessárias existem
        if not all(col in df.columns for col in required_columns):
            raise ValueError("O arquivo CSV do Google Ads não contém todas as colunas necessárias")
        
        # Adiciona a coluna de plataforma
        df['platform'] = 'Google'
        
        # Renomeia colunas para padronizar com o Facebook
        df = df.rename(columns={
            'cost': 'spend',
            'avg_cpc': 'cpc',
            'avg_cpm': 'cpm'
        })
        
        # Garante que os tipos de dados estão corretos
        df['spend'] = pd.to_numeric(df['spend'], errors='coerce')
        df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
        df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
        df['ctr'] = pd.to_numeric(df['ctr'], errors='coerce')
        df['cpc'] = pd.to_numeric(df['cpc'], errors='coerce')
        df['cpm'] = pd.to_numeric(df['cpm'], errors='coerce')
        
        # Adiciona coluna de conversões se existir
        if 'conversions' in df.columns:
            df['conversions'] = pd.to_numeric(df['conversions'], errors='coerce')
        else:
            df['conversions'] = 0
            
        # Adiciona coluna de alcance se existir
        if 'reach' in df.columns:
            df['reach'] = pd.to_numeric(df['reach'], errors='coerce')
        else:
            df['reach'] = df['impressions']  # Usa impressões como aproximação
            
        return df
        
    except Exception as e:
        print(f"Erro ao processar arquivo CSV do Google Ads: {str(e)}")
        return pd.DataFrame() 