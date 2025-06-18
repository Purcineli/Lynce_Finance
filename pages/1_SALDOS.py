import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import plotly.express as px
import numpy as np
import json
from LYNCE import verificar_login, verificar_login_cookie_ou_session, logout
from cookies_manager import cookies
from gspread.exceptions import APIError
import time
from TRADUTOR import traaducaoapp
from streamlit_cookies_manager import EncryptedCookieManager
st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
#col1,col2,col3 = st.columns(3)
#with col2:
  #st.image('https://i.postimg.cc/yxJnfSLs/logo-lynce.png',)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.stop()

language_of_page = st.session_state.useridioma

verificar_login_cookie_ou_session()

idiomadasdisponiveis = ['PORTUGUÊS', 'ENGLISH', 'РУССКИЙ']
idxidioma = idiomadasdisponiveis.index(language_of_page)
# Agora é seguro acessar os valores da sessão
bemvido, x, language = st.columns([0.3,0.5,0.2], vertical_alignment='bottom')
with language:
  language_of_page = st.selectbox("", options=idiomadasdisponiveis, index=idxidioma)
  textos = traaducaoapp(language_of_page)
  st.session_state.useridioma = language_of_page
  st.sidebar.page_link("pages/1_SALDOS.py", label=textos['SALDOS'], icon=":material/account_balance:")
  st.sidebar.page_link("pages/2_LANCAMENTOS.py", label=textos['LANÇAMENTOS'], icon=":material/list:")
  st.sidebar.page_link("pages/3_CONFIGURACOES.py", label=textos['CONFIGURAÇÕES'], icon=":material/settings:")
  st.sidebar.page_link("pages/4_CARTOES DE CREDITO.py", label=textos['CARTÕES_DE_CRÉDITO'], icon=":material/credit_card:")
  st.sidebar.page_link("pages/5_RECEITAS X DESPESAS.py", label=textos['RECEITAS X DESPESAS'], icon=":material/finance:")
  st.sidebar.page_link("pages/6_VERSAO.py", label=textos['VERSÃO'], icon=":material/info:")
  if st.sidebar.button("🚪 Logout"):
    logout()
  st.sidebar.divider()


with bemvido:
  st.write(f"{textos['BEMVINDO']} {st.session_state.name}!")
  
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
  return dados_records, workbook



#informe o id e name da arquivo google sheets

tempo_espera = 5


try:
  lançamentos, workbook = lerdados(sheeitid, sheetname)
  sheet = workbook.get_worksheet(0)
except APIError:
  st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
  time.sleep(tempo_espera)
  st.rerun()

sheet = workbook.get_worksheet(0)
lançamentos2 = sheet.get_all_values()
lançamentos_CONTAS = pd.DataFrame(lançamentos2[1:], columns=lançamentos2[0])
lançamentos_CONTAS = lançamentos_CONTAS.set_index('ID')
lançamentos_CONTAS = lançamentos_CONTAS[lançamentos_CONTAS["CONCILIADO"]=="TRUE"]
lançamentos_CONTAS = lançamentos_CONTAS[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]
lancamento_cartao = workbook.get_worksheet(1)
tabela_lancamentos_cartao = lancamento_cartao.get_all_values()
tabela_lancamentos_cartao = pd.DataFrame(tabela_lancamentos_cartao[1:], columns=tabela_lancamentos_cartao[0])
tabela_lancamentos_cartao = tabela_lancamentos_cartao.set_index('ID')
tabela_lancamentos_cartao.index = tabela_lancamentos_cartao.index.astype(int)
tabela_lancamentos_cartao = tabela_lancamentos_cartao[tabela_lancamentos_cartao["CONCILIADO"]=="TRUE"]
tabela_lancamentos_cartao = tabela_lancamentos_cartao[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]

lançamentos_RECDES = pd.concat([lançamentos_CONTAS, tabela_lancamentos_cartao], axis=0)

lançamentos_RECDES = lançamentos_RECDES.reset_index()
lançamentos_RECDES = lançamentos_RECDES[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]

