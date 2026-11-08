import numpy as np
import pandas as pd
import streamlit as st

from components.como_interpretar import como_interpretar
from data.load_data import carregar_demonstrativo
from pages.regressao import (
    _moeda_mi,
    _normalizar,
    _num,
    ajustar_ols,
    remover_colineares,
)

RECEITA = "DRE - Receita"
EBITDA = "DRE - EBITDA"
CAIXA = "FLU - Geração de Caixa"
RESULTADO = "DRE - Resultado Líquido"


DRIVERS = {
    "Receita": "DRE - Receita",
    "Custos": "DRE - Custos",
    "Investimentos": "FLU - Investimentos",
}

VARIACAO_SENSIBILIDADE = 0.10

ICONE_ALERTA = "⚠️"

ICONES_STATUS = {
    "positivo": "✓",
    "atencao": ICONE_ALERTA,
    "negativo": "✕",
    "neutro": "i",
}

ROTULOS_STATUS = {
    "positivo": ("favorável", "favoráveis"),
    "atencao": ("atenção", "atenção"),
    "negativo": ("crítico", "críticos"),
    "neutro": ("informativo", "informativos"),
}

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

    /* chips de resumo dos status */
    .ins-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .ins-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid #E3ECF5;
        border-radius: 999px;
        padding: 5px 14px 5px 6px;
        font-size: 13px;
        font-weight: 650;
    }

    .ins-chip--positivo { background: #E6F6EE; border-color: #BFE3D0; color: #19623F; }
    .ins-chip--atencao  { background: #FFF6DD; border-color: #F1DDA0; color: #7A5600; }
    .ins-chip--negativo { background: #FDECEC; border-color: #F3C6C6; color: #8F2222; }
    .ins-chip--neutro   { background: #F4F8FC; border-color: #E1ECF7; color: #4A5E75; }

    /* selos de status */
    .ins-status {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        min-width: 28px;
        border-radius: 50%;
        font-size: 14px;
        font-weight: 800;
        line-height: 1;
    }

    .ins-status--sm {
        width: 20px;
        height: 20px;
        min-width: 20px;
        font-size: 11px;
    }

    .ins-status--positivo { background: #E6F6EE; color: #1F7A4F; }
    .ins-status--atencao  { background: #FFF6DD; color: #9A6B00; }
    .ins-status--negativo { background: #FDECEC; color: #B02A2A; }
    .ins-status--neutro   { background: #E8F2FA; color: #1B6AA0; }

    /* cards */
    .ins-card {
        display: flex;
        flex-direction: column;
        height: 100%;
        box-sizing: border-box;
        background: #fff;
        border: 1px solid #E1ECF7;
        border-left: 4px solid #2585C5;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 18px 20px;
        transition: all 0.2s ease;
    }

    .ins-card:hover {
        box-shadow: 0 6px 18px rgba(23, 59, 99, .10);
        transform: translateY(-2px);
    }

    .ins-card--positivo { border-left-color: #2E9E6B; }
    .ins-card--atencao  { border-left-color: #E0A100; background: #FFFDF5; }
    .ins-card--negativo { border-left-color: #D64545; background: #FFF9F9; }
    .ins-card--neutro   { border-left-color: #2585C5; }

    .ins-card-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
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
    }

    .ins-value {
        font-size: clamp(20px, 1.9vw, 28px);
        font-weight: 700;
        color: var(--cti-blue);
        line-height: 1.2;
        white-space: nowrap;
    }

    .ins-card--positivo .ins-value { color: #1F7A4F; }
    .ins-card--atencao  .ins-value { color: #9A6B00; }
    .ins-card--negativo .ins-value { color: #B02A2A; }

    .ins-card-title {
        font-size: 14px;
        font-weight: 700;
        color: var(--cti-text);
        margin-top: 4px;
    }

    .ins-text {
        flex: 1;
        font-size: 12.5px;
        color: var(--cti-muted);
        line-height: 1.5;
        margin-top: 4px;
        padding-bottom: 10px;
        border-bottom: 1px solid #EEF3F9;
    }

    .ins-action {
        font-size: 12px;
        font-weight: 600;
        color: #2E8B6A;
        margin-top: 10px;
    }

    .ins-card--atencao .ins-action { color: #9A6B00; }
    .ins-card--negativo .ins-action { color: #B02A2A; }
    .ins-card--neutro .ins-action { color: #1B6AA0; }

    /* conclusão */
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
        margin: 0 0 8px 0;
        font-size: 14px;
        line-height: 1.75;
        color: rgba(255, 255, 255, .92);
    }

    .ins-pitch p:last-child {
        margin-bottom: 0;
    }
</style>
"""


def _html_seguro(texto):
    """Evita que o Markdown do Streamlit interprete R$ ... R$ como fórmula."""
    return str(texto).replace("$", "&#36;")


def _pct(valor, sinal=False):
    texto = _num(valor * 100, 1) + "%"
    return ("+" + texto) if sinal and valor > 0 else texto


def _caixa_do_cenario(dados_ano, cenario):
    caixa = dados_ano.groupby("Cenario")[CAIXA].mean().dropna() / 1e6
    valor = caixa.get(cenario, np.nan)
    posicao = int((caixa > valor).sum()) + 1 if not np.isnan(valor) else None
    media = caixa.mean() if len(caixa) else np.nan
    return valor, media, posicao, len(caixa)


def _caixa_todos(dados_ano):
    """Resumo do caixa de todos os cenários do ano, ou None se não houver dados."""
    caixa = dados_ano.groupby("Cenario")[CAIXA].mean().dropna() / 1e6

    if caixa.empty:
        return None

    melhor = caixa.idxmax()
    pior = caixa.idxmin()

    return {
        "media": float(caixa.mean()),
        "p10": float(caixa.quantile(.10)),
        "p90": float(caixa.quantile(.90)),
        "melhor": (int(melhor), float(caixa[melhor])),
        "pior": (int(pior), float(caixa[pior])),
        "negativos": int((caixa < 0).sum()),
        "total": len(caixa),
    }


def _crescimento_receita(df, ano):
    receita_media = df.groupby("Ano")[RECEITA].mean().sort_index()
    anterior = receita_media.shift(1)

    crescimento = (
        ((receita_media - anterior) / anterior.abs())
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if ano not in crescimento.index:
        return None, None

    posicao = int((crescimento > crescimento[ano]).sum()) + 1
    return crescimento[ano], posicao


def _melhor_margem(dados_ano):
    validos = dados_ano[dados_ano[RECEITA] > 0]
    margem = (validos[EBITDA] / validos[RECEITA]).dropna()

    if margem.empty:
        return None, None, None

    melhor = margem.idxmax()
    linha = validos.loc[melhor]

    if isinstance(linha, pd.DataFrame):
        linha = linha.iloc[0]

    return margem[melhor], int(linha["Cenario"]), margem.mean()


def _maior_sensibilidade(dados_ano):
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


def cenario_padrao(df):
    """Na primeira visita, destaca o cenário com mais caixa no último ano."""
    base = _normalizar(df)

    ultimo_ano = base[base["Ano"] == base["Ano"].max()]
    caixa = ultimo_ano.groupby("Cenario")[CAIXA].mean().dropna()

    if caixa.empty:
        return int(sorted(base["Cenario"].unique())[0])

    return int(caixa.idxmax())


def calcular_insights(df, ano, cenario):
    """Os 4 cartões e a conclusão (usado pela tela e pelo relatório em PDF).

    Cada cartão: {"valor", "titulo", "texto", "acao", "status"}.
    Com cenario="Todos", o primeiro cartão resume todos os cenários.
    """
    base = _normalizar(df)
    dados_ano = base[base["Ano"] == ano]
    todos = cenario == "Todos"

    crescimento, posicao_cresc = _crescimento_receita(base, ano)
    margem, cenario_margem, margem_media = _melhor_margem(dados_ano)
    driver, impacto = _maior_sensibilidade(dados_ano)

    if todos:
        resumo_caixa = _caixa_todos(dados_ano)
        caixa = np.nan
        caixa_media = resumo_caixa["media"] if resumo_caixa else np.nan
        posicao_caixa, total = None, (resumo_caixa["total"] if resumo_caixa else 0)
    else:
        resumo_caixa = None
        caixa, caixa_media, posicao_caixa, total = _caixa_do_cenario(dados_ano, cenario)

    def card(valor, titulo, texto, acao, status="neutro"):
        return {
            "valor": valor,
            "titulo": titulo,
            "texto": texto,
            "acao": acao,
            "status": status,
        }

    cards = []

    # 01. Caixa
    if todos:
        if resumo_caixa is None:
            cards.append(card("N/D", "Caixa dos cenários",
                              f"Nenhum cenário tem geração de caixa no Ano {ano}.",
                              "Selecione outro ano"))
        else:
            r = resumo_caixa
            texto = (
                f"Os {_num(r['total'], 0)} cenários geram, em média, "
                f"{_moeda_mi(r['media'])} no Ano {ano}; 80% ficaram entre "
                f"{_moeda_mi(r['p10'])} e {_moeda_mi(r['p90'])}. "
                f"O melhor foi o Cenário {r['melhor'][0]} ({_moeda_mi(r['melhor'][1])}) "
                f"e o pior, o Cenário {r['pior'][0]} ({_moeda_mi(r['pior'][1])})."
            )

            if r["negativos"] > 0:
                plural = "cenários terminam" if r["negativos"] > 1 else "cenário termina"
                texto += f" {_num(r['negativos'], 0)} {plural} com caixa negativo."

            if r["media"] < 0:
                status = "negativo"
            elif r["negativos"] > 0:
                status = "atencao"
            else:
                status = "positivo"

            cards.append(card(
                _moeda_mi(r["media"]),
                "Caixa médio dos cenários",
                texto,
                "Escolha um cenário para compará-lo com a média",
                status,
            ))

    elif np.isnan(caixa):
        cards.append(card("N/D", "Caixa em destaque",
                          f"Cenário {cenario} sem geração de caixa no Ano {ano}.",
                          "Escolha outro cenário"))
    else:
        diferenca = caixa - caixa_media
        comparacao = "acima" if diferenca >= 0 else "abaixo"
        topo = posicao_caixa <= max(1, total // 10)

        if caixa < 0:
            status = "negativo"
        elif diferenca >= 0:
            status = "positivo"
        else:
            status = "atencao"

        cards.append(card(
            _moeda_mi(caixa),
            "Caixa em destaque",
            f"O Cenário {cenario} gera {_moeda_mi(abs(diferenca))} {comparacao} "
            f"da média dos cenários e ocupa a posição {_num(posicao_caixa, 0)} "
            f"de {_num(total, 0)} no Ano {ano}.",
            "Use-o como referência para o planejamento" if topo
            else "Compare com os cenários de maior caixa",
            status,
        ))

    # 02. Crescimento da receita média
    if crescimento is None:
        cards.append(card("N/D", "Receita",
                          f"O Ano {ano} é o primeiro da série; não há ano anterior para comparar.",
                          "Selecione um ano posterior"))
    else:
        if posicao_cresc == 1:
            destaque = "o maior crescimento anual da série"
        else:
            destaque = f"o {posicao_cresc}º maior crescimento anual da série"

        if crescimento > 0:
            status = "positivo"
        elif crescimento < 0:
            status = "negativo"
        else:
            status = "neutro"

        cards.append(card(
            _pct(crescimento, sinal=True),
            "Receita acelera" if crescimento > 0 else "Receita recua",
            f"A receita média do Ano {ano} varia {_pct(crescimento, sinal=True)} "
            f"sobre o Ano {ano - 1}, {destaque}.",
            "Proteja a capacidade operacional para sustentar o ritmo"
            if crescimento > 0
            else "Investigue as causas da queda de receita",
            status,
        ))

    # 03. Melhor margem EBITDA do ano
    if margem is None:
        cards.append(card("N/D", "Melhor margem",
                          f"Sem receita positiva no Ano {ano} para calcular a margem.",
                          "Revise os dados do ano"))
    else:
        cards.append(card(
            _pct(margem),
            "Melhor margem",
            f"O Cenário {cenario_margem} tem a maior margem EBITDA do Ano {ano}; "
            f"a média dos cenários é {_pct(margem_media)}.",
            "Priorize o mix de maior contribuição",
            "positivo" if margem_media > 0 else "negativo",
        ))

    # 04. Variável com maior impacto no Resultado Líquido
    if driver is None:
        cards.append(card("N/D", "Maior sensibilidade",
                          "Não há dados suficientes para medir a sensibilidade neste ano.",
                          "Selecione outro ano"))
    else:
        cards.append(card(
            driver,
            "Maior sensibilidade",
            f"Uma variação de {VARIACAO_SENSIBILIDADE:.0%} em {driver} muda o "
            f"Resultado Líquido em cerca de {_moeda_mi(impacto)}.",
            f"Monitore {driver} de perto nas simulações",
            "neutro",
        ))

    # Conclusão: junta os sinais dos cartões
    cresce = crescimento is not None and crescimento > 0

    if todos:
        caixa_acima = not np.isnan(caixa_media) and caixa_media > 0
    else:
        caixa_acima = not np.isnan(caixa) and caixa >= caixa_media

    if todos:
        if cresce and caixa_acima:
            titulo = "Crescimento com caixa positivo"
        elif cresce:
            titulo = "Crescimento que pede atenção ao caixa"
        elif caixa_acima:
            titulo = "Caixa positivo em um ano de receita fraca"
        else:
            titulo = "Momento de proteger resultado e caixa"
    else:
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
            + (f" e a margem EBITDA média é de {_pct(margem_media)}."
               if margem is not None else ".")
        )
    elif margem is not None:
        linhas.append(f"No Ano {ano}, a margem EBITDA média é de {_pct(margem_media)}.")

    if todos:
        if resumo_caixa is not None:
            linhas.append(
                f"Entre os {_num(resumo_caixa['total'], 0)} cenários, a geração de "
                f"caixa média é de {_moeda_mi(resumo_caixa['media'])}, variando de "
                f"{_moeda_mi(resumo_caixa['pior'][1])} a "
                f"{_moeda_mi(resumo_caixa['melhor'][1])}."
            )
    elif not np.isnan(caixa):
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

    return {"cards": cards, "conclusao_titulo": titulo, "conclusao": linhas}


def _topo(anos, cenarios, cenario_padrao):
    opcoes = ["Todos"] + cenarios

    indice = 1 + cenarios.index(cenario_padrao) if cenario_padrao in cenarios else 1

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
                options=opcoes,
                index=indice,
                format_func=lambda c: "Todos os cenários" if c == "Todos" else f"Cenário {c}",
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


def _chips(cards):
    contagem = {status: 0 for status in ROTULOS_STATUS}

    for card in cards:
        contagem[card.get("status", "neutro")] += 1

    chips = []

    for status, (singular, plural) in ROTULOS_STATUS.items():
        n = contagem[status]

        if n == 0:
            continue

        chips.append(
            f'<span class="ins-chip ins-chip--{status}">'
            f'<span class="ins-status ins-status--sm ins-status--{status}">'
            f'{ICONES_STATUS[status]}</span>'
            f'{n} {singular if n == 1 else plural}</span>'
        )

    st.markdown(
        f'<div class="ins-chips">{"".join(chips)}</div>',
        unsafe_allow_html=True
    )


def _card(numero, valor, titulo, texto, acao, status="neutro"):
    st.markdown(
        _html_seguro(
            f'<div class="ins-card ins-card--{status}">'
            f'<div class="ins-card-head">'
            f'<span class="ins-badge">{numero:02d}</span>'
            f'<span class="ins-status ins-status--{status}">{ICONES_STATUS[status]}</span>'
            f'</div>'
            f'<div class="ins-value">{valor}</div>'
            f'<div class="ins-card-title">{titulo}</div>'
            f'<div class="ins-text">{texto}</div>'
            f'<div class="ins-action">{acao} →</div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )


def _pitch(titulo, linhas):
    corpo = "".join(f"<p>{linha}</p>" for linha in linhas)

    st.markdown(
        _html_seguro(
            '<div class="ins-pitch">'
            '<div class="ins-pitch-eyebrow">CONCLUSÃO PARA A APRESENTAÇÃO</div>'
            f'<div class="ins-pitch-title">{titulo}</div>'
            f'{corpo}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_insights():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="ins_page"):
        try:
            df = carregar_demonstrativo()
        except Exception as erro:
            st.error(f"Não foi possível carregar a base do demonstrativo: {erro}")
            return

        base = _normalizar(df)

        anos = sorted(base["Ano"].unique().tolist())
        cenarios = sorted(base["Cenario"].unique().tolist())

        if not anos or not cenarios:
            st.warning("Não há anos ou cenários disponíveis na base.")
            return


        ano, cenario = _topo(anos, cenarios, cenario_padrao(base))
        resultado = calcular_insights(base, ano, cenario)

        _chips(resultado["cards"])

        colunas = st.columns(4, gap="small")
        for numero, (coluna, card) in enumerate(zip(colunas, resultado["cards"]), start=1):
            with coluna:
                _card(
                    numero,
                    card["valor"],
                    card["titulo"],
                    card["texto"],
                    card["acao"],
                    card["status"],
                )

        _pitch(resultado["conclusao_titulo"], resultado["conclusao"])

        como_interpretar(
            "ins",
            [
                "**01 Caixa em destaque:** compara a geração de caixa do cenário "
                "escolhido com a média dos cenários do ano. Em \"Todos os cenários\", "
                "mostra o caixa médio, a faixa que concentra 80% dos cenários, o "
                "melhor e o pior.",
                "**02 Receita:** variação da receita média sobre o ano anterior.",
                "**03 Melhor margem:** cenário com a maior margem EBITDA do ano.",
                "**04 Maior sensibilidade:** variável que mais move o Resultado "
                "Líquido se variar 10%.",
                "**Cores:** verde é favorável, amarelo pede atenção, vermelho é "
                "crítico e azul é informativo.",
                "**Conclusão:** junta os quatro sinais em um texto pronto para a "
                "apresentação.",
            ],
            "são leituras descritivas dos cenários simulados, não previsões.",
        )