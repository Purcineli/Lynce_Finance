import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
from gspread.exceptions import APIError
import time
import plotly.express as px
import numpy as np
import math
from LYNCE import verificar_login
from TRADUTOR import traaducaoapp
from streamlit_cookies_manager import EncryptedCookieManager

st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.stop()

language_of_page = st.session_state.useridioma


idiomadasdisponiveis = ['PORTUGUÊS', 'ENGLISH', 'РУССКИЙ']
idxidioma = idiomadasdisponiveis.index(language_of_page)

cookies = EncryptedCookieManager(
    prefix="login_LYNCE",
    password="JAYTEST123"  # coloque sua senha forte aqui
)
if not cookies.ready():
    st.stop()

def logout():
    # Limpa session_state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
        
    # Limpa cookies
    cookies["logged_in"] = ""
    cookies["username"] = ""
    st.session_state.logged_in = False
    #cookies.set_expiry(0)   # 🔥 Faz o cookie expirar imediatamente
    cookies.save()

    
    st.success("Logout realizado com sucesso!")
    st.switch_page('LYNCE.py')
    # Atualiza a página, levando o usuário de volta para a tela de login

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
  lançamentos = sheet.get_all_values()
except APIError:
  st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
  time.sleep(tempo_espera)
  st.rerun()

hoje = pd.to_datetime(date.today()) 

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
  data_inicio = st.date_input(textos['DATA INICIAL TEXT'], date.today() - timedelta(days=30),format="DD/MM/YYYY")
  data_inicio = pd.to_datetime(data_inicio)
with col02:
  data_final = st.date_input(textos['DATA FINAL TEXT'], date.today(), format="DD/MM/YYYY")
  data_final = pd.to_datetime(data_final)





tamanho_tabela = len(lançamentos)
tamanho_tabela = lançamentos.shape[0] + 2
#maxid = lançamentos['ID'].max()
#maxid = int(maxid)
tamanho_tabela = tamanho_tabela
#st.write(maxid)
if tamanho_tabela==2:
   st.write("SEM LANÇAMENTOS")
   maxid = tamanho_tabela
else:


  lançamentos['BANCO'] = lançamentos['BANCO'].str.upper()
  lançamentos = lançamentos.set_index('ID')
  colunas = list(lançamentos.columns)


  colunas_selecionadas = st.multiselect(textos['SELECIONE_AS_COLUNAS_DA_TABELA_TEXT'], colunas, colunas,)
  contasbancarias_selecionadas = st.sidebar.multiselect(textos['SELECIONE_O_BANCOTEXT'],lançamentos['BANCO'].unique(),None)
  if not contasbancarias_selecionadas:
    contasbancarias_selecionadas = lançamentos['BANCO'].unique()
  contasconta_selecionadas = st.sidebar.multiselect(textos['SELECIONE_O_LANÇAMENTOTEXT'],lançamentos['LANÇAMENTO'].unique(),None)
  if not contasconta_selecionadas:
    contasconta_selecionadas = lançamentos['LANÇAMENTO'].unique()
  contascategoria_selecionadas = st.sidebar.multiselect(textos['SELECIONE_A_CATEGORIA_TEXT'],lançamentos['CATEGORIA'].unique(),None)
  if not contascategoria_selecionadas:
    contascategoria_selecionadas = lançamentos['CATEGORIA'].unique()
  pesqdescri = st.sidebar.text_input(textos['PESQUISAR_DESCRICAO_TEXT'])


  #lançamentos['VALOR'] = (
  #  lançamentos['VALOR']
  #  .str.replace('.', '', regex=False)        # Remove separador de milhar
  #  .str.replace(',', '.', regex=False)       # Converte vírgula decimal para ponto
