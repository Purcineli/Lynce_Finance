import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import date, timedelta, datetime
import plotly.express as px
import numpy as np
import math
from LYNCE import verificar_login
from TRADUTOR import traaducaoapp
from dateutil.relativedelta import relativedelta


st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.stop()

idiomado_do_user = st.session_state.useridioma


idiomadasdisponiveis = ['PORTUGUÊS', 'ENGLISH', 'РУССКИЙ']
idxidioma = idiomadasdisponiveis.index(idiomado_do_user)
# Agora é seguro acessar os valores da sessão
bemvido, x, language = st.columns([0.3,0.5,0.2], vertical_alignment='bottom')
with language:
  language_of_page = st.selectbox("", options=idiomadasdisponiveis, index=idxidioma)
  st.session_state.useridioma = language_of_page
  textos = traaducaoapp(language_of_page)
  
  st.sidebar.page_link("pages/1_SALDOS.py", label=textos['SALDOS'], icon=":material/account_balance:")
  st.sidebar.page_link("pages/2_LANCAMENTOS.py", label=textos['LANÇAMENTOS'], icon=":material/list:")
  st.sidebar.page_link("pages/3_CONFIGURACOES.py", label=textos['CONFIGURAÇÕES'], icon=":material/settings:")
  st.sidebar.page_link("pages/4_CARTOES DE CREDITO.py", label=textos['CARTÕES_DE_CRÉDITO'], icon=":material/credit_card:")
  st.sidebar.page_link("pages/5_RECEITAS X DESPESAS.py", label=textos['RECEITAS X DESPESAS'], icon=":material/finance:")
  st.sidebar.page_link("pages/6_VERSAO.py", label=textos['VERSÃO'], icon=":material/info:")
  st.sidebar.divider()

with bemvido:
  st.write(f"{textos['BEMVINDO']} {st.session_state.name}!")
  
  sheeitid = st.session_state.id
  sheetname = st.session_state.arquivo

def lerdados(sheet_id_login_password,sheet_name_login_password):

  scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive'
]
  service_account_info = st.secrets["gcp_service_account"]
  creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
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
#lançamentos_CONTAS = lançamentos_CONTAS[lançamentos_CONTAS["CONCILIADO"]=="TRUE"]
lançamentos_CONTAS = lançamentos_CONTAS[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]
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
#tabela_lancamentos_cartao = tabela_lancamentos_cartao[tabela_lancamentos_cartao["CONCILIADO"]=="TRUE"]
tabela_lancamentos_cartao = tabela_lancamentos_cartao[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]
#PROJETO#
tabela_evenproj_sheet = workbook.get_worksheet(5)
tabela_evenproj = tabela_evenproj_sheet.get_all_values()
tabela_evenproj = pd.DataFrame(tabela_evenproj[1:], columns=tabela_evenproj[0])
tabela_evenproj = tabela_evenproj.set_index('ID')
tabela_evenproj_ativa = tabela_evenproj[tabela_evenproj['ATIVO']=='TRUE']



lançamentos = pd.concat([lançamentos_CONTAS, tabela_lancamentos_cartao], axis=0)

lançamentos = lançamentos.reset_index()
lançamentos = lançamentos[['DATA','PROPRIETÁRIO','LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO','ANALISE','PROJETO/EVENTO', 'MOEDA', 'CONCILIADO']]




st.divider()
lista_project = tabela_evenproj_ativa['NOME'].unique().tolist()
project_report = st.checkbox(textos['PROJETOS/EVENTOSTEXT'])
all_records = st.toggle(textos['INCLUIR_LANÇAMENTOS_NÃO_CONCILIADOS_TEXT'])

if not project_report:
  col01, col02 = st.columns(2)
  with col01:
    data_inicio = st.date_input(textos['DATA INICIAL TEXT'], date.today().replace(day=1), format="DD/MM/YYYY")
    data_inicio = pd.to_datetime(data_inicio)
  with col02:
    data_final = st.date_input(textos['DATA FINAL TEXT'], date.today(),format="DD/MM/YYYY")
    data_final = pd.to_datetime(data_final)
else:
  PROJECT_CHOSEN = st.selectbox(textos['SELECIONE_O_PROJETOTEXT'], options=lista_project)
tamanho_tabela = len(lançamentos)
if tamanho_tabela==1:
  st.write(textos['SEM_LANCAMENTOS_TEXT'])
