import os
from datetime import datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from google.ads.googleads.client import GoogleAdsClient
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class FacebookAdsConnector:
    def __init__(self):
        self.api = FacebookAdsApi.init(
            access_token=os.getenv('FB_ACCESS_TOKEN'),
            app_id=os.getenv('FB_APP_ID'),
            app_secret=os.getenv('FB_APP_SECRET')
        )
        self.account_id = os.getenv('FB_ACCOUNT_ID')
        self.account = AdAccount(f'act_{self.account_id}')

    def get_insights(self, start_date, end_date):
        try:
            insights = self.account.get_insights(
                params={
                    'level': 'account',
                    'time_range': {
                        'since': start_date.strftime('%Y-%m-%d'),
                        'until': end_date.strftime('%Y-%m-%d')
                    },
                    'fields': [
                        'spend',
                        'impressions',
                        'clicks',
                        'ctr',
                        'cpc',
                        'actions'
                    ]
                }
            )
            
            df = pd.DataFrame(insights)
            return df
        except Exception as e:
            print(f"Erro ao obter dados do Facebook Ads: {str(e)}")
            return pd.DataFrame()

class GoogleAdsConnector:
    def __init__(self):
        self.client = GoogleAdsClient.load_from_env()
        self.customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')

    def get_campaign_stats(self, start_date, end_date):
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.conversions,
                    metrics.cost_micros
                FROM campaign
                WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            """

            response = ga_service.search(
                customer_id=self.customer_id,
                query=query
            )

            rows = []
            for row in response:
                rows.append({
                    'campaign_name': row.campaign.name,
                    'impressions': row.metrics.impressions,
                    'clicks': row.metrics.clicks,
                    'ctr': row.metrics.ctr,
                    'cpc': row.metrics.average_cpc / 1_000_000,  # Convert micros
                    'conversions': row.metrics.conversions,
                    'cost': row.metrics.cost_micros / 1_000_000  # Convert micros
                })

            return pd.DataFrame(rows)
        except Exception as e:
            print(f"Erro ao obter dados do Google Ads: {str(e)}")
            return pd.DataFrame() 