#)
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(str).str.replace('.', '', regex=False)
  lançamentos['VALOR'] = lançamentos['VALOR'].str.replace(',', '.', regex=False)
  lançamentos['VALOR'] = pd.to_numeric(lançamentos['VALOR'], errors='coerce')
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(float)
  lançamentos = lançamentos[lançamentos['BANCO'].notna()]
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')
  lançamentos_conciliados = lançamentos[lançamentos['CONCILIADO']=="TRUE"]
  lançamentos_conciliados = lançamentos_conciliados.iloc[::-1]
  #lançamentos_conciliados = lançamentos_conciliados[['DATA','BANCO','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE']]
  lançamentos_conciliados = lançamentos_conciliados[(lançamentos_conciliados['DATA']>=data_inicio)&(lançamentos_conciliados['DATA']<=data_final)&(lançamentos_conciliados['BANCO'].isin(contasbancarias_selecionadas))&(lançamentos_conciliados['LANÇAMENTO'].isin(contasconta_selecionadas))&(lançamentos_conciliados['CATEGORIA'].isin(contascategoria_selecionadas))&(lançamentos_conciliados['DESCRIÇÃO'].str.contains(pesqdescri, case=False))]
  lançamentos_conciliados['DATA'] = lançamentos_conciliados['DATA'].dt.strftime('%d/%m/%Y')
  st.dataframe(lançamentos_conciliados[colunas_selecionadas])


  st.markdown(f'{textos['SALDO_TOTALTEXT']} R$ {lançamentos_conciliados['VALOR'].sum().round(2)}')

  #st.write(lançamentos_conciliados)
  lançamentos_nao_conciliados = lançamentos[(lançamentos['CONCILIADO'] == "FALSE") & (lançamentos['DATA'] <= data_final)]
  lançamentos_nao_conciliados['DATA'] = lançamentos_nao_conciliados['DATA'].dt.strftime('%d/%m/%Y')
  lançamentos_nao_conciliados = lançamentos_nao_conciliados[colunas_selecionadas]
  #lançamentos_nao_conciliados = lançamentos_nao_conciliados[['DATA','BANCO','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE']]
  if len(lançamentos_nao_conciliados) >0:
    st.divider()
    st.write(textos['VOCE_TEM_LANCAMENTOS_NAO_CONCILIADOS_TEXT'])

    st.write(lançamentos_nao_conciliados)
    col11, col12 = st.columns(2)
    with col11:
      if st.button(textos['CONCILIAR_TODOS_TEXT']):
        ids = pd.Series(lançamentos_nao_conciliados.index)
        ids = ids.tolist()
        for i in reversed(ids):
          sheet.update_acell(f'I{i}',True)
        st.success(textos['TODOS_OS_LANCAMENTOS_FORAM_CONCILIADOS_TEXT'])
        st.rerun()
      else:
        st.write()
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
        st.write(textos['Inserir_novo_registroTEXT'])
        with st.form(clear_on_submit=True,key="form_inserir", border=False):
            data = st.date_input(textos['DATATEXT'], date.today(), format="DD/MM/YYYY")
            banco = st.selectbox(textos['SELECIONE_O_BANCOTEXT'], bancos, index=None, placeholder="Selecione")
            despesa = st.selectbox(textos['SELECIONE_O_LANÇAMENTOTEXT'], contas, index=None, placeholder="Selecione")
            valor, estorno = st.columns(2, vertical_alignment="bottom")
            with valor:
               number = st.number_input(textos['INSIRA_O_VALORTEXT'], format="%0.2f")
            with estorno:
               estornolan = st.checkbox(textos['ESTORNOTEXT'], key="lançamento de estorno")
            descricao = st.text_input(textos['DESCRIÇÃOTEXT'])
            descricao = str(descricao)
            descricao = descricao.upper()
            proj = st.selectbox(textos['SELECIONE_O_PROJETOTEXT'], projetos, index=None)
            status = st.checkbox(textos['CONCILIADOTEXT'], key='conciliado_checkbox')
            analise = st.checkbox(textos['ANALÍTICATEXT'], key='lançamento analitico')
            submit = st.form_submit_button(label=textos['INSERIRTEXT'])
            

        if submit:
            if banco == None or despesa == None:
              st.warning(textos['Preencha_todos_os_camposTEXT'])
            else:
              if tamanho_tabela > 2:     
                sheet.add_rows(1)
              sheet.update_acell(f'A{tamanho_tabela}', f"=ROW(B{tamanho_tabela})")
              sheet.update_acell(f'B{tamanho_tabela}', data.strftime('%d/%m/%Y'))
              sheet.update_acell(f'C{tamanho_tabela}', banco.split(" / ")[0])
              sheet.update_acell(f'D{tamanho_tabela}', banco.split(" / ")[1])
              sheet.update_acell(f'E{tamanho_tabela}', despesa.split(" / ")[0])
              sheet.update_acell(f'F{tamanho_tabela}', despesa.split(" / ")[1])
              if analise:
                analise = "ANALÍTICA"
                sheet.update_acell(f'G{tamanho_tabela}', number)
              else:
                analise = tabela_contas_cont_ativa.loc[(tabela_contas_cont_ativa['CONTA CONTÁBIL'] == despesa.split(" / ")[0])&(tabela_contas_cont_ativa['CATEGORIA'] == despesa.split(" / ")[1]),'ATRIBUIÇÃO'].values[0]
                if analise == "DESPESAS":
                  sheet.update_acell(f'G{tamanho_tabela}', -number)
                  if estornolan:
                    sheet.update_acell(f'G{tamanho_tabela}', number)
                elif analise == "RECEITAS":
                  sheet.update_acell(f'G{tamanho_tabela}', number)
                  if estornolan:
                    sheet.update_acell(f'G{tamanho_tabela}', -number)
              sheet.update_acell(f'H{tamanho_tabela}', descricao)
              sheet.update_acell(f'I{tamanho_tabela}', status)
              sheet.update_acell(f'J{tamanho_tabela}', analise)
              sheet.update_acell(f'K{tamanho_tabela}', proj)
              moeda = tabela_contas_banco_ativa.loc[(tabela_contas_banco_ativa['NOME BANCO'] == banco.split(" / ")[0])&(tabela_contas_banco_ativa['PROPRIETÁRIO'] == banco.split(" / ")[1]),'MOEDA'].values[0]
              sheet.update_acell(f'L{tamanho_tabela}', moeda)
              sheet.update_acell(f'M{tamanho_tabela}', st.session_state.name)
              sheet.update_acell(f'N{tamanho_tabela}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
              st.success(textos['Registro_inserido_com_sucessoTEXT'])
              st.rerun()
    with editar:
        st.write(textos['Editar_registroTEXT'])
        subcol1,subcol2 = st.columns(2)
        if tamanho_tabela==2:
           st.write(textos['INSERIR_NOVO_LANÇAMENTOTEXT']),
        else:
          with subcol1:
            id_selected = st.number_input(textos['Digite_o_IDTEXT'], min_value=2, max_value=tamanho_tabela-1, step=1, format="%d", value=None)
          with subcol2:
            if id_selected == None:
              data2 = st.date_input(textos['DATATEXT'],value=None)
            else:
              data2 = st.date_input(textos['DATATEXT'],value=lançamentos.loc[str(id_selected), 'DATA'])
          with st.form(clear_on_submit=True, key="form_editar", border=False):
            contas.append('TRANSFERÊNCIA / TRANSFERÊNCIA')
            if id_selected == None:
              idxbanco = None
              idxdespesas = None
            else:
              try:
                idxbanco = lançamentos.loc[str(id_selected), 'BANCO'] + " / " + lançamentos.loc[str(id_selected), 'PROPRIETÁRIO']
                idxbanco = bancos.index(idxbanco)
              except:
                idxbanco = None
              try:
                idxdespesas = lançamentos.loc[str(id_selected), 'LANÇAMENTO'] + " / " + lançamentos.loc[str(id_selected), 'CATEGORIA']
                idxdespesas = contas.index(idxdespesas)
              except:
                idxdespesas = None
            banco2 = st.selectbox(textos['SELECIONE_O_BANCOTEXT'], bancos, index=idxbanco, placeholder="Selecione")
            despesa2 = st.selectbox(textos['SELECIONE_O_LANÇAMENTOTEXT'], contas, index=idxdespesas, placeholder="Selecione", )
            if id_selected == None:
              valor2, estorno2 = st.columns(2, vertical_alignment="bottom")
              with valor2:
                number2 = st.number_input(textos['INSIRA_O_VALORTEXT'], format="%0.2f", value=None)
              with estorno2:
                estornolan2 = st.checkbox(textos['ESTORNOTEXT'], key="lançamento de estorno2", value=False)
              descricao2 = st.text_input(textos['DESCRIÇÃOTEXT'], value=None)
              proj2 = st.selectbox(textos['SELECIONE_O_PROJETOTEXT'], projetos, index=None)
              status2 = st.checkbox(textos['CONCILIADOTEXT'], key='conciliado_checkbox_EDITOR', value=None)
              analise2 = st.checkbox(textos['ANALÍTICATEXT'], key='lançamento analitico2')
            else:
              checkanalise = tabela_contas_cont_ativa.loc[(tabela_contas_cont_ativa['CONTA CONTÁBIL'] == despesa2.split(" / ")[0])&(tabela_contas_cont_ativa['CATEGORIA'] == despesa2.split(" / ")[1]),'ATRIBUIÇÃO'].values[0]
              valor2, estorno2 = st.columns(2, vertical_alignment="bottom")
              with valor2:
                number2 = st.number_input(textos['INSIRA_O_VALORTEXT'], format="%0.2f", value=abs(lançamentos.loc[str(id_selected), 'VALOR']))
                numbercalc = lançamentos.loc[str(id_selected), 'VALOR']
              with estorno2:
                if checkanalise == "DESPESAS" and numbercalc > 0:
                  estornolan2 = st.checkbox(textos['ESTORNOTEXT'], key="lançamento de estorno2", value=True)
                elif checkanalise == "RECEITAS" and numbercalc < 0:
                  estornolan2 = st.checkbox(textos['ESTORNOTEXT'], key="lançamento de estorno2", value=True)
                else:
                  estornolan2 = st.checkbox(textos['ESTORNOTEXT'], key="lançamento de estorno2", value=False)
              descricao2 = st.text_input(textos['DESCRIÇÃOTEXT'], value=lançamentos.loc[str(id_selected), 'DESCRIÇÃO'])
              proj2 = st.selectbox(textos['SELECIONE_O_PROJETOTEXT'], projetos, index=None)
              status2 = st.checkbox(textos['CONCILIADOTEXT'], key='conciliado_checkbox_EDITOR', value=lançamentos.loc[str(id_selected), 'CONCILIADO'])
              analise2 = st.checkbox(textos['ANALÍTICATEXT'], key='lançamento analitico2')
            subcol3, subcol4 = st.columns(2)
            with subcol3:   
              Submit_edit = st.form_submit_button(label=textos['EDITARTEXT'])
            with subcol4:
              Submit_delete = st.form_submit_button(label=textos['DELETARTEXT'])

            if Submit_delete:
                sheet.delete_rows(id_selected)
                st.success(textos['Registro_deletado_com_sucessoTEXT'])
                st.rerun()

            if Submit_edit:
                sheet.update_acell(f'B{id_selected}', data2.strftime('%d/%m/%Y'))
                sheet.update_acell(f'C{id_selected}', banco2.split(" / ")[0])
                sheet.update_acell(f'D{id_selected}', banco2.split(" / ")[1])
                sheet.update_acell(f'E{id_selected}', despesa2.split(" / ")[0])
                sheet.update_acell(f'F{id_selected}', despesa2.split(" / ")[1])
                if analise2:
                  analise2 = "ANALÍTICA"
                  sheet.update_acell(f'G{tamanho_tabela}', number2)
                  print(1)
                else:
                  analise2 = tabela_contas_cont_ativa.loc[(tabela_contas_cont_ativa['CONTA CONTÁBIL'] == despesa2.split(" / ")[0])&(tabela_contas_cont_ativa['CATEGORIA'] == despesa2.split(" / ")[1]),'ATRIBUIÇÃO'].values[0]
                  if analise2 == "DESPESAS":
                    if estornolan2:
                      sheet.update_acell(f'G{id_selected}', number2)
                      print(3)
                    else:
                      sheet.update_acell(f'G{id_selected}', -number2)
                      print(2)
                    
                  elif analise2 == "RECEITAS":
                    if estornolan2:
                      sheet.update_acell(f'G{id_selected}', -number2)
                      print(5)                   
                    else:
                      sheet.update_acell(f'G{id_selected}', number2)
                      print(4)

                
                descricao2 = str(descricao2)
                descricao2 = descricao2.upper()
                sheet.update_acell(f'H{id_selected}', descricao2)
                sheet.update_acell(f'I{id_selected}', status2)
                if analise2:
                   sheet.update_acell(f'J{id_selected}', "ANALÍTICA")
                sheet.update_acell(f'K{id_selected}', proj2)
                sheet.update_acell(f'M{id_selected}', st.session_state.name)
                sheet.update_acell(f'N{id_selected}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                st.success(textos['Registro_editado_com_sucessoTEXT'])
                st.rerun()  


Alt_lançamentos()
st.divider()

transf, pagarfatura = st.columns(2, vertical_alignment='top')

def inserir_lançamento():
    with transf:
        st.write(textos['Inserir_nova_transferência_entre_contasTEXT'])
        with st.form(clear_on_submit=True, key="form_inserir_transf", border=False):
            data_transf = st.date_input(textos['DATATEXT'], date.today(),format="DD/MM/YYYY")
            banco_origem = st.selectbox(textos['SELECIONE_O_BANCO_DE_ORIGEMTEXT'], bancos, index=None, placeholder="Selecione", key="banco_origem")
            banco_destino = st.selectbox(textos['SELECIONE_O_BANCO_DE_DESTINOTEXT'], bancos, index=None, placeholder="Selecione", key="banco_destino")
            valor = st.number_input(textos['INSIRA_O_VALORTEXT'], format="%0.2f", key="valor_transf")
            inserir_transf = st.form_submit_button(label=textos['INSERIRTEXT'])

            if inserir_transf:
                if banco_origem == banco_destino:
                    st.warning(textos['Selecione_contas_diferentesTEXT'])
                elif banco_origem is None or banco_destino is None or valor == 0:
                    st.warning(textos['Preencha_todos_os_camposTEXT'])
                else:
                    # Linhas onde os dados serão inseridos
                    linha_origem = tamanho_tabela 
                    linha_destino = tamanho_tabela + 1

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

                    st.success(textos['Registro_inserido_com_sucessoTEXT'])
                    st.rerun()

inserir_lançamento()