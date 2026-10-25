import base64
import unicodedata
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image

LOGO = Path(__file__).resolve().parents[1] / "assets" / "logo cti 1.png"

# Os nomes das páginas continuam exatamente os mesmos.
GRUPOS = [
    (None, [("Visão Geral", "dashboard")]),
    ("DESEMPENHO", [
        ("Indicadores", "monitoring"),
        ("Tendência", "trending_up"),
    ]),
    ("CENÁRIOS", [
        ("Comparação", "compare_arrows"),
        ("Ranking", "leaderboard"),
    ]),
    ("META ANALÍTICA", [
        ("Metas x Realizado", "target"),
    ]),
    ("SIMULADOR", [
        ("Simular novo cenário", "add_circle"),
    ]),
    ("ANÁLISE E INSIGHTS", [
        ("Regressão", "scatter_plot"),
        ("Insights", "lightbulb"),
    ]),
]

ICONE_AJUDA = (
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="9.5"/>'
    '<path d="M9.4 9.2a2.7 2.7 0 0 1 5.2.9c0 1.8-2.6 2.3-2.6 3.9"/>'
    '<circle cx="12" cy="17.2" r=".6" fill="currentColor"/></svg>'
)


def _slug(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "_" for c in texto.lower()).strip("_")


def _data_uri(img):
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


@st.cache_resource(show_spinner=False)
def _logos():
    """Devolve (logo completa, logo compacta) como data-URI.

    A compacta é só a sigla "CTI" recortada da própria logo, para caber
    legível no sidebar recolhido. Nenhum arquivo novo é necessário.
    """
    if not LOGO.exists():
        return None, None

    img = Image.open(LOGO).convert("RGBA")
    img = img.crop(img.getchannel("A").getbbox())  # tira margem transparente

    # A sigla ocupa ~50% da largura da logo (antes do símbolo azul)
    sigla = img.crop((0, 0, int(img.width * 0.505), img.height))
    sigla = sigla.crop(sigla.getchannel("A").getbbox())

    return _data_uri(img), _data_uri(sigla)


def item_menu(nome, icone, recolhido=False):
    ativo = st.session_state.pagina_atual == nome

    if st.button(
        nome,
        icon=f":material/{icone}:",
        key=f"cti_nav_{_slug(nome)}",
        type="primary" if ativo else "secondary",
        use_container_width=True,
        help=nome if recolhido else None,
    ):
        st.session_state.pagina_atual = nome
        st.rerun()


def _botao_recolher(recolhido):
    if st.button(
        "",
        icon=(
            ":material/left_panel_open:"
            if recolhido
            else ":material/left_panel_close:"
        ),
        key="cti_toggle",
        help="Expandir menu" if recolhido else "Recolher menu",
    ):
        st.session_state.sidebar_recolhido = not recolhido
        st.rerun()


def render_sidebar():
    st.session_state.setdefault("pagina_atual", "Visão Geral")
    st.session_state.setdefault("sidebar_recolhido", False)

    recolhido = st.session_state.sidebar_recolhido
    logo_cheia, logo_compacta = _logos()

    with st.sidebar:
        # ── Logo (sempre visível, nos dois estados) ──────────────────────
        with st.container(key="cti_sidebar_logo"):
            if recolhido:
                logo = (
                    f'<img src="{logo_compacta}" alt="CTI" class="cti-logo-mini">'
                    if logo_compacta
                    else "<strong>CTI</strong>"
                )
                st.markdown(
                    f'<div class="cti-logo-wrap">{logo}</div>',
                    unsafe_allow_html=True,
                )
            else:
                logo_col, toggle_col = st.columns(
                    [5, 1], vertical_alignment="center", gap="small"
                )
                with logo_col:
                    logo = (
                        f'<img src="{logo_cheia}" alt="CTI" class="cti-logo-full">'
                        if logo_cheia
                        else "<strong>CTI</strong>"
                    )
                    st.markdown(
                        f'<div class="cti-logo-wrap">{logo}</div>',
                        unsafe_allow_html=True,
                    )
                with toggle_col:
                    _botao_recolher(recolhido)

        if recolhido:
            with st.container(key="cti_toggle_row"):
                _botao_recolher(recolhido)

        # ── Navegação (única área que rola, só se a tela for muito baixa) ─
        with st.container(key="cti_sidebar_navigation"):
            for titulo, itens in GRUPOS:
                if titulo:
                    if recolhido:
                        st.markdown(
                            '<div class="cti-group-sep"></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="cti-group-title">{titulo}</div>',
                            unsafe_allow_html=True,
                        )

                for nome, icone in itens:
                    item_menu(nome, icone, recolhido)

        # ── Rodapé fixo ─────────────────────────────────────────────────
        with st.container(key="cti_sidebar_bottom"):
            if not recolhido:
                with st.container(key="cti_help_card"):
                    st.markdown(
                        f"""
                        <div class="cti-help-heading">
                            <span class="cti-help-icon">{ICONE_AJUDA}</span>
                            <div>
                                <strong>Precisa de ajuda?</strong>
                                <p>Verifique nossa seção explicativa.</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Ajuda",
                        key="cti_ajuda",
                        use_container_width=True,
                    ):
                        st.session_state.pagina_atual = "Ajuda"
                        st.rerun()

            item_menu("Configurações", "settings", recolhido)

            if st.button(
                "Sair",
                icon=":material/logout:",
                key="cti_sair",
                use_container_width=True,
                help="Sair" if recolhido else None,
            ):
                st.toast("Logout será integrado ao cadastro.")

    return st.session_state.pagina_atual