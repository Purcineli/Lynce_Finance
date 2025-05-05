import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import plotly.express as px
import numpy as np
import math
from LYNCE import verificar_login\

st.set_page_config(layout="wide")

st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Você precisa fazer login primeiro.")
    st.stop()

# Agora é seguro acessar os valores da sessão
st.write(f"Bem-vindo, {st.session_state.name}!")
sheeitid = st.session_state.id
sheetname = st.session_state.arquivo

def lerdados(sheet_id_login_password,sheet_name_login_password):

  scopes = ["https://www.googleapis.com/auth/spreadsheets"]
  service_account_info = st.secrets["gcp_service_account"]
  creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
  #creds = Credentials.from_service_account_file(r"C:\Users\alepu\OneDrive\Área de Trabalho\Python_projects\CONTROLE_FINANCEIRO\credentials.json", scopes=scopes)
  #D:\Python_projects\CONTROLE_FINANCEIRO
  client = gspread.authorize(creds)


  workbook = client.open_by_key(sheet_id_login_password)
  
  
  url = f"https://docs.google.com/spreadsheets/d/{sheet_id_login_password}/gviz/tq?tqx=out:csv&sheet={sheet_name_login_password}"

  dados_records = pd.read_csv(url, decimal='.', index_col=False)

  return dados_records,workbook


#sheeitid = '1mR63AgJd3tW4slEywlcylKCtEzAgcT2icHwOhUr6mdk'
#sheetname = "records"
lançamentos, workbook = lerdados(sheeitid, sheetname)
sheet1 = workbook.get_worksheet(1)
contas_cadastradas1 = sheet1.get_all_values()
sheet = workbook.get_worksheet(0)
contas_cadastradas = pd.DataFrame(contas_cadastradas1[1:], columns=contas_cadastradas1[0])
hoje = pd.to_datetime(date.today()) 

#CONTAS BANCÁRIAS#
conta_banco_cadastradas = workbook.get_worksheet(2)
tabela_contas_banco = conta_banco_cadastradas.get_all_values()
tabela_contas_banco = pd.DataFrame(tabela_contas_banco[1:], columns=tabela_contas_banco[0])
tabela_contas_banco = tabela_contas_banco.set_index('ID')
tabela_contas_banco_ativa = tabela_contas_banco[tabela_contas_banco['ATIVO']=='TRUE']
tabela_contas_banco_ativa = tabela_contas_banco_ativa[['NOME BANCO','PROPRIETÁRIO']]
tamanho_tabela_contas_banco = len(tabela_contas_banco)+2
#CONTAS CONTÁBEIS#
conta_cont_cadastradas = workbook.get_worksheet(3)
tabela_contas_cont = conta_cont_cadastradas.get_all_values()
tabela_contas_cont = pd.DataFrame(tabela_contas_cont[1:], columns=tabela_contas_cont[0])
tabela_contas_cont = tabela_contas_cont.set_index('ID')
tabela_contas_cont_ativa = tabela_contas_cont[tabela_contas_cont['ATIVO']=='TRUE']
tabela_contas_cont_ativa = tabela_contas_cont_ativa[['CONTA CONTÁBIL','CATEGORIA','ATRIBUIÇÃO']]
tamanho_tabela_contas_cont = len(tabela_contas_cont)+2



st.divider()

col01, col02 = st.columns(2)
with col01:
  data_inicio = st.date_input("Data Inicial", date.today() - timedelta(days=30))
  data_inicio = pd.to_datetime(data_inicio)
with col02:
  data_final = st.date_input("Data Final", date.today())
  data_final = pd.to_datetime(data_final)

tamanho_tabela = len(lançamentos)
if tamanho_tabela==1:
   st.write("SEM LANÇAMENTOS")
else:
  maxid = lançamentos['ID'].max()

  lançamentos['BANCO'] = lançamentos['BANCO'].str.upper()
  tamanho_tabela = len(lançamentos)
  lançamentos['VALOR'] = lançamentos['VALOR'].str.replace('.', '', regex=False)  # remove pontos de milhar se houver
  lançamentos['VALOR'] = lançamentos['VALOR'].str.replace(',', '.', regex=False)  # troca vírgula por ponto
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(float)
  lançamentos = lançamentos.set_index('ID')

  listas_owners = list(lançamentos['PROPRIETÁRIO'].unique())
  lista_prop_selecionado = st.multiselect("Selecione", listas_owners, listas_owners)


  lançamentos = lançamentos[lançamentos['BANCO'].notna()]
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')
  lançamentos_conciliados = lançamentos[lançamentos['CONCILIADO']==True]
  lançamentos_conciliados = lançamentos_conciliados.iloc[::-1]

  lançamentos_conciliados = lançamentos_conciliados[(lançamentos_conciliados['DATA']>=data_inicio)&(lançamentos_conciliados['DATA']<=data_final)&(lançamentos_conciliados['PROPRIETÁRIO'].isin(lista_prop_selecionado))]
  #st.dataframe(lançamentos_conciliados[colunas_selecionadas])

  lançamentos_conciliados_receitas = lançamentos_conciliados[lançamentos_conciliados['ANALISE']=="RECEITAS"]

  lançamentos_conciliados_despesas = lançamentos_conciliados[lançamentos_conciliados['ANALISE']=="DESPESAS"]
  lançamentos_conciliados_despesas['VALOR'] = lançamentos_conciliados_despesas['VALOR'] * -1


  fig1 = px.pie(lançamentos_conciliados_receitas, names='CATEGORIA', values='VALOR')
  fig2 = px.pie(lançamentos_conciliados_despesas, names='CATEGORIA', values='VALOR')
  fig2.update_traces(textposition='inside', textinfo='percent')
  fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

  fig3 = px.bar(lançamentos_conciliados_receitas, x='LANÇAMENTO', y='VALOR', color='PROPRIETÁRIO')
  fig4 = px.bar(lançamentos_conciliados_despesas, x='LANÇAMENTO', y='VALOR' ,color='PROPRIETÁRIO')
  fig2.update_traces(textposition='inside', textinfo='percent')
  fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
  col1, col2 = st.columns(2)
  with col1:
    st.markdown(lançamentos_conciliados_receitas['VALOR'].sum())
    st.plotly_chart(fig1)
    st.plotly_chart(fig3)
  with col2:
    st.markdown(lançamentos_conciliados_despesas['VALOR'].sum())
    st.plotly_chart(fig2)
    st.plotly_chart(fig4)