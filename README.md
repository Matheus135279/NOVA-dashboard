# Dashboard de Anúncios

Dashboard interativo para visualização de dados de campanhas do Facebook Ads e Google Ads.

## 🚀 Como usar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o dashboard:
```bash
streamlit run app.py
```

3. Para usar com arquivos CSV:
   - Acesse a aba "📥 Upload de Arquivos"
   - Faça upload do seu arquivo CSV do Facebook Ads ou Google Ads
   - O sistema reconhece automaticamente as colunas em português ou inglês

## 📊 Formato dos arquivos CSV

### Facebook Ads
O arquivo deve conter as seguintes colunas (em português ou inglês):
- data/date
- impressões/impressions
- cliques/clicks
- ctr
- cpc
- conversões/conversions
- custo/cost
- valor_conversão/conversion_value
- campanha/campaign (opcional)

### Google Ads
O arquivo deve conter as mesmas colunas, mas preferencialmente em inglês:
- date
- impressions
- clicks
- ctr
- cpc
- conversions
- cost
- conversion_value
- campaign (opcional)

## 📝 Exemplos
Incluímos dois arquivos de exemplo para referência:
- `exemplo_facebook_ads.csv`: Exemplo de dados do Facebook Ads
- `exemplo_google_ads.csv`: Exemplo de dados do Google Ads

## 🔑 Configuração de APIs (Opcional)
Se quiser conectar diretamente com as APIs:
1. Copie o arquivo `.env.example` para `.env`
2. Preencha suas credenciais no arquivo `.env`
3. Acesse a aba "⚙️ Configurações" para configurar as APIs

## 📱 Funcionalidades
- Visualização de KPIs principais
- Gráficos de evolução temporal
- Exportação de relatórios em Excel e PDF
- Suporte a múltiplas campanhas
- Interface responsiva e moderna
- Filtros por data 