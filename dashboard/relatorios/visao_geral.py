"""Relatório em PDF da Visão Geral."""
import pandas as pd

from data.load_data import carregar_indicadores
from pages.visao_geral import (
    TODOS_OS_CENARIOS,
    avisos_de_qualidade,
    formatar_dias,
    formatar_moeda,
    formatar_numero,
    formatar_percentual,
    mapa_cenarios,
    valor_indicador,
    variacao_anual,
)
from relatorios.base import RelatorioPDF, descrever_evolucao, figura_linhas, numero_br

# (coluna, rótulo, formato) na mesma ordem dos cartões da tela
INDICADORES = [
    ("EBITDA", "EBITDA médio", "moeda"),
    ("Margem EBITDA", "Margem EBITDA", "percentual"),
    ("Margem Líquida", "Margem Líquida", "percentual"),
    ("NOPAT", "NOPAT", "moeda"),
    ("LC", "Liquidez Corrente", "numero"),
    ("ROIC", "ROIC", "percentual"),
    ("EVA", "EVA", "moeda"),
    ("WACC", "WACC", "percentual"),
    ("ROE", "ROE", "percentual"),
    ("FCO", "FCO", "moeda"),
    ("FCL", "FCL", "moeda"),
    ("Ciclo Financeiro", "Ciclo Financeiro", "dias"),
]

FORMATADORES = {
    "moeda": formatar_moeda,
    "percentual": formatar_percentual,
    "numero": formatar_numero,
    "dias": formatar_dias,
}


def _resumo_executivo(df, ano, cenario):
    """Frases interpretativas montadas a partir dos números (sem IA)."""
    v = lambda coluna: valor_indicador(df, ano, cenario, coluna)  # noqa: E731
    frases = []

    ebitda = v("EBITDA")
    if pd.notna(ebitda):
        variacao = variacao_anual(df, ano, cenario, "EBITDA", "moeda")["texto"]
        if variacao.startswith(("↑", "↓")):
            direcao = "cresceu" if variacao.startswith("↑") else "caiu"
            percentual = variacao[2:].replace(" vs. ano anterior", "")
            complemento = f", e {direcao} {percentual} em relação ao ano anterior"
        else:
            complemento = ""
        frases.append(
            f"O EBITDA, que mostra quanto a operação gera antes de juros e impostos, "
            f"é de {formatar_moeda(ebitda)}{complemento}."
        )

    margem_ebitda, margem_liquida = v("Margem EBITDA"), v("Margem Líquida")
    if pd.notna(margem_ebitda) and margem_ebitda > 1:
        # margem acima de 100% não tem leitura econômica: aponta o problema
        frases.append(
            f"A margem EBITDA da base está em {formatar_percentual(margem_ebitda)}, acima de "
            "100%, o que não tem leitura econômica direta e indica um ponto a validar na "
            "planilha (veja “Qualidade e disponibilidade dos dados”)."
            + (f" A margem líquida é de {formatar_percentual(margem_liquida)}."
               if pd.notna(margem_liquida) else "")
        )
    elif pd.notna(margem_ebitda) and pd.notna(margem_liquida):
        frases.append(
            f"De cada R$ 100 de receita, R$ {numero_br(margem_ebitda * 100)} viram resultado "
            f"operacional (margem EBITDA) e R$ {numero_br(margem_liquida * 100)} sobram como "
            "lucro líquido depois de juros e impostos (margem líquida)."
        )

    roic, wacc, eva = v("ROIC"), v("WACC"), v("EVA")
    if pd.notna(roic) and pd.notna(wacc):
        if roic > wacc:
            frase = (
                f"O retorno sobre o capital investido (ROIC de {formatar_percentual(roic)}) "
                f"supera o custo desse capital (WACC de {formatar_percentual(wacc)}): "
                "o negócio gera valor."
            )
        else:
            frase = (
                f"O retorno sobre o capital investido (ROIC de {formatar_percentual(roic)}) "
                f"não cobre o custo desse capital (WACC de {formatar_percentual(wacc)}): "
                "o negócio destrói valor neste recorte."
            )
        if pd.notna(eva):
            frase += f" O EVA, que mede esse valor em reais, é de {formatar_moeda(eva)}."
        frases.append(frase)
    elif pd.isna(roic):
        frases.append(
            "Não há ROIC disponível para este ano na base, então não é possível comparar "
            "o retorno do capital com o seu custo (WACC)."
        )

    liquidez = v("LC")
    if pd.notna(liquidez):
        if liquidez >= 1.5:
            leitura = "folga confortável para pagar as obrigações de curto prazo"
        elif liquidez >= 1:
            leitura = "recursos suficientes, mas sem muita folga, para as obrigações de curto prazo"
        else:
            leitura = "menos recursos de curto prazo do que obrigações: ponto de atenção"
        frases.append(
            f"A liquidez corrente de {formatar_numero(liquidez)} indica {leitura}."
        )

    fco, fcl = v("FCO"), v("FCL")
    if pd.notna(fco) and pd.notna(fcl):
        if fcl >= 0:
            leitura = "a operação gera caixa suficiente para cobrir os investimentos"
        else:
            leitura = "os investimentos consomem mais caixa do que a operação gera"
        frases.append(
            f"A operação gera {formatar_moeda(fco)} de caixa (FCO) e, depois dos "
            f"investimentos, sobram {formatar_moeda(fcl)} (FCL): {leitura}."
        )

    ciclo = v("Ciclo Financeiro")
    if pd.notna(ciclo):
        if ciclo > 0:
            frases.append(
                f"O ciclo financeiro é de {formatar_dias(ciclo)}: é o tempo em que o "
                "caixa fica preso entre pagar fornecedores e receber dos clientes."
            )
        else:
            frases.append(
                f"O ciclo financeiro é de {formatar_dias(ciclo)}: a empresa recebe dos "
                "clientes antes de pagar os fornecedores, o que favorece o caixa."
            )

    return frases


