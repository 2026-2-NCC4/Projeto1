import streamlit as st

from components.auth import usuario_logado


def render_header():
    usuario = usuario_logado() or {}

    with st.container(key="cti_topbar"):
        busca, ajuda, notificacoes, perfil = st.columns(
            [1, 1, 1, 1],
            vertical_alignment="center",
            gap="small",
        )

        with busca:
            st.text_input(
                "Pesquisar",
                placeholder="Buscar indicadores, cenários ou análises...",
                label_visibility="collapsed",
                key="cti_busca",
                icon=":material/search:",
            )

        with ajuda:
            if st.button(
                "",
                icon=":material/help:",
                key="cti_header_ajuda",
                help="Ajuda",
            ):
                st.session_state.pagina_atual = "Ajuda"
                st.rerun()

        with notificacoes:
            if st.button(
                "",
                icon=":material/notifications:",
                key="cti_header_notificacoes",
                help="Notificações",
            ):
                st.toast("Notificações em desenvolvimento.")

        with perfil:
            if st.button(
                "",
                icon=":material/account_circle:",
                key="cti_header_perfil",
                help=usuario.get("nome", "Perfil"),
            ):
                st.toast(f"{usuario.get('nome', '')} · {usuario.get('email', '')}")