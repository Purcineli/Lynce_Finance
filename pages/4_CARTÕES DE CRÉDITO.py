import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
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
conta_banco_cadastradas = workbook.get_worksheet(2)
tabela_contas_banco = conta_banco_cadastradas.get_all_values()
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


contasconta_selecionadas = st.sidebar.multiselect('Selecione o tipo de lançamento',tabela_lancamentos_cartao['LANÇAMENTO'].unique(),None)
if not contasconta_selecionadas:
   contasconta_selecionadas = tabela_lancamentos_cartao['LANÇAMENTO'].unique()

contascategoria_selecionadas = st.sidebar.multiselect('Selecione a categoria',tabela_lancamentos_cartao['CATEGORIA'].unique(),None)
if not contascategoria_selecionadas:
   contascategoria_selecionadas = tabela_lancamentos_cartao['CATEGORIA'].unique()

pesqdescri = st.sidebar.text_input('Pesquisar descrição')


hoje = pd.Timestamp.today()
primeiro_dia_mes_atual = hoje.replace(day=1)
primeiro_dia_mes_anterior = (primeiro_dia_mes_atual - pd.DateOffset(months=1))

tabela_filtrada = tabela_lancamentos_cartao[
    tabela_lancamentos_cartao['FATURA'] >= primeiro_dia_mes_anterior
].copy()
tabela_filtrada['FATURA_MES'] = tabela_filtrada['FATURA'].dt.to_period('M')
tabela_filtrada['CARTÃO'] = tabela_filtrada['CARTÃO'] + "  /  " + tabela_filtrada['PROPRIETÁRIO']
lista_faturas = list(tabela_lancamentos_cartao['FATURA'].dropna().unique())

cadastro_cartao = workbook.get_worksheet(4)
tabela_cadastro_cartao = cadastro_cartao.get_all_values()
tabela_cadastro_cartao = pd.DataFrame(tabela_cadastro_cartao[1:], columns=tabela_cadastro_cartao[0])
tabela_cadastro_cartao = tabela_cadastro_cartao.set_index('ID')

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
st.write(faturas_cartao)



st.markdown(f'VALOR TOTAL À PAGAR: {-faturas_cartao.values.sum()}')
listas_cartoes = list(tabela_lancamentos_cartao['CARTÃO'].dropna().unique())
listas_owners = list(tabela_lancamentos_cartao['PROPRIETÁRIO'].dropna().unique())
colun1, colun2 = st.columns(2)
with colun1:
  lista_cartoes_selecionado = st.selectbox("Selecione", listas_cartoes, index=0, key="1")
with colun2:
  lista_owners_selecionado = st.selectbox("Selecione", listas_owners, index=0, key="2")

tabela_lancamentos_cartao_filtrada = tabela_lancamentos_cartao[
    (tabela_lancamentos_cartao['CARTÃO'] == lista_cartoes_selecionado) & 
    (tabela_lancamentos_cartao['PROPRIETÁRIO'] == lista_owners_selecionado)
]

