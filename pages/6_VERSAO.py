import streamlit as st
import pandas as pd
import streamlit as st
from LYNCE import verificar_login
from TRADUTOR import traaducaoapp
from shared_components import create_sidebar_navigation
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.markdown('Você precisa fazer <a href="https://lyncefinanceiro.streamlit.app/" target="_self">login</a> primeiro.', unsafe_allow_html=True)
    st.switch_page('LYNCE.py')

# Create sidebar navigation and get translated texts
textos = create_sidebar_navigation()

# Welcome section
bemvido, x, language = st.columns([0.3,0.5,0.2], vertical_alignment='bottom')

with bemvido:
  st.write(f"{textos['BEMVINDO']} {st.session_state.name}!")
  
  sheeitid = st.session_state.id
  sheetname = st.session_state.arquivo

st.image('https://i.ibb.co/xKhjx0ny/lynce-versao.png')
st.logo('https://i.postimg.cc/yxJnfSLs/logo-lynce.png', size='large' )

st.write('07/05/2025 - Lançamento da primeira versão')
