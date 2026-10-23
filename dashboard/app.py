import streamlit as st

from components.auth import render_auth
from components.carousel import render_carousel

st.set_page_config(
    page_title="CTI | Cadastro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        isolation: isolate;
        background:
            radial-gradient(60% 50% at 6% 10%, rgba(56, 189, 248, 0.50), transparent 70%),
            radial-gradient(55% 55% at 96% 8%, rgba(129, 140, 248, 0.42), transparent 70%),
            radial-gradient(60% 60% at 88% 96%, rgba(14, 165, 233, 0.38), transparent 70%),
            radial-gradient(50% 50% at 8% 96%, rgba(99, 102, 241, 0.28), transparent 70%),
            linear-gradient(135deg, #EAF6FD 0%, #D5E8F8 50%, #E4E3FA 100%);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
        background-image: radial-gradient(rgba(23, 77, 131, 0.22) 1.5px, transparent 1.5px);
        background-size: 26px 26px;
        -webkit-mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.55), transparent 65%);
        mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.55), transparent 65%);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1120px;
        padding: 4rem 2rem 3rem;
    }

    .st-key-login_card {
        background: #FFFFFF;
        border: 1px solid #DCE8F2;
        border-radius: 26px;
        overflow: hidden;
        box-shadow: 0 30px 70px rgba(28, 65, 110, 0.20);
    }

    .st-key-login_card > div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    .st-key-login_card div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: stretch !important;
    }

    .st-key-login_card div[data-testid="stColumn"],
    .st-key-login_card div[data-testid="column"] {
        min-width: 0;
        padding: 0 !important;
    }

    .st-key-carousel_col,
    .st-key-carousel_col div[data-testid="stElementContainer"] {
        margin: 0;
        padding: 0;
    }

    .st-key-carousel_col iframe {
        display: block;
        width: 100%;
        border: 0;
    }

    .st-key-login_card .st-key-auth_content {
        padding: 42px 48px !important;
        min-height: 520px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    @media (max-width: 800px) {
        .block-container {
            padding: 1rem;
        }

        .st-key-login_card div[data-testid="stColumn"]:first-child,
        .st-key-login_card div[data-testid="column"]:first-child {
            display: none;
        }

        .st-key-login_card .st-key-auth_content {
            padding: 30px 24px !important;
            min-height: auto;
        }
    }
</style>
""", unsafe_allow_html=True)

with st.container(key="login_card"):
    col_carousel, col_auth = st.columns([1, 1.1], gap="small")

    with col_carousel:
        with st.container(key="carousel_col"):
            render_carousel()

    with col_auth:
        with st.container(key="auth_content"):
            render_auth()