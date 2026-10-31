from datetime import datetime
from html import escape

import streamlit as st

from components.auth import sair, usuario_logado
from components.sidebar import GRUPOS
from data.usuarios import (
    ErroCadastro,
    alterar_senha,
    atualizar_nome,
    excluir_conta,
    obter_preferencias,
    obter_usuario,
    salvar_preferencias,
)

PAGINAS = [nome for _, itens in GRUPOS for nome, _ in itens]

PAGE_STYLE = """
<style>
    .st-key-cfg_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .cfg-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .cfg-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .cfg-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    /* cartões brancos */
    .st-key-cfg_perfil,
    .st-key-cfg_seguranca,
    .st-key-cfg_preferencias,
    .st-key-cfg_perigo {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 20px 24px;
    }

    .st-key-cfg_perigo {
        border-color: #F3D2D2;
    }

    .st-key-cfg_page div[data-testid="stForm"] {
        border: none;
        padding: 0;
    }

    .st-key-cfg_page label p {
        font-size: 12.5px !important;
        color: var(--cti-muted) !important;
    }

    /* campos visíveis dentro dos cartões brancos */
    .st-key-cfg_page [data-testid="stTextInputRootElement"],
    .st-key-cfg_page [data-testid="stSelectbox"] [role="group"],
    .st-key-cfg_page [data-baseweb="select"] > div {
        background: #F5F9FD !important;
        border: 1px solid #D5E3EE !important;
        border-radius: 10px !important;
    }

    .st-key-cfg_page [data-testid="stTextInputRootElement"]:focus-within {
        border-color: var(--cti-blue) !important;
        box-shadow: 0 0 0 3px rgba(0, 75, 133, .12);
    }

    .st-key-cfg_page [data-testid="stTextInputRootElement"] * {
        background: transparent !important;
    }

    .cfg-card-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--cti-text);
    }

    .cfg-card-note {
        font-size: 12px;
        color: #8AA4BF;
        margin: 2px 0 6px;
    }

    .cfg-perfil {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 6px 0 10px;
    }

    .cfg-avatar {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: var(--cti-blue);
        color: #fff;
        font-size: 18px;
        font-weight: 700;
    }

    .cfg-nome {
        font-size: 16px;
        font-weight: 700;
        color: var(--cti-text);
    }

    .cfg-detalhe {
        font-size: 12px;
        color: var(--cti-muted);
    }

    .st-key-cfg_page div[data-testid="stFormSubmitButton"] button {
        background: var(--cti-blue) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600;
    }

    .st-key-cfg_page div[data-testid="stFormSubmitButton"] button:hover {
        background: var(--cti-dark) !important;
    }

    .st-key-cfg_perigo .cfg-card-title {
        color: #B42318;
    }

    .st-key-cfg_perigo div[data-testid="stFormSubmitButton"] button {
        background: #B42318 !important;
    }

    .st-key-cfg_perigo div[data-testid="stFormSubmitButton"] button:hover {
        background: #912018 !important;
    }
</style>
"""


