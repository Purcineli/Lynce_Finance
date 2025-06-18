from streamlit_cookies_manager import EncryptedCookieManager
import streamlit as st

cookies = EncryptedCookieManager(
    prefix="login_LYNCE",
    password="JAYTEST123"
)

if not cookies.ready():
    st.stop()