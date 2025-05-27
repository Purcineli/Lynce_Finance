import streamlit as st
import pandas as pd
import streamlit as st
from LYNCE import verificar_login
from TRADUTOR import traaducaoapp
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
  st.sidebar.page_link("pages/2_LANÇAMENTOS.py", label=textos['LANÇAMENTOS'], icon=":material/list:")
  st.sidebar.page_link("pages/3_CONFIGURAÇÕES.py", label=textos['CONFIGURAÇÕES'], icon=":material/settings:")
  st.sidebar.page_link("pages/4_CARTÕES DE CRÉDITO.py", label=textos['CARTÕES_DE_CRÉDITO'], icon=":material/credit_card:")
  st.sidebar.page_link("pages/5_RECEITAS X DESPESAS.py", label=textos['RECEITAS X DESPESAS'], icon=":material/finance:")
  st.sidebar.page_link("pages/6_VERSÃO.py", label=textos['VERSÃO'], icon=":material/info:")
  st.sidebar.divider()

with bemvido:
  st.write(f"{textos['BEMVINDO']} {st.session_state.name}!")
  
  sheeitid = st.session_state.id
  sheetname = st.session_state.arquivo

st.image('https://i.ibb.co/xKhjx0ny/lynce-versao.png')
st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )

st.write('07/05/2025 - Lançamento da primeira versão')