import streamlit as st
from TRADUTOR import traaducaoapp

def create_sidebar_navigation():
    """
    Creates the sidebar navigation that is common across all pages.
    This function handles language selection and creates all navigation links.
    """
    # Get available languages and current language
    idiomadasdisponiveis = ["PORTUGUÊS", "ENGLISH", "ESPAÑOL"]
    idxidioma = idiomadasdisponiveis.index(st.session_state.get('useridioma', 'PORTUGUÊS'))
    
    # Language selector in sidebar
    language_of_page = st.sidebar.selectbox("", options=idiomadasdisponiveis, index=idxidioma)
    textos = traaducaoapp(language_of_page)
    st.session_state.useridioma = language_of_page
    
    # Navigation links
    st.sidebar.page_link("pages/1_SALDOS.py", label=textos['SALDOS'], icon=":material/account_balance:")
    st.sidebar.page_link("pages/2_LANCAMENTOS.py", label=textos['LANÇAMENTOS'], icon=":material/list:")
    st.sidebar.page_link("pages/3_CONFIGURACOES.py", label=textos['CONFIGURAÇÕES'], icon=":material/settings:")
    st.sidebar.page_link("pages/4_CARTOES DE CREDITO.py", label=textos['CARTÕES_DE_CRÉDITO'], icon=":material/credit_card:")
    st.sidebar.page_link("pages/5_RECEITAS X DESPESAS.py", label=textos['RECEITAS X DESPESAS'], icon=":material/finance:")
    st.sidebar.page_link("pages/6_VERSAO.py", label=textos['VERSÃO'], icon=":material/info:")
    st.sidebar.page_link("pages/8_PYGWALKER.py", label="📊 Análise Interativa", icon=":material/analytics:")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        logout()
    
    st.sidebar.divider()
    
    return textos, language_of_page

def logout():
    """
    Handles user logout by clearing session state and redirecting to login.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page('LYNCE.py')
