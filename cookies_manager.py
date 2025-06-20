from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st

cookies = EncryptedCookieManager(
    prefix="login_LYNCE_financeiro",
    password="JAYTEST123"
)

if not cookies.ready():
    st.stop()