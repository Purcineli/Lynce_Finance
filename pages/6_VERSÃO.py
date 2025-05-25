import streamlit as st
import pandas as pd
import streamlit as st
from LYNCE import verificar_login
st.sidebar.page_link("pages/1_SALDOS.py", label="SALDOS")
st.sidebar.page_link("pages/2_LANÇAMENTOS.py", label="LANÇAMENTOS")
st.sidebar.page_link("pages/3_CONFIGURAÇÕES.py", label="CONFIGURAÇÕES")
st.sidebar.page_link("pages/4_CARTÕES DE CRÉDITO.py", label="CARTÕES DE CRÉDITO")
st.sidebar.page_link("pages/5_RECEITAS X DESPESAS.py", label="RECEITAS X DESPESAS")
st.sidebar.page_link("pages/6_VERSÃO.py", label="VERSÃO")
st.sidebar.divider()

st.image('https://i.ibb.co/xKhjx0ny/lynce-versao.png')
st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )

st.write('07/05/2025 - Lançamento da primeira versão')