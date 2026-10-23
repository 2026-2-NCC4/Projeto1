import base64
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent.parent / "assets"

AUTH_STYLE = """
<style>
    .auth-header {
        margin-bottom: 22px;
    }

    .auth-brand-logo {
        width: 150px;
        height: auto;
        display: block;
        object-fit: contain;
    }

    .auth-title {
        font-size: 26px;
        font-weight: 700;
        color: #102B50;
        margin-bottom: 8px;
    }

    .auth-description {
        font-size: 13px;
        color: #64748B;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    .auth-footer {
        text-align: center;
        color: #64748B;
        font-size: 12px;
        margin-top: 18px;
    }

    .st-key-auth_content div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    .st-key-auth_content div[data-testid="stTextInput"] label,
    .st-key-auth_content div[data-testid="stTextInput"] label p {
        color: #29435C !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] {
        background: #FFFFFF !important;
        border: 1px solid #D5E3EE !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 2px rgba(23, 77, 131, 0.05) !important;
        overflow: hidden;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"]:hover {
        border-color: #9CC4DE !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"]:focus-within {
        border-color: #2E91C9 !important;
        box-shadow: 0 0 0 3px rgba(46, 145, 201, 0.16) !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] *:not(input):not(svg):not(path) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] input {
        background: transparent !important;
        color: #183B61 !important;
        -webkit-text-fill-color: #183B61 !important;
        caret-color: #174D83 !important;
        min-height: 44px;
        padding: 0 14px;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] input::placeholder {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] input:-webkit-autofill {
        -webkit-box-shadow: 0 0 0 1000px #FFFFFF inset !important;
        -webkit-text-fill-color: #183B61 !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] button {
        color: #7A8CA3 !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] button:hover {
        color: #174D83 !important;
    }

    .st-key-auth_content [data-testid="stTextInputRootElement"] button svg {
        color: inherit !important;
        fill: currentColor !important;
    }

    .st-key-auth_content div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 46px;
        background: #174D83 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600;
        box-shadow: 0 6px 14px rgba(23, 77, 131, 0.18);
    }

    .st-key-auth_content div[data-testid="stFormSubmitButton"] button:hover {
        background: #267DB2 !important;
    }

    .st-key-auth_content div[data-testid="stButton"] button[kind="tertiary"] {
        color: #174D83 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 13px;
    }

    .st-key-auth_content div[data-testid="stButton"] button[kind="secondary"] {
        background: #F5F9FC !important;
        color: #174D83 !important;
        border: 1px solid #CBDDEA !important;
        border-radius: 12px !important;
        min-height: 44px;
        font-weight: 600;
    }

    .st-key-auth_content div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: #EAF3FA !important;
        border-color: #2E91C9 !important;
    }
</style>
"""


def _logo_base64():
    logo_path = ASSETS / "logo cti 1.png"

    if not logo_path.is_file():
        return ""

    return base64.b64encode(logo_path.read_bytes()).decode("utf-8")


def _render_login():
    st.markdown("""
        <div class="auth-title">Bem-vindo à CTI</div>
        <div class="auth-description">
            Entre na sua conta para acessar seus indicadores
            e análises financeiras.
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="Digite seu e-mail")
        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha"
        )
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    if entrar:
        if not email or not senha:
            st.warning("Preencha o e-mail e a senha.")
        else:
            st.info("A autenticação será integrada depois.")

    if st.button("Esqueceu sua senha?", key="forgot_password", type="tertiary"):
        st.info("A recuperação de senha será implementada depois.")

    st.markdown(
        '<div class="auth-footer">Ainda não tem uma conta?</div>',
        unsafe_allow_html=True
    )

    if st.button("Criar conta", use_container_width=True, key="go_register"):
        st.session_state.auth_mode = "register"
        st.rerun()


def _render_register():
    st.markdown("""
        <div class="auth-title">Crie sua conta</div>
        <div class="auth-description">
            Cadastre-se para começar a explorar a plataforma.
        </div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        nome = st.text_input("Nome completo", placeholder="Digite seu nome")
        email = st.text_input("E-mail", placeholder="Digite seu e-mail")
        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Crie uma senha"
        )
        confirmar = st.text_input(
            "Confirmar senha",
            type="password",
            placeholder="Confirme sua senha"
        )
        cadastrar = st.form_submit_button("Criar conta", use_container_width=True)

    if cadastrar:
        if not all([nome, email, senha, confirmar]):
            st.warning("Preencha todos os campos.")
        elif senha != confirmar:
            st.error("As senhas não coincidem.")
        else:
            st.info("O cadastro será conectado ao banco de dados depois.")

    if st.button("Já tenho uma conta", use_container_width=True, key="go_login"):
        st.session_state.auth_mode = "login"
        st.rerun()


def render_auth():
    st.markdown(AUTH_STYLE, unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    logo = _logo_base64()

    if logo:
        st.markdown(f"""
            <div class="auth-header">
                <img src="data:image/png;base64,{logo}" class="auth-brand-logo" alt="Logo CTI">
            </div>
        """, unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        _render_login()
    else:
        _render_register()