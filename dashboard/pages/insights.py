import numpy as np
import streamlit as st

from data.load_data import carregar_demonstrativo
from pages.regressao import _moeda_mi, _num, ajustar_ols, remover_colineares

RECEITA = "DRE - Receita"
EBITDA = "DRE - EBITDA"
CAIXA = "FLU - Geração de Caixa"
RESULTADO = "DRE - Resultado Líquido"

# Variáveis testadas no card de sensibilidade (impacto no Resultado Líquido)
DRIVERS = {
    "Receita": "DRE - Receita",
    "Custos": "DRE - Custos",
    "Investimentos": "FLU - Investimentos",
}

VARIACAO_SENSIBILIDADE = 0.10

PAGE_STYLE = """
<style>
    .st-key-ins_page {
        padding: 28px 32px 40px;
        gap: 18px !important;
    }

    .ins-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .ins-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .ins-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .st-key-ins_topo label p {
        font-size: 12px !important;
        color: var(--cti-muted) !important;
    }

    .st-key-ins_nova_simulacao button {
        background: var(--cti-blue) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 40px;
        font-weight: 600;
        white-space: nowrap;
    }

    .st-key-ins_nova_simulacao button:hover {
        background: var(--cti-dark) !important;
    }

    /* cartões da mesma linha com a mesma altura */
    .st-key-ins_page [data-testid="stHorizontalBlock"]:has(.ins-card) {
        align-items: stretch;
    }

    .st-key-ins_page [data-testid="stColumn"]:has(.ins-card) > div,
    .st-key-ins_page [data-testid="stColumn"]:has(.ins-card) [data-testid="stVerticalBlock"],
    .st-key-ins_page [data-testid="stColumn"]:has(.ins-card) [data-testid="stElementContainer"],
    .st-key-ins_page [data-testid="stColumn"]:has(.ins-card) [data-testid="stMarkdown"],
    .st-key-ins_page [data-testid="stColumn"]:has(.ins-card) [data-testid="stMarkdown"] > div,
    .st-key-ins_page [data-testid="stColumn"]:has(.ins-card) [data-testid="stMarkdownContainer"] {
        height: 100%;
    }

    .st-key-ins_page [data-testid="stColumn"]:has(.ins-card) [data-testid="stMarkdownContainer"] {
        margin-bottom: 0 !important;
    }

    .ins-card {
        display: flex;
        flex-direction: column;
        height: 100%;
        box-sizing: border-box;
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 20px;
    }

    .ins-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: var(--cti-blue);
        color: #fff;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 18px;
    }

    .ins-value {
        font-size: clamp(20px, 1.9vw, 28px);
        font-weight: 700;
        color: var(--cti-blue);
        line-height: 1.2;
        white-space: nowrap;
    }

    .ins-card-title {
        font-size: 14px;
        font-weight: 700;
        color: var(--cti-text);
        margin-top: 4px;
    }

    .ins-text {
        flex: 1;
        font-size: 12px;
        color: var(--cti-muted);
        line-height: 1.45;
        margin-top: 4px;
        padding-bottom: 10px;
        border-bottom: 1px solid #EEF3F9;
    }

    .ins-action {
        font-size: 11.5px;
        font-weight: 600;
        color: #2E8B6A;
        margin-top: 10px;
    }

    .ins-pitch {
        background: linear-gradient(135deg, #0B5FA5 0%, var(--cti-blue) 45%, #003563 100%);
        border-radius: 16px;
        box-shadow: 0 14px 34px rgba(0, 63, 117, .22);
        padding: 30px 32px 34px;
        color: #fff;
    }

    .ins-pitch-eyebrow {
        font-size: 11px;
        letter-spacing: .12em;
        color: rgba(255, 255, 255, .7);
    }

    .ins-pitch-title {
        font-size: 24px;
        font-weight: 700;
        margin: 10px 0 12px;
    }

    .ins-pitch p {
        margin: 0;
        font-size: 13.5px;
        line-height: 1.75;
        color: rgba(255, 255, 255, .92);
    }
</style>
"""


# ---------- Cálculos ----------

def _pct(valor, sinal=False):
    texto = _num(valor * 100, 1) + "%"
    return ("+" + texto) if sinal and valor > 0 else texto


def _caixa_do_cenario(dados_ano, cenario):
    caixa = dados_ano.set_index("Cenario")[CAIXA].dropna() / 1e6
    valor = caixa.get(cenario, np.nan)
    posicao = int((caixa > valor).sum()) + 1 if not np.isnan(valor) else None
    return valor, caixa.mean(), posicao, len(caixa)


