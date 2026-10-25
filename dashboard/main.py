
from pathlib import Path

import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header
from pages.visao_geral import render_visao_geral


st.set_page_config(
    page_title="CTI | Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.session_state.setdefault("pagina_atual", "Visão Geral")
st.session_state.setdefault("sidebar_recolhido", False)

# Carrega o CSS antes de montar os componentes
CSS = Path(__file__).resolve().parent / "assets" / "dashboard_shell.css"

if CSS.is_file():
    st.markdown(
        f"<style>{CSS.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

# Informa ao CSS quando o menu está recolhido
if st.session_state.sidebar_recolhido:
    st.markdown(
        '<span class="cti-collapsed-marker" style="display:none"></span>',
        unsafe_allow_html=True,
    )

pagina = render_sidebar()

render_header()

if pagina == "Visão Geral":
    render_visao_geral()
else:
    st.title(pagina)
    st.info(f"A página {pagina} será desenvolvida posteriormente.")