def _historico(df, cenario):
    if cenario == TODOS_OS_CENARIOS:
        return df
    return df[df["Cenario"].astype(str) == cenario]


def _serie(historico, coluna):
    if coluna not in historico.columns:
        return pd.Series(dtype=float)
    return historico.groupby("Ano_Numero")[coluna].mean().sort_index()


def _escala(series):
    maximo = pd.concat(series).abs().max() if series else float("nan")
    if pd.isna(maximo):
        return 1, "R$"
    for divisor, unidade in ((1e9, "R$ bi"), (1e6, "R$ mi"), (1e3, "R$ mil")):
        if maximo >= divisor:
            return divisor, unidade
    return 1, "R$"


def gerar(ano, cenario_exibido):
    """PDF da Visão Geral para o ano e o cenário (nome exibido na tela)."""
    df = carregar_indicadores()
    inverso = {exibido: original for original, exibido in mapa_cenarios(df).items()}
    cenario = inverso.get(cenario_exibido, TODOS_OS_CENARIOS)

    pdf = RelatorioPDF(
        "Visão Geral",
        "Principais números e saúde financeira do negócio, com uma leitura "
        "interpretativa gerada a partir dos dados do painel.",
        [("Ano", str(ano)), ("Cenário", cenario_exibido)],
    )

    # 1. Resumo executivo
    pdf.secao(
        "Resumo executivo",
        "Leitura gerada automaticamente a partir dos números do recorte. "
        + ("Com “Todos os cenários”, os valores são a média dos cenários."
           if cenario == TODOS_OS_CENARIOS else "Valores do cenário escolhido."),
    )
    frases = _resumo_executivo(df, ano, cenario)
    if frases:
        pdf.topicos(frases)
    else:
        pdf.paragrafo("Não há dados suficientes neste recorte para montar o resumo.")

    # 2. Indicadores (os mesmos da tela, com a comparação anual)
    pdf.secao(
        "Indicadores do período",
        "A nota abaixo de cada valor compara com o ano anterior. A cor indica só a "
        "direção da mudança, não se ela é boa ou ruim.",
    )
    cartoes = []
    for coluna, rotulo, formato in INDICADORES:
        valor = valor_indicador(df, ano, cenario, coluna)
        variacao = variacao_anual(df, ano, cenario, coluna,
                                  "moeda" if formato == "moeda" else
                                  "percentual" if formato == "percentual" else "numero")
        tom = {"positive": "positivo", "negative": "negativo"}.get(variacao["classe"])
        # no cartão do PDF cabe pouco texto: "— dados insuficientes..." vira uma nota curta
        nota = variacao["texto"] if not variacao["texto"].startswith("—") else "Sem comparação anual"
        cartoes.append((rotulo, FORMATADORES[formato](valor), nota, tom))
    pdf.cards(cartoes)

    # 3. Evolução ao longo dos anos
    historico = _historico(df, cenario)
    pdf.secao(
        "Evolução ao longo dos anos",
        "Média dos cenários em cada ano." if cenario == TODOS_OS_CENARIOS
        else f"Valores do {cenario_exibido} em cada ano.",
    )

    ebitda = _serie(historico, "EBITDA")
    if not ebitda.dropna().empty:
        divisor, unidade = _escala([ebitda])
        pdf.grafico(figura_linhas({"EBITDA": ebitda / divisor}, unidade,
                                  lambda y, _: numero_br(y)), titulo="EBITDA")
        frase = descrever_evolucao("O EBITDA", ebitda, formatar_moeda)
        if frase:
            pdf.leitura(frase)

    retorno = {c: _serie(historico, c) * 100 for c in ("ROIC", "ROE", "WACC")}
    retorno = {c: s for c, s in retorno.items() if not s.dropna().empty}
    if retorno:
        pdf.grafico(figura_linhas(retorno, "%", lambda y, _: f"{numero_br(y)}%"),
                    titulo="Retorno (ROIC, ROE) e custo de capital (WACC)")
        if "ROIC" in retorno and "WACC" in retorno:
            comparacao = (retorno["ROIC"] - retorno["WACC"]).dropna()
            if not comparacao.empty:
                acima = int((comparacao > 0).sum())
                pdf.leitura(
                    f"O ROIC fica acima do WACC em {acima} de {len(comparacao)} anos com dados. "
                    "Quando o retorno do capital supera o seu custo, o negócio gera valor."
                )

    caixa = {c: _serie(historico, c) for c in ("FCO", "FCL")}
    caixa = {c: s for c, s in caixa.items() if not s.dropna().empty}
    if caixa:
        divisor, unidade = _escala(list(caixa.values()))
        pdf.grafico(figura_linhas({c: s / divisor for c, s in caixa.items()}, unidade,
                                  lambda y, _: numero_br(y)),
                    titulo="Caixa da operação (FCO) e caixa livre (FCL)")
        if "FCL" in caixa:
            frase = descrever_evolucao("O caixa livre (FCL)", caixa["FCL"], formatar_moeda)
            if frase:
                pdf.leitura(frase)

    # 4. Qualidade dos dados
    pdf.secao("Qualidade e disponibilidade dos dados")
    ausentes, margem_acima = avisos_de_qualidade(df, ano, cenario)
    avisos = list(ausentes)
    if margem_acima:
        avisos.append(
            "A Margem EBITDA ultrapassa 100% neste recorte. É necessário validar a "
            "fórmula e a origem desse indicador antes de interpretar o resultado."
        )
    if avisos:
        pdf.topicos(avisos)
    else:
        pdf.paragrafo("Os indicadores verificados têm valores disponíveis para o recorte.")

    pdf.aviso(
        "Metodologia: os indicadores vêm da planilha de indicadores e não são recalculados. "
        "Com “Todos os cenários”, os valores são a média dos cenários disponíveis. Dados "
        "ausentes não são preenchidos. As frases interpretativas são descritivas: não são "
        "metas nem previsões."
    )

    return pdf.gerar()
