import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from dependencies import getloginandpasswords

# Configure app
# st.set_page_config(layout="wide")
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Set up cookie manager
cookies = EncryptedCookieManager(
    prefix="lynce_",  # optional prefix to prevent conflicts
    password="super-secret-key"  # 🔒 use a strong password in production
)

# Wait until cookies are ready
if not cookies.ready():
    st.stop()  # Wait until cookies are initialized

# Check for existing login
if cookies.get("username"):
    st.success(f"Bem-vindo de volta, {cookies.get('name')}!")
    st.session_state.logged_in = True
    st.session_state.username = cookies.get("username")
    st.session_state.name = cookies.get("name")
    st.session_state.id = cookies.get("id")
    st.session_state.arquivo = cookies.get("arquivo")
    st.switch_page("pages/1_SALDOS.py")

# Login form
st.title("Tela de Login")
username = st.text_input("Usuário")
password = st.text_input("Senha", type="password")

def verificar_login(username, password):
    lgnpass = getloginandpasswords()
    user_data = lgnpass[lgnpass["LOGIN"] == username]
    if not user_data.empty and password == user_data["SENHA"].values[0]:
        return user_data.iloc[0]  # Return the user row
    return None

if st.button("Entrar"):
    user_data = verificar_login(username, password)
    if user_data is not None:
        nome_completo = user_data["NOME"] + " " + user_data["SOBRENOME"]

        # Save in session_state
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.name = nome_completo
        st.session_state.id = user_data["ID ARQUIVO"]
        st.session_state.arquivo = user_data["ARQUIVO"]

        # Save in cookies
        cookies["username"] = username
        cookies["name"] = nome_completo
        cookies["id"] = user_data["ID ARQUIVO"]
        cookies["arquivo"] = user_data["ARQUIVO"]
        cookies.save()

        st.success("Login bem-sucedido!")
        st.switch_page('pages/1_SALDOS.py')
    else:
        st.error("Usuário ou senha incorretos!")
