import unicodedata
import streamlit as st
from components.auth import usuario_logado


# Termos que cada página mostra. A busca procura em todas as páginas e
# oferece um botão para ir até a página onde o termo aparece.
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
        "Evolução anual": ["evolução", "evolucao", "histórico", "historico"],
    },
    "Indicadores": {
        "Rentabilidade": ["rentabilidade", "margem", "retorno", "roic"],
        "Liquidez": ["liquidez", "liquidez corrente", "liquidez seca", "capacidade de pagamento"],
        "Estrutura de capital": ["estrutura de capital", "endividamento", "dívida", "divida"],
        "Resultado e valor econômico": ["eva", "nopat", "valor econômico", "valor economico", "mva"],
        "Capital investido": ["capital investido", "capital"],
        "Tabela de indicadores": ["tabela", "indicadores", "kpi", "kpis"],
    },
    "Comparação": {
        "Comparação de cenários": ["comparar", "comparação", "comparacao", "cenários", "cenarios"],
        "EBITDA × Margem EBITDA": ["ebitda", "margem ebitda"],
    },
    "Ranking": {
        "Ranking de cenários": ["ranking", "melhores", "piores", "classificação", "classificacao"],
        "EBITDA por cenário": ["ebitda", "maiores", "menores"],
    },
    "Regressão": {
        "Regressão": ["regressão", "regressao", "modelo", "geração de caixa", "geracao de caixa"],
        "Impacto de cada fator": ["impacto", "fator", "fatores", "influência", "influencia", "correlação", "correlacao"],
        "Confiança": ["confiança", "confianca", "p-valor", "significância", "significancia"],
        "O modelo acerta?": ["previsão", "previsao", "previsto", "real", "predição", "predicao"],
        "Quanto o modelo explica": ["r²", "r2", "explica", "ajuste", "coeficiente de determinação"],
        "Erro típico da previsão": ["erro", "rmse", "precisão", "precisao"],
    },
    "Insights": {
        "Insights": ["insight", "insights", "destaques", "conclusão", "conclusao", "pitch"],
        "Caixa em destaque": ["caixa", "geração de caixa", "geracao de caixa"],
        "Crescimento da receita": ["receita", "crescimento"],
        "Melhor margem": ["margem", "melhor margem"],
        "Maior sensibilidade": ["sensibilidade", "variação", "variacao"],
    },
    "Simular novo cenário": {
        "Simulador": ["simular", "simulação", "simulacao", "novo cenário", "novo cenario"],
    },
    "Configurações": {
        "Perfil da conta": ["perfil", "conta", "usuário", "usuario", "email", "e-mail", "nome"],
        "Senha": ["senha", "segurança", "seguranca", "alterar senha"],
        "Preferências": ["preferência", "preferencia", "página inicial", "pagina inicial", "menu"],
        "Excluir conta": ["excluir", "apagar", "deletar"],
    },
}

AJUDA_POR_PAGINA = {
    "Visão Geral": (
        "A Visão Geral reúne os principais indicadores financeiros da CTI. "
        "Use os filtros de ano e cenário para consultar os resultados e os gráficos "
        "para acompanhar a evolução dos indicadores. As comparações dependem dos dados disponíveis."
    ),
    "Indicadores": (
        "A página de Indicadores detalha rentabilidade, liquidez, estrutura de capital, "
        "resultado econômico e capital investido. Escolha o ano e o cenário no topo; "
        "a tabela no fim mostra todos os valores do recorte."
    ),
    "Comparação": (
        "A página de Comparação coloca cenários lado a lado no mesmo ano. "
        "Escolha o ano e os cenários que quer comparar para ver EBITDA e Margem EBITDA de cada um."
    ),
    "Ranking": (
        "O Ranking ordena os cenários pelo EBITDA no ano escolhido, mostrando os de maior "
        "e de menor resultado."
    ),
    "Regressão": (
        "A página de Regressão responde o que mais influencia a Geração de Caixa, comparando os "
        "1.200 cenários de um ano. Escolha o ano; as barras mostram quanto o caixa muda se cada fator "
        "crescer 10%, com o grau de confiança. Associação não comprova causa e efeito."
    ),
    "Insights": (
        "A página de Insights resume os destaques do ano escolhido: caixa do cenário selecionado, "
        "crescimento da receita, melhor margem e o fator de maior sensibilidade, "
        "com uma conclusão pronta para o pitch."
    ),
    "Configurações": (
        "Nesta página você edita seu nome, troca a senha, escolhe a página inicial "
        "e se o menu lateral abre recolhido. Também é possível excluir a conta, "
        "o que exige a sua senha."
    ),
}

