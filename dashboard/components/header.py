import unicodedata
import streamlit as st
from components.auth import usuario_logado


# Busca por termos que existem em cada página. A busca é contextual:
# só lista resultados relacionados à página atualmente aberta.
BUSCA_POR_PAGINA = {
    "Visão Geral": {
        "EBITDA": ["ebitda", "resultado operacional"],
        "Margem EBITDA": ["margem ebitda", "margem operacional"],
        "Margem Líquida": ["margem líquida", "margem liquida"],
        "NOPAT": ["nopat", "lucro operacional após impostos"],
        "Liquidez Corrente": ["liquidez corrente", "liquidez", "lc"],
        "ROIC": ["roic", "retorno sobre capital"],
        "EVA": ["eva", "valor econômico agregado", "valor economico agregado"],
        "WACC": ["wacc", "custo médio ponderado de capital", "custo de capital"],
        "Cenários": ["cenário", "cenarios", "cenário base", "cenario base"],
        "Evolução anual": ["evolução", "evolucao", "ano", "histórico", "historico"],
    },
    "Regressão": {
        "Regressão": ["regressão", "regressao", "modelo", "variável", "variavel"],
        "Correlação": ["correlação", "correlacao", "correlacionar"],
        "Previsão": ["previsão", "previsao", "predição", "predicao"],
        "Resíduos": ["resíduo", "residuo", "resíduos", "residuos"],
        "R²": ["r²", "r2", "coeficiente de determinação", "coeficiente de determinacao"],
    },
    "Insights": {
        "Insights": ["insight", "insights", "destaques", "análise", "analise"],
        "Indicadores": ["indicador", "indicadores", "kpi", "kpis"],
        "Tendências": ["tendência", "tendencia", "evolução", "evolucao"],
    },
    "Configurações": {
        "Perfil da conta": ["perfil", "conta", "usuário", "usuario", "email", "e-mail"],
    },
}

AJUDA_POR_PAGINA = {
    "Visão Geral": (
        "A Visão Geral reúne os principais indicadores financeiros da CTI. "
        "Use os filtros de ano e cenário para consultar os resultados e os gráficos "
        "para acompanhar a evolução dos indicadores. As comparações dependem dos dados disponíveis."
    ),
    "Regressão": (
        "A página de Regressão permite investigar relações entre variáveis por meio de modelos estatísticos. "
        "Observe os coeficientes, as métricas de ajuste e os resíduos. Associação estatística, por si só, "
        "não comprova causalidade."
    ),
    "Insights": (
        "A página de Insights reúne destaques e análises derivados da base financeira para ajudar a "
        "identificar tendências e pontos que merecem investigação."
    ),
    "Configurações": (
        "Nesta página você consulta os dados básicos do perfil autenticado. "
        "A edição de dados e as preferências ainda não estão disponíveis."
    ),
}

def _normalizar(texto):
    texto = str(texto or "").casefold().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return " ".join(texto.split())


def render_header(pagina_atual=None):
    usuario = usuario_logado() or {}
    pagina = pagina_atual or st.session_state.get("pagina_atual", "Visão Geral")


    with st.container(key="cti_topbar"):
        busca, ajuda, _espaco_notificacao, perfil = st.columns(
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
                help="Digite um termo para procurar nesta página.",
            )

        with ajuda:
            if st.button(
                "",
                icon=":material/help:",
                key="cti_header_ajuda",
                help="Ajuda sobre esta página",
            ):
                st.session_state["cti_ajuda_aberta"] = not st.session_state.get(
                    "cti_ajuda_aberta", False
                )

        with perfil:
            if st.button(
                "",
                icon=":material/account_circle:",
                key="cti_header_perfil",
                help=usuario.get("nome", "Perfil"),
            ):
                st.session_state["cti_navegar_para"] = "Configurações"
                st.rerun()

    if st.session_state.get("cti_ajuda_aberta", False):
        st.info(
            AJUDA_POR_PAGINA.get(
                pagina,
                f"A página {pagina} ainda não tem uma explicação específica.",
            ),
            icon=":material/help:",
        )

    # A busca é atualizada enquanto a pessoa digita, sem exigir Enter.
    consulta_original = st.session_state.get("cti_busca", "").strip()
    consulta = _normalizar(consulta_original)
    if consulta:
        termos_pagina = BUSCA_POR_PAGINA.get(pagina, {})
        encontrados = []
        for nome, sinonimos in termos_pagina.items():
            termos = [nome, *sinonimos]
            if any(
                consulta in _normalizar(termo) or _normalizar(termo) in consulta
                for termo in termos
            ):
                encontrados.append(nome)

        if encontrados:
            st.success(
                "Encontrado nesta página: " + ", ".join(dict.fromkeys(encontrados)),
                icon=":material/search:",
            )
        else:
            st.warning(
                f"Não encontrei ‘{consulta_original}’ entre os termos cadastrados para a página {pagina}.",
                icon=":material/search_off:",
            )
