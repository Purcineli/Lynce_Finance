import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime

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


lançamentos, workbook = lerdados(sheeitid, sheetname)
sheet = workbook.get_worksheet(0)
hoje = pd.to_datetime(date.today()) 

lançamentos = sheet.get_all_values()
lançamentos = pd.DataFrame(lançamentos[1:], columns=lançamentos[0])
#CONTAS BANCÁRIAS#
conta_banco_cadastradas = workbook.get_worksheet(2)
tabela_contas_banco = conta_banco_cadastradas.get_all_values()
tabela_contas_banco = pd.DataFrame(tabela_contas_banco[1:], columns=tabela_contas_banco[0])
tabela_contas_banco = tabela_contas_banco.set_index('ID')
tabela_contas_banco_ativa = tabela_contas_banco[tabela_contas_banco['ATIVO']=='TRUE']
tabela_contas_banco_ativa = tabela_contas_banco_ativa[['NOME BANCO','PROPRIETÁRIO','MOEDA']]
tamanho_tabela_contas_banco = len(tabela_contas_banco)+2
#CONTAS CONTÁBEIS#
conta_cont_cadastradas = workbook.get_worksheet(3)
tabela_contas_cont = conta_cont_cadastradas.get_all_values()
tabela_contas_cont = pd.DataFrame(tabela_contas_cont[1:], columns=tabela_contas_cont[0])
tabela_contas_cont = tabela_contas_cont.set_index('ID')
tabela_contas_cont_ativa = tabela_contas_cont[tabela_contas_cont['ATIVO']=='TRUE']
tabela_contas_cont_ativa = tabela_contas_cont_ativa[['CONTA CONTÁBIL','CATEGORIA','ATRIBUIÇÃO']]
tamanho_tabela_contas_cont = len(tabela_contas_cont)+2

#PROJETOS#
tabela_evenproj_sheet = workbook.get_worksheet(5)
tabela_evenproj = tabela_evenproj_sheet.get_all_values()
tabela_evenproj = pd.DataFrame(tabela_evenproj[1:], columns=tabela_evenproj[0])
tabela_evenproj = tabela_evenproj.set_index('ID')
tabela_evenproj_ativa = tabela_evenproj[tabela_evenproj['ATIVO']=='TRUE']
tabela_evenproj_inativa = tabela_evenproj[tabela_evenproj['ATIVO']=='FALSE']
tamanho_tabela_evenproj = len(tabela_evenproj_ativa)+2


st.divider()

col01, col02 = st.columns(2)
with col01:
  data_inicio = st.date_input("Data Inicial", date.today() - timedelta(days=30))
  data_inicio = pd.to_datetime(data_inicio)
with col02:
  data_final = st.date_input("Data Final", date.today())
  data_final = pd.to_datetime(data_final)


tamanho_tabela = len(lançamentos)
tamanho_tabela = lançamentos.shape[0] + 2
if tamanho_tabela==2:
   st.write("SEM LANÇAMENTOS")
   maxid = 0