def _iniciais(nome):
    partes = nome.split()
    if not partes:
        return "?"
    return (partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")).upper()


def _data_cadastro(texto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return None


def _titulo_cartao(titulo, nota):
    st.markdown(
        f'<div class="cfg-card-title">{titulo}</div>'
        f'<div class="cfg-card-note">{nota}</div>',
        unsafe_allow_html=True,
    )


# ---------- Cartões ----------

def _perfil(usuario):
    with st.container(key="cfg_perfil"):
        _titulo_cartao("Perfil", "Como você aparece na plataforma.")

        membro_desde = _data_cadastro(usuario.get("criado_em"))
        detalhe = escape(usuario["email"])
        if membro_desde:
            detalhe += f" · membro desde {membro_desde}"

        st.markdown(f"""
            <div class="cfg-perfil">
                <span class="cfg-avatar">{escape(_iniciais(usuario["nome"]))}</span>
                <div>
                    <div class="cfg-nome">{escape(usuario["nome"])}</div>
                    <div class="cfg-detalhe">{detalhe}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("cfg_form_perfil"):
            nome = st.text_input("Nome completo", value=usuario["nome"])
            st.text_input(
                "E-mail",
                value=usuario["email"],
                disabled=True,
                help="O e-mail é usado para entrar e não pode ser alterado aqui.",
            )
            salvar = st.form_submit_button("Salvar perfil")

        if salvar:
            try:
                novo_nome = atualizar_nome(usuario["id"], nome)
            except ErroCadastro as erro:
                st.error(str(erro))
            else:
                st.session_state.usuario = {**st.session_state.usuario, "nome": novo_nome}
                st.session_state.cfg_aviso = "Perfil atualizado."
                st.rerun()


def _seguranca(usuario):
    with st.container(key="cfg_seguranca"):
        _titulo_cartao("Segurança", "Troque sua senha de acesso.")

        with st.form("cfg_form_senha", clear_on_submit=True):
            atual = st.text_input("Senha atual", type="password")
            nova = st.text_input("Nova senha", type="password")
            confirmar = st.text_input("Confirmar nova senha", type="password")
            trocar = st.form_submit_button("Alterar senha")

        st.caption("A senha deve ter pelo menos 8 caracteres, com letras e números.")

        if trocar:
            try:
                alterar_senha(usuario["id"], atual, nova, confirmar)
            except ErroCadastro as erro:
                st.error(str(erro))
            else:
                st.success("Senha alterada. Use a nova senha no próximo acesso.")


def _preferencias(usuario):
    preferencias = obter_preferencias(usuario["id"])
    pagina_salva = preferencias["pagina_inicial"]

    with st.container(key="cfg_preferencias"):
        _titulo_cartao("Preferências", "Valem a partir do próximo acesso.")

        with st.form("cfg_form_preferencias"):
            pagina = st.selectbox(
                "Página inicial",
                options=PAGINAS,
                index=PAGINAS.index(pagina_salva) if pagina_salva in PAGINAS else 0,
                help="Página aberta logo depois de entrar.",
            )
            recolhido = st.toggle(
                "Abrir com o menu lateral recolhido",
                value=preferencias["menu_recolhido"],
            )
            salvar = st.form_submit_button("Salvar preferências")

        if salvar:
            salvar_preferencias(usuario["id"], pagina, recolhido)
            st.success("Preferências salvas.")


def _excluir_conta(usuario):
    with st.container(key="cfg_perigo"):
        _titulo_cartao(
            "Excluir conta",
            "Apaga sua conta e suas preferências. Essa ação não pode ser desfeita.",
        )

        with st.form("cfg_form_excluir", clear_on_submit=True):
            senha = st.text_input("Senha", type="password")
            confirmo = st.checkbox("Entendo que minha conta será excluída permanentemente.")
            excluir = st.form_submit_button("Excluir minha conta")

        if excluir:
            if not confirmo:
                st.warning("Marque a confirmação para excluir a conta.")
                return

            try:
                excluir_conta(usuario["id"], senha)
            except ErroCadastro as erro:
                st.error(str(erro))
            else:
                sair()


# ---------- Página principal ----------

def render_configuracoes():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="cfg_page"):
        st.markdown("""
            <div class="cfg-eyebrow">PAINEL FINANCEIRO</div>
            <div class="cfg-title">Configurações</div>
            <div class="cfg-subtitle">
                Gerencie seu perfil, sua senha e suas preferências.
            </div>
        """, unsafe_allow_html=True)

        sessao = usuario_logado() or {}
        usuario = obter_usuario(sessao.get("id"))

        # A conta pode ter sido excluída em outra sessão
        if usuario is None:
            st.error("Não encontramos sua conta. Entre novamente.")
            if st.button("Ir para o login", key="cfg_relogin"):
                sair()
            return

        aviso = st.session_state.pop("cfg_aviso", None)
        if aviso:
            st.success(aviso)

        col_esq, col_dir = st.columns(2, gap="medium")

        with col_esq:
            _perfil(usuario)
            _preferencias(usuario)

        with col_dir:
            _seguranca(usuario)
            _excluir_conta(usuario)