def _crescimento_receita(df, ano):
    receita_media = df.groupby("Ano")[RECEITA].mean().sort_index()
    crescimento = receita_media.pct_change().dropna()

    if ano not in crescimento.index:
        return None, None

    # posição do ano entre todos os crescimentos anuais da série (1 = maior)
    posicao = int((crescimento > crescimento[ano]).sum()) + 1
    return crescimento[ano], posicao


def _melhor_margem(dados_ano):
    validos = dados_ano[dados_ano[RECEITA] > 0]
    margem = (validos[EBITDA] / validos[RECEITA]).dropna()

    if margem.empty:
        return None, None, None

    melhor = margem.idxmax()
    return margem[melhor], int(validos.loc[melhor, "Cenario"]), margem.mean()


def _maior_sensibilidade(dados_ano):
    """Driver cuja variação de 10% mais mexe no Resultado Líquido.

    Usa a mesma regressão da página de Regressão (entre os cenários do ano):
    impacto = coeficiente x 10% do valor médio do driver.
    """
    colunas = [RESULTADO] + list(DRIVERS.values())
    dados = dados_ano[colunas].dropna()

    if len(dados) <= len(DRIVERS) + 1:
        return None, None

    y = dados[RESULTADO].to_numpy(dtype=float) / 1e6
    X = dados[list(DRIVERS.values())].to_numpy(dtype=float) / 1e6
    nomes = list(DRIVERS)

    mantidos, _ = remover_colineares(X, nomes)
    if not mantidos:
        return None, None

    modelo = ajustar_ols(y, X[:, mantidos])
    impactos = {
        nomes[i]: abs(coef * VARIACAO_SENSIBILIDADE * X[:, i].mean())
        for i, coef in zip(mantidos, modelo["coef"])
    }

    driver = max(impactos, key=impactos.get)
    return driver, impactos[driver]


# ---------- Blocos da página ----------

def _topo(anos, cenarios, cenario_padrao):
    with st.container(key="ins_topo"):
        titulo, col_ano, col_cenario, col_botao = st.columns(
            [2.6, 1, 1.2, 1.3], vertical_alignment="bottom"
        )

        with titulo:
            st.markdown("""
                <div class="ins-eyebrow">PAINEL FINANCEIRO</div>
                <div class="ins-title">Insights</div>
                <div class="ins-subtitle">
                    Explore dados, cenários e recomendações para apoiar decisões.
                </div>
            """, unsafe_allow_html=True)

        with col_ano:
            ano = st.selectbox(
                "Ano",
                options=anos,
                index=len(anos) - 1,
                format_func=lambda a: f"Ano {a}",
                key="ins_ano",
            )

        with col_cenario:
            cenario = st.selectbox(
                "Cenário",
                options=cenarios,
                index=cenarios.index(cenario_padrao),
                format_func=lambda c: f"Cenário {c}",
                key="ins_cenario",
            )

        with col_botao:
            if st.button(
                "Nova simulação",
                icon=":material/add:",
                key="ins_nova_simulacao",
                use_container_width=True,
            ):
                st.session_state.pagina_atual = "Simular novo cenário"
                st.rerun()

    return ano, cenario


def _card(numero, valor, titulo, texto, acao):
    st.markdown(f"""
        <div class="ins-card">
            <span class="ins-badge">{numero:02d}</span>
            <div class="ins-value">{valor}</div>
            <div class="ins-card-title">{titulo}</div>
            <div class="ins-text">{texto}</div>
            <div class="ins-action">{acao} →</div>
        </div>
    """, unsafe_allow_html=True)


def _pitch(titulo, linhas):
    corpo = "".join(f"<p>{linha}</p>" for linha in linhas)
    st.markdown(f"""
        <div class="ins-pitch">
            <div class="ins-pitch-eyebrow">CONCLUSÃO PARA O PITCH</div>
            <div class="ins-pitch-title">{titulo}</div>
            {corpo}
        </div>
    """, unsafe_allow_html=True)


# ---------- Página principal ----------