else:
  maxid = lançamentos['ID'].max()
  maxid = int(maxid)
  tamanho_tabela = tamanho_tabela - 1
  lançamentos['BANCO'] = lançamentos['BANCO'].str.upper()
  lançamentos = lançamentos.set_index('ID')
  colunas = list(lançamentos.columns)
  colunas_selecionadas = st.multiselect('Selecione as colunas da tabela:', colunas, colunas,)

  contasbancarias_selecionadas = st.sidebar.multiselect('Selecione o banco',lançamentos['BANCO'].unique(),None)
  if not contasbancarias_selecionadas:
    contasbancarias_selecionadas = lançamentos['BANCO'].unique()

  contasconta_selecionadas = st.sidebar.multiselect('Selecione o tipo de lançamento',lançamentos['LANÇAMENTO'].unique(),None)
  if not contasconta_selecionadas:
    contasconta_selecionadas = lançamentos['LANÇAMENTO'].unique()

  contascategoria_selecionadas = st.sidebar.multiselect('Selecione a categoria',lançamentos['CATEGORIA'].unique(),None)
  if not contascategoria_selecionadas:
    contascategoria_selecionadas = lançamentos['CATEGORIA'].unique()

  pesqdescri = st.sidebar.text_input('Pesquisar descrição')

  lançamentos['VALOR'] = pd.to_numeric(lançamentos['VALOR'], errors='coerce')
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(float)
  lançamentos = lançamentos[lançamentos['BANCO'].notna()]
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')
  lançamentos_conciliados = lançamentos[lançamentos['CONCILIADO']=="TRUE"]
  lançamentos_conciliados = lançamentos_conciliados.iloc[::-1]
  #lançamentos_conciliados = lançamentos_conciliados[['DATA','BANCO','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE']]
  lançamentos_conciliados = lançamentos_conciliados[(lançamentos_conciliados['DATA']>=data_inicio)&(lançamentos_conciliados['DATA']<=data_final)&(lançamentos_conciliados['BANCO'].isin(contasbancarias_selecionadas))&(lançamentos_conciliados['LANÇAMENTO'].isin(contasconta_selecionadas))&(lançamentos_conciliados['CATEGORIA'].isin(contascategoria_selecionadas))&(lançamentos_conciliados['DESCRIÇÃO'].str.contains(pesqdescri, case=False))]
  st.dataframe(lançamentos_conciliados[colunas_selecionadas])
  st.markdown(f'SALDO TOTAL: R$ {lançamentos_conciliados['VALOR'].sum().round(2)}')
  #st.write(lançamentos_conciliados)
  lançamentos_nao_conciliados = lançamentos[(lançamentos['CONCILIADO'] == "FALSE") & (lançamentos['DATA'] < hoje)]
  lançamentos_nao_conciliados = lançamentos_nao_conciliados[colunas_selecionadas]
  #lançamentos_nao_conciliados = lançamentos_nao_conciliados[['DATA','BANCO','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE']]
  if len(lançamentos_nao_conciliados) >0:
    st.divider()
    st.write('Você tem lançamentos não conciliados. Favor verificar.')
    st.write(lançamentos_nao_conciliados)
    col11, col12 = st.columns(2)
    with col11:
      if st.button("Conciliar todos"):
        ids = pd.Series(lançamentos_nao_conciliados.index)
        ids = ids.tolist()
        for i in reversed(ids):
          sheet.update_acell(f'I{i}',True)
        st.success("Todos os lançamentos foram conciliados!")
        st.rerun()
      else:
        st.write()
    with col12:
      st.button('Editar Lançamentos')
  else:
    st.write()



st.divider()

inserir, editar = st.columns(2, vertical_alignment='top')

tabela_contas_banco_ativa['BANCO_PROP'] = tabela_contas_banco_ativa["NOME BANCO"] + " / " + tabela_contas_banco_ativa["PROPRIETÁRIO"]
bancos = tabela_contas_banco_ativa['BANCO_PROP'].tolist()

tabela_contas_cont_ativa['CONT_CAT'] = tabela_contas_cont_ativa['CONTA CONTÁBIL'] + " / " + tabela_contas_cont_ativa["CATEGORIA"]
contas = tabela_contas_cont_ativa['CONT_CAT'].tolist()

