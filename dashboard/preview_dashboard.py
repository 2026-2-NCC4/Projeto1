
from pathlib import Path
import streamlit as st

from components.sidebar import render_sidebar
from components.header import render_header

st.set_page_config(
    page_title="CTI | Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.session_state.setdefault("sidebar_recolhido", False)

CSS = Path(__file__).resolve().parent / "assets" / "dashboard_shell.css"

st.markdown(
    f"<style>{CSS.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

if st.session_state.sidebar_recolhido:
    st.markdown(
        '<span class="cti-collapsed-marker" style="display:none"></span>',
        unsafe_allow_html=True,
    )

render_sidebar()
render_header()