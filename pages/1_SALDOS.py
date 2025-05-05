import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta
import plotly.express as px
import numpy as np
import json
from LYNCE import verificar_login

st.set_page_config(layout="wide")
st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
#col1,col2,col3 = st.columns(3)
#with col2:
  #st.image('https://i.postimg.cc/yxJnfSLs/logo-lynce.png',)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.write("Você precisa fazer [login](https://lyncefinanceiro.streamlit.app/) primeiro ")
    st.warning("Você precisa fazer login primeiro.")
    st.page_link("http://www.google.com", label="Google", icon="🌎")
    st.stop()

# Agora é seguro acessar os valores da sessão
st.write(f"Bem-vindo, {st.session_state.name}!")
sheeitid = st.session_state.id
sheetname = st.session_state.arquivo


#ler dados do google sheet
def lerdados(sheet_id_login_password,sheet_name_login_password):

  scopes = ["https://www.googleapis.com/auth/spreadsheets"]
  service_account_info = st.secrets["gcp_service_account"]
  creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
  #creds = Credentials.from_service_account_file(r"C:\Users\alepu\OneDrive\Área de Trabalho\Python_projects\CONTROLE_FINANCEIRO\credentials.json", scopes=scopes)
  client = gspread.authorize(creds)
  workbook = client.open_by_key(sheet_id_login_password)
  url = f"https://docs.google.com/spreadsheets/d/{sheet_id_login_password}/gviz/tq?tqx=out:csv&sheet={sheet_name_login_password}"
  dados_records = pd.read_csv(url, decimal='.')
  return dados_records

#informe o id e name da arquivo google sheets


lançamentos = lerdados(sheeitid, sheetname)  # Ler a tabela de lançamentos do Google Sheets
lançamentos = lançamentos.set_index('ID')  # Definir a coluna 'ID' como índice do DataFrame
if len(lançamentos)==1:
  st.write("Sem lançamentos")
