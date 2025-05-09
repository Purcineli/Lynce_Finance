import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta
from gspread.exceptions import APIError
import time
import plotly.express as px
import numpy as np
import math
from LYNCE import verificar_login
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

tempo_espera = 5
try:
  lançamentos, workbook = lerdados(sheeitid, sheetname)
  sheet = workbook.get_worksheet(0)

except APIError:
  st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
  time.sleep(tempo_espera)
  st.rerun()

lançamentos = sheet.get_all_values()
lançamentos = pd.DataFrame(lançamentos[1:], columns=lançamentos[0])


toggle11,toggle12,toggle13,toggle14 = st.columns(4)
with toggle11:
  togglecontas_bancarias = st.toggle('CONTAS BANCÁRIAS')
with toggle12:
  togglecontas_contábeis = st.toggle('CONTAS CONTÁBEIS')
with toggle13:
  togglecontas_proj = st.toggle('PROJETOS/EVENTOS')
with toggle14:
  togglecontas_card = st.toggle('CARTÕES DE CRÉDITO')
###################CONTAS BANCÁRIAS####################
if togglecontas_bancarias:
  conta_banco_cadastradas = workbook.get_worksheet(2)
  tabela_contas_banco = conta_banco_cadastradas.get_all_values()
  tabela_contas_banco = pd.DataFrame(tabela_contas_banco[1:], columns=tabela_contas_banco[0])
  tabela_contas_banco = tabela_contas_banco.set_index('ID')
  tabela_contas_banco_ativa = tabela_contas_banco[tabela_contas_banco['ATIVO']=='TRUE']
  tabela_contas_banco_ativa = tabela_contas_banco_ativa[['NOME BANCO','PROPRIETÁRIO','MOEDA']]
  tabela_contas_banco_inativa = tabela_contas_banco[tabela_contas_banco['ATIVO']=='FALSE']
  tabela_contas_banco_inativa = tabela_contas_banco_inativa[['NOME BANCO','PROPRIETÁRIO','MOEDA']]
  #st.write(len(tabela_contas_banco))
  tabela_contas_banco.index = pd.to_numeric(tabela_contas_banco.index, errors='coerce')
  tabela_contas_banco = tabela_contas_banco[~tabela_contas_banco.index.isna()]
  tabela_contas_banco.index = tabela_contas_banco.index.astype(int)
  tamanho_tabela_contas_banco = tabela_contas_banco.shape[0] + 2


  st.title('CONTAS BANCÁRIAS')
  inativos, ativos = st.columns(2)
  with inativos:
    st.write('INATIVAS')
    st.dataframe(tabela_contas_banco_inativa, height=500)
    col01, col02 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col01:
        id_selecionada = st.selectbox('SELECIONE A ID', list(tabela_contas_banco_inativa.index))
    with col02:
        if st.button('ATIVAR'):
          conta_banco_cadastradas.update_acell(f'D{id_selecionada}', True)
          st.rerun()
    with st.form(key="Inserir nova conta"):
      st.write('NOVA CONTA BANCÁRIA')
      nome,prop,but =st.columns((0.3,0.55,0.15), vertical_alignment='bottom')
      with nome:
        new_bank = st.text_input('NOME')
        new_bank = str(new_bank)
        new_bank = new_bank.upper()
      with prop:
        nowner = st.text_input('PROPRIETÁRIO')
        nowner = str(nowner)
        nowner = nowner.upper()
      with but:
        submit = st.form_submit_button(label="INSERIR")
        if submit: #st.button('INSERIR NOVA CONTA'):
          if tamanho_tabela_contas_banco > 2:
            conta_banco_cadastradas.add_rows(1)
          conta_banco_cadastradas.update_acell(f'A{tamanho_tabela_contas_banco}', f'=ROW(B{tamanho_tabela_contas_banco})')
          conta_banco_cadastradas.update_acell(f'B{tamanho_tabela_contas_banco}', new_bank)
          conta_banco_cadastradas.update_acell(f'C{tamanho_tabela_contas_banco}', nowner)
          conta_banco_cadastradas.update_acell(f'D{tamanho_tabela_contas_banco}', True)
          conta_banco_cadastradas.update_acell(f'E{tamanho_tabela_contas_banco}', 'BRL')
          st.rerun()

  with ativos:
    st.write('ATIVAS')
    st.dataframe(tabela_contas_banco_ativa, height=500)
    col01, col02 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col01:
        if pd.isna(tabela_contas_banco_ativa.index.max()):
          id_selecionada2 = st.selectbox('SELECIONE A ID',options=None, key="id_contas")
        else:
          id_selecionada2 = int(st.selectbox('SELECIONE A ID', list(tabela_contas_banco_ativa.index), key="id_contas2"))
    with col02:
        if st.button('INATIVAR'):
          conta_banco_cadastradas.update_acell(f'D{id_selecionada2}', False)
          st.rerun()

    with st.form(key='Editar conta'):
      st.write('EDITAR CONTA BANCÁRIA') 
      nome,prop,but,but2 =st.columns((0.3,0.32,0.13,0.15), vertical_alignment='bottom')
      with nome:
        if len(tabela_contas_banco_ativa)<1:
          bank = st.text_input("NOME BANCO",value=None, key="one")
          bank = str(bank)
          bank = bank.upper()
        else:
          bank = st.text_input("NOME BANCO",tabela_contas_banco.loc[id_selecionada2, "NOME BANCO"])
      with prop:
        if len(tabela_contas_banco_ativa)<1:
          owner = st.text_input("NOME BANCO",value=None, key="two")
        else:
          owner = st.text_input("NOME BANCO",tabela_contas_banco.loc[id_selecionada2, "PROPRIETÁRIO"], key="two two")
          owner = str(owner)
          owner = owner.upper()
      with but:
        submit = st.form_submit_button(label="EDITAR")
    if submit:
      conta_banco_cadastradas.update_acell(f'B{int(id_selecionada2)}', bank)
      conta_banco_cadastradas.update_acell(f'C{int(id_selecionada2)}', owner)
      st.rerun()