AJUDA_EM_CONSTRUCAO = (
    "A página {pagina} ainda está em desenvolvimento. Enquanto isso, use o menu lateral "
    "para acessar as páginas disponíveis."
)


def _normalizar(texto):
    texto = str(texto or "").casefold().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    return " ".join(texto.split())


def _buscar(consulta):
    """Páginas (e itens dentro delas) que combinam com o termo digitado."""
    consulta = _normalizar(consulta)
    resultados = {}

    for pagina, itens in BUSCA_POR_PAGINA.items():
        encontrados = []

        for nome, sinonimos in itens.items():
            for termo in (_normalizar(t) for t in [nome, *sinonimos]):
                # termo dentro da consulta só vale para termos maiores, senão
                # siglas curtas casariam com qualquer palavra
                if consulta in termo or (len(termo) >= 4 and termo in consulta):
                    encontrados.append(nome)
                    break

        # Digitar o nome da página também leva até ela
        if not encontrados and consulta in _normalizar(pagina):
            encontrados.append(pagina)

        if encontrados:
            resultados[pagina] = encontrados

    return resultados


def _ir_para(pagina):
    # Callback: roda antes de o menu lateral ser desenhado, então o item
    # certo já aparece destacado, e pode limpar a busca
    st.session_state["pagina_atual"] = pagina
    st.session_state["cti_navegar_para"] = pagina
    st.session_state["cti_busca"] = ""


def _limpar_busca():
    st.session_state["cti_busca"] = ""


def _resultados_busca(pagina_atual):
    consulta = st.session_state.get("cti_busca", "").strip()
    if not consulta:
        return

    resultados = _buscar(consulta)

    with st.container(key="cti_busca_resultados"):
        if not resultados:
            st.warning(
                f"Nada encontrado para ‘{consulta}’. Tente outro termo, como EBITDA, "
                "liquidez, ranking ou senha.",
                icon=":material/search_off:",
            )
        else:
            if pagina_atual in resultados:
                st.success(
                    "Nesta página: " + ", ".join(resultados[pagina_atual]),
                    icon=":material/search:",
                )

            outras = [p for p in resultados if p != pagina_atual]
            if outras:
                st.caption("Também aparece em:")
                # Sempre 4 colunas: com um resultado só, o botão não ocupa a linha toda
                colunas = st.columns(4)
                for i, pagina in enumerate(outras):
                    with colunas[i % 4]:
                        st.button(
                            f"Ir para {pagina}",
                            icon=":material/arrow_forward:",
                            key=f"cti_busca_ir_{i}",
                            help=", ".join(resultados[pagina]),
                            on_click=_ir_para,
                            args=(pagina,),
                            use_container_width=True,
                        )

        st.button(
            "Limpar busca",
            icon=":material/close:",
            key="cti_busca_limpar",
            type="tertiary",
            on_click=_limpar_busca,
        )


def render_header(pagina_atual=None):
    usuario = usuario_logado() or {}
    pagina = pagina_atual or st.session_state.get("pagina_atual", "Visão Geral")

    with st.container(key="cti_topbar"):
        busca, ajuda, perfil = st.columns(
            [1, 1, 1],
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
                help="Procura o termo em todas as páginas.",
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
            st.button(
                "",
                icon=":material/account_circle:",
                key="cti_header_perfil",
                help=f"{usuario.get('nome', 'Perfil')} · Configurações da conta",
                on_click=_ir_para,
                args=("Configurações",),
            )

    if st.session_state.get("cti_ajuda_aberta", False):
        with st.container(key="cti_ajuda_box"):
            st.info(
                AJUDA_POR_PAGINA.get(pagina, AJUDA_EM_CONSTRUCAO.format(pagina=pagina)),
                icon=":material/help:",
            )

    _resultados_busca(pagina)
