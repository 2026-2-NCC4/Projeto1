import streamlit as st


def render_header():
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
                help="Perfil",
            ):
                st.toast("Perfil em desenvolvimento.")