conta_cont_cadastradas = workbook.get_worksheet(3)
tabela_contas_cont = conta_cont_cadastradas.get_all_values()
tabela_contas_cont = pd.DataFrame(tabela_contas_cont[1:], columns=tabela_contas_cont[0])
tabela_contas_cont = tabela_contas_cont.set_index('ID')
tabela_contas_cont_ativa = tabela_contas_cont[tabela_contas_cont['ATIVO']=='TRUE']
tabela_contas_cont_ativa = tabela_contas_cont_ativa[['CONTA CONTÁBIL','CATEGORIA','ATRIBUIÇÃO']]
tamanho_tabela_contas_cont = len(tabela_contas_cont)+2
tabela_contas_cont_ativa['CONT_CAT'] = tabela_contas_cont_ativa['CONTA CONTÁBIL'] + " / " + tabela_contas_cont_ativa["CATEGORIA"]
contas_contabeis = tabela_contas_cont_ativa['CONT_CAT'].tolist()

conta_banco_cadastradas = workbook.get_worksheet(2)
tabela_contas_banco = conta_banco_cadastradas.get_all_values()
tabela_contas_banco = pd.DataFrame(tabela_contas_banco[1:], columns=tabela_contas_banco[0])
tabela_contas_banco = tabela_contas_banco.set_index('ID')
tabela_contas_banco_ativa = tabela_contas_banco[tabela_contas_banco['ATIVO']=='TRUE']
tabela_contas_banco_ativa = tabela_contas_banco_ativa[['NOME BANCO','PROPRIETÁRIO','MOEDA']]
tamanho_tabela_contas_banco = len(tabela_contas_banco)+2

  # Ler a tabela de lançamentos do Google Sheets
lançamentos = lançamentos.set_index('ID')  # Definir a coluna 'ID' como índice do DataFrame

if len(lançamentos)==0:
  st.write("Sem lançamentos")
