import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from gspread.exceptions import APIError
import time
from TRADUTOR import traaducaoapp
import plotly.express as px
import numpy as np
import math
from LYNCE import verificar_login
from zoneinfo import ZoneInfo


st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.switch_page('LYNCE.py')

idiomado_do_user = st.session_state.useridioma


idiomadasdisponiveis = ['PORTUGUÊS', 'ENGLISH', 'РУССКИЙ']
idxidioma = idiomadasdisponiveis.index(idiomado_do_user)
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

  st.sidebar.divider()

today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
with bemvido:
  st.write(f"{textos['BEMVINDO']} {st.session_state.name}!")
  
  sheeitid = st.session_state.id
  sheetname = st.session_state.arquivo
def lerdados(sheet_id_login_password,sheet_name_login_password):

  scopes = ["https://www.googleapis.com/auth/spreadsheets"]
  service_account_info = st.secrets["gcp_service_account"]
  creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
  client = gspread.authorize(creds)


  workbook = client.open_by_key(sheet_id_login_password)
  
  
  url = f"https://docs.google.com/spreadsheets/d/{sheet_id_login_password}/gviz/tq?tqx=out:csv&sheet={sheet_name_login_password}"

  dados_records = pd.read_csv(url, decimal='.', index_col=False)

  return dados_records,workbook

@st.cache_data(ttl=300)
def get_contas_bancarias(_workbook, sheet_index):
    conta_banco_cadastradas = _workbook.get_worksheet(sheet_index)
    tabela_contas_banco = conta_banco_cadastradas.get_all_values()
    return tabela_contas_banco

#import locale
#locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
tempo_espera = 5


try:
  lançamentos, workbook = lerdados(sheeitid, sheetname)
  sheet = workbook.get_worksheet(0)
  lançamentos = sheet.get_all_values()
except APIError:
  st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
  time.sleep(tempo_espera)
  st.rerun()
lançamentos = pd.DataFrame(lançamentos[1:], columns=lançamentos[0])
tamanho_tabela_lançamentos = lançamentos.shape[0] + 2
#CONTAS BANCÁRIAS#
tabela_contas_banco = get_contas_bancarias(workbook, 2)
tabela_contas_banco = pd.DataFrame(tabela_contas_banco[1:], columns=tabela_contas_banco[0])
tabela_contas_banco = tabela_contas_banco.set_index('ID')
tabela_contas_banco_ativa = tabela_contas_banco[tabela_contas_banco['ATIVO']=='TRUE']
tabela_contas_banco_ativa = tabela_contas_banco_ativa[['NOME BANCO','PROPRIETÁRIO','MOEDA']]
tamanho_tabela_contas_banco = len(tabela_contas_banco)+2

tabela_contas_banco_ativa['BANCO_PROP'] = tabela_contas_banco_ativa["NOME BANCO"] + " / " + tabela_contas_banco_ativa["PROPRIETÁRIO"]
bancos = tabela_contas_banco_ativa['BANCO_PROP'].tolist()
#CONTAS BANCÁRIAS#
lancamento_cartao = workbook.get_worksheet(1)

tabela_lancamentos_cartao = lancamento_cartao.get_all_values()

tabela_lancamentos_cartao = pd.DataFrame(tabela_lancamentos_cartao[1:], columns=tabela_lancamentos_cartao[0])

tabela_lancamentos_cartao = tabela_lancamentos_cartao.set_index('ID')
tabela_lancamentos_cartao.index = tabela_lancamentos_cartao.index.astype(int)
tamanhotabela_lancamento_cartao = tabela_lancamentos_cartao.index.max()
tabela_lancamentos_cartao = tabela_lancamentos_cartao.iloc[::-1]


tabela_lancamentos_cartao['FATURA'] = pd.to_datetime(tabela_lancamentos_cartao['FATURA'], dayfirst=True, errors='coerce')

