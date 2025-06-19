import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
from gspread.exceptions import APIError
import time
import plotly.express as px
import numpy as np
from LYNCE import verificar_login, logout
from TRADUTOR import traaducaoapp

st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.switch_page('LYNCE.py')


hoje = pd.to_datetime(date.today()) 
language_of_page = st.session_state.useridioma


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
  sheet_cartao = workbook.get_worksheet(1)
except APIError:
  st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
  time.sleep(tempo_espera)
  st.rerun()

lançamentos = sheet.get_all_values()
lançamentos = pd.DataFrame(lançamentos[1:], columns=lançamentos[0])
lançamentos = lançamentos[['ID', 'BANCO', 'PROPRIETÁRIO','LANÇAMENTO','CATEGORIA', 'PROJETO/EVENTO']]
lançamentos_cartao = sheet_cartao.get_all_values()
lançamentos_cartao = pd.DataFrame(lançamentos_cartao[1:], columns=lançamentos_cartao[0])
lançamentos_cartao = lançamentos_cartao[['ID','CARTÃO', 'PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','PROJETO/EVENTO']]


toggle11,toggle12,toggle13,toggle14 = st.columns(4)
with toggle11:
  togglecontas_bancarias = st.toggle(textos['CONTASBANCARIASTEXT'],value=False)
with toggle12:
  togglecontas_contábeis = st.toggle(textos['CONTASCONTABEISTEXT'],value=False)
with toggle13:
  togglecontas_proj = st.toggle(textos['PROJETOS/EVENTOSTEXT'],value=False)
with toggle14:
  togglecontas_card = st.toggle(textos['CARTOES_DE_CREDITOTEXT'],value=False)
