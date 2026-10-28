import streamlit as st

from components.auth import usuario_logado


def render_configuracoes():
    usuario = usuario_logado() or {}

    st.title("Configurações")
    st.caption("Consulte as informações básicas da sua conta.")

    with st.container(border=True):
        st.subheader("Perfil")
        st.text_input("Nome", value=str(usuario.get("nome") or "Não informado"), disabled=True)
        st.text_input("E-mail", value=str(usuario.get("email") or "Não informado"), disabled=True)
        st.caption("Os dados são exibidos conforme o usuário autenticado. A edição do perfil ainda não está disponível.")

    with st.container(border=True):
        st.subheader("Preferências")
        st.info("As opções de personalização serão adicionadas aqui quando estiverem disponíveis.")