projetos = tabela_evenproj_ativa['NOME'].tolist()
def Alt_lançamentos():
    with inserir:
        st.write("Inserir novo registro")
        with st.form(key="form_inserir", border=False):
            data = st.date_input('DATA', date.today())
            banco = st.selectbox('SELECIONE O BANCO', bancos, index=None, placeholder="Selecione")
            despesa = st.selectbox('SELECIONE A DESPESA', contas, index=None, placeholder="Selecione")
            number = st.number_input("INSIRA O VALOR", format="%0.2f")
            descricao = st.text_input('DESCRIÇÃO')
            descricao = str(descricao)
            descricao = descricao.upper()
            proj = st.selectbox('SELECIONE O PROJETO', projetos, index=None)
            status = st.checkbox('CONCILIADO', key='conciliado_checkbox')
            analise = st.checkbox("ANALÍTICA", key='lançamento analitico')
            submit = st.form_submit_button(label="INSERIR")

        if submit:
            if banco == None or despesa == None:
              st.warning("Preencha todos os campos")
            else:  
              sheet.add_rows(1)
              sheet.update_acell(f'A{tamanho_tabela}', f"=ROW(B{tamanho_tabela})")
              sheet.update_acell(f'B{tamanho_tabela}', data.strftime('%d/%m/%Y'))
              sheet.update_acell(f'C{tamanho_tabela}', banco.split(" / ")[0])
              sheet.update_acell(f'D{tamanho_tabela}', banco.split(" / ")[1])
              sheet.update_acell(f'E{tamanho_tabela}', despesa.split(" / ")[0])
              sheet.update_acell(f'F{tamanho_tabela}', despesa.split(" / ")[1])
              sheet.update_acell(f'G{tamanho_tabela}', number)
              sheet.update_acell(f'H{tamanho_tabela}', descricao)
              sheet.update_acell(f'I{tamanho_tabela}', status)
              if analise:
                 analise = "ANALÍTICA"
              else:
                 analise = tabela_contas_cont_ativa.loc[(tabela_contas_cont_ativa['CONTA CONTÁBIL'] == despesa.split(" / ")[0])&(tabela_contas_cont_ativa['CATEGORIA'] == despesa.split(" / ")[1]),'ATRIBUIÇÃO'].values[0]
              sheet.update_acell(f'J{tamanho_tabela}', analise)
              sheet.update_acell(f'K{tamanho_tabela}', proj)
              moeda = tabela_contas_banco_ativa.loc[(tabela_contas_banco_ativa['NOME BANCO'] == banco.split(" / ")[0])&(tabela_contas_banco_ativa['PROPRIETÁRIO'] == banco.split(" / ")[1]),'MOEDA'].values[0]
              sheet.update_acell(f'L{tamanho_tabela}', moeda)
              sheet.update_acell(f'M{tamanho_tabela}', st.session_state.name)
              sheet.update_acell(f'N{tamanho_tabela}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
              st.success("Registro inserido com sucesso!")
              st.rerun()
    with editar:
        st.write('Editar registro')
        subcol1,subcol2 = st.columns(2)
        if tamanho_tabela==2:
           st.write("INSERIR NOVO LANÇAMENTO"),
        else:
          with subcol1:
            id_selected = st.number_input('Digite o ID', min_value=0, max_value=maxid, step=1, format="%d", value=maxid)
          with subcol2:
            data2 = st.date_input('DATA',value=lançamentos.loc[str(id_selected), 'DATA'])
          with st.form(key="form_editar", border=False):
            contas.append('TRANSFERÊNCIA / TRANSFERÊNCIA')
            idxbanco = lançamentos.loc[str(id_selected), 'BANCO'] + " / " + lançamentos.loc[str(id_selected), 'PROPRIETÁRIO']
            idxbanco = bancos.index(idxbanco)
            banco2 = st.selectbox('SELECIONE O BANCO', bancos, index=idxbanco, placeholder="Selecione")
            try:
              idxdespesas = lançamentos.loc[str(id_selected), 'LANÇAMENTO'] + " / " + lançamentos.loc[str(id_selected), 'CATEGORIA']
              idxdespesas = contas.index(idxdespesas)
            except ValueError:
              idxdespesas = None
            despesa2 = st.selectbox('SELECIONE A DESPESA', contas, index=idxdespesas, placeholder="Selecione", )
            number2 = st.number_input("VALOR", format="%0.2f", value=abs(lançamentos.loc[str(id_selected), 'VALOR']))
            descricao2 = st.text_input('DESCRIÇÃO', value=lançamentos.loc[str(id_selected), 'DESCRIÇÃO'])
            proj2 = st.selectbox('SELECIONE O PROJETO', projetos, index=None)
            status2 = st.checkbox('CONCILIADO', key='conciliado_checkbox_EDITOR', value=lançamentos.loc[str(id_selected), 'CONCILIADO'])
            analise2 = st.checkbox("ANALÍTICA", key='lançamento analitico2')
            subcol3, subcol4 = st.columns(2)
            with subcol3:   
              Submit_edit = st.form_submit_button(label="EDITAR")
            with subcol4:
              Submit_delete = st.form_submit_button(label="DELETAR")

            if Submit_delete:
                sheet.delete_rows(id_selected)
                st.success("Registro deletado com sucesso!")
                st.rerun()

            if Submit_edit:
                sheet.update_acell(f'B{id_selected}', data2.strftime('%d/%m/%Y'))
                sheet.update_acell(f'C{id_selected}', banco2.split(" / ")[0])
                sheet.update_acell(f'D{id_selected}', banco2.split(" / ")[1])
                sheet.update_acell(f'E{id_selected}', despesa2.split(" / ")[0])
                sheet.update_acell(f'F{id_selected}', despesa2.split(" / ")[1])
                sheet.update_acell(f'G{id_selected}', number2)
                descricao2 = str(descricao2)
                descricao2 = descricao2.upper()
                sheet.update_acell(f'H{id_selected}', descricao2)
                sheet.update_acell(f'I{id_selected}', status2)
                if analise2:
                   sheet.update_acell(f'J{id_selected}', "ANALÍTICA")
                sheet.update_acell(f'K{id_selected}', proj2)
                sheet.update_acell(f'M{id_selected}', st.session_state.name)
                sheet.update_acell(f'N{id_selected}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                st.success("Registro editado com sucesso!")
                st.rerun()  


Alt_lançamentos()
st.divider()

transf, pagarfatura = st.columns(2, vertical_alignment='top')

def inserir_lançamento():
    with transf:
        st.write("Inserir nova transferência entre contas")
        with st.form(key="form_inserir_transf", border=False):
            data_transf = st.date_input('DATA', date.today())
            banco_origem = st.selectbox('SELECIONE O BANCO DE ORIGEM', bancos, index=None, placeholder="Selecione", key="banco_origem")
            banco_destino = st.selectbox('SELECIONE O BANCO DE DESTINO', bancos, index=None, placeholder="Selecione", key="banco_destino")
            valor = st.number_input("INSIRA O VALOR", format="%0.2f", key="valor_transf")
            inserir_transf = st.form_submit_button(label="INSERIR")

            if inserir_transf:
                if banco_origem == banco_destino:
                    st.warning("Selecione contas diferentes")
                elif banco_origem is None or banco_destino is None or valor == 0:
                    st.warning("Preencha todos os campos")
                else:
                    # Linhas onde os dados serão inseridos
                    linha_origem = tamanho_tabela + 1
                    linha_destino = tamanho_tabela + 2

                    # Informações comuns
                    data_str = data_transf.strftime('%d/%m/%Y')
                    hora_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                    usuario = st.session_state.name

                    banco_o_nome, banco_o_dono = banco_origem.split(" / ")
                    banco_d_nome, banco_d_dono = banco_destino.split(" / ")

                    moeda_origem = tabela_contas_banco_ativa.loc[
                        (tabela_contas_banco_ativa['NOME BANCO'] == banco_o_nome) &
                        (tabela_contas_banco_ativa['PROPRIETÁRIO'] == banco_o_dono),
                        'MOEDA'
                    ].values[0]

                    moeda_destino = tabela_contas_banco_ativa.loc[
                        (tabela_contas_banco_ativa['NOME BANCO'] == banco_d_nome) &
                        (tabela_contas_banco_ativa['PROPRIETÁRIO'] == banco_d_dono),
                        'MOEDA'
                    ].values[0]

                    # Linhas a serem atualizadas
                    valores = [
                        [f"=ROW(B{linha_origem})", data_str, banco_o_nome, banco_o_dono, "TRANSFERÊNCIA", "TRANSFERÊNCIA", -valor, "TRANSFERÊNCIA ENTRE CONTAS", True, "ANALÍTICA", "", moeda_origem, usuario, hora_str],
                        [f"=ROW(B{linha_destino})", data_str, banco_d_nome, banco_d_dono, "TRANSFERÊNCIA", "TRANSFERÊNCIA", valor, "TRANSFERÊNCIA ENTRE CONTAS", True, "ANALÍTICA", "", moeda_destino, usuario, hora_str]
                    ]

                    # Adiciona 2 linhas antes de atualizar
                    sheet.add_rows(2)
                    
                    # Atualiza as células de A:N nas duas linhas
                    cell_range = f"A{linha_origem}:N{linha_destino}"
                    sheet.update(cell_range, valores, raw=False)

                    st.success("Registro inserido com sucesso!")
                    st.rerun()

inserir_lançamento()