###################CONTAS BANCÁRIAS####################
if togglecontas_bancarias:
  st.session_state['togglecontas_bancarias_status'] = False
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
  lista_owners = tabela_contas_banco['PROPRIETÁRIO'].unique().tolist()

  st.title(textos['CONTASBANCARIASTEXT'])
  inativos, ativos = st.columns(2)
  with inativos:
    st.write(textos['INATIVAS_TEXT'])
    st.dataframe(tabela_contas_banco_inativa, height=500)
    col01, col02 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col01:
        id_selecionada = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_contas_banco_inativa.index))
    with col02:
        if st.button(textos['ATIVAR_TEXT']):
          conta_banco_cadastradas.update_acell(f'D{id_selecionada}', True)
          st.rerun()
    with st.form(clear_on_submit=True,key="Inserir nova conta"):
      st.write(textos['NOVA_CONTA_BANCÁRIA_TEXT'])
      nome,prop,but =st.columns((0.3,0.55,0.15), vertical_alignment='bottom')
      with nome:
        new_bank = st.text_input(textos['NOME_TEXT'])
        new_bank = str(new_bank)
        new_bank = new_bank.upper()
      with prop:
        nowner = st.selectbox(textos['PROPRIETÁRIO_TEXT'], options=lista_owners,accept_new_options=True)
        nowner = str(nowner)
        nowner = nowner.upper()
      with but:
        submit = st.form_submit_button(label=textos['INSERIRTEXT'])
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
    st.write(textos['ATIVAS_TEXT'])
    st.dataframe(tabela_contas_banco_ativa, height=500)
    col01, col02 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col01:
        if pd.isna(tabela_contas_banco_ativa.index.max()):
          id_selecionada2 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'],options=None, key="id_contas")
        else:
          id_selecionada2 = int(st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_contas_banco_ativa.index), key="id_contas2"))
    with col02:
        if st.button(textos['INATIVAR_TEXT']):
          conta_banco_cadastradas.update_acell(f'D{id_selecionada2}', False)
          st.rerun()

    with st.form(clear_on_submit=True, key='Editar conta'):
      st.write(textos['EDITAR_CONTA_BANCÁRIA_TEXT']) 
      nome,prop,but,but2 =st.columns((0.3,0.32,0.13,0.15), vertical_alignment='bottom')
      with nome:
        if len(tabela_contas_banco_ativa)<1:
          bank = st.text_input(textos['NOME_BANCO_TEXT'],value=None, key="one")
          bank = str(bank)
          bank = bank.upper()
        else:
          bank = st.text_input(textos['NOME_BANCO_TEXT'],tabela_contas_banco.loc[id_selecionada2, 'NOME BANCO'])
          bank = str(bank)
          bank = bank.upper()
      with prop:
        if len(tabela_contas_banco_ativa)<1:
          owner = st.text_input(textos['PROPRIETÁRIO_TEXT'],value=None, key="two")
          owner = str(owner)
          owner = owner.upper()
        else:
          owner = st.text_input(textos['PROPRIETÁRIO_TEXT'],tabela_contas_banco.loc[id_selecionada2, 'PROPRIETÁRIO'], key="two two")
          owner = str(owner)
          owner = owner.upper()
      st.session_state['IDSEL'] = id_selecionada2

      print(f"NEW {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
      lancamentos_filtro_BANK = lançamentos[(lançamentos['BANCO'] == bank) & (lançamentos['PROPRIETÁRIO'] == owner)]
      if 'lista_id_BANK' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_BANK'] = []
      if 'lista_id_BANK2' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_BANK2'] = []
      lista_id_BANK = lancamentos_filtro_BANK['ID'].tolist()
      if lista_id_BANK:  # só salva se houver algo
        st.session_state['lista_id_BANK'] = lista_id_BANK
      else:
        st.session_state['lista_id_BANK2'] = st.session_state['lista_id_BANK']
        st.session_state['lista_id_BANK'] = lista_id_BANK
      
      totallançamentos_BANK = lancamentos_filtro_BANK.shape[0]


      st.write(f"{totallançamentos_BANK} {textos['LANCAMENTOS LOCALIZADOS']}")



      
      submit = st.form_submit_button(label=textos['EDITARTEXT'])
    if submit:
      if not st.session_state['lista_id_BANK']:
        lista_BANK = st.session_state['lista_id_BANK2']
      else:
        lista_BANK = st.session_state['lista_id_BANK']
      oldBANK = tabela_contas_banco.loc[id_selecionada2, 'NOME BANCO']
      oldOWNER = tabela_contas_banco.loc[id_selecionada2, 'PROPRIETÁRIO']

      if bank == oldBANK and oldOWNER == owner:
        pass
      else:
        progesso_barra = 0
        progress_bar = st.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
        st.write(len(lista_BANK))
        for x in lista_BANK:
            try:
              if bank == oldBANK:
                pass
              else:
                sheet.update(values=[[bank]], range_name=f'C{x}')
              if owner == oldOWNER:
                pass
              else:
                sheet.update(values=[[owner]], range_name=f'D{x}')
              time.sleep(0.5)
              
              progesso_barra = progesso_barra + int(100/len(lista_BANK))
              progress_bar.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
            except APIError as e:
                # Check if the error is related to quota being exceeded
                if e.response.status_code == 429:
                  print("Quota exceeded, waiting 60 seconds...")
                  time.sleep(60)  # Wait for 60 seconds before retrying
                  # Retry the current iteration after waiting
                  if bank == oldBANK:
                    pass
                  else:
                    sheet.update(values=[[bank]], range_name=f'C{x}')
                  if owner == oldOWNER:
                    pass
                  else:
                    sheet.update(values=[[owner]], range_name=f'D{x}')
        #print(f'4{st.session_state['lista_id']}')
        conta_banco_cadastradas.update( values=[[bank]],range_name=f'B{id_selecionada2}')
        conta_banco_cadastradas.update(values=[[owner]],range_name=f'C{id_selecionada2}')
        
        #print("alterações efetuadas com sucesso na tabela de contas contábeis")
        st.success(textos['ALTERACOES_EFETUADAS_TEXT'])
        st.session_state['lista_id_BANK'] = []
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
  listcategorias = tabela_contas_cont['CATEGORIA'].unique().tolist()
  st.title(textos['CONTASCONTABEISTEXT'])
  inativos_contas_cont, ativos_contas_cont = st.columns(2)
  with inativos_contas_cont:
    st.write(textos['INATIVAS_TEXT'])
    st.dataframe(tabela_contas_cont_inativa, height=500)
    col11, col12 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col11:
        id_selecionada_cont = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_contas_cont_inativa.index), key="idcont")
    with col12:
        if st.button(textos['ATIVAR_TEXT']):
          conta_cont_cadastradas.update_acell(f'D{id_selecionada_cont}', True)
          st.rerun()
    with st.form(clear_on_submit=True,key="Inserir nova conta contabil"):
      st.write(textos['NOVA_CONTA_CONTÁBIL_TEXT'])
      nome1,cat, atr,but =st.columns((0.3,0.3,0.25,0.15), vertical_alignment='bottom')
      with nome1:
        new_conta = st.text_input(textos['CONTA_CONTÁBIL_TEXT'])
        new_conta = str(new_conta)
        new_conta = new_conta.upper()
      with cat:
        new_cat = st.selectbox(textos['CATEGORIA_TEXT'], options =listcategorias,accept_new_options=True)
        new_cat = str(new_cat)
        new_cat = new_cat.upper()
      with atr:
        new_atr = st.selectbox(textos['ATRIBUIÇÃO_TEXT'],['DESPESAS','RECEITAS','ANALÍTICA'], index=0)
        new_atr = str(new_atr)
        new_atr = new_atr.upper()
      with but:
        submit = st.form_submit_button(label=textos['INSERIRTEXT'])
        if submit: #st.button('INSERIR NOVA CONTA'):
          if tamanho_tabela_contas_cont > 2:
            conta_cont_cadastradas.add_rows(1)
          conta_cont_cadastradas.update_acell(f'A{tamanho_tabela_contas_cont}', f'=ROW(B{tamanho_tabela_contas_cont})')
          conta_cont_cadastradas.update_acell(f'B{tamanho_tabela_contas_cont}', new_conta)
          conta_cont_cadastradas.update_acell(f'C{tamanho_tabela_contas_cont}', new_cat)
          conta_cont_cadastradas.update_acell(f'E{tamanho_tabela_contas_cont}', True)
          conta_cont_cadastradas.update_acell(f'D{tamanho_tabela_contas_cont}', new_atr)
          st.rerun()
    
  with ativos_contas_cont:
    st.write(textos['ATIVAS_TEXT'])
    st.dataframe(tabela_contas_cont_ativa, height=500)
    col01, col02 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col01:
        if pd.isna(tabela_contas_cont_ativa.index.max()):
          id_selecionada3 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], options=None, key="four")
        else:
          id_selecionada3 = int(st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_contas_cont_ativa.index), key="five"))
    with col02:
        if st.button(textos['INATIVAR_TEXT']):
          conta_cont_cadastradas.update_acell(f'E{id_selecionada3}', False)
          st.rerun()

    with st.form(clear_on_submit=True, key='Editar conta contabil'):
      st.write(textos['EDITARTEXT']) 
      conta,cate,atr =st.columns(3, vertical_alignment='bottom')
      with conta:
        if len(tabela_contas_cont_ativa)<1:
          cont = st.text_input(textos['NOME_TEXT'],value=None, key="1")
        else:
          cont = st.text_input(textos['NOME_TEXT'],tabela_contas_cont.loc[id_selecionada3, "CONTA CONTÁBIL"])
        cont = str(cont)
        cont = cont.upper()
      with cate:
        if len(tabela_contas_cont_ativa)<1:
          categor = st.text_input(textos['CATEGORIA_TEXT'],value=None, key="2")
        else:
          categor = st.text_input(textos['CATEGORIA_TEXT'],tabela_contas_cont.loc[id_selecionada3, "CATEGORIA"])    
        categor = str(categor)
        categor = categor.upper()
      with atr:
        
        if len(tabela_contas_cont_ativa)<1:
          atrib = st.selectbox(textos['ATRIBUIÇÃO_TEXT'],['DESPESAS','RECEITAS','ANALÍTICA'], index=0)
        else:
          analiseslist = ['DESPESAS','RECEITAS','ANALÍTICA']
          idxanalises = tabela_contas_cont.loc[id_selecionada3, 'ATRIBUIÇÃO']
          idxanalises = analiseslist.index(idxanalises)
          atrib = st.selectbox(textos['ATRIBUIÇÃO_TEXT'],['DESPESAS','RECEITAS','ANALÍTICA'], index=idxanalises)    
        atrib = str(atrib)
        atrib = atrib.upper()
        st.session_state['IDSEL'] = id_selecionada3
      
        #submit = st.popover(label=textos['EDITARTEXT'])
        #with submit:
      print(f"NEW {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
      lancamentos_filtro = lançamentos[(lançamentos['LANÇAMENTO'] == cont) & (lançamentos['CATEGORIA'] == categor)]
      lancamentos_filtro_cartao = lançamentos_cartao[(lançamentos_cartao['LANÇAMENTO'] == cont) & (lançamentos_cartao['CATEGORIA'] == categor)]
      if 'lista_id' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id'] = []
      if 'lista_id2' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id2'] = []
      if 'lista_id_cart1' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_cart1'] = []
      if 'lista_id_cart2' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_cart2'] = []
      lista_id = lancamentos_filtro['ID'].tolist()
      lista_id_cart = lancamentos_filtro_cartao['ID'].tolist()
      if lista_id:  # só salva se houver algo
        st.session_state['lista_id'] = lista_id
      else:
        st.session_state['lista_id2'] = st.session_state['lista_id']
        st.session_state['lista_id'] = lista_id
      if lista_id_cart:  # só salva se houver algo
        st.session_state['lista_id_cart1'] = lista_id_cart
      else:
        st.session_state['lista_id_cart2'] = st.session_state['lista_id_cart1']
        st.session_state['lista_id_cart1'] = lista_id_cart
      
      totallançamentos = lancamentos_filtro.shape[0] + lancamentos_filtro_cartao.shape[0]


      st.write(f"{totallançamentos} {textos['LANCAMENTOS LOCALIZADOS']}")
      editar = st.form_submit_button(textos['EDITARTEXT'])
      #print(f'1{st.session_state['lista_id']}')
      #print(f'ID: {st.session_state['IDSEL']}')
      #print(id_selecionada3)
      #print(f'2{st.session_state['lista_id2']}')
      if editar:
        #print(f'3{st.session_state['lista_id']}')
        if not st.session_state['lista_id']:
          lista = st.session_state['lista_id2']
        else:
          lista = st.session_state['lista_id']
        oldcont = tabela_contas_cont.loc[id_selecionada3, "CONTA CONTÁBIL"]
        oldcateg = tabela_contas_cont.loc[id_selecionada3, "CATEGORIA"]
        oldatrib = tabela_contas_cont.loc[id_selecionada3, "ATRIBUIÇÃO"]
        if cont == oldcont and oldcateg == categor and oldatrib == atrib:
          pass
        else:
          progesso_barra = 0
          progress_bar = st.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
          for x in lista:
              try:
                if cont == oldcont:
                  pass
                else:
                  sheet.update(values=[[cont]], range_name=f'E{x}')
                if categor == oldcateg:
                  pass
                else:
                  sheet.update(values=[[categor]], range_name=f'F{x}')
                if atrib == oldatrib:
                  pass
                else:
                  sheet.update(values=[[atrib]], range_name=f'J{x}')
                time.sleep(0.5)
                progesso_barra = progesso_barra + int(100/len(lista))
                progress_bar.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
              except APIError as e:
                  # Check if the error is related to quota being exceeded
                  if e.response.status_code == 429:
                    print("Quota exceeded, waiting 60 seconds...")
                    time.sleep(60)  # Wait for 60 seconds before retrying
                    # Retry the current iteration after waiting
                    if cont == oldcont:
                      pass
                    else:
                      sheet.update(values=[[cont]], range_name=f'E{x}')
                    if categor == oldcateg:
                      pass
                    else:
                      sheet.update(values=[[categor]], range_name=f'F{x}')
                    if atrib == oldatrib:
                      pass
                    else:
                      sheet.update(values=[[atrib]], range_name=f'J{x}')
                    time.sleep(0.5)

          if not st.session_state['lista_id_cart1']:
            lista = st.session_state['lista_id_cart2']
          else:
            lista = st.session_state['lista_id_cart1']
          progesso_barra = 0
          progress_bar = st.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
          for x in lista:
              try:
                if cont == oldcont:
                  pass
                else:
                  sheet_cartao.update(values=[[cont]], range_name=f'E{x}')
                if categor == oldcateg:
                  pass
                else:
                  sheet_cartao.update(values=[[categor]], range_name=f'F{x}')
                if atrib == oldatrib:
                  pass
                else:
                  sheet_cartao.update(values=[[atrib]], range_name=f'J{x}')
                time.sleep(0.5)
                progesso_barra = progesso_barra + int(100/len(lista))
                progress_bar.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
              except APIError as e:
                  # Check if the error is related to quota being exceeded
                  if e.response.status_code == 429:
                    print("Quota exceeded, waiting 60 seconds...")
                    time.sleep(60)  # Wait for 60 seconds before retrying
                    # Retry the current iteration after waiting
                    if cont == oldcont:
                      pass
                    else:
                      sheet_cartao.update(values=[[cont]], range_name=f'E{x}')
                    if categor == oldcateg:
                      pass
                    else:
                      sheet_cartao.update(values=[[categor]], range_name=f'F{x}')
                    if atrib == oldatrib:
                      pass
                    else:
                      sheet_cartao.update(values=[[atrib]], range_name=f'J{x}')
                    time.sleep(0.5) 
          #print(f'4{st.session_state['lista_id']}')
          conta_cont_cadastradas.update( values=[[cont]],range_name=f'B{id_selecionada3}')
          conta_cont_cadastradas.update(values=[[categor]],range_name=f'C{id_selecionada3}')
          conta_cont_cadastradas.update(values=[[atrib]],range_name=f'D{id_selecionada3}')
          #print("alterações efetuadas com sucesso na tabela de contas contábeis")
          st.success(textos['ALTERACOES_EFETUADAS_TEXT'])
          st.session_state['lista_id'] = []
          st.rerun()

      
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


  st.title(textos['PROJETOS/EVENTOSTEXT'])
  proj_inativos, proj_ativos = st.columns(2)
  with proj_inativos:
    st.write(textos['INATIVAS_TEXT'])
    st.dataframe(tabela_evenproj_inativa, height=500)
    col21, col22 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col21:
        id_selecionada3 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_evenproj_inativa.index), key="select3")
    with col22:
        if st.button(textos['ATIVAR_TEXT'], key="123"):
          tabela_evenproj_sheet.update_acell(f'D{id_selecionada3}', True)
          st.rerun()
    with st.form(clear_on_submit=True, key="Inserir novo projeto / evento"):
      st.write(textos['NOVO_PROJECT_TEXT'])
      new_name = st.text_input(textos['NOME_TEXT'])
      new_name = str(new_name)
      new_name = new_name.upper()
      submit = st.form_submit_button(label=textos['INSERIRTEXT'])
      if submit: #st.button('INSERIR NOVA CONTA'):
        if tamanho_tabela_evenproj > 2:
          tabela_evenproj_sheet.add_rows(1)
        tabela_evenproj_sheet.update_acell(f'A{tamanho_tabela_evenproj}', f'=ROW(B{tamanho_tabela_evenproj})')
        tabela_evenproj_sheet.update_acell(f'B{tamanho_tabela_evenproj}', new_name)
        tabela_evenproj_sheet.update_acell(f'C{tamanho_tabela_evenproj}', True)
        tabela_evenproj_sheet.update_acell(f'D{tamanho_tabela_evenproj}', True)
        st.rerun()
    
  with proj_ativos:
    st.write(textos['ATIVAS_TEXT'])
    st.dataframe(tabela_evenproj_ativa, height=500)
    col31, col32 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col31:
        if pd.isna(tabela_evenproj_ativa.index.max()):
          id_selecionada5 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], options=None, key='5')
        else:
          id_selecionada5 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_evenproj_ativa.index))
    with col32:
        if st.button(textos['INATIVAR_TEXT'], key="1234"):
          tabela_evenproj_sheet.update_acell(f'D{id_selecionada5}', False)
          st.rerun()

    with st.form(clear_on_submit=True, key='Editar nome'):
      st.write(textos['EDITAR_PROJETO_EVENTO_TEXT']) 
      if pd.isna(tabela_evenproj_ativa.index.max()):
        nome = st.text_input(textos['NOME_TEXT'], value=None, key="7")
      else:
        nome = st.text_input(textos['NOME_TEXT'],tabela_evenproj_ativa.loc[id_selecionada5, 'NOME'])
      nome = str(nome)
      nome = nome.upper()
      st.session_state['IDSEL'] = id_selecionada5

      lancamentos_filtro_PROJECT = lançamentos[(lançamentos['PROJETO/EVENTO'] == nome)]
      lancamentos_filtro_cartao_PROJECT = lançamentos_cartao[(lançamentos_cartao['PROJETO/EVENTO'] == nome)]
      if 'lista_id_PROJECT' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_PROJECT'] = []
      if 'lista_id_PROJECT2' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_PROJECT2'] = []
      if 'lista_id_cart_PROJECT1' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_cart_PROJECT1'] = []
      if 'lista_id_cart_PROJECT2' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_cart_PROJECT2'] = []
      lista_id_PROJECT = lancamentos_filtro_PROJECT['ID'].tolist()
      lista_id_cart_PROJECT = lancamentos_filtro_cartao_PROJECT['ID'].tolist()
      if lista_id_PROJECT:  # só salva se houver algo
        st.session_state['lista_id_PROJECT'] = lista_id_PROJECT
      else:
        st.session_state['lista_id_PROJECT2'] = st.session_state['lista_id_PROJECT']
        st.session_state['lista_id_PROJECT'] = lista_id_PROJECT
      if lista_id_cart_PROJECT:  # só salva se houver algo
        st.session_state['lista_id_cart_PROJECT1'] = lista_id_cart_PROJECT
      else:
        st.session_state['lista_id_cart_PROJECT2'] = st.session_state['lista_id_cart_PROJECT1']
        st.session_state['lista_id_cart_PROJECT1'] = lista_id_cart_PROJECT
      
      totallançamentos_PROJECT = lancamentos_filtro_PROJECT.shape[0] + lancamentos_filtro_cartao_PROJECT.shape[0]


      st.write(f"{totallançamentos_PROJECT} {textos['LANCAMENTOS LOCALIZADOS']}")
      editar_PROJECT = st.form_submit_button(textos['EDITARTEXT'])
      if editar_PROJECT:
        #print(f'3{st.session_state['lista_id']}')
        if not st.session_state['lista_id_PROJECT']:
          lista_PROJECT = st.session_state['lista_id_PROJECT2']
        else:
          lista_PROJECT = st.session_state['lista_id_PROJECT']
        oldproject = tabela_evenproj_ativa.loc[id_selecionada5, 'NOME']
        if oldproject == nome:
          pass
        else:
          progesso_barra = 0
          progress_bar = st.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
          for x in lista_PROJECT:
              try:
                sheet.update(values=[[nome]], range_name=f'K{x}')
              except APIError as e:
                  # Check if the error is related to quota being exceeded
                if e.response.status_code == 429:
                  print("Quota exceeded, waiting 60 seconds...")
                  time.sleep(60)  # Wait for 60 seconds before retrying
                  # Retry the current iteration after waitin
                  sheet.update(values=[[nome]], range_name=f'K{x}')
                progesso_barra = progesso_barra + int(100/len(lista_PROJECT))
                progress_bar.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
          if not st.session_state['lista_id_cart_PROJECT1']:
            lista_PROJECT_CARD = st.session_state['lista_id_cart_PROJECT2']
          else:
            lista_PROJECT_CARD = st.session_state['lista_id_cart_PROJECT1']
          for x in lista_PROJECT_CARD:
              try:
                sheet_cartao.update(values=[[nome]], range_name=f'L{x}')
              except APIError as e:
                # Check if the error is related to quota being exceeded
                if e.response.status_code == 429:
                  print("Quota exceeded, waiting 60 seconds...")
                  time.sleep(60)  # Wait for 60 seconds before retrying
                  # Retry the current iteration after waiting
                  sheet_cartao.update(values=[[nome]], range_name=f'L{x}')
          #print(f'4{st.session_state['lista_id']}')
          tabela_evenproj_sheet.update( values=[[nome]],range_name=f'B{id_selecionada5}')
          #print("alterações efetuadas com sucesso na tabela de contas contábeis")
          st.success(textos['ALTERACOES_EFETUADAS_TEXT'])
          st.session_state['lista_id'] = []
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
  listaprop = tabela_cartoes['PROPRIETÁRIO'].unique().tolist()

  st.divider() 
  st.title(textos['CARTOES_DE_CREDITOTEXT'])
  card_inativos, card_ativos = st.columns(2)
  with card_inativos:
    st.write(textos['INATIVAS_TEXT'])
    st.dataframe(tabela_cartoes_inativa, height=500)
    col31, col32 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col31:
        id_selecionada4 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_cartoes_inativa.index), key ="select4")
    with col32:
        if st.button('ATIVAR', key="ativa cartões"):
          tabela_cartoes_sheet.update_acell(f'G{id_selecionada4}', True)
          st.rerun()
    with st.form(clear_on_submit=True, key="Inserir cartão"):
      st.write(textos['NOVO_CARTÃO_DE_CRÉDITO_TEXT'])
      nome1,prop2,but3 =st.columns((0.3,0.55,0.15), vertical_alignment='bottom')
      with nome1:
        new_card = st.text_input(textos['NOME_TEXT'], key="new card")
        new_card = str(new_card)
        new_card = new_card.upper()
      with prop2:
        newcardowner = st.selectbox(textos['PROPRIETÁRIO_TEXT'],options =listaprop,accept_new_options=True, key="new owner")
        newcardowner = str(newcardowner)
        newcardowner = newcardowner.upper()
      with but3:
        submit = st.form_submit_button(label=textos['INSERIRTEXT'])
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
    st.write(textos['ATIVAS_TEXT'])
    st.dataframe(tabela_cartoes_ativa, height=500)
    col41, col42 = st.columns([0.2,0.8], vertical_alignment='bottom')
    with col41:
        if pd.isna(tabela_cartoes_ativa.index.max()):
          id_selecionada6 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], options=None, key='10')
        else:
          id_selecionada6 = st.selectbox(textos['SELECIONAR_A_ID_TEXT'], list(tabela_cartoes_ativa.index))
    with col42:
        if st.button(textos['INATIVAR_TEXT'], key="inativar cartões"):
          tabela_cartoes_sheet.update_acell(f'G{id_selecionada6}', False)
          st.rerun()

    with st.form(clear_on_submit=True,key='Editar cartao'):
      st.write(textos['EDITAR_CARTÃO_DE_CRÉDITO_TEXT']) 
      if len(tabela_cartoes_ativa)<1:
        new_nome_card = st.text_input(textos['NOME_TEXT'], value=None, key="17")
      else:
        new_nome_card = st.text_input(textos['NOME_TEXT'],tabela_cartoes_ativa.loc[id_selecionada6, "CARTÃO"])
      new_nome_card = str(new_nome_card)
      new_nome_card = new_nome_card.upper()
      if len(tabela_cartoes_ativa)<1:
        new_nome_owner = st.text_input(textos['PROPRIETÁRIO_TEXT'], value=None, key="18")
      else:
        new_nome_owner = st.text_input(textos['PROPRIETÁRIO_TEXT'],tabela_cartoes_ativa.loc[id_selecionada6, 'PROPRIETÁRIO'], key="20")
      new_nome_owner = str(new_nome_owner)
      new_nome_owner = new_nome_owner.upper()

      st.session_state['IDSEL'] = id_selecionada6

      print(f"NEW {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
      lancamentos_filtro_CARD = lançamentos_cartao[(lançamentos_cartao['CARTÃO'] == new_nome_card) & (lançamentos_cartao['PROPRIETÁRIO'] == new_nome_owner)]
      if 'lista_id_CARD' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_CARD'] = []
      if 'lista_id_CARD2' not in st.session_state:  # só salva se houver algo
        st.session_state['lista_id_CARD2'] = []
      lista_id_CARD = lancamentos_filtro_CARD['ID'].tolist()
      if lista_id_CARD:  # só salva se houver algo
        st.session_state['lista_id_CARD'] = lista_id_CARD
      else:
        st.session_state['lista_id_CARD2'] = st.session_state['lista_id_CARD']
        st.session_state['lista_id_CARD'] = lista_id_CARD
      
      totallançamentos_CARD = lancamentos_filtro_CARD.shape[0]


      st.write(f"{totallançamentos_CARD} {textos['LANCAMENTOS LOCALIZADOS']}")



      
      submit = st.form_submit_button(label=textos['EDITARTEXT'])
    if submit:
      if not st.session_state['lista_id_CARD']:
        lista_CARD = st.session_state['lista_id_CARD2']
      else:
        lista_CARD = st.session_state['lista_id_CARD']
      oldCARD = tabela_cartoes_ativa.loc[id_selecionada6, "CARTÃO"]
      oldOWNER = tabela_cartoes_ativa.loc[id_selecionada6, 'PROPRIETÁRIO']

      if new_nome_card == oldCARD and new_nome_owner == oldOWNER:
        pass
      else:
        progesso_barra = 0
        progress_bar = st.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])
        for x in lista_CARD:
            try:
              if new_nome_card == oldCARD:
                pass
              else:
                sheet.update(values=[[new_nome_card]], range_name=f'C{x}')
              if new_nome_owner == oldOWNER:
                pass
              else:
                sheet.update(values=[[new_nome_owner]], range_name=f'D{x}')
                time.sleep(0.2)
                progesso_barra = progesso_barra + int(100/len(lista_CARD))
                progress_bar.progress(progesso_barra, text=textos['INSERINDO_INFORMAÇÕESTEXT'])     
            except APIError as e:
                # Check if the error is related to quota being exceeded
                if e.response.status_code == 429:
                  print("Quota exceeded, waiting 60 seconds...")
                  time.sleep(60)  # Wait for 60 seconds before retrying
                  # Retry the current iteration after waiting
                  if new_nome_card == oldCARD:
                    pass
                  else:
                    sheet.update(values=[[new_nome_card]], range_name=f'C{x}')
                  if new_nome_owner == oldOWNER:
                    pass
                  else:
                    sheet.update(values=[[new_nome_owner]], range_name=f'D{x}')
        #print(f'4{st.session_state['lista_id']}')
        tabela_cartoes_sheet.update( values=[[new_nome_card]],range_name=f'B{id_selecionada2}')
        tabela_cartoes_sheet.update(values=[[new_nome_owner]],range_name=f'C{id_selecionada2}')
        
        #print("alterações efetuadas com sucesso na tabela de contas contábeis")
        st.success(textos['ALTERACOES_EFETUADAS_TEXT'])
        st.session_state['lista_id_CARD'] = []
        st.rerun()