tabela_lancamentos_cartao['VALOR'] = tabela_lancamentos_cartao['VALOR'].str.replace('.', '', regex=False)  # Remover pontos de milhar
tabela_lancamentos_cartao['VALOR'] = tabela_lancamentos_cartao['VALOR'].str.replace(',', '.', regex=False)  # Trocar vírgula por ponto decimal
tabela_lancamentos_cartao['VALOR'] = tabela_lancamentos_cartao['VALOR'].replace('', np.nan)
tabela_lancamentos_cartao['VALOR'] = tabela_lancamentos_cartao['VALOR'].astype(float)
tabela_lancamentos_cartao['VALOR'] = tabela_lancamentos_cartao['VALOR'].round(2)


contasconta_selecionadas = st.sidebar.multiselect(textos['SELECIONE_O_LANÇAMENTOTEXT'],tabela_lancamentos_cartao['LANÇAMENTO'].unique(),None)
if not contasconta_selecionadas:
   contasconta_selecionadas = tabela_lancamentos_cartao['LANÇAMENTO'].unique()

contascategoria_selecionadas = st.sidebar.multiselect(textos['SELECIONE_A_CATEGORIA_TEXT'],tabela_lancamentos_cartao['CATEGORIA'].unique(),None)
if not contascategoria_selecionadas:
   contascategoria_selecionadas = tabela_lancamentos_cartao['CATEGORIA'].unique()

pesqdescri = st.sidebar.text_input(textos['PESQUISAR_DESCRICAO_TEXT'])


hoje = pd.Timestamp.today()
primeiro_dia_mes_atual = hoje.replace(day=1)
primeiro_dia_mes_anterior = (primeiro_dia_mes_atual - pd.DateOffset(months=2))

tabela_filtrada = tabela_lancamentos_cartao[
    tabela_lancamentos_cartao['FATURA'] >= primeiro_dia_mes_anterior
].copy()

tabela_filtrada['FATURA_MES'] = tabela_filtrada['FATURA'].dt.to_period('M')
tabela_filtrada['CARTÃO'] = tabela_filtrada['CARTÃO'] + "  /  " + tabela_filtrada['PROPRIETÁRIO']
lista_faturas = list(tabela_lancamentos_cartao['FATURA'].dropna().unique())
#st.write(tabela_filtrada)
@st.cache_data(ttl=300)
def get_cartoes_bancarias(_workbook, sheet_index):
    cadastro_cartao = workbook.get_worksheet(sheet_index)
    tabela_cadastro_cartao = cadastro_cartao.get_all_values()
    return tabela_cadastro_cartao

tabela_cadastro_cartao = get_contas_bancarias(workbook, 4)

tabela_cadastro_cartao = pd.DataFrame(tabela_cadastro_cartao[1:], columns=tabela_cadastro_cartao[0])
tabela_cadastro_cartao = tabela_cadastro_cartao.set_index('ID')
tabela_cadastro_cartao_ATIVOS = tabela_cadastro_cartao[tabela_cadastro_cartao['ATIVO']=='TRUE']

saldo,lancamentos = st.columns([0.3,0.7],vertical_alignment='top')

faturas_cartao = tabela_filtrada.pivot_table(
  values='VALOR',
  index='CARTÃO',
  columns='FATURA_MES',
  aggfunc='sum'
).round(2)

faturas_cartao.columns = [col.strftime('%b/%Y') for col in faturas_cartao.columns.to_timestamp()]
faturas_cartao = faturas_cartao.replace(0, pd.NA)
faturas_cartao = faturas_cartao.dropna(axis=0, how='all')
faturas_cartao = faturas_cartao.dropna(axis=1, how='all')
faturas_cartao = faturas_cartao.fillna(0)
st.write(faturas_cartao)
VALORTOTAL = f"{faturas_cartao.values.sum().round(2):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
st.markdown(f'{textos['VALOR_TOTAL_À_PAGAR']} R$: {VALORTOTAL}')
#st.header(f"RECEITAS: R$ {lançamentos_conciliados_receitas['VALOR'].sum().round(2):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), divider="blue")
listas_cartoes = list(tabela_cadastro_cartao_ATIVOS['CARTÃO'].dropna().unique())
listas_owners = list(tabela_cadastro_cartao_ATIVOS['PROPRIETÁRIO'].dropna().unique())
colun1, colun2 = st.columns(2)
with colun1:
  lista_cartoes_selecionado = st.multiselect(textos['SELECIONE_TEXT'], listas_cartoes, default=listas_cartoes, key="1")
  numberofcard = len(lista_cartoes_selecionado)
  st.text(str(lista_cartoes_selecionado))
