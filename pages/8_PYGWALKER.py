import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import plotly.express as px
import numpy as np
import math
from LYNCE import verificar_login
from TRADUTOR import traaducaoapp
from shared_components import create_sidebar_navigation
from dateutil.relativedelta import relativedelta
import openai
import io
import time
import pygwalker as pyg
from pygwalker.api.streamlit import init_streamlit_comm, get_streamlit_html


st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.stop()



# Create sidebar navigation and get translated texts
textos, _ = create_sidebar_navigation()

# Welcome section
bemvido, x, language = st.columns([0.3,0.5,0.2], vertical_alignment='bottom')

with bemvido:
  st.write(f"{textos['BEMVINDO']} {st.session_state.name}!")

sheeitid = st.session_state.id
sheetname = st.session_state.arquivo

def lerdados(sheet_id_login_password,sheet_name_login_password):

  scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive'
]
  service_account_info = st.secrets["gcp_service_account"]
  creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
  client = gspread.authorize(creds)


  workbook = client.open_by_key(sheet_id_login_password)
  
  
  url = f"https://docs.google.com/spreadsheets/d/{sheet_id_login_password}/gviz/tq?tqx=out:csv&sheet={sheet_name_login_password}"

  dados_records = pd.read_csv(url, decimal='.', index_col=False)

  return dados_records,workbook



lançamentos, workbook = lerdados(sheeitid, sheetname)
sheet = workbook.get_worksheet(0)
hoje = pd.to_datetime(date.today()) 
lançamentos = sheet.get_all_values()
lançamentos_CONTAS = pd.DataFrame(lançamentos[1:], columns=lançamentos[0])
lançamentos_CONTAS = lançamentos_CONTAS.set_index('ID')
lançamentos_CONTAS = lançamentos_CONTAS[lançamentos_CONTAS["ANALISE"]!="ANALÍTICA"]
lançamentos_CONTAS = lançamentos_CONTAS[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]

#CARTÕES#
lancamento_cartao = workbook.get_worksheet(1)
tabela_lancamentos_cartao = lancamento_cartao.get_all_values()
tabela_lancamentos_cartao = pd.DataFrame(tabela_lancamentos_cartao[1:], columns=tabela_lancamentos_cartao[0])
tabela_lancamentos_cartao = tabela_lancamentos_cartao.set_index('ID')
tabela_lancamentos_cartao.index = tabela_lancamentos_cartao.index.astype(int)
tabela_lancamentos_cartao = tabela_lancamentos_cartao[tabela_lancamentos_cartao["ANALISE"]!="ANALÍTICA"]
tabela_lancamentos_cartao = tabela_lancamentos_cartao[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]




lançamentos = pd.concat([lançamentos_CONTAS, tabela_lancamentos_cartao], axis=0)

lançamentos = lançamentos.reset_index()
lançamentos = lançamentos[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]


sheetia = workbook.get_worksheet(6)

# Data preprocessing for Pygwalker
if len(lançamentos) > 0:
    # Convert data types for better analysis
    lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')
    lançamentos['VALOR'] = pd.to_numeric(lançamentos['VALOR'], errors='coerce')
    
    # Clean and prepare data
    lançamentos_clean = lançamentos.copy()
    lançamentos_clean = lançamentos_clean.dropna(subset=['VALOR'])
    
    # Add some useful derived columns
    lançamentos_clean['MÊS'] = lançamentos_clean['DATA'].dt.month
    lançamentos_clean['ANO'] = lançamentos_clean['DATA'].dt.year
    lançamentos_clean['DIA_SEMANA'] = lançamentos_clean['DATA'].dt.day_name()
    lançamentos_clean['TIPO'] = lançamentos_clean['ANALISE'].map({'RECEITAS': 'Receita', 'DESPESAS': 'Despesa'})
    
    # Main title
    st.title("📊 Análise Interativa de Dados Financeiros")
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filtros")
    
    # Date range filter
    if not lançamentos_clean['DATA'].isna().all():
        min_date = lançamentos_clean['DATA'].min()
        max_date = lançamentos_clean['DATA'].max()
        
        date_range = st.sidebar.date_input(
            "Período de Análise",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            lançamentos_filtered = lançamentos_clean[
                (lançamentos_clean['DATA'].dt.date >= start_date) &
                (lançamentos_clean['DATA'].dt.date <= end_date)
            ]
        else:
            lançamentos_filtered = lançamentos_clean
    else:
        lançamentos_filtered = lançamentos_clean
    
    # Proprietário filter
    proprietarios = ['Todos'] + list(lançamentos_filtered['PROPRIETÁRIO'].unique())
    proprietario_selecionado = st.sidebar.selectbox("Proprietário", proprietarios)
    
    if proprietario_selecionado != 'Todos':
        lançamentos_filtered = lançamentos_filtered[lançamentos_filtered['PROPRIETÁRIO'] == proprietario_selecionado]
    
    # Tipo filter
    tipos = ['Todos'] + list(lançamentos_filtered['TIPO'].unique())
    tipo_selecionado = st.sidebar.selectbox("Tipo", tipos)
    
    if tipo_selecionado != 'Todos':
        lançamentos_filtered = lançamentos_filtered[lançamentos_filtered['TIPO'] == tipo_selecionado]
    
    # Show data summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", len(lançamentos_filtered))
    
    with col2:
        total_receitas = lançamentos_filtered[lançamentos_filtered['TIPO'] == 'Receita']['VALOR'].sum()
        st.metric("Total Receitas", f"R$ {total_receitas:,.2f}")
    
    with col3:
        total_despesas = lançamentos_filtered[lançamentos_filtered['TIPO'] == 'Despesa']['VALOR'].sum()
        st.metric("Total Despesas", f"R$ {total_despesas:,.2f}")
    
    with col4:
        saldo = total_receitas - total_despesas
        st.metric("Saldo", f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}")
    
    st.markdown("---")
    
    # Pygwalker integration
    st.header("🎯 Análise Interativa com Pygwalker")
    st.markdown("""
    **Como usar:**
    - Arraste campos para criar visualizações
    - Clique nos gráficos para interagir
    - Use filtros para explorar os dados
    - Exporte gráficos e insights
    """)
    
    # Initialize Pygwalker
    @st.cache_data
    def load_data():
        return lançamentos_filtered
    
    df = load_data()
    
    # Initialize Streamlit communication for Pygwalker
    init_streamlit_comm()
    
    # Create Pygwalker HTML
    html = get_streamlit_html(df, spec="./gw_config.json", debug=False)
    
    # Display Pygwalker interface
    st.components.v1.html(html, height=600, scrolling=True)
    
    # Download button for filtered data
    st.markdown("---")
    st.subheader("📥 Exportar Dados")
    
    csv = lançamentos_filtered.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📊 Download CSV",
        data=csv,
        file_name=f"dados_financeiros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Show raw data
    with st.expander("📋 Ver Dados Brutos"):
        st.dataframe(lançamentos_filtered, use_container_width=True)
        
else:
    st.warning("Nenhum dado encontrado para análise.")
    st.info("Adicione alguns lançamentos financeiros para começar a usar o Pygwalker.")