def render_insights():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="ins_page"):
        try:
            df = carregar_demonstrativo()
        except Exception as erro:
            st.error(f"Não foi possível carregar a base do demonstrativo: {erro}")
            return

        anos = sorted(df["Ano"].dropna().astype(int).unique().tolist())
        cenarios = sorted(df["Cenario"].dropna().astype(int).unique().tolist())

        if not anos or not cenarios:
            st.warning("Não há anos ou cenários disponíveis na base.")
            return

        # Na primeira visita, destaca o cenário com mais caixa no último ano
        ultimo_ano = df[df["Ano"] == anos[-1]]
        cenario_padrao = int(ultimo_ano.loc[ultimo_ano[CAIXA].idxmax(), "Cenario"])

        ano, cenario = _topo(anos, cenarios, cenario_padrao)
        dados_ano = df[df["Ano"] == ano]

        caixa, caixa_media, posicao_caixa, total = _caixa_do_cenario(dados_ano, cenario)
        crescimento, posicao_cresc = _crescimento_receita(df, ano)
        margem, cenario_margem, margem_media = _melhor_margem(dados_ano)
        driver, impacto = _maior_sensibilidade(dados_ano)

        col1, col2, col3, col4 = st.columns(4, gap="small")

        # 01. Caixa do cenário escolhido
        with col1:
            if np.isnan(caixa):
                _card(1, "N/D", "Caixa em destaque",
                      f"Cenário {cenario} sem geração de caixa no Ano {ano}.",
                      "Escolha outro cenário")
            else:
                diferenca = caixa - caixa_media
                comparacao = "acima" if diferenca >= 0 else "abaixo"
                topo = posicao_caixa <= max(1, total // 10)
                _card(
                    1,
                    _moeda_mi(caixa),
                    "Caixa em destaque",
                    f"O Cenário {cenario} gera {_moeda_mi(abs(diferenca))} {comparacao} "
                    f"da média dos cenários e ocupa a posição {_num(posicao_caixa, 0)} "
                    f"de {_num(total, 0)} no Ano {ano}.",
                    "Use-o como referência para o planejamento" if topo
                    else "Compare com os cenários de maior caixa",
                )

        # 02. Crescimento da receita média
        with col2:
            if crescimento is None:
                _card(2, "N/D", "Receita",
                      f"O Ano {ano} é o primeiro da série; não há ano anterior para comparar.",
                      "Selecione um ano posterior")
            else:
                if posicao_cresc == 1:
                    destaque = "o maior crescimento anual da série"
                else:
                    destaque = f"o {posicao_cresc}º maior crescimento anual da série"

                _card(
                    2,
                    _pct(crescimento, sinal=True),
                    "Receita acelera" if crescimento > 0 else "Receita recua",
                    f"A receita média do Ano {ano} varia {_pct(crescimento, sinal=True)} "
                    f"sobre o Ano {ano - 1}, {destaque}.",
                    "Proteja a capacidade operacional para sustentar o ritmo"
                    if crescimento > 0
                    else "Investigue as causas da queda de receita",
                )

        # 03. Melhor margem EBITDA do ano
        with col3:
            if margem is None:
                _card(3, "N/D", "Melhor margem",
                      f"Sem receita positiva no Ano {ano} para calcular a margem.",
                      "Revise os dados do ano")
            else:
                _card(
                    3,
                    _pct(margem),
                    "Melhor margem",
                    f"O Cenário {cenario_margem} tem a maior margem EBITDA do Ano {ano}; "
                    f"a média dos cenários é {_pct(margem_media)}.",
                    "Priorize o mix de maior contribuição",
                )

        # 04. Variável com maior impacto no Resultado Líquido
        with col4:
            if driver is None:
                _card(4, "N/D", "Maior sensibilidade",
                      "Não há dados suficientes para medir a sensibilidade neste ano.",
                      "Selecione outro ano")
            else:
                _card(
                    4,
                    driver,
                    "Maior sensibilidade",
                    f"Uma variação de {VARIACAO_SENSIBILIDADE:.0%} em {driver} muda o "
                    f"Resultado Líquido em cerca de {_moeda_mi(impacto)}.",
                    f"Monitore {driver} de perto nas simulações",
                )

        # Conclusão: junta os sinais dos cards
        cresce = crescimento is not None and crescimento > 0
        caixa_acima = not np.isnan(caixa) and caixa >= caixa_media

        if cresce and caixa_acima:
            titulo = "Crescimento com qualidade e caixa"
        elif cresce:
            titulo = "Crescimento que pede atenção ao caixa"
        elif caixa_acima:
            titulo = "Caixa sólido em um ano de receita fraca"
        else:
            titulo = "Momento de proteger resultado e caixa"

        linhas = []
        if crescimento is not None:
            linhas.append(
                f"No Ano {ano}, a receita média "
                f"{'cresce' if crescimento > 0 else 'recua'} {_pct(abs(crescimento))}"
                + (f" e a margem EBITDA média é de {_pct(margem_media)}." if margem else ".")
            )
        elif margem:
            linhas.append(f"No Ano {ano}, a margem EBITDA média é de {_pct(margem_media)}.")

        if not np.isnan(caixa):
            linhas.append(
                f"O Cenário {cenario} gera {'mais' if caixa_acima else 'menos'} caixa "
                "que a média e serve de "
                f"{'referência de retorno' if caixa_acima else 'alerta para o planejamento'}."
            )

        if driver:
            linhas.append(
                f"O foco recomendado é {driver}: é a variável que mais move o "
                "Resultado Líquido, então protegê-la protege o lucro."
            )

        _pitch(titulo, linhas)
