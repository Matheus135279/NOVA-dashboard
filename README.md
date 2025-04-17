# Dashboard de Performance de Anúncios

Uma dashboard interativa para análise de performance de campanhas de anúncios do Facebook Ads e Google Ads, construída com Streamlit.

## Funcionalidades

- Visualização de métricas importantes de campanhas publicitárias
- Integração com Facebook Ads e Google Ads
- Suporte para upload manual de arquivos CSV
- Gráficos interativos com Plotly
- Exportação de relatórios em Excel e PDF
- Filtros por data, plataforma e campanha
- Interface responsiva e moderna
- Sistema de autenticação básico

## Requisitos

- Python 3.8+
- Pip (gerenciador de pacotes Python)
- Credenciais de API do Facebook Ads e Google Ads

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd ads_dashboard
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
   - Copie o arquivo `.env.example` para `.env`
   - Preencha as credenciais necessárias no arquivo `.env`

## Configuração das APIs

### Facebook Ads
1. Crie um app no Facebook Developers
2. Obtenha o Access Token com permissões de ads_read
3. Configure as credenciais no arquivo `.env`

### Google Ads
1. Configure uma conta Google Ads API
2. Crie credenciais OAuth 2.0
3. Configure o arquivo `.env` com as credenciais

## Uso

1. Ative o ambiente virtual:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Execute a aplicação:
```bash
streamlit run app.py
```

3. Acesse a dashboard no navegador:
```
http://localhost:8501
```

## Estrutura do Projeto

```
ads_dashboard/
├── app.py              # Aplicação principal Streamlit
├── api_connectors.py   # Conectores para APIs
├── utils.py           # Funções utilitárias
├── requirements.txt   # Dependências do projeto
├── .env.example      # Template de variáveis de ambiente
└── README.md         # Documentação
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para suporte, envie um email para [seu-email@exemplo.com] ou abra uma issue no repositório.