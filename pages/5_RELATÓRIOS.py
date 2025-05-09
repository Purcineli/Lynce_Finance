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
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
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
sheet = workbook.get_worksheet(0)
hoje = pd.to_datetime(date.today()) 
lançamentos = sheet.get_all_values()
lançamentos_CONTAS = pd.DataFrame(lançamentos[1:], columns=lançamentos[0])
lançamentos_CONTAS = lançamentos_CONTAS.set_index('ID')
lançamentos_CONTAS = lançamentos_CONTAS[lançamentos_CONTAS["CONCILIADO"]=="TRUE"]
lançamentos_CONTAS = lançamentos_CONTAS[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA']]
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
tabela_contas_cont_ativa = tabela_contas_cont_ativa[['CONTA CONTÁBIL','CATEGORIA', 'ATRIBUIÇÃO']]
tamanho_tabela_contas_cont = len(tabela_contas_cont)+2

#CARTÕES#
lancamento_cartao = workbook.get_worksheet(1)
tabela_lancamentos_cartao = lancamento_cartao.get_all_values()
tabela_lancamentos_cartao = pd.DataFrame(tabela_lancamentos_cartao[1:], columns=tabela_lancamentos_cartao[0])
tabela_lancamentos_cartao = tabela_lancamentos_cartao.set_index('ID')
tabela_lancamentos_cartao.index = tabela_lancamentos_cartao.index.astype(int)
tabela_lancamentos_cartao = tabela_lancamentos_cartao[tabela_lancamentos_cartao["CONCILIADO"]=="TRUE"]
tabela_lancamentos_cartao = tabela_lancamentos_cartao[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA']]
#CONTAS BANCÁRIAS#

lançamentos = pd.concat([lançamentos_CONTAS, tabela_lancamentos_cartao], axis=0)
lançamentos = lançamentos.reset_index()
lançamentos = lançamentos[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA']]




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
  tamanho_tabela = len(lançamentos)
  lançamentos['VALOR'] = (
    lançamentos['VALOR']
    .str.replace('.', '', regex=False)        # Remove separador de milhar
    .str.replace(',', '.', regex=False)       # Converte vírgula decimal para ponto
)
  lançamentos['VALOR'] = pd.to_numeric(lançamentos['VALOR'], errors='coerce')
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(float)
  
  listas_owners = list(lançamentos['PROPRIETÁRIO'].unique())
  lista_prop_selecionado = st.multiselect("Selecione", listas_owners, listas_owners)

  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')
  lançamentos_conciliados = lançamentos.iloc[::-1]

  lançamentos_conciliados = lançamentos_conciliados[(lançamentos_conciliados['DATA']>=data_inicio)&(lançamentos_conciliados['DATA']<=data_final)&(lançamentos_conciliados['PROPRIETÁRIO'].isin(lista_prop_selecionado))]
  #st.dataframe(lançamentos_conciliados[colunas_selecionadas])

  lançamentos_conciliados_receitas = lançamentos_conciliados[lançamentos_conciliados['ANALISE']=="RECEITAS"]

  lançamentos_conciliados_despesas = lançamentos_conciliados[lançamentos_conciliados['ANALISE']=="DESPESAS"]
  lançamentos_conciliados_despesas['VALOR'] = abs(lançamentos_conciliados_despesas['VALOR'])


  fig1 = px.pie(lançamentos_conciliados_receitas, names='CATEGORIA', values='VALOR',color_discrete_sequence=px.colors.sequential.Plasma)
  fig2 = px.pie(lançamentos_conciliados_despesas, names='CATEGORIA', values='VALOR',color_discrete_sequence=px.colors.sequential.RdBu)
  fig2.update_traces(textposition='inside', textinfo='percent')
  fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

  fig3 = px.bar(lançamentos_conciliados_receitas, x='LANÇAMENTO', y='VALOR', color='PROPRIETÁRIO',color_discrete_sequence=px.colors.sequential.Plasma)
  fig4 = px.bar(lançamentos_conciliados_despesas, x='LANÇAMENTO', y='VALOR' ,color='PROPRIETÁRIO',color_discrete_sequence=px.colors.sequential.RdBu)
  fig2.update_traces(textposition='inside', textinfo='percent')
  fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
  col1, col2 = st.columns(2)
  with col1:
    st.markdown(lançamentos_conciliados_receitas['VALOR'].sum())
    st.plotly_chart(fig1, key ='1')
    st.plotly_chart(fig3, key ='2')
  with col2:
    st.markdown(lançamentos_conciliados_despesas['VALOR'].sum())
    st.plotly_chart(fig2, key ='3')
    st.plotly_chart(fig4, key ='4')