########################################################################



###################CONTAS CONTÁBEIS####################

#CONTAS CONTÁBEIS#
if togglecontas_contábeis:
  st.divider()
  conta_cont_cadastradas = workbook.get_worksheet(3)
  tabela_contas_cont = conta_cont_cadastradas.get_all_values()
  tabela_contas_cont = pd.DataFrame(tabela_contas_cont[1:], columns=tabela_contas_cont[0])
  tabela_contas_cont = tabela_contas_cont.set_index('ID')
  tabela_contas_cont_ativa = tabela_contas_cont[tabela_contas_cont['ATIVO']=='TRUE']
  tabela_contas_cont_ativa = tabela_contas_cont_ativa[['CONTA CONTÁBIL','CATEGORIA', 'ATRIBUIÇÃO']]
  tabela_contas_cont_inativa = tabela_contas_cont[tabela_contas_cont['ATIVO']=='FALSE']
  tabela_contas_cont_inativa = tabela_contas_cont_inativa[['CONTA CONTÁBIL','CATEGORIA', 'ATRIBUIÇÃO']]

  tabela_contas_cont.index = pd.to_numeric(tabela_contas_cont.index, errors='coerce')
  tabela_contas_cont = tabela_contas_cont[~tabela_contas_cont.index.isna()]
  tabela_contas_cont.index = tabela_contas_cont.index.astype(int)
  tamanho_tabela_contas_cont = tabela_contas_cont.shape[0] + 2

  st.title('CONTAS CONTÁBEIS')
  inativos_contas_cont, ativos_contas_cont = st.columns(2)
  with inativos_contas_cont:
    st.write('INATIVAS')
    st.dataframe(tabela_contas_cont_inativa, height=500)
    col11, col12 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col11:
        id_selecionada_cont = st.selectbox('SELECIONE A ID', list(tabela_contas_cont_inativa.index), key="idcont")
    with col12:
        if st.button('ATIVAR CONTA CONTABIL'):
          conta_cont_cadastradas.update_acell(f'D{id_selecionada_cont}', True)
          st.rerun()
    with st.form(key="Inserir nova conta contabil"):
      st.write('NOVA CONTA CONTÁBIL')
      nome1,cat, atr,but =st.columns((0.3,0.3,0.25,0.15), vertical_alignment='bottom')
      with nome1:
        new_conta = st.text_input('CONTA CONTÁBIL')
        new_conta = str(new_conta)
        new_conta = new_conta.upper()
      with cat:
        new_cat = st.text_input('CATEGORIA')
        new_cat = str(new_cat)
        new_cat = new_cat.upper()
      with atr:
        new_atr = st.selectbox("ATRIBUIÇÃO",['DESPESAS','RECEITAS','ANALÍTICA'], index=0)
        new_atr = str(new_atr)
        new_atr = new_atr.upper()
      with but:
        submit = st.form_submit_button(label="INSERIR")
        if submit: #st.button('INSERIR NOVA CONTA'):
          if tamanho_tabela_contas_cont > 2:
            conta_cont_cadastradas.add_rows(1)
          conta_cont_cadastradas.update_acell(f'A{tamanho_tabela_contas_cont}', f'=ROW(B{tamanho_tabela_contas_cont})')
          conta_cont_cadastradas.update_acell(f'B{tamanho_tabela_contas_cont}', new_conta)
          conta_cont_cadastradas.update_acell(f'C{tamanho_tabela_contas_cont}', new_cat)
          conta_cont_cadastradas.update_acell(f'D{tamanho_tabela_contas_cont}', True)
          conta_cont_cadastradas.update_acell(f'E{tamanho_tabela_contas_cont}', new_atr)
          st.rerun()
    
  with ativos_contas_cont:
    st.write('ATIVAS')
    st.dataframe(tabela_contas_cont_ativa, height=500)
    col01, col02 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col01:
        if pd.isna(tabela_contas_cont_ativa.index.max()):
          id_selecionada3 = st.selectbox('SELECIONE A ID', options=None, key="four")
        else:
          id_selecionada3 = int(st.selectbox('SELECIONE A ID', list(tabela_contas_cont_ativa.index), key="five"))
    with col02:
        if st.button('INATIVAR CONTA CONTÁBIL'):
          conta_cont_cadastradas.update_acell(f'D{id_selecionada3}', False)
          st.rerun()

    with st.form(key='Editar conta contabil'):
      st.write('EDITAR CONTA CONTÁBIL') 
      conta,cate,atr,but,but2 =st.columns((0.25,0.28,0.2,0.14,0.16), vertical_alignment='bottom')
      with conta:
        if len(tabela_contas_cont_ativa)<1:
          cont = st.text_input("CONTA",value=None, key="1")
        else:
          cont = st.text_input("CONTA",tabela_contas_cont.loc[id_selecionada3, "CONTA CONTÁBIL"])
        cont = str(cont)
        cont = cont.upper()
      with cate:
        if len(tabela_contas_cont_ativa)<1:
          categor = st.text_input("CATEGORIA",value=None, key="2")
        else:
          categor = st.text_input("CATEGORIA",tabela_contas_cont.loc[id_selecionada3, "CATEGORIA"])    
        categor = str(categor)
        categor = categor.upper()
      with atr:
        
        if len(tabela_contas_cont_ativa)<1:
          atrib = st.selectbox("ATRIBUIÇÃO",['DESPESAS','RECEITAS','ANALÍTICA'], index=0)
        else:
          analiseslist = ['DESPESAS','RECEITAS','ANALÍTICA']
          idxanalises = tabela_contas_cont.loc[id_selecionada3, 'ATRIBUIÇÃO']
          idxanalises = analiseslist.index(idxanalises)
          atrib = st.selectbox("ATRIBUIÇÃO",['DESPESAS','RECEITAS','ANALÍTICA'], index=idxanalises)    
        atrib = str(atrib)
        atrib = atrib.upper()
      with but:
        submit = st.popover(label="EDITAR")
        with submit:
          lancamentos_filtro = lançamentos[(lançamentos['LANÇAMENTO'] == cont) & (lançamentos['CATEGORIA'] == categor)]
          lista_id = lancamentos_filtro['ID'].tolist()
          st.write(lancamentos_filtro)
          st.write(f"Há {lancamentos_filtro.shape[0]} lançamentos localizados, deseja alterar?")
          st.write(lista_id)
          editar = st.form_submit_button('EDITAR')
          if editar:
            conta_cont_cadastradas.update( values=[[cont]],range_name=f'B{id_selecionada3}')
            conta_cont_cadastradas.update(values=[[categor]],range_name=f'C{id_selecionada3}')
            conta_cont_cadastradas.update(values=[[atrib]],range_name=f'E{id_selecionada3}')
            print("alterações efetuadas com sucesso na tabela de contas contábeis")
            print(lista_id)
            for x in lista_id:
              sheet.update(values=[[cont]],range_name=f'E{x}')
              sheet.update(values=[[categor]],range_name=f'F{x}')
              sheet.update( values=[[atrib]], range_name=f'J{x}')
              print(x)
      with but2:
        st.write("")
        #delete = st.form_submit_button(label="DELETAR")
    #if submit:

      #st.rerun()
    #if delete:
      #st.rerun()

