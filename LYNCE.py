import streamlit as st
from dependencies import getloginandpasswords

st.set_page_config(layout="wide") # configurar página wide
# Função para verificar o login (simples, sem hash de senha)
def verificar_login(username, password):
    lgnpass = getloginandpasswords()
    try:
        if lgnpass[lgnpass['LOGIN']==username].index[0] >= 0:
            user = lgnpass[lgnpass['LOGIN']==username].index[0]
            print(user)
            if password == lgnpass['SENHA'][user]:
                return True
    except:
        return False

# Função para a tela de login
def tela_login():
    print(f"O tipo de st é: {type(st)}")
    st.title("Tela de Login")
    # Inputs de login
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        # Verifica o login
        if verificar_login(username, password):
            
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login bem-sucedido!")
            
            lgnpass = getloginandpasswords()
            user = lgnpass[lgnpass['LOGIN']==username].index[0]
            nome = lgnpass['NOME'][user] + " " + lgnpass['SOBRENOME'][user]
            id_arquivo = lgnpass['ID ARQUIVO'][user]
            nome_arquivo = lgnpass['ARQUIVO'][user]
            st.session_state.name = nome
            st.session_state.id = id_arquivo
            st.session_state.arquivo = nome_arquivo
            st.switch_page('pages/1_SALDOS.py')  # Atualiza para a próxima página
        else:
            st.error("Usuário ou senha incorretos!")


# Função principal para controlar as páginas
def main():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        tela_login()  # Exibe a tela de login
    else:
        st.switch_page('pages/1_SALDOS.py')

# Rodar a aplicação
if __name__ == "__main__":
    main()