import base64
import time
from html import escape
from pathlib import Path

import streamlit as st

from components.carousel import render_carousel
from data.envio_email import configuracao_smtp, enviar_codigo_redefinicao
from data.usuarios import (
    VALIDADE_CODIGO_MINUTOS,
    ErroCadastro,
    autenticar,
    cadastrar_usuario,
    gerar_codigo_redefinicao,
    normalizar_email,
    redefinir_senha,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"

MAX_TENTATIVAS = 5
BLOQUEIO_SEGUNDOS = 60

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


PAGE_STYLE = """
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

    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"] {
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
"""


# ---------- Sessão ----------

def usuario_logado():
    """Devolve o usuário autenticado nesta sessão (dict com id, nome e email) ou None."""
    return st.session_state.get("usuario")


def _iniciar_sessao(usuario):
    st.session_state.usuario = usuario
    st.session_state.pop("login_falhas", None)
    st.session_state.pop("login_bloqueado_ate", None)
    st.rerun()


def sair():
    """Encerra a sessão e limpa o estado do dashboard."""
    st.session_state.clear()
    st.rerun()


def _registrar_falha():
    falhas = st.session_state.get("login_falhas", 0) + 1
    st.session_state.login_falhas = falhas

    if falhas >= MAX_TENTATIVAS:
        st.session_state.login_bloqueado_ate = time.time() + BLOQUEIO_SEGUNDOS
        st.session_state.login_falhas = 0


def _segundos_bloqueado():
    restante = st.session_state.get("login_bloqueado_ate", 0) - time.time()
    return int(restante) + 1 if restante > 0 else 0


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

    # Mensagem deixada por outra tela (ex.: senha redefinida)
    aviso = st.session_state.pop("auth_aviso", None)
    if aviso:
        st.success(aviso)

    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="Digite seu e-mail")
        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha"
        )
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    if entrar:
        restante = _segundos_bloqueado()

        if restante:
            st.error(
                "Muitas tentativas sem sucesso. "
                f"Tente novamente em {restante} segundos."
            )
        elif not email or not senha:
            st.warning("Preencha o e-mail e a senha.")
        else:
            usuario = autenticar(email, senha)

            if usuario:
                _iniciar_sessao(usuario)
            else:
                _registrar_falha()
                st.error("E-mail ou senha incorretos.")

    if st.button("Esqueceu sua senha?", key="forgot_password", type="tertiary"):
        st.session_state.auth_mode = "forgot"
        st.rerun()

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

    st.caption("A senha deve ter pelo menos 8 caracteres, com letras e números.")

    if cadastrar:
        try:
            usuario = cadastrar_usuario(nome, email, senha, confirmar)
        except ErroCadastro as erro:
            st.error(str(erro))
        else:
            _iniciar_sessao(usuario)

    if st.button("Já tenho uma conta", use_container_width=True, key="go_login"):
        st.session_state.auth_mode = "login"
        st.rerun()


def _limpar_redefinicao():
    for chave in ("redef_email", "redef_codigo_teste"):
        st.session_state.pop(chave, None)


def _voltar_ao_login(aviso=None):
    _limpar_redefinicao()
    st.session_state.auth_mode = "login"
    if aviso:
        st.session_state.auth_aviso = aviso
    st.rerun()


def _solicitar_codigo(email):
    """Gera o código e envia por e-mail (ou guarda para mostrar, no modo de teste)."""
    resultado = gerar_codigo_redefinicao(email)

    if resultado:
        nome, codigo = resultado
        st.session_state.pop("redef_codigo_teste", None)

        if configuracao_smtp() is None:
            st.session_state.redef_codigo_teste = codigo
        else:
            try:
                enviar_codigo_redefinicao(email, nome, codigo, VALIDADE_CODIGO_MINUTOS)
            except Exception:
                st.error("Não foi possível enviar o e-mail agora. Tente novamente em instantes.")
                return False

    st.session_state.redef_email = normalizar_email(email)
    return True


def _render_esqueci_email():
    st.markdown("""
        <div class="auth-title">Esqueceu sua senha?</div>
        <div class="auth-description">
            Informe o e-mail da sua conta. Vamos enviar um código
            de 6 dígitos para você criar uma nova senha.
        </div>
    """, unsafe_allow_html=True)

    with st.form("forgot_form"):
        email = st.text_input("E-mail", placeholder="Digite seu e-mail")
        enviar = st.form_submit_button("Enviar código", use_container_width=True)

    if enviar:
        if not email.strip():
            st.warning("Informe o e-mail.")
        elif _solicitar_codigo(email):
            st.rerun()

    if st.button("Voltar ao login", use_container_width=True, key="forgot_back"):
        _voltar_ao_login()


def _render_esqueci_codigo():
    email = st.session_state.redef_email

    st.markdown(f"""
        <div class="auth-title">Crie uma nova senha</div>
        <div class="auth-description">
            Se houver uma conta com <strong>{escape(email)}</strong>, enviamos um código
            de 6 dígitos. Ele vale por {VALIDADE_CODIGO_MINUTOS} minutos.
        </div>
    """, unsafe_allow_html=True)

    codigo_teste = st.session_state.get("redef_codigo_teste")
    if codigo_teste:
        st.warning(
            f"Modo de teste: o envio de e-mail não está configurado, por isso "
            f"o código aparece aqui: **{codigo_teste}**. Configure o SMTP em "
            "`.streamlit/secrets.toml` antes de publicar a plataforma."
        )

    with st.form("reset_form"):
        codigo = st.text_input("Código", placeholder="Digite o código de 6 dígitos", max_chars=6)
        senha = st.text_input("Nova senha", type="password", placeholder="Crie uma nova senha")
        confirmar = st.text_input(
            "Confirmar nova senha", type="password", placeholder="Confirme a nova senha"
        )
        redefinir = st.form_submit_button("Redefinir senha", use_container_width=True)

    st.caption("A senha deve ter pelo menos 8 caracteres, com letras e números.")

    if redefinir:
        try:
            redefinir_senha(email, codigo, senha, confirmar)
        except ErroCadastro as erro:
            st.error(str(erro))
        else:
            _voltar_ao_login("Senha redefinida. Entre com a nova senha.")

    if st.button("Reenviar código", key="reset_resend", type="tertiary"):
        if _solicitar_codigo(email):
            st.info("Se o e-mail tiver conta, um novo código foi enviado.")

    if st.button("Voltar ao login", use_container_width=True, key="reset_back"):
        _voltar_ao_login()


def _render_esqueci_senha():
    if st.session_state.get("redef_email"):
        _render_esqueci_codigo()
    else:
        _render_esqueci_email()


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
    elif st.session_state.auth_mode == "forgot":
        _render_esqueci_senha()
    else:
        _render_register()


def render_auth_page():
    """Tela completa de entrada: carrossel à esquerda e login/cadastro à direita."""
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="login_card"):
        col_carousel, col_auth = st.columns([1, 1.1], gap="small")

        with col_carousel:
            with st.container(key="carousel_col"):
                render_carousel()

        with col_auth:
            with st.container(key="auth_content"):
                render_auth()