with colun2:
  lista_owners_selecionado = st.multiselect(textos['SELECIONE_TEXT'], listas_owners, default=listas_owners, key="2")
  numberofowners = len(lista_owners_selecionado)
  st.text(str(lista_owners_selecionado))

tabela_lancamentos_cartao_filtrada = tabela_lancamentos_cartao[
    (tabela_lancamentos_cartao['CARTÃO'].isin(lista_cartoes_selecionado))& 
    (tabela_lancamentos_cartao['PROPRIETÁRIO'].isin(lista_owners_selecionado))
]

tamanho_tabela = tabela_lancamentos_cartao.shape[0] + 2
if st.toggle(textos['CONCILIAR_FATURA']):
  if tamanho_tabela == 2:
    st.write(textos['INSERIR_LANCAMENTOS_TEXT'])
  else:
    # Criar coluna FATURA_MES para ordenação
    tabela_lancamentos_cartao_filtrada['FATURA_MES'] = tabela_lancamentos_cartao_filtrada['FATURA'].dt.to_period('M')

    # Obter lista de faturas no formato 'Abr/2025'
    lista_faturas = sorted(tabela_lancamentos_cartao_filtrada['FATURA_MES'].dropna().unique())
    lista_faturas_str = [f.strftime('%b/%Y') for f in pd.PeriodIndex(lista_faturas).to_timestamp()][::-1]

    hoje_str = hoje.strftime('%b/%Y')
    try:
        hojed = lista_faturas_str.index(hoje_str)
    except ValueError:
        hojed = 2  # valor padrão se hoje não estiver na lista

    # Selectbox para fatura
    if 'pesquisarbutton' not in st.session_state:
        st.session_state['fatura_str_l'] = False
    if 'fatura_str_l' not in st.session_state:
        st.session_state['fatura_str_l'] = ''
        fatura_str = st.selectbox("SELECIONE A FATURA", faturas_cartao.columns, index=0)
    else:
        try:
            indexfatura = faturas_cartao.columns.get_loc(st.session_state['fatura_str_l'])
            fatura_str = st.selectbox(textos['SELECIONE_A_FATURA_TEXT'], faturas_cartao.columns, index=indexfatura)
        except:
            fatura_str = st.selectbox(textos['SELECIONE_A_FATURA_TEXT'], faturas_cartao.columns, index=0)
  with st.form(clear_on_submit=True, key="forms"):
    st.session_state['fatura_str_l'] = fatura_str
    st.session_state['pesquisarbutton'] = True
    fatura_dt = pd.to_datetime(fatura_str, format='%b/%Y')
    fatura_period = fatura_dt.to_period('M')

    # Filtrar lançamentos pela fatura selecionada
    filtro = tabela_lancamentos_cartao_filtrada['FATURA_MES'] == fatura_period
    lancamentos_filtrados = tabela_lancamentos_cartao_filtrada[filtro].copy()

    lancamentos_filtrados['FATURA_MES'] = lancamentos_filtrados['FATURA_MES'].dt.strftime('%b/%Y')
    lancamentos_visual = lancamentos_filtrados[['DATA', 'CARTÃO', 'PROPRIETÁRIO', 'LANÇAMENTO', 'CATEGORIA', 'VALOR', 'DESCRIÇÃO', 'ANALISE', 'FATURA_MES', 'DATA COMPRA']].copy()
    lancamentos_visual = lancamentos_visual.rename(columns={'FATURA_MES': 'FATURA CARTÃO'})

    df_false = lancamentos_filtrados[lancamentos_filtrados['CONCILIADO'] == "FALSE"].copy()
    df_true = lancamentos_filtrados[lancamentos_filtrados['CONCILIADO'] == "TRUE"].copy()
    naoconc, conc = st.columns(2)
    with naoconc:
      df_false_display = df_false[['DATA COMPRA', 'LANÇAMENTO', 'VALOR', 'DESCRIÇÃO']].copy()
      df_false_display.insert(3, 'SELECIONAR', False)
      editar_false = st.data_editor(
          df_false_display,
          column_config={"SELECIONAR": st.column_config.CheckboxColumn('SELECT')},
          hide_index=False,
          height=500
      )
      st.markdown(f"**TOTAL:** {df_false['VALOR'].sum():,.2f}")
      conciliar = st.form_submit_button(textos['CONCILIAR_TEXT'])

      if conciliar:
          selected_rows = editar_false[editar_false["SELECIONAR"]]
          selected_indexes = selected_rows.index.tolist()
          print(f"2 - NEW {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
          print(selected_rows)
          print(selected_indexes)
          for idx in selected_indexes:
              lancamento_cartao.update_acell(f'I{int(idx)}', True)
          time.sleep(1)
          st.rerun()
    with conc:
      df_true_display = df_true[['DATA COMPRA', 'LANÇAMENTO', 'VALOR', 'DESCRIÇÃO']].copy()
      df_true_display.insert(3, 'SELECIONAR', False)
      editar_true = st.data_editor(
          df_true_display,
          column_config={"SELECIONAR": st.column_config.CheckboxColumn('SELECT')},
          hide_index=False,
          height=500,
          key="editdataframe"
      )
      selected_rows = editar_true[editar_true["SELECIONAR"]]
      st.markdown(f"**TOTAL:** {df_true['VALOR'].sum():,.2f}")

      DESCONCILIAR, PAGAR = st.columns(2)
      with DESCONCILIAR:
          desconciliar = st.form_submit_button(textos['DESCONCILIAR_TEXT'])
          if desconciliar:
              selected_indexes = selected_rows.index.tolist()
              for idx in selected_indexes:
                  lancamento_cartao.update_acell(f'I{int(idx)}', False)
              time.sleep(1)
              st.rerun()

      with PAGAR:
          with st.popover(textos['PAGAR_FATURA_TEXT']):
              fatura_data = datetime.strptime(fatura_str, '%b/%Y').replace(day=1)
              fatura_data_str = fatura_data.strftime('%Y-%m-%d')
              data = st.date_input(textos['DATATEXT'], today,format="DD/MM/YYYY")
              banco = st.selectbox(textos['SELECIONE_O_BANCOTEXT'], bancos, index=None, placeholder=textos['SELECIONE_TEXT'])
              number = abs(st.number_input(textos['INSIRA_O_VALORTEXT'], format="%0.2f", value=df_true['VALOR'].sum()))
              if numberofcard + numberofowners > 2:
                pagar_fatura = st.form_submit_button(textos['PAGAR_FATURA_TEXT'], disabled=True, help="Selecione apenas um cartão e proprietário")
              else:
                pagar_fatura = st.form_submit_button(textos['PAGAR_FATURA_TEXT'])

              if pagar_fatura:
                now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                row_cartao = [
                    f"=ROW(B{tamanho_tabela})",
                    data.strftime('%d/%m/%Y'),
                    lista_cartoes_selecionado,
                    lista_owners_selecionado,
                    "FATURA",
                    "CARTÃO DE CRÉDITO",
                    number,
                    f"PAGAMENTO FATURA CARTÃO REF. {fatura_str}",
                    True,
                    "ANALÍTICA",
                    fatura_data_str,
                    "",
                    "",
                    "BRL",
                    st.session_state.name,
                    now
                ]

                row_banco = [
                    f"=ROW(B{tamanho_tabela_lançamentos})",
                    data.strftime('%d/%m/%Y'),
                    banco.split(" / ")[0],
                    banco.split(" / ")[1],
                    "FATURA",
                    "CARTÃO DE CRÉDITO",
                    -number,
                    f"PAGAMENTO FATURA CARTÃO REF. {fatura_str}",
                    True,
                    "ANALÍTICA",
                    "",
                    "BRL",
                    st.session_state.name,
                    now
                ]

                if tamanho_tabela > 2:
                    lancamento_cartao.add_rows(1)
                lancamento_cartao.update(f'A{tamanho_tabela}:P{tamanho_tabela}', [row_cartao], raw=False)
                sheet.add_rows(1)
                sheet.update(f'A{tamanho_tabela_lançamentos}:O{tamanho_tabela_lançamentos}', [row_banco], raw=False)
                time.sleep(1)
                st.rerun()



          
else:
  dataini, datafim, optiondata =st.columns(3, vertical_alignment="center")
  with dataini:
    data_inicio = st.date_input(textos['DATA INICIAL TEXT'], today - timedelta(days=30), format="DD/MM/YYYY")
    data_inicio = pd.to_datetime(data_inicio,format="DD/MM/YYYY")
    
  with datafim:
    data_final = st.date_input(textos['DATA FINAL TEXT'], today, format="DD/MM/YYYY")
    data_final = pd.to_datetime(data_final)

  with optiondata:
     optionslist = (textos['DATA_DA_COMPRA_TEXT'],textos['DATA_DA_DESPESA_TEXT'])
     filterrecords = st.radio(label="opção", options=optionslist, label_visibility="hidden", index=0, horizontal=True)
     selected_indexradio = optionslist.index(filterrecords)

  tabela_lancamentos_cartao['DATA'] = pd.to_datetime(tabela_lancamentos_cartao['DATA'], dayfirst=True, errors='coerce')
  tabela_lancamentos_cartao['DATA COMPRA'] = pd.to_datetime(tabela_lancamentos_cartao['DATA COMPRA'], dayfirst=True, errors='coerce')
  tabela_lancamentos_cartao['FATURA'] = pd.to_datetime(tabela_lancamentos_cartao['FATURA'], dayfirst=True, errors='coerce')

  if selected_indexradio == 0:
    lançamentos_cartao_filtro_data = tabela_lancamentos_cartao[
      (tabela_lancamentos_cartao['DATA COMPRA'] >= data_inicio) &
      (tabela_lancamentos_cartao['DATA COMPRA'] <= data_final) &
      (tabela_lancamentos_cartao['LANÇAMENTO'].isin(contasconta_selecionadas))&
      (tabela_lancamentos_cartao['CATEGORIA'].isin(contascategoria_selecionadas))&
      (tabela_lancamentos_cartao['DESCRIÇÃO'].str.contains(pesqdescri, case=False))]
    lançamentos_cartao_filtro_data = lançamentos_cartao_filtro_data.sort_values(by='DATA COMPRA')
    lançamentos_cartao_filtro_data['DATA COMPRA'] = lançamentos_cartao_filtro_data['DATA COMPRA'].dt.strftime('%d/%m/%Y')
    lançamentos_cartao_filtro_data['DATA'] = lançamentos_cartao_filtro_data['DATA'].dt.strftime('%d/%m/%Y')
    lançamentos_cartao_filtro_data['FATURA'] = lançamentos_cartao_filtro_data['FATURA'].dt.strftime('%m/%Y')
    lançamentos_cartao_filtro_data= lançamentos_cartao_filtro_data[lançamentos_cartao_filtro_data.columns[[10,1,2,3,4,5,6,7,8,9,0,11,12,13,14]]]
  elif selected_indexradio == 1:
    lançamentos_cartao_filtro_data = tabela_lancamentos_cartao[
      (tabela_lancamentos_cartao['DATA'] >= data_inicio) &
      (tabela_lancamentos_cartao['DATA'] <= data_final) &
      (tabela_lancamentos_cartao['LANÇAMENTO'].isin(contasconta_selecionadas))&
      (tabela_lancamentos_cartao['CATEGORIA'].isin(contascategoria_selecionadas))&
      (tabela_lancamentos_cartao['DESCRIÇÃO'].str.contains(pesqdescri, case=False))]
    lançamentos_cartao_filtro_data = lançamentos_cartao_filtro_data.sort_values(by='DATA COMPRA')
    lançamentos_cartao_filtro_data['DATA COMPRA'] = lançamentos_cartao_filtro_data['DATA COMPRA'].dt.strftime('%d/%m/%Y')
    lançamentos_cartao_filtro_data['DATA'] = lançamentos_cartao_filtro_data['DATA'].dt.strftime('%d/%m/%Y')
    lançamentos_cartao_filtro_data['FATURA'] = lançamentos_cartao_filtro_data['FATURA'].dt.strftime('%m/%Y')


  st.write(lançamentos_cartao_filtro_data)

st.divider()


@st.cache_data(ttl=60)
def ler_dados_cartao(_workbook, sheet_index):
    try:
        cards_cont_cadastradas = workbook.get_worksheet(sheet_index)
        tabela_cards_cont = cards_cont_cadastradas.get_all_values()
        return tabela_cards_cont

    except APIError:
        st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
        time.sleep(tempo_espera)
        st.rerun()

@st.cache_data(ttl=60)
def ler_dados_contas(_workbook, sheet_index):
    try:
        conta_cont_cadastradas = workbook.get_worksheet(sheet_index)
        tabela_contas_cont = conta_cont_cadastradas.get_all_values()


        return tabela_contas_cont

    except APIError:
        st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
        time.sleep(tempo_espera)
        st.rerun()

@st.cache_data(ttl=60)
def ler_dados_projetos(_workbook, sheet_index):
    try:
        tabela_evenproj_sheet = workbook.get_worksheet(sheet_index)
        tabela_evenproj = tabela_evenproj_sheet.get_all_values()


        return tabela_evenproj

    except APIError:
        st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
        time.sleep(tempo_espera)
        st.rerun()

tabela_cards_cont = ler_dados_cartao(workbook, 4)
tabela_contas_cont = ler_dados_contas(workbook, 3)
tabela_evenproj = ler_dados_projetos(workbook, 5)

tabela_cards_cont = pd.DataFrame(tabela_cards_cont[1:], columns=tabela_cards_cont[0])
tabela_cards_cont = tabela_cards_cont.set_index('ID')
tabela_cards_cont = tabela_cards_cont[tabela_cards_cont['ATIVO']=='TRUE']
tabela_cards_cont = tabela_cards_cont[['CARTÃO','PROPRIETÁRIO','MOEDA','FECHAMENTO', 'VENCIMENTO']]
tamanho_tabela_contas_cards = len(tabela_cards_cont)+2


tabela_contas_cont = pd.DataFrame(tabela_contas_cont[1:], columns=tabela_contas_cont[0])
tabela_contas_cont = tabela_contas_cont.set_index('ID')
tabela_contas_cont_ativa = tabela_contas_cont[tabela_contas_cont['ATIVO']=='TRUE']
tabela_contas_cont_ativa = tabela_contas_cont_ativa[['CONTA CONTÁBIL','CATEGORIA', 'ATRIBUIÇÃO']]
tamanho_tabela_contas_cont = len(tabela_contas_cont)+2

#PROJETOS#

tabela_evenproj = pd.DataFrame(tabela_evenproj[1:], columns=tabela_evenproj[0])
tabela_evenproj = tabela_evenproj.set_index('ID')
tabela_evenproj_ativa = tabela_evenproj[tabela_evenproj['ATIVO']=='TRUE']
tabela_evenproj_inativa = tabela_evenproj[tabela_evenproj['ATIVO']=='FALSE']
tamanho_tabela_evenproj = len(tabela_evenproj_ativa)+2

#tamanho_tabela = len(tabela_lancamentos_cartao)


inserir, editar = st.columns(2, vertical_alignment='top')

tabela_cards_cont['CARTÃO_PROP'] = tabela_cards_cont["CARTÃO"] + " / " + tabela_cards_cont["PROPRIETÁRIO"]
cards = tabela_cards_cont['CARTÃO_PROP'].tolist()

tabela_contas_cont_ativa['CONT_CAT'] = tabela_contas_cont_ativa['CONTA CONTÁBIL'] + " / " + tabela_contas_cont_ativa["CATEGORIA"]
contas = tabela_contas_cont_ativa['CONT_CAT'].tolist()

projetos = tabela_evenproj_ativa['NOME'].tolist()

def Alt_lançamentos_CC():
    with inserir:
        st.write(textos['Inserir_novo_registroTEXT'])
        with st.form(clear_on_submit=True, key="form_inserir", border=False):
            data = st.date_input(textos['DATATEXT'], today, format="DD/MM/YYYY")
            cart = st.selectbox(textos['SELECIONE_O_CARTAO_TEXT'], cards, index=None, placeholder="Selecione")
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
            dt,fat = st.columns(2)
            with dt:
              parcelas = st.number_input(textos['NUMERO_DE_PARCELAS_TEXT'],1,36)
            with fat:
              
              data2 = st.date_input(textos['FATURA_TEXT'], today,format="DD/MM/YYYY")
              
            submit = st.form_submit_button(label=textos['INSERIRTEXT'])

        if submit:
          if cart == None or despesa == None or analise == None:
            st.warning(textos['Preencha_todos_os_camposTEXT'])
          else:
            linhas = []  # Lista para armazenar as linhas a serem inseridas
            for x in range(parcelas):
                data_parcela = (data + relativedelta(months=x)).strftime('%d/%m/%Y')
                data_compra = data.strftime('%d/%m/%Y')
                data_fatura = (data2.replace(day=1) + relativedelta(months=x)).strftime('%d/%m/%Y')
                valor_parcela = round(number / parcelas, 2)
                moeda = tabela_cards_cont.loc[
                    (tabela_cards_cont['CARTÃO'] == cart.split(" / ")[0]) &
                    (tabela_cards_cont['PROPRIETÁRIO'] == cart.split(" / ")[1]),
                    'MOEDA'
                ].values[0]
                descricao_formatada = f'{descricao}  {x+1}/{parcelas}'
                timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                row = f"=ROW(B{tamanho_tabela + x})"
                if analise:
                    analise_valor = "ANALÍTICA"
                else:
                    analise_valor = tabela_contas_cont_ativa.loc[
                        (tabela_contas_cont_ativa['CONTA CONTÁBIL'] == despesa.split(" / ")[0]) &
                        (tabela_contas_cont_ativa['CATEGORIA'] == despesa.split(" / ")[1]),
                        'ATRIBUIÇÃO'
                    ].values[0]
                print(analise)
                if analise_valor == "DESPESAS":
                  if estornolan:
                    valor_parcela = round(number / parcelas, 2)
                  else:
                    valor_parcela = round(-number / parcelas, 2)
                else:
                  if estornolan:
                    valor_parcela = round(-number / parcelas, 2)
                  else:
                    valor_parcela = round(number / parcelas, 2)



                linha = [
                    row,                               # A - Row 
                    data_parcela,                      # B - Data
                    cart.split(" / ")[0],              # C - Cartão
                    cart.split(" / ")[1],              # D - Proprietário
                    despesa.split(" / ")[0],           # E - Despesa
                    despesa.split(" / ")[1],           # F - Tipo de despesa
                    valor_parcela,                     # G - Valor
                    descricao_formatada,               # H - Descrição
                    status,                            # I - Conciliado
                    analise_valor,                     # J - Alínea
                    data_fatura,                       # K - Data base
                    data_compra,                       # L - DATA COMPRA 
                    proj,                              # M - PROJETO
                    moeda,                             # N - Moeda
                    st.session_state.name,             # O - Usuário
                    timestamp                          # P - Timestamp
                ]
                linhas.append(linha)

            # Calcular a faixa de células que será atualizada
            if tamanho_tabela > 2:
              lancamento_cartao.add_rows(parcelas)
            else: 
              lancamento_cartao.add_rows(parcelas-1)
            inicio_linha = tamanho_tabela 
            fim_linha = inicio_linha + parcelas - 1
            faixa = f"A{inicio_linha}:P{fim_linha}"

            # Atualizar todas as linhas de uma vez só
            lancamento_cartao.update(values=linhas,range_name=faixa,raw=False)

            st.success(textos['Registro_inserido_com_sucessoTEXT'])
            st.rerun()
    with editar:
        st.write(textos['Editar_registroTEXT'])
        subcol1,subcol2 = st.columns(2)
        if tamanho_tabela==2:
           st.write(textos['INSERIR_NOVO_LANÇAMENTOTEXT'])
        else:
          with subcol1:
            id_selected = st.number_input(textos['Digite_o_IDTEXT'], min_value=0, max_value=tamanhotabela_lancamento_cartao, step=1, format="%d", value=None)
          if id_selected == None:
            idxbanco = None
          else:
            with subcol2:
              data_raw = tabela_lancamentos_cartao.loc[id_selected, 'FATURA']
              data2 = st.date_input(textos['DATATEXT'], value=pd.to_datetime(data_raw).date(),format="DD/MM/YYYY")
              data2 = data2.replace(day=1).strftime('%d/%m/%Y')
              
            idxbanco = tabela_lancamentos_cartao.loc[id_selected, 'CARTÃO'] + " / " + tabela_lancamentos_cartao.loc[id_selected, 'PROPRIETÁRIO']
            idxbanco = cards.index(idxbanco)
          
            
            banco2 = st.selectbox(textos['SELECIONE_O_BANCOTEXT'], cards, index=idxbanco, placeholder="Selecione")
            try:
              idxdespesas = tabela_lancamentos_cartao.loc[id_selected, 'LANÇAMENTO'] + " / " + tabela_lancamentos_cartao.loc[id_selected, 'CATEGORIA']
              idxdespesas = contas.index(idxdespesas)
            except ValueError:
              idxdespesas = None
            despesa2 = st.selectbox(textos['SELECIONE_O_LANÇAMENTOTEXT'], contas, index=idxdespesas, placeholder="Selecione", )
            number2 = st.number_input(textos['INSIRA_O_VALORTEXT'], format="%0.2f", value=tabela_lancamentos_cartao.loc[id_selected, 'VALOR'])
            descricao2 = st.text_input(textos['DESCRIÇÃOTEXT'], value=tabela_lancamentos_cartao.loc[id_selected, 'DESCRIÇÃO'])

            proj2 = st.selectbox(textos['SELECIONE_O_PROJETOTEXT'], projetos, index=None)
            status2 = st.checkbox(textos['CONCILIADOTEXT'], key='conciliado_checkbox_EDITOR', value=tabela_lancamentos_cartao.loc[id_selected, 'CONCILIADO'])
            analise2 = st.checkbox(textos['ANALÍTICATEXT'], key='lançamento analitico2')
            subcol3, subcol4 = st.columns(2)
            with subcol3:   
              Submit_edit = st.button(label=textos['EDITARTEXT'])
            with subcol4:
              Submit_delete = st.button(label=textos['DELETARTEXT'])

            if Submit_delete:
                lancamento_cartao.delete_rows(id_selected)
                st.success(textos['Registro_deletado_com_sucessoTEXT'])
                st.rerun()

            if Submit_edit:
                lancamento_cartao.update_acell(f'K{id_selected}', data2)
                lancamento_cartao.update_acell(f'C{id_selected}', banco2.split(" / ")[0])
                lancamento_cartao.update_acell(f'D{id_selected}', banco2.split(" / ")[1])
                lancamento_cartao.update_acell(f'E{id_selected}', despesa2.split(" / ")[0])
                lancamento_cartao.update_acell(f'F{id_selected}', despesa2.split(" / ")[1])
                lancamento_cartao.update_acell(f'G{id_selected}', number2)
                lancamento_cartao.update_acell(f'H{id_selected}', descricao2)
                lancamento_cartao.update_acell(f'I{id_selected}', status2)
                if analise2:
                  lancamento_cartao.update_acell(f'J{id_selected}', "ANALÍTICA")
                lancamento_cartao.update_acell(f'M{id_selected}', proj2)
                lancamento_cartao.update_acell(f'N{id_selected}', "BRL")
                lancamento_cartao.update_acell(f'O{id_selected}', st.session_state.name)
                lancamento_cartao.update_acell(f'P{id_selected}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                st.success(textos['Registro_editado_com_sucessoTEXT'])
                st.rerun()


Alt_lançamentos_CC()
st.divider()