tamanho_tabela = tabela_lancamentos_cartao.shape[0] + 2
if st.toggle('Conciliar fatura'):
  with st.form(key="form_ediar_con", border=False):
    if tamanho_tabela==2:
      st.write("Inserir lançamentos")
    else:
      # Step 1: Create a FATURA_MES column as Period for natural month sorting
      tabela_lancamentos_cartao_filtrada['FATURA_MES'] = tabela_lancamentos_cartao_filtrada['FATURA'].dt.to_period('M')

      # Step 2: Get unique months, sort them, and convert to string (e.g., 'Apr/2025')
      lista_faturas = sorted(tabela_lancamentos_cartao_filtrada['FATURA_MES'].dropna().unique())
      lista_faturas_str = [f.strftime('%b/%Y') for f in pd.PeriodIndex(lista_faturas).to_timestamp()][::-1]

      hoje = hoje.strftime(('%b/%Y'))
      try:
        hojed = lista_faturas_str.index(hoje)
      except ValueError:
        hojed = 2  # ou outro valor padrão


      # Step 3: Show in selectbox
      fatura_str = st.selectbox("SELECIONE A FATURA", faturas_cartao.columns, index=0)
      pesquisar = st.form_submit_button('PESQUISAR')

      # Step 4: Convert selection back to datetime for filtering
      fatura_dt = pd.to_datetime(fatura_str, format='%b/%Y')
      fatura_period = fatura_dt.to_period('M')

      # Step 5: Filter rows where FATURA_MES matches the selected one
      lançamentos_cartao_filtro_fatura = tabela_lancamentos_cartao_filtrada[
          tabela_lancamentos_cartao_filtrada['FATURA_MES'] == fatura_period
      ]
      # Step 6: Display filtered results
      lançamentos_cartao_filtro_fatura['FATURA_MES'] = lançamentos_cartao_filtro_fatura['FATURA_MES'].dt.strftime('%b/%Y')
      lançamentos_cartao_filtro_fatura_visual = lançamentos_cartao_filtro_fatura[['DATA','CARTÃO','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE', 'FATURA_MES']]
      lançamentos_cartao_filtro_fatura_visual = lançamentos_cartao_filtro_fatura.rename(columns={'FATURA_MES': 'FATURA CARTÃO'})
      lançamentos_cartao_filtro_fatura_visual_false = lançamentos_cartao_filtro_fatura[lançamentos_cartao_filtro_fatura['CONCILIADO']=="FALSE"]
      lançamentos_cartao_filtro_fatura_visual_true = lançamentos_cartao_filtro_fatura[lançamentos_cartao_filtro_fatura['CONCILIADO']=="TRUE"]
      naoconc, conc = st.columns(2)
      with naoconc:
        lançamentos_cartao_filtro_fatura_visual_false = lançamentos_cartao_filtro_fatura_visual_false[['DATA', 'LANÇAMENTO','VALOR', 'DESCRIÇÃO']]
        lançamentos_cartao_filtro_fatura_visual_false.insert(3,'SELECIONAR',False)
        editar_lançamentos_cartao_filtro_fatura_visual_false = st.data_editor(lançamentos_cartao_filtro_fatura_visual_false, 
                                                                              column_config={"SELECIONAR": st.column_config.CheckboxColumn('SELECT')},hide_index=False, height=500)
        st.markdown(f'TOTAL: {lançamentos_cartao_filtro_fatura_visual_false['VALOR'].sum()}')
        conciliar = st.form_submit_button("CONCILIAR")
        if conciliar:
          selected_rows = editar_lançamentos_cartao_filtro_fatura_visual_false[editar_lançamentos_cartao_filtro_fatura_visual_false["SELECIONAR"]]
          selected_indexes = selected_rows.index.tolist()
          for id in selected_indexes:
            lancamento_cartao.update_acell(f'I{int(id)}', True)
          st.rerun()
          
        
      with conc:
        lançamentos_cartao_filtro_fatura_visual_true = lançamentos_cartao_filtro_fatura_visual_true[['DATA', 'LANÇAMENTO','VALOR', 'DESCRIÇÃO']]
        lançamentos_cartao_filtro_fatura_visual_true.insert(3,'SELECIONAR',False)
        editar_lançamentos_cartao_filtro_fatura_visual_true = st.data_editor(lançamentos_cartao_filtro_fatura_visual_true, 
                                                                              column_config={"SELECIONAR": st.column_config.CheckboxColumn('SELECT')},hide_index=False, height=500, key="editdataframe")
        selected_rows = editar_lançamentos_cartao_filtro_fatura_visual_true[editar_lançamentos_cartao_filtro_fatura_visual_true["SELECIONAR"]]
        st.markdown(f'TOTAL: {lançamentos_cartao_filtro_fatura_visual_true['VALOR'].sum()}')
        DESCONCILIAR, PAGAR = st.columns(2)
        with DESCONCILIAR:
          desconciliar = st.form_submit_button('DESCONCILIAR')
          if desconciliar:
            selected_indexes = selected_rows.index.tolist()
            for id in selected_indexes:
              lancamento_cartao.update_acell(f'I{int(id)}', False)
            st.rerun() 
        with PAGAR:
          with st.popover("PAGAR FATURA"):
            fatura_data = datetime.strptime(fatura_str, '%b/%Y').replace(day=1)
            fatura_data_str = fatura_data.strftime('%Y-%m-%d')
            data = st.date_input('DATA', date.today())
            banco = st.selectbox('SELECIONE O BANCO', bancos, index=None, placeholder="Selecione")
            number = abs(st.number_input("INSIRA O VALOR", format="%0.2f", value=lançamentos_cartao_filtro_fatura_visual_true['VALOR'].sum()))
            pagar_fatura = st.form_submit_button("PAGAR FATURA")
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
              lancamento_cartao.update(f'A{tamanho_tabela}:O{tamanho_tabela}', [row_cartao], raw=False)
              sheet.add_rows(1)
              sheet.update(f'A{tamanho_tabela_lançamentos}:O{tamanho_tabela_lançamentos}', [row_banco], raw=False)


          