########################################################################


###################PROJETOS/EVENTOS####################
#PROJETOS#
if togglecontas_proj:
  tabela_evenproj_sheet = workbook.get_worksheet(5)
  tabela_evenproj = tabela_evenproj_sheet.get_all_values()
  tabela_evenproj = pd.DataFrame(tabela_evenproj[1:], columns=tabela_evenproj[0])
  tabela_evenproj = tabela_evenproj.set_index('ID')
  tabela_evenproj_ativa = tabela_evenproj[tabela_evenproj['ATIVO']=='TRUE']
  tabela_evenproj_inativa = tabela_evenproj[tabela_evenproj['ATIVO']=='FALSE']

  tabela_evenproj.index = pd.to_numeric(tabela_evenproj.index, errors='coerce')
  tabela_evenproj = tabela_evenproj[~tabela_evenproj.index.isna()]
  tabela_evenproj.index = tabela_evenproj.index.astype(int)
  tamanho_tabela_evenproj = tabela_evenproj.shape[0] + 2


  st.title('PROJETOS / EVENTOS')
  proj_inativos, proj_ativos = st.columns(2)
  with proj_inativos:
    st.write('INATIVOS')
    st.dataframe(tabela_evenproj_inativa, height=500)
    col21, col22 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col21:
        id_selecionada3 = st.selectbox('SELECIONE A ID', list(tabela_evenproj_inativa.index), key="select3")
    with col22:
        if st.button('ATIVAR', key="123"):
          tabela_evenproj_sheet.update_acell(f'D{id_selecionada3}', True)
          st.rerun()
    with st.form(key="Inserir novo projeto / evento"):
      st.write('NOVA PROJETO / EVENTO')
      new_name = st.text_input('NOME')
      new_name = str(new_name)
      new_name = new_name.upper()
      submit = st.form_submit_button(label="INSERIR")
      if submit: #st.button('INSERIR NOVA CONTA'):
        if tamanho_tabela_evenproj > 2:
          tabela_evenproj_sheet.add_rows(1)
        tabela_evenproj_sheet.update_acell(f'A{tamanho_tabela_evenproj}', f'=ROW(B{tamanho_tabela_evenproj})')
        tabela_evenproj_sheet.update_acell(f'B{tamanho_tabela_evenproj}', new_name)
        tabela_evenproj_sheet.update_acell(f'C{tamanho_tabela_evenproj}', True)
        tabela_evenproj_sheet.update_acell(f'D{tamanho_tabela_evenproj}', True)
        st.rerun()
    
  with proj_ativos:
    st.write('ATIVAS')
    st.dataframe(tabela_evenproj_ativa, height=500)
    col31, col32 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col31:
        if pd.isna(tabela_evenproj_ativa.index.max()):
          id_selecionada5 = st.selectbox('SELECIONE A ID', options=None, key='5')
        else:
          id_selecionada5 = st.selectbox('SELECIONE A ID', list(tabela_evenproj_ativa.index))
    with col32:
        if st.button('INATIVAR', key="1234"):
          tabela_evenproj_sheet.update_acell(f'D{id_selecionada5}', False)
          st.rerun()

    with st.form(key='Editar nome'):
      st.write('EDITAR PROJETO') 
      if pd.isna(tabela_evenproj_ativa.index.max()):
        nome = st.text_input("NOME", value=None, key="7")
      else:
        nome = st.text_input("NOME",tabela_evenproj_ativa.loc[id_selecionada5, "NOME"])
      nome = str(nome)
      nome = nome.upper()
      submit = st.form_submit_button(label="EDITAR")
      if submit:
        tabela_evenproj_sheet.update_acell(f'B{int(id_selecionada5)}', nome)
        st.rerun()
