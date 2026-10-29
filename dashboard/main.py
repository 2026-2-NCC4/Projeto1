
from pathlib import Path
import streamlit as st
from components.auth import render_auth_page, usuario_logado
from components.sidebar import render_sidebar
from components.header import render_header
from pages.insights import render_insights
from pages.regressao import render_regressao
from pages.visao_geral import render_visao_geral
from pages.configuracoes import render_configuracoes
from pages.ranking import render_ranking
from pages.comparacao import render_comparacao



st.set_page_config(
    page_title="CTI | Dashboard" if usuario_logado() else "CTI | Entrar",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Verifica se o usuário está autenticado
if not usuario_logado():
    render_auth_page()
    st.stop()

st.session_state.setdefault("pagina_atual", "Visão Geral")
st.session_state.setdefault("sidebar_recolhido", False)


# Carrega o CSS original do dashboard
CSS = Path(__file__).resolve().parent / "assets" / "dashboard_shell.css"

if CSS.is_file():
    st.markdown(
        f"<style>{CSS.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

if st.session_state.sidebar_recolhido:
    st.markdown(
        '<span class="cti-collapsed-marker" style="display:none"></span>',
        unsafe_allow_html=True,
    )


pagina_sidebar = render_sidebar()


# Permite que o cabeçalho solicite navegação para Configurações
destino = st.session_state.pop("cti_navegar_para", None)
ultima_pagina_sidebar = st.session_state.get(
    "_cti_ultima_pagina_sidebar"
)

if destino:
    st.session_state["pagina_atual"] = destino
elif (
    ultima_pagina_sidebar is None
    or pagina_sidebar != ultima_pagina_sidebar
):
    st.session_state["pagina_atual"] = pagina_sidebar

st.session_state["_cti_ultima_pagina_sidebar"] = pagina_sidebar

pagina = st.session_state.get("pagina_atual", pagina_sidebar)


# Renderiza o cabeçalho
render_header(pagina)


# Exibe a página selecionada
if pagina == "Visão Geral":
    render_visao_geral()

elif pagina == "Regressão":
    render_regressao()

elif pagina == "Insights":
    render_insights()

elif pagina == "Configurações":
    render_configuracoes()

elif pagina == "Ranking":
    render_ranking()

elif pagina == "Comparação":
    render_comparacao()

else:
    st.title(pagina)
    st.info(
        f"A página {pagina} será desenvolvida posteriormente."
    )