else:
  dataini, datafim =st.columns(2)
  with dataini:
    data_inicio = st.date_input("Data Inicial", date.today() - timedelta(days=30), format="DD/MM/YYYY")
    data_inicio = pd.to_datetime(data_inicio,format="DD/MM/YYYY")
    
  with datafim:
    data_final = st.date_input("Data Final", date.today(), format="DD/MM/YYYY")
    data_final = pd.to_datetime(data_final)

  tabela_lancamentos_cartao['DATA'] = pd.to_datetime(tabela_lancamentos_cartao['DATA'], dayfirst=True, errors='coerce')
  tabela_lancamentos_cartao['FATURA'] = pd.to_datetime(tabela_lancamentos_cartao['FATURA'], dayfirst=True, errors='coerce')
  lançamentos_cartao_filtro_data = tabela_lancamentos_cartao[
    (tabela_lancamentos_cartao['DATA'] >= data_inicio) &
    (tabela_lancamentos_cartao['DATA'] <= data_final) &
    (tabela_lancamentos_cartao['LANÇAMENTO'].isin(contasconta_selecionadas))&
    (tabela_lancamentos_cartao['CATEGORIA'].isin(contascategoria_selecionadas))&
    (tabela_lancamentos_cartao['DESCRIÇÃO'].str.contains(pesqdescri, case=False))]
  lançamentos_cartao_filtro_data = lançamentos_cartao_filtro_data.sort_values(by='DATA')
  lançamentos_cartao_filtro_data['DATA'] = lançamentos_cartao_filtro_data['DATA'].dt.strftime('%d/%m/%Y')
  lançamentos_cartao_filtro_data['FATURA'] = lançamentos_cartao_filtro_data['FATURA'].dt.strftime('%m/%Y')
  
  st.write(lançamentos_cartao_filtro_data)

st.divider()

try:
  cards_cont_cadastradas = workbook.get_worksheet(4)
  tabela_cards_cont = cards_cont_cadastradas.get_all_values()
  conta_cont_cadastradas = workbook.get_worksheet(3)
  tabela_contas_cont = conta_cont_cadastradas.get_all_values()
  tabela_evenproj_sheet = workbook.get_worksheet(5)
  tabela_evenproj = tabela_evenproj_sheet.get_all_values()