########################################################################

###################CARTÕES DE CRÉDITOS####################
#CARTÕES DE CRÉDITO#
if togglecontas_card:
  tabela_cartoes_sheet = workbook.get_worksheet(4)
  tabela_cartoes = tabela_cartoes_sheet.get_all_values()
  tabela_cartoes = pd.DataFrame(tabela_cartoes[1:], columns=tabela_cartoes[0])
  tabela_cartoes = tabela_cartoes.set_index('ID')
  tabela_cartoes_ativa = tabela_cartoes[tabela_cartoes['ATIVO']=='TRUE']
  tabela_cartoes_ativa = tabela_cartoes_ativa[['CARTÃO', 'PROPRIETÁRIO', 'FECHAMENTO', 'VENCIMENTO']]
  tabela_cartoes_inativa = tabela_cartoes[tabela_cartoes['ATIVO']=='FALSE']
  tabela_cartoes_inativa = tabela_cartoes_inativa[['CARTÃO', 'PROPRIETÁRIO', 'FECHAMENTO', 'VENCIMENTO']]
  tamanho_tabela_cartoes = len(tabela_cartoes)+1

  tabela_cartoes.index = pd.to_numeric(tabela_cartoes.index, errors='coerce')
  tabela_cartoes = tabela_cartoes[~tabela_cartoes.index.isna()]
  tabela_cartoes.index = tabela_cartoes.index.astype(int)
  tamanho_tabela_cartoes = tabela_cartoes.shape[0] + 2


  st.divider() 
  st.title('CARTÕES DE CRÉDITO')
  card_inativos, card_ativos = st.columns(2)
  with card_inativos:
    st.write('INATIVOS')
    st.dataframe(tabela_cartoes_inativa, height=500)
    col31, col32 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col31:
        id_selecionada4 = st.selectbox('SELECIONE A ID', list(tabela_cartoes_inativa.index), key ="select4")
    with col32:
        if st.button('ATIVAR', key="ativa cartões"):
          tabela_cartoes_sheet.update_acell(f'G{id_selecionada4}', True)
          st.rerun()
    with st.form(key="Inserir cartão"):
      st.write('NOVO CARTÃO DE CRÉDITO')
      nome1,prop2,but3 =st.columns((0.3,0.55,0.15), vertical_alignment='bottom')
      with nome1:
        new_card = st.text_input('NOME', key="new card")
        new_card = str(new_card)
        new_card = new_card.upper()
      with prop2:
        newcardowner = st.text_input('PROPRIETÁRIO', key="new owner")
        newcardowner = str(newcardowner)
        newcardowner = newcardowner.upper()
      with but3:
        submit = st.form_submit_button(label="INSERIR")
      if submit: #st.button('INSERIR NOVA CONTA'):
        if tamanho_tabela_cartoes > 2:
          tabela_cartoes_sheet.add_rows(1)
        tabela_cartoes_sheet.update_acell(f'A{tamanho_tabela_cartoes}', f'=ROW(B{tamanho_tabela_cartoes})')
        tabela_cartoes_sheet.update_acell(f'B{tamanho_tabela_cartoes}', new_card)
        tabela_cartoes_sheet.update_acell(f'C{tamanho_tabela_cartoes}', newcardowner)
        tabela_cartoes_sheet.update_acell(f'D{tamanho_tabela_cartoes}', 'BRL')
        tabela_cartoes_sheet.update_acell(f'G{tamanho_tabela_cartoes}', True)
        st.rerun()
    
  with card_ativos:
    st.write('ATIVAS')
    st.dataframe(tabela_cartoes_ativa, height=500)
    col41, col42 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col41:
        if pd.isna(tabela_cartoes_ativa.index.max()):
          id_selecionada6 = st.selectbox('SELECIONE A ID', options=None, key='10')
        else:
          id_selecionada6 = st.selectbox('SELECIONE A ID', list(tabela_cartoes_ativa.index))
    with col42:
        if st.button('INATIVAR', key="inativar cartões"):
          tabela_cartoes_sheet.update_acell(f'G{id_selecionada6}', False)
          st.rerun()

    with st.form(key='Editar cartao'):
      st.write('EDITAR CARTÃO') 
      if len(tabela_cartoes_ativa)<1:
        new_nome_card = st.text_input("NOME", value=None, key="17")
      else:
        new_nome_card = st.text_input("NOME",tabela_cartoes_ativa.loc[id_selecionada6, "CARTÃO"])
      new_nome_card = str(new_nome_card)
      new_nome_card = new_nome_card.upper()
      if len(tabela_cartoes_ativa)<1:
        new_nome_owner = st.text_input("PROPRIETÁRIO", value=None, key="18")
      else:
        new_nome_owner = st.text_input("PROPRIETÁRIO",tabela_cartoes_ativa.loc[id_selecionada6, "PROPRIETÁRIO"], key="20")
      new_nome_owner = str(new_nome_owner)
      new_nome_owner = new_nome_owner.upper()
      submit = st.form_submit_button(label="EDITAR")
      if submit:
        tabela_cartoes_sheet.update_acell(f'B{int(id_selecionada6)}', new_nome_card)
        tabela_cartoes_sheet.update_acell(f'C{int(id_selecionada6)}', new_nome_owner)
        st.rerun()
