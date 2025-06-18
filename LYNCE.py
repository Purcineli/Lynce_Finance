import streamlit as st
from dependencies import getloginandpasswords
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(layout="wide")

# === Inicializa cookies ===
def initialize_cookies():
    cookies = EncryptedCookieManager(
        prefix="login_LYNCE",
        password="JAYTEST123"  # Troque por uma senha forte
    )
    if not cookies.ready():
        st.stop()

# === Função para verificar o login ===
def verificar_login(username, password):
    lgnpass = getloginandpasswords()
    try:
        if lgnpass[lgnpass['LOGIN'] == username].index[0] >= 0:
            user = lgnpass[lgnpass['LOGIN'] == username].index[0]
            if password == lgnpass['SENHA'][user]:
                return True
    except:
        return False

# === Função para carregar dados do usuário ===
def carregar_dados_usuario(username):
    lgnpass = getloginandpasswords()
    user = lgnpass[lgnpass['LOGIN'] == username].index[0]
    nome = lgnpass['NOME'][user] + " " + lgnpass['SOBRENOME'][user]
    id_arquivo = lgnpass['ID ARQUIVO'][user]
    nome_arquivo = lgnpass['ARQUIVO'][user]
    idioma = lgnpass['IDIOMA'][user]
    return nome, id_arquivo, nome_arquivo, idioma

# === Função para a tela de login ===
def tela_login():
    initialize_cookies()
    iamge, logn, cont = st.columns([0.3, 0.3, 0.4])
    with iamge:
        st.image('https://i.ibb.co/xKhjx0ny/lynce-versao.png')
    with logn:
        st.title("Tela de Login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if verificar_login(username, password):
                # Preenche o session_state
                st.session_state.logged_in = True
                st.session_state.username = username

                nome, id_arquivo, nome_arquivo, idioma = carregar_dados_usuario(username)
                st.session_state.name = nome
                st.session_state.id = id_arquivo
                st.session_state.arquivo = nome_arquivo
                st.session_state.useridioma = idioma

                # Grava os cookies (login persiste após refresh)
                cookies["logged_in"] = "true"
                cookies["username"] = username
                #cookies.set_expiry(days=1)  # <<< Definindo expiração de 1 dia
                cookies.save()

                st.success("Login bem-sucedido!")
                st.switch_page('pages/1_SALDOS.py')
            else:
                st.error("Usuário ou senha incorretos!")

# === Função para checar login ativo ===
def verificar_login_cookie_ou_session():
    if st.session_state.get("logged_in"):
        return True
    elif cookies.get("logged_in") == "true":
        username = cookies.get("username")
        if username:
            # Recupera dados do usuário e popula o session_state
            st.session_state.logged_in = True
            st.session_state.username = username

            nome, id_arquivo, nome_arquivo, idioma = carregar_dados_usuario(username)
            st.session_state.name = nome
            st.session_state.id = id_arquivo
            st.session_state.arquivo = nome_arquivo
            st.session_state.useridioma = idioma

            return True
    return False

# === Função de logout ===
def logout():
    st.session_state.logged_in = False
    print("logout com sucesso")
    # Limpa cookies
    cookies["logged_in"] = ""
    cookies["username"] = ""
    
    #cookies.set_expiry(0)   # 🔥 Faz o cookie expirar imediatamente
    cookies.save()

    
    st.success("Logout realizado com sucesso!")
    st.switch_page('LYNCE.py')
    # Atualiza a página, levando o usuário de volta para a tela de login

# === Função principal ===
def main():
    initialize_cookies()
    if verificar_login_cookie_ou_session():
        # Sidebar com informações do usuário e botão de logout
        with st.sidebar:
            st.markdown(f"👤 **Usuário:** {st.session_state.name}")
            st.markdown(f"📄 **Arquivo:** {st.session_state.arquivo}")
            st.markdown(f"🌐 **Idioma:** {st.session_state.useridioma}")
            if st.button("🚪 Logout"):
                logout()

        st.switch_page('pages/1_SALDOS.py')
    else:
        tela_login()

# === Executa o app ===
if __name__ == "__main__":
    main()