except APIError:
  st.warning(f"Limite excedido. Tentando novamente em {tempo_espera} segundos...")
  time.sleep(tempo_espera)
  st.rerun()


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
        st.write("Inserir novo registro")
        with st.form(key="form_inserir", border=False):
            data = st.date_input('DATA', date.today())
            cart = st.selectbox('SELECIONE O CARTÃO', cards, index=None, placeholder="Selecione")
            despesa = st.selectbox('SELECIONE A DESPESA', contas, index=None, placeholder="Selecione")
            number = st.number_input("INSIRA O VALOR", format="%0.2f")
            descricao = st.text_input('DESCRIÇÃO')
            descricao = str(descricao)
            descricao = descricao.upper()
            proj = st.selectbox('SELECIONE O PROJETO', projetos, index=None)
            status = st.checkbox('CONCILIADO', key='conciliado_checkbox')
            analise = st.checkbox("ANALÍTICA", key='lançamento analitico')
            dt,fat = st.columns(2)
            with dt:
              parcelas = st.number_input('Número de parcelas',1,36)
            with fat:
              data2 = st.date_input('FATURA', date.today())
            submit = st.form_submit_button(label="INSERIR")

        if submit:
          if cart == None or despesa == None or analise == None:
            st.warning("Preencha todos os campos")
          else:
            linhas = []  # Lista para armazenar as linhas a serem inseridas
            for x in range(parcelas):
                data_parcela = (data + relativedelta(months=x)).strftime('%d/%m/%Y')
                data_fatura = (data2 + relativedelta(months=x)).strftime('%d/%m/%Y')
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
                    proj,                              # L - Projeto
                    moeda,                             # M - Moeda
                    st.session_state.name,             # N - Usuário
                    timestamp                          # O - Timestamp
                ]
                linhas.append(linha)

            # Calcular a faixa de células que será atualizada
            if tamanho_tabela > 2:
              lancamento_cartao.add_rows(parcelas)
            else: 
              lancamento_cartao.add_rows(parcelas-1)
            inicio_linha = tamanho_tabela 
            fim_linha = inicio_linha + parcelas - 1
            faixa = f"A{inicio_linha}:O{fim_linha}"

            # Atualizar todas as linhas de uma vez só
            lancamento_cartao.update(values=linhas,range_name=faixa,raw=False)

            st.success("Registro(s) inserido(s) com sucesso!")
            st.rerun()
    with editar:
        st.write('Editar registro')
        subcol1,subcol2 = st.columns(2)
        if tamanho_tabela==2:
           st.write("INSERIR NOVO LANÇAMENTO")
        else:
          with subcol1:
            id_selected = st.number_input('Digite o ID', min_value=0, max_value=tamanhotabela_lancamento_cartao, step=1, format="%d", value=tamanhotabela_lancamento_cartao)
          with subcol2:
            data_raw = tabela_lancamentos_cartao.loc[id_selected, 'DATA']
            data2 = st.date_input('DATA', value=pd.to_datetime(data_raw).date())
          try:  
            idxbanco = tabela_lancamentos_cartao.loc[id_selected, 'CARTÃO'] + " / " + tabela_lancamentos_cartao.loc[id_selected, 'PROPRIETÁRIO']
            idxbanco = cards.index(idxbanco)
          except:
            idxbanco = None
          banco2 = st.selectbox('SELECIONE O BANCO', cards, index=idxbanco, placeholder="Selecione")
          try:
            idxdespesas = tabela_lancamentos_cartao.loc[id_selected, 'LANÇAMENTO'] + " / " + tabela_lancamentos_cartao.loc[id_selected, 'CATEGORIA']
            idxdespesas = contas.index(idxdespesas)
          except ValueError:
            idxdespesas = None
          despesa2 = st.selectbox('SELECIONE A DESPESA', contas, index=idxdespesas, placeholder="Selecione", )
          number2 = st.number_input("VALOR", format="%0.2f", value=tabela_lancamentos_cartao.loc[id_selected, 'VALOR'])
          descricao2 = st.text_input('DESCRIÇÃO', value=tabela_lancamentos_cartao.loc[id_selected, 'DESCRIÇÃO'])

          proj2 = st.selectbox('SELECIONE O PROJETO', projetos, index=None)
          status2 = st.checkbox('CONCILIADO', key='conciliado_checkbox_EDITOR', value=tabela_lancamentos_cartao.loc[id_selected, 'CONCILIADO'])
          analise2 = st.checkbox("ANALÍTICA", key='lançamento analitico2')
          subcol3, subcol4 = st.columns(2)
          with subcol3:   
            Submit_edit = st.button(label="EDITAR")
          with subcol4:
            Submit_delete = st.button(label="DELETAR")

          if Submit_delete:
              lancamento_cartao.delete_rows(id_selected)
              st.success("Registro deletado com sucesso!")
              st.rerun()

          if Submit_edit:
              lancamento_cartao.update_acell(f'B{id_selected}', data2.strftime('%d/%m/%Y'))
              lancamento_cartao.update_acell(f'C{id_selected}', banco2.split(" / ")[0])
              lancamento_cartao.update_acell(f'D{id_selected}', banco2.split(" / ")[1])
              lancamento_cartao.update_acell(f'E{id_selected}', despesa2.split(" / ")[0])
              lancamento_cartao.update_acell(f'F{id_selected}', despesa2.split(" / ")[1])
              lancamento_cartao.update_acell(f'G{id_selected}',number2)
              lancamento_cartao.update_acell(f'H{id_selected}', descricao2)
              lancamento_cartao.update_acell(f'I{id_selected}', status2)
              if analise2:
                lancamento_cartao.update_acell(f'J{id_selected}', "ANALÍTICA")
              lancamento_cartao.update_acell(f'K{id_selected}', data2.strftime('%d/%m/%Y'))
              lancamento_cartao.update_acell(f'L{id_selected}', proj2)
              lancamento_cartao.update_acell(f'M{id_selected}', st.session_state.name)
              lancamento_cartao.update_acell(f'N{id_selected}', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
              st.success("Registro editado com sucesso!")
              st.rerun()


Alt_lançamentos_CC()
st.divider()