else:
  tamanho_tabela = len(lançamentos)
  try:
    lançamentos['VALOR'] = lançamentos['VALOR'].astype(str).str.replace('.', '', regex=False)
  except:
    pass
  lançamentos['VALOR'] = lançamentos['VALOR'].str.replace(',', '.', regex=False)
  lançamentos['VALOR'] = pd.to_numeric(lançamentos['VALOR'], errors='coerce')
  lançamentos['VALOR'] = lançamentos['VALOR'].astype(float)
  
  listas_owners = list(
    lançamentos['PROPRIETÁRIO']
    .dropna()
    .loc[lançamentos['PROPRIETÁRIO'].str.strip() != '']
    .str.strip()
    .unique()
)
  lista_prop_selecionado = st.multiselect(textos['SELECIONE_TEXT'], listas_owners, listas_owners)
  lançamentos['DATA'] = pd.to_datetime(lançamentos['DATA'], dayfirst=True, errors='coerce')
  lançamentos['ANO'] = lançamentos['DATA'].dt.year
  lançamentos['ANO_MES'] = lançamentos['DATA'].dt.to_period('M').astype(str)
  lançamentos_todos = lançamentos
  lançamentos_todos = lançamentos_todos.iloc[::-1]
  lançamentos = lançamentos[lançamentos['CONCILIADO']=='TRUE']
  lançamentos_conciliados = lançamentos.iloc[::-1]
  
  if not project_report:
    if all_records:
      lançamentos_conciliados = lançamentos_todos[(lançamentos_todos['DATA']>=data_inicio)&(lançamentos_todos['DATA']<=data_final)&(lançamentos_todos['PROPRIETÁRIO'].isin(lista_prop_selecionado))]

    else:
      lançamentos_conciliados = lançamentos_conciliados[(lançamentos_conciliados['DATA']>=data_inicio)&(lançamentos_conciliados['DATA']<=data_final)&(lançamentos_conciliados['PROPRIETÁRIO'].isin(lista_prop_selecionado))]   
  else:
    if all_records:
      lançamentos_conciliados = lançamentos_todos[(lançamentos_todos['PROJETO/EVENTO']==PROJECT_CHOSEN)&(lançamentos_todos['PROPRIETÁRIO'].isin(lista_prop_selecionado))]
    else:
      lançamentos_conciliados = lançamentos_conciliados[(lançamentos_conciliados['PROJETO/EVENTO']==PROJECT_CHOSEN)&(lançamentos_conciliados['PROPRIETÁRIO'].isin(lista_prop_selecionado))]


  lançamentos_conciliados['DATA'] = lançamentos_conciliados['DATA'].dt.strftime('%d/%m/%Y')
  lançamentos_conciliados_receitas = lançamentos_conciliados[lançamentos_conciliados['ANALISE']=="RECEITAS"]
 
  lançamentos_conciliados_receitas_agrupado = lançamentos_conciliados_receitas.groupby(['LANÇAMENTO', 'PROPRIETÁRIO'], as_index=False).agg({'VALOR':'sum'})

  lançamentos_conciliados_despesas = lançamentos_conciliados[lançamentos_conciliados['ANALISE']=="DESPESAS"]
  lançamentos_conciliados_despesas_agrupado = lançamentos_conciliados_despesas.groupby(['LANÇAMENTO', 'PROPRIETÁRIO'], as_index=False).agg({'VALOR':'sum'})
  lançamentos_conciliados_despesas_agrupado['VALOR'] = -lançamentos_conciliados_despesas_agrupado['VALOR']
  lançamentos_conciliados_despesas['VALOR'] = -lançamentos_conciliados_despesas['VALOR']
  

  fig1 = px.pie(lançamentos_conciliados_receitas, names='CATEGORIA', values='VALOR',color_discrete_sequence=px.colors.sequential.Plasma)
  fig2 = px.pie(lançamentos_conciliados_despesas, names='CATEGORIA', values='VALOR',color_discrete_sequence=px.colors.sequential.RdBu)
  fig2.update_traces(textposition='inside', textinfo='percent')
  fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

  fig3 = px.bar(lançamentos_conciliados_receitas_agrupado, x='LANÇAMENTO', y='VALOR', color='PROPRIETÁRIO', color_discrete_sequence=px.colors.sequential.Plasma, category_orders={'LANÇAMENTO': lançamentos_conciliados_receitas.groupby('LANÇAMENTO')['VALOR'].sum().sort_values(ascending=False).index.tolist()})
  fig4 = px.bar(lançamentos_conciliados_despesas_agrupado, x='LANÇAMENTO', y='VALOR' ,color='PROPRIETÁRIO',color_discrete_sequence=px.colors.sequential.RdBu, category_orders={'LANÇAMENTO': lançamentos_conciliados_despesas.groupby('LANÇAMENTO')['VALOR'].sum().sort_values(ascending=False).index.tolist()})
  fig2.update_traces(textposition='inside', textinfo='percent')
  fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
  col1, col2 = st.columns(2)
  with col1:
    st.header(f"{textos['RECEITASTEXT']} R$ {lançamentos_conciliados_receitas['VALOR'].sum().round(2):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), divider="blue")
    st.plotly_chart(fig1, key ='1')
    st.plotly_chart(fig3, key ='2')
    lançamentos_conciliados_receitas = lançamentos_conciliados_receitas.set_index('DATA')
    st.dataframe(lançamentos_conciliados_receitas[['LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO']], height=300)
  with col2:
    valor_total_despesas = abs(lançamentos_conciliados_despesas['VALOR'].sum().round(2))
    valor_formatado = f"R$ {valor_total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.header(f"{textos['DESPESATEXT']} {valor_formatado}", divider="red")
    st.plotly_chart(fig2, key ='3')
    st.plotly_chart(fig4, key ='4')
    lançamentos_conciliados_despesas = lançamentos_conciliados_despesas.set_index('DATA')
    st.dataframe(lançamentos_conciliados_despesas[['LANÇAMENTO','CATEGORIA','VALOR','DESCRIÇÃO']], height=300)

st.divider()


listaCat_receitas = tabela_contas_cont[tabela_contas_cont['ATRIBUIÇÃO'] == 'RECEITAS']['CONTA CONTÁBIL'].unique().tolist()
listaCat_despesas = tabela_contas_cont[tabela_contas_cont['ATRIBUIÇÃO'] == 'DESPESAS']['CONTA CONTÁBIL'].unique().tolist()
@st.fragment
def makegraph():
  ST01, ST02 = st.columns(2)
  with ST01:
    categoriasescolhidasrec = st.multiselect("select", listaCat_receitas)
  with ST02:
    categoriasescolhidasdesp = st.multiselect("select", listaCat_despesas)

  categoriasescolhidas = categoriasescolhidasrec + categoriasescolhidasdesp

  lancamentoscatt = lançamentos[lançamentos['LANÇAMENTO'].isin(categoriasescolhidas)]

  minimomes = lançamentos['ANO_MES'].min()
  minimomes = datetime.strptime(minimomes, "%Y-%m")
  maximomes = lançamentos['ANO_MES'].max()
  maximomes = datetime.strptime(maximomes, "%Y-%m")

  # Slider de período
  periodo = st.slider("PERÍODO", 
                      min_value=minimomes, 
                      max_value=maximomes, 
                      value=(minimomes, maximomes), 
                      format="MM/YYYY")

  lancamentoscatt = lancamentoscatt[
    (lancamentoscatt['DATA'] >= periodo[0]) &
    (lancamentoscatt['DATA'] <= periodo[1] + relativedelta(months=1) - timedelta(days=1))
]
  #lancamentoscatt = lancamentoscatt[lancamentoscatt['DATA']<=periodo[1]+relativedelta(months=1)-timedelta(days=1)]
  lancamentograph = pd.pivot_table(
      lancamentoscatt,
      index='LANÇAMENTO',
      columns='ANO_MES',
      values='VALOR',
      aggfunc='sum' # Preenche com 0 onde não houver dados
  )
  df_plot = lancamentograph.reset_index()

  # "Derretendo" o DataFrame para o formato longo (long format)
  df_long = df_plot.melt(id_vars='LANÇAMENTO', var_name='ANO_MES', value_name='VALOR')

  # Criando o gráfico interativo de linhas
  fig = px.line(
      df_long,
      x='ANO_MES',
      y='VALOR',
      color='LANÇAMENTO',
      markers=True,
      title='Despesas por Categoria ao Longo do Tempo'
  )

  # Exibir o gráfico
  st.plotly_chart(fig)

makegraph()

try:
    # Exportar como Excel (XLSX)
    excel_bytes = workbook.export(format='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # Botão único: exporta e baixa
    st.download_button(
        label="📥 Exportar e Baixar Planilha",
        data=excel_bytes,
        file_name="planilha.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
except Exception as e:
    st.error(f"Erro ao exportar a planilha: {e}")
#GRAPH_RECEITAS = px.line(lançamentos_conciliados_para_pivot_receitas_GRAPH, x=lançamentos_conciliados_para_pivot_receitas_GRAPH.index, y='VALOR', title="Receitas Mensais")
#st.plotly_chart(GRAPH_RECEITAS, key ='GRAPH RECEITAS')