else:
  lançamentos['BANCO'] = lançamentos['BANCO'].str.upper()  # Transformar nomes dos bancos para maiúsculas
  try:
    lançamentos['VALOR'] = lançamentos['VALOR'].astype(str).str.replace('.', '', regex=False)
  except:
    pass
  lançamentos['VALOR'] = lançamentos['VALOR'].str.replace(',', '.', regex=False)
  lançamentos['VALOR'] = pd.to_numeric(lançamentos['VALOR'], errors='coerce')
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(float)  # Converter 'VALOR' de texto para float
  lançamentos = lançamentos[lançamentos['CONCILIADO'] == True]  # Filtrar apenas registros conciliados
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')  # Converter 'DATA' para datetime (dia/mês/ano)
  tamanho_tabela = lançamentos.index.max()+1
  contas = list(lançamentos['BANCO'].dropna().unique())  # Lista de bancos únicos, ignorando valores nulos
  users = list(lançamentos['PROPRIETÁRIO'].dropna().unique())  # Lista de proprietários únicos, ignorando valores nulos
  
  

  col01, col02, col03, col04, col05 = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])  # Define layout de 3 colunas com larguras proporcionais
  with col01:
    data_saldo = pd.to_datetime(st.date_input(textos['DATA_SALDOTEXT'], date.today(),format="DD/MM/YYYY"))  # Input de data para filtrar os saldos

    df_saldos_user = lançamentos[lançamentos['DATA'] <= data_saldo]  # Filtra lançamentos com data menor ou igual à selecionada
    df_saldo_user1 = df_saldos_user['VALOR'].sum().round(2)
    df_saldo_user1 = df_saldo_user1
    valor_formatado = f"{df_saldo_user1:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    #st.markdown(f'SALDO TOTAL: R$ {df_saldos_user['VALOR'].sum().round(2)}')
    #st.markdown(f"SALDO TOTAL: R$ {df_saldos_user['VALOR'].sum().round(2):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    DATAESCOLHIDA = pd.to_datetime(data_saldo)
    ultimo_dia_mes_anterior = (DATAESCOLHIDA.replace(day=1) - pd.Timedelta(days=1)).date()
    ultimo_dia_mes_anterior = pd.to_datetime(ultimo_dia_mes_anterior)
    df_saldos_user2 = lançamentos[lançamentos['DATA'] <= ultimo_dia_mes_anterior]
    df_saldo_user3 = df_saldos_user2['VALOR'].sum()
    saldoanterior = round(float(df_saldo_user1)-float(df_saldo_user3),2)
    saldoanterior = f"{saldoanterior:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
  with col02:
    st.metric(label=textos['SALDO_ATUALTEXT'], value=f'R$ {valor_formatado}', delta=saldoanterior, border=True)
  with col03:
    lançamentos_RECDES['DATA'] = pd.to_datetime(lançamentos_RECDES['DATA'], dayfirst=True, errors='coerce')
    try:
      lançamentos_RECDES['VALOR'] = lançamentos_RECDES['VALOR'].astype(str).str.replace('.', '', regex=False)
    except:
      pass
    lançamentos_RECDES['VALOR'] = lançamentos_RECDES['VALOR'].str.replace(',', '.', regex=False)
    lançamentos_RECDES['VALOR'] = pd.to_numeric(lançamentos_RECDES['VALOR'], errors='coerce')
    lançamentos_RECDES['VALOR'] = lançamentos_RECDES['VALOR'].astype(float)
    primeiro_dia_do_mes = DATAESCOLHIDA.replace(day=1).date()
    primeiro_dia_do_mes = pd.to_datetime(primeiro_dia_do_mes)
    ultimo_dia_do_mes = DATAESCOLHIDA + pd.offsets.MonthEnd(0)
    
    primeiro_dia_ultimo_mes = (DATAESCOLHIDA.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    # Último dia do mês anterior
    ultimo_dia_ultimo_mes = DATAESCOLHIDA.replace(day=1) - pd.DateOffset(days=1)

    
    lançamentos_RECDES_mes = lançamentos_RECDES[(lançamentos_RECDES['DATA']>=primeiro_dia_do_mes)&(lançamentos_RECDES['DATA']<=ultimo_dia_do_mes)]
    lançamentos_RECDES_RECEITAS = lançamentos_RECDES_mes[lançamentos_RECDES_mes['ANALISE']=="RECEITAS"]
    lançamentos_RECDES_DESPESAS = lançamentos_RECDES_mes[lançamentos_RECDES_mes['ANALISE']=="DESPESAS"]
    soma_receitas = lançamentos_RECDES_RECEITAS['VALOR'].sum()
    soma_despesas = lançamentos_RECDES_DESPESAS['VALOR'].sum()
    lançamentos_RECDES_mesanterior = lançamentos_RECDES[(lançamentos_RECDES['DATA']>=primeiro_dia_ultimo_mes)&(lançamentos_RECDES['DATA']<=ultimo_dia_ultimo_mes)]
    lançamentos_RECDES_RECEITAS_mesanterior = lançamentos_RECDES_mesanterior[lançamentos_RECDES['ANALISE']=="RECEITAS"]
    lançamentos_RECDES_DESPESAS_mesanterior = lançamentos_RECDES_mesanterior[lançamentos_RECDES['ANALISE']=="DESPESAS"]
    soma_receitas_mes_anterior = lançamentos_RECDES_RECEITAS_mesanterior['VALOR'].sum()
    soma_despesas_mes_anterior = lançamentos_RECDES_DESPESAS_mesanterior['VALOR'].sum()   

    diferencarec = soma_receitas - soma_receitas_mes_anterior
    diferencarec = f"{diferencarec:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    soma_receitas = f"{soma_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")



    st.metric(label=textos['RECEITASTEXT'], value=f'R$ {soma_receitas}', delta=diferencarec, border=True)

  with col04:
    diferencades = abs(soma_despesas) - abs(soma_despesas_mes_anterior)
    diferencades = f"{diferencades:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    soma_despesas = f"{soma_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    st.metric(label=textos['DESPESATEXT'], value=f'R$ {soma_despesas}', delta=diferencades, border=True, delta_color="inverse" )

    
  st.divider()  # Linha divisória no app
  col011, col012 = st.columns([0.2, 0.8])  # Define nova linha com duas colunas
  with col011:
    filtro1 = st.toggle(textos['FILTRAR_PROPRIETÁRIOTEXT'])  # Botão liga/desliga para aplicar filtro por usuário
    if filtro1:
      users_selecionado = st.selectbox(textos['SELECIONE UM PROPRIETÁRIOTEXT'], users, disabled=False)  # Seleção do proprietário (usuário)
    else:
      users_selecionado = st.selectbox(textos['SELECIONE UM PROPRIETÁRIOTEXT'], users, index=None, disabled=True, placeholder="")  # Seleção do proprietário (usuário)
    




  df_saldos_user = df_saldos_user.groupby(['PROPRIETÁRIO', 'BANCO']).agg({'VALOR': 'sum'}).round(2)  # Agrupa e soma valores por proprietário e banco
  df_saldos_user = df_saldos_user[df_saldos_user['VALOR'] != 0]  # Remove registros com valor igual a zero
  df_saldos_user = df_saldos_user.sort_values(by='VALOR', ascending=False)  # Ordena pelo valor em ordem decrescente
  df_saldos_user = df_saldos_user.reset_index()  # Reseta o índice para transformar os agrupamentos em colunas normais
  df_saldos_user_filtrado = df_saldos_user[df_saldos_user['PROPRIETÁRIO'] == users_selecionado]  # Aplica filtro pelo usuário selecionado



  # Calcular o acumulado
  lançamentos2 = lançamentos[['DATA','PROPRIETÁRIO', 'VALOR']]
  lançamentos2['ACUMULADO'] = lançamentos2.groupby('PROPRIETÁRIO')['VALOR'].cumsum()
  lançamentos2['ACUMULADO'] = lançamentos2['ACUMULADO'].round(2)
  lançamentos['ACUMULADO'] = lançamentos.groupby(['BANCO', 'PROPRIETÁRIO'])['VALOR'].cumsum()
  lançamentos = lançamentos[['DATA','BANCO','PROPRIETÁRIO','ACUMULADO']]
  lançamentos['ACUMULADO'] = lançamentos['ACUMULADO'].round(2)
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'])
  lançamentos_filtrado = lançamentos[lançamentos['PROPRIETÁRIO'] == users_selecionado] 
  df_saldos_user_total = df_saldos_user.groupby(['PROPRIETÁRIO']).agg({'VALOR': 'sum'}).round(2)  # Exibe tabela completa
  df_saldos_user_total = df_saldos_user_total.sort_values(by='VALOR', ascending=False)
  df_saldos_user_total['VALOR'] = df_saldos_user_total['VALOR'].apply(lambda x: f"{x:.2f}")
  df_saldos_user_total = df_saldos_user_total.reset_index()
  userscomsaldo = df_saldos_user_total['PROPRIETÁRIO'].dropna().unique()
  lançamentos_filtrado12 = lançamentos2[lançamentos2['PROPRIETÁRIO'].isin(userscomsaldo)]
  bancoscomsaldo = df_saldos_user_filtrado['BANCO'].dropna().unique()
  lançamentos_filtrado2 = lançamentos_filtrado[lançamentos_filtrado['BANCO'].isin(bancoscomsaldo)]
  resultado_mensal = (
      lançamentos2
      .set_index('DATA')
      .groupby('PROPRIETÁRIO')['ACUMULADO']
      .resample('ME')
      .last()
      .reset_index()
  )
  resultado_mensal4 = (
      lançamentos_filtrado12
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
  resultado_mensal3 = (
      lançamentos_filtrado2
      .set_index('DATA')
      .groupby(['BANCO', 'PROPRIETÁRIO'])['ACUMULADO']
      .resample('ME')
      .last()
      .reset_index()
  )


  if filtro1:
    fig1 = px.pie(df_saldos_user_filtrado, names='BANCO', values='VALOR')  # Gráfico de pizza com saldos filtrados
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig2 = px.bar(df_saldos_user_filtrado, x='BANCO', y='VALOR', color='PROPRIETÁRIO', text_auto=True)  # Gráfico de barras com saldos filtrados
    fig3 = px.line(resultado_mensal3, x="DATA", y="ACUMULADO", color='BANCO', title='Saldo acumulado no fim de cada mês', markers=False)
    fig3.update_traces(connectgaps=True)
    fig3.update_xaxes(tickformat="%m/%Y")
    fig4 = px.line(resultado_mensal2, x="DATA", y="ACUMULADO", color='BANCO', title='Saldo acumulado no fim de cada mês', markers=False)
    fig4.update_xaxes(tickformat="%m/%Y")
  else:
    fig1 = px.pie(df_saldos_user, names='PROPRIETÁRIO', values='VALOR')  # Gráfico de pizza com todos os dados
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig2 = px.bar(df_saldos_user, x='BANCO', y='VALOR', color='PROPRIETÁRIO', text_auto=True)  # Gráfico de barras com todos os dados
    fig3 = px.line(resultado_mensal4, x="DATA", y="ACUMULADO", color='PROPRIETÁRIO', title=textos['SALDO ACUMULADO NO FIM DE CADA MÊSTEXT'], markers=False)
    fig3.update_traces(connectgaps=True)
    fig3.update_xaxes(tickformat="%m/%Y")

  col11, col12, col13 = st.columns(3)  # Layout de três colunas para exibir tabelas e gráficos

  with col11:
    a,b = st.columns(2, vertical_alignment='center')
    with a:
      st.write(textos['SALDOS_BANCÁRIOSTEXT'])  # Título da tabela
      
    if filtro1:
      saldototalperprop = df_saldos_user_filtrado['VALOR'].sum().round(2)
      with b:
        ajustar = st.checkbox(textos['AJUSTAR_SALDOTEXT'])
        
      df_saldos_user_filtrado['VALOR'] = df_saldos_user_filtrado['VALOR'].apply(lambda x: f"{x:.2f}")
      selected_rows_original = df_saldos_user_filtrado["VALOR"]
      if ajustar:
        with st.form(key="editar_form", border=False):
          editar_df = st.data_editor(df_saldos_user_filtrado)
          data = st.date_input(textos['DATATEXT'], date.today(), format="DD/MM/YYYY")
          contacont = st.selectbox(textos['SELECIONE_O_LANÇAMENTOTEXT'], options=contas_contabeis, index = None)
          check = st.form_submit_button(textos['INSERIRTEXT'])

          if check:
            if contacont is None:
              st.warning(textos['SELECIONE_O_LANÇAMENTOTEXT'])
              
            else:
              selected_rows = editar_df["VALOR"]
              listofaccount = []
              selected_indexes = selected_rows.index.tolist()
              print(selected_indexes)
              for i in selected_indexes:
                if df_saldos_user_filtrado.loc[i,'VALOR'] != editar_df.loc[i,'VALOR']:
                  listofaccount.append(i)
              print(listofaccount)   
              progesso_barra = 0
              progress_bar = st.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
              for index, i in enumerate(listofaccount):
                sheet.add_rows(1)
                sheet.update_acell(f'A{tamanho_tabela+index}', f"=ROW(B{tamanho_tabela+index})")
                sheet.update_acell(f'B{tamanho_tabela+index}', data.strftime('%d/%m/%Y'))
                sheet.update_acell(f'C{tamanho_tabela+index}', editar_df.loc[i,'BANCO'])
                sheet.update_acell(f'D{tamanho_tabela+index}', editar_df.loc[i,'PROPRIETÁRIO'])
                sheet.update_acell(f'E{tamanho_tabela+index}', contacont.split(" / ")[0])
                sheet.update_acell(f'F{tamanho_tabela+index}', contacont.split(" / ")[1])
                valor1 = float(str(editar_df.loc[i, 'VALOR']).replace(',', '.'))
                valor2 = float(str(df_saldos_user_filtrado.loc[i, 'VALOR']).replace(',', '.'))
                resultado = valor1 - valor2
                sheet.update_acell(f'G{tamanho_tabela+index}', resultado)
                sheet.update_acell(f'H{tamanho_tabela+index}', "AJUSTE DE SALDO: " + contacont.split(" / ")[0])
                sheet.update_acell(f'I{tamanho_tabela+index}', "TRUE")
                analise = tabela_contas_cont_ativa.loc[(tabela_contas_cont_ativa['CONTA CONTÁBIL'] == contacont.split(" / ")[0])&(tabela_contas_cont_ativa['CATEGORIA'] == contacont.split(" / ")[1]),'ATRIBUIÇÃO'].values[0]
                sheet.update_acell(f'J{tamanho_tabela+index}', analise)
                moeda = tabela_contas_banco_ativa.loc[(tabela_contas_banco_ativa['NOME BANCO'] == editar_df.loc[i,'BANCO'])&(tabela_contas_banco_ativa['PROPRIETÁRIO'] == editar_df.loc[i,'PROPRIETÁRIO']),'MOEDA'].values[0]
                sheet.update_acell(f'L{tamanho_tabela+index}', moeda)
                sheet.update_acell(f'M{tamanho_tabela+index}', st.session_state.name)
                sheet.update_acell(f'N{tamanho_tabela+index}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                progesso_barra = progesso_barra + int(100/len(listofaccount))
                progress_bar.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
                
                #st.success(f"Registro {index+1} inserido com sucesso!")
              st.rerun()                


      else:
        if language_of_page == "PORTUGUÊS":
          st.dataframe(df_saldos_user_filtrado, hide_index=True)  # Exibe tabela filtrada
        elif language_of_page =="ENGLISH":
          df_saldos_user_filtrado = df_saldos_user_filtrado.rename(columns={'PROPRIETÁRIO': 'OWNER','BANCO': 'BANK', 'VALOR': 'VALUE'})
          st.dataframe(df_saldos_user_filtrado, hide_index=True)  # Exibe tabela filtrad
        elif language_of_page == "РУССКИЙ":
          df_saldos_user_filtrado = df_saldos_user_filtrado.rename(columns={'PROPRIETÁRIO': 'ВЛАДЕЛЕЦ','BANCO': 'БАНК', 'VALOR': 'ЦЕНИТЬ'})
          st.dataframe(df_saldos_user_filtrado, hide_index=True)  # Exibe tabela filtrada
          
        st.markdown(f"{textos['SALDO_ATUALTEXT']} R$ {saldototalperprop:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
      
    else:
      if language_of_page == "PORTUGUÊS":
        st.dataframe(df_saldos_user_total, hide_index=True)

      elif language_of_page =="ENGLISH":
        df_saldos_user_total = df_saldos_user_total.rename(columns={'PROPRIETÁRIO': 'OWNER', 'VALOR': 'VALUE'})
        st.dataframe(df_saldos_user_total, hide_index=True)
      elif language_of_page == "РУССКИЙ":
        df_saldos_user_total = df_saldos_user_total.rename(columns={'PROPRIETÁRIO': 'ВЛАДЕЛЕЦ', 'VALOR': 'ЦЕНИТЬ'})
        st.dataframe(df_saldos_user_total, hide_index=True)
      st.markdown(f'{textos['SALDO_TOTALTEXT']} R$ {df_saldos_user['VALOR'].sum().round(2):,.2f}'.replace(",", "X").replace(".", ",").replace("X", "."))


  with col12:
    st.plotly_chart(fig1)  # Exibe gráfico de pizza
  with col13:
    st.plotly_chart(fig2)  # Exibe gráfico de barras

  st.divider()  # Linha divisória no app
  if filtro1:
    todasascontas = st.checkbox(textos['MOSTRAR TODAS AS CONTASTEXT'])

    if todasascontas:
      st.plotly_chart(fig4)
    else:
      st.plotly_chart(fig3)
  else:
    st.plotly_chart(fig3)


def lancamentorapido():
  novolancamentodestination = st.sidebar.radio('',("BANCO","CARTÃO DE CRÉDITO"),horizontal=True)

  with st.sidebar.form(key="formsidebar", clear_on_submit=True):
    data = st.sidebar.date_input(textos['DATATEXT'], date.today(), format="DD/MM/YYYY")
    
    #CONTAS BANCÁRIAS#
    conta_banco_cadastradas = workbook.get_worksheet(2)
    tabela_contas_banco = conta_banco_cadastradas.get_all_values()
    tabela_contas_banco = pd.DataFrame(tabela_contas_banco[1:], columns=tabela_contas_banco[0])
    tabela_contas_banco = tabela_contas_banco.set_index('ID')
    tabela_contas_banco_ativa = tabela_contas_banco[tabela_contas_banco['ATIVO']=='TRUE']
    tabela_contas_banco_ativa = tabela_contas_banco_ativa[['NOME BANCO','PROPRIETÁRIO','MOEDA']]

    tabela_contas_banco_ativa['BANCO_PROP'] = tabela_contas_banco_ativa["NOME BANCO"] + " / " + tabela_contas_banco_ativa["PROPRIETÁRIO"]
    bancos = tabela_contas_banco_ativa['BANCO_PROP'].tolist()

    conta_cards_cadastradas = workbook.get_worksheet(4)
    tabela_cards_cont = conta_cards_cadastradas.get_all_values()
    tabela_cards_cont = pd.DataFrame(tabela_cards_cont[1:], columns=tabela_cards_cont[0])
    tabela_cards_cont = tabela_cards_cont.set_index('ID')
    tabela_cards_cont = tabela_cards_cont[tabela_cards_cont['ATIVO']=='TRUE']
    tabela_cards_cont = tabela_cards_cont[['CARTÃO','PROPRIETÁRIO','MOEDA','FECHAMENTO', 'VENCIMENTO']]

    tabela_cards_cont['CARTÃO_PROP'] = tabela_cards_cont["CARTÃO"] + " / " + tabela_cards_cont["PROPRIETÁRIO"]
    cards = tabela_cards_cont['CARTÃO_PROP'].tolist()

    if novolancamentodestination == 'BANCO':
      textos1 = "BANCO"
      opcoes = bancos
    else:
      textos1 = "CARTÃO"
      opcoes = cards

    bankorcard = st.sidebar.selectbox(textos1,options=opcoes)

    conta_cont_cadastradas = workbook.get_worksheet(3)
    tabela_contas_cont = conta_cont_cadastradas.get_all_values()
    tabela_contas_cont = pd.DataFrame(tabela_contas_cont[1:], columns=tabela_contas_cont[0])
    tabela_contas_cont = tabela_contas_cont.set_index('ID')
    tabela_contas_cont_ativa = tabela_contas_cont[tabela_contas_cont['ATIVO']=='TRUE']
    tabela_contas_cont_ativa = tabela_contas_cont_ativa[['CONTA CONTÁBIL','CATEGORIA','ATRIBUIÇÃO']]

    tabela_contas_cont_ativa['CONT_CAT'] = tabela_contas_cont_ativa['CONTA CONTÁBIL'] + " / " + tabela_contas_cont_ativa["CATEGORIA"]
    contas = tabela_contas_cont_ativa['CONT_CAT'].tolist()

    despesa = st.sidebar.selectbox(textos['SELECIONE_O_LANÇAMENTOTEXT'], contas, index=None, placeholder="Selecione")
    number = st.sidebar.number_input(textos['INSIRA_O_VALORTEXT'], format="%0.2f")
    descricao = st.text_input(textos['DESCRIÇÃOTEXT'])
    descricao = str(descricao)
    descricao = descricao.upper()

    #inserirbutton = st.form_submit_button('INSERIR')
  inserirbutton2 = st.sidebar.button('INSERIR')

  if inserirbutton2:
    if novolancamentodestination == 'BANCO':
      sheet.add_rows(1)
      sheet.update_acell(f'A{tamanho_tabela}', f"=ROW(B{tamanho_tabela})")
      sheet.update_acell(f'B{tamanho_tabela}', data.strftime('%d/%m/%Y'))
      sheet.update_acell(f'C{tamanho_tabela}', bankorcard.split(" / ")[0])
      sheet.update_acell(f'D{tamanho_tabela}', bankorcard.split(" / ")[1])
      sheet.update_acell(f'E{tamanho_tabela}', despesa.split(" / ")[0])
      sheet.update_acell(f'F{tamanho_tabela}', despesa.split(" / ")[1])
      analise = tabela_contas_cont_ativa.loc[(tabela_contas_cont_ativa['CONTA CONTÁBIL'] == despesa.split(" / ")[0])&(tabela_contas_cont_ativa['CATEGORIA'] == despesa.split(" / ")[1]),'ATRIBUIÇÃO'].values[0]
      if analise == "DESPESAS":
        sheet.update_acell(f'G{tamanho_tabela}', -number)
      elif analise == "RECEITAS":
        sheet.update_acell(f'G{tamanho_tabela}', number)
      sheet.update_acell(f'H{tamanho_tabela}', descricao)
      sheet.update_acell(f'I{tamanho_tabela}', 'TRUE')
      sheet.update_acell(f'J{tamanho_tabela}', analise)
      moeda = tabela_contas_banco_ativa.loc[(tabela_contas_banco_ativa['NOME BANCO'] == bankorcard.split(" / ")[0])&(tabela_contas_banco_ativa['PROPRIETÁRIO'] == bankorcard.split(" / ")[1]),'MOEDA'].values[0]
      sheet.update_acell(f'L{tamanho_tabela}', moeda)
      sheet.update_acell(f'M{tamanho_tabela}', st.session_state.name)
      sheet.update_acell(f'N{tamanho_tabela}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
      st.success(textos['Registro_inserido_com_sucessoTEXT'])
      st.rerun()
    else:
      textos1 = "CARTÃO"
      opcoes = cards



#lancamentorapido()