else:
  lançamentos['BANCO'] = lançamentos['BANCO'].str.upper()  # Transformar nomes dos bancos para maiúsculas
  lançamentos['VALOR'] = lançamentos['VALOR'].str.replace('.', '', regex=False)  # Remover pontos de milhar
  lançamentos['VALOR'] = lançamentos['VALOR'].str.replace(',', '.', regex=False)  # Trocar vírgula por ponto decimal
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(float)  # Converter 'VALOR' de texto para float
  lançamentos = lançamentos[lançamentos['CONCILIADO'] == True]  # Filtrar apenas registros conciliados
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')  # Converter 'DATA' para datetime (dia/mês/ano)

  contas = list(lançamentos['BANCO'].dropna().unique())  # Lista de bancos únicos, ignorando valores nulos
  users = list(lançamentos['PROPRIETÁRIO'].dropna().unique())  # Lista de proprietários únicos, ignorando valores nulos



  col01, col02, col03 = st.columns([0.1, 0.1, 0.8])  # Define layout de 3 colunas com larguras proporcionais
  with col01:
    data_saldo = pd.to_datetime(st.date_input("Data Saldo", date.today(),format="DD/MM/YYYY"))  # Input de data para filtrar os saldos
    df_saldos_user = lançamentos[lançamentos['DATA'] <= data_saldo]  # Filtra lançamentos com data menor ou igual à selecionada
    #st.markdown(f'SALDO TOTAL: R$ {df_saldos_user['VALOR'].sum().round(2)}')
    st.markdown(f"SALDO TOTAL: R$ {df_saldos_user['VALOR'].sum().round(2):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
  st.divider()  # Linha divisória no app

  col011, col012 = st.columns([0.2, 0.8])  # Define nova linha com duas colunas
  with col011:
    filtro1 = st.toggle("Filtar por usuário")  # Botão liga/desliga para aplicar filtro por usuário
    users_selecionado = st.selectbox("Selecione um proprietário", users)  # Seleção do proprietário (usuário)



  df_saldos_user = df_saldos_user.groupby(['PROPRIETÁRIO', 'BANCO']).agg({'VALOR': 'sum'}).round(2)  # Agrupa e soma valores por proprietário e banco
  df_saldos_user = df_saldos_user[df_saldos_user['VALOR'] != 0]  # Remove registros com valor igual a zero
  df_saldos_user = df_saldos_user.sort_values(by='VALOR', ascending=False)  # Ordena pelo valor em ordem decrescente
  df_saldos_user = df_saldos_user.reset_index()  # Reseta o índice para transformar os agrupamentos em colunas normais
  df_saldos_user_filtrado = df_saldos_user[df_saldos_user['PROPRIETÁRIO'] == users_selecionado]  # Aplica filtro pelo usuário selecionado


  # Calcular o acumulado
  lançamentos2 = lançamentos[['DATA','PROPRIETÁRIO', 'VALOR']]
  lançamentos2['ACUMULADO'] = lançamentos2.groupby('PROPRIETÁRIO')['VALOR'].cumsum()
  lançamentos['ACUMULADO'] = lançamentos.groupby(['BANCO', 'PROPRIETÁRIO'])['VALOR'].cumsum()
  lançamentos = lançamentos[['DATA','BANCO','PROPRIETÁRIO','ACUMULADO']]
  lançamentos['ACUMULADO'] = lançamentos['ACUMULADO'].round(2)
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'])
  lançamentos_filtrado = lançamentos[lançamentos['PROPRIETÁRIO'] == users_selecionado] 

  resultado_mensal = (
      lançamentos2
      .set_index('DATA')
      .groupby('PROPRIETÁRIO')['ACUMULADO']
      .resample('ME')
      .last()
      .reset_index()
  )

  resultado_mensal2 = (
      lançamentos_filtrado
      .set_index('DATA')
      .groupby(['BANCO', 'PROPRIETÁRIO'])['ACUMULADO']
      .resample('ME')
      .last()
      .reset_index()
  )


  if filtro1:
    fig1 = px.pie(df_saldos_user_filtrado, names='BANCO', values='VALOR')  # Gráfico de pizza com saldos filtrados
    fig2 = px.bar(df_saldos_user_filtrado, x='BANCO', y='VALOR', color='PROPRIETÁRIO', text_auto=True)  # Gráfico de barras com saldos filtrados
    fig3 = px.line(resultado_mensal2, x="DATA", y="ACUMULADO", color='BANCO', title='Saldo acumulado no fim de cada mês', markers=False)
    fig3.update_xaxes(tickformat="%m/%Y")
  else:
    fig1 = px.pie(df_saldos_user, names='BANCO', values='VALOR')  # Gráfico de pizza com todos os dados
    fig2 = px.bar(df_saldos_user, x='BANCO', y='VALOR', color='PROPRIETÁRIO', text_auto=True)  # Gráfico de barras com todos os dados
    fig3 = px.line(resultado_mensal, x="DATA", y="ACUMULADO", color='PROPRIETÁRIO', title='Saldo acumulado no fim de cada mês', markers=False)
    fig3.update_xaxes(tickformat="%m/%Y")

  col11, col12, col13 = st.columns(3)  # Layout de três colunas para exibir tabelas e gráficos

  with col11:
    st.write("Saldos bancários")  # Título da tabela
    if filtro1:
      saldototalperprop = df_saldos_user_filtrado['VALOR'].sum().round(2)
      df_saldos_user_filtrado['VALOR'] = df_saldos_user_filtrado['VALOR'].apply(lambda x: f"{x:.2f}")
      st.write(df_saldos_user_filtrado)  # Exibe tabela filtrada
      st.markdown(f"SALDO TOTAL: R$ {saldototalperprop:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
      
    else:
      df_saldos_user_total = df_saldos_user.groupby(['PROPRIETÁRIO']).agg({'VALOR': 'sum'}).round(2)  # Exibe tabela completa
      df_saldos_user_total = df_saldos_user_total.sort_values(by='VALOR', ascending=False)
      df_saldos_user_total['VALOR'] = df_saldos_user_total['VALOR'].apply(lambda x: f"{x:.2f}")
      df_saldos_user_total = df_saldos_user_total.reset_index()
      st.write(df_saldos_user_total)
      st.markdown(f'SALDO TOTAL: R$ {df_saldos_user['VALOR'].sum().round(2)}')
  with col12:
    st.plotly_chart(fig1)  # Exibe gráfico de pizza
  with col13:
    st.plotly_chart(fig2)  # Exibe gráfico de barras

  st.divider()  # Linha divisória no app





  st.plotly_chart(fig3)