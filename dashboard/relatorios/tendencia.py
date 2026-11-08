"""Relatório em PDF da Tendência."""
import re

import pandas as pd

from pages.tendencias import (
    INDICADORES,
    _alertas,
    _carregar_indicador,
    _formatar,
    _resumo_anual,
    _variacoes,
    resumo_evolucao,
)
from relatorios.base import (
    RelatorioPDF,
    figura_barras_agrupadas,
    figura_faixa,
    numero_br,
)


def _virgula(texto):
    """'+42.7%' -> '+42,7%': os textos da tela usam ponto decimal nos percentuais."""
    return re.sub(r"(\d)\.(\d)", r"\1,\2", texto)


def _escala(unidade, valores):
    """Divisor e rótulo do eixo para mostrar o indicador no gráfico."""
    if unidade == "moeda":
        maximo = pd.Series(valores).abs().max()
        return (1e9, "R$ bi") if maximo >= 1e9 else (1e6, "R$ mi")
    if unidade == "percentual":
        return 0.01, "%"
    if unidade == "dias":
        return 1, "dias"
    if unidade == "multiplo":
        return 1, "vezes"
    return 1, ""


def gerar(indicador, periodo, cenario, secundario="Nenhum"):
    """PDF da tendência do indicador no período, com o cenário em destaque."""
    _, _, _, unidade, direcao = INDICADORES[indicador]
    formatar = lambda v: _formatar(v, unidade)  # noqa: E731

    dados = _carregar_indicador(indicador)
    dados = dados[dados["Ano"].between(periodo[0], periodo[1])].copy()

    pdf = RelatorioPDF(
        "Tendências",
        "Evolução histórica do indicador, a distribuição dos cenários e os principais "
        "sinais de atenção no período.",
        [("Indicador", indicador), ("Período", f"Ano {periodo[0]} a Ano {periodo[1]}"),
         ("Cenário em destaque", f"Cenário {cenario}")],
    )

    if dados.empty:
        pdf.secao("Resultado")
        pdf.paragrafo("Não há dados do indicador no período selecionado.")
        return pdf.gerar()

    resumo = _resumo_anual(dados)
    variacoes = _variacoes(resumo)
    cagr, maior_txt, melhor_txt, pior_txt = resumo_evolucao(resumo, variacoes, direcao)

    # 1. Leitura
    primeiro, ultimo = resumo.iloc[0], resumo.iloc[-1]
    frases = [
        f"A média dos cenários vai de {formatar(primeiro['Media'])} no Ano {int(primeiro['Ano'])} "
        f"para {formatar(ultimo['Media'])} no Ano {int(ultimo['Ano'])}"
        + (f", um crescimento médio de {numero_br(cagr * 100)}% ao ano (CAGR)." if pd.notna(cagr)
           else "."),
    ]
    if maior_txt != "—":
        frases.append(
            f"A maior oscilação anual foi de {_virgula(maior_txt).replace('·', 'no')}. "
            f"Considerando que, para este indicador, {'maior' if direcao == 'maior' else 'menor'} "
            f"é melhor, o melhor ano foi o {melhor_txt} e o pior, o {pior_txt}."
        )

    destaque = dados[dados["Cenario"] == cenario].set_index("Ano")["Valor"].sort_index()
    comparacao = (destaque - resumo.set_index("Ano")["Media"]).dropna()
    if not comparacao.empty:
        acima = int((comparacao > 0).sum())
        frases.append(
            f"O Cenário {cenario} fica acima da média em {acima} de {len(comparacao)} anos."
        )

    faixa = ultimo["P90"] - ultimo["P10"]
    frases.append(
        f"No Ano {int(ultimo['Ano'])}, 80% dos cenários ficam entre {formatar(ultimo['P10'])} e "
        f"{formatar(ultimo['P90'])} (faixa P10–P90 de {formatar(faixa)})."
    )

    pdf.secao("Resumo da evolução", "Calculado com a média anual dos cenários válidos.")
    pdf.topicos(frases)
    pdf.cards([
        ("Crescimento médio anual", f"{cagr:+.1%}".replace(".", ",") if pd.notna(cagr) else "N/A",
         "CAGR do período", None),
        ("Maior variação anual", _virgula(maior_txt), "maior oscilação", None),
        ("Melhor ano", melhor_txt, "considera a direção do indicador", None),
        ("Pior ano", pior_txt, "considera a direção do indicador", None),
    ])

    # 2. Gráficos
    divisor, rotulo = _escala(unidade, resumo["Media"])
    anos = resumo["Ano"].astype(int).tolist()
    pdf.grafico(
        figura_faixa(
            anos, resumo["Media"] / divisor, resumo["P10"] / divisor, resumo["P90"] / divisor,
            destaque / divisor, f"Cenário {cenario}", rotulo, lambda v, _: numero_br(v),
        ),
        titulo="Evolução histórica e faixa dos cenários",
    )
    pdf.leitura(
        "A linha azul é a média dos cenários; a faixa sombreada concentra os 80% centrais "
        "dos cenários (P10 a P90); a linha laranja é o cenário em destaque."
    )

    validas = variacoes.dropna(subset=["Variacao"])
    if not validas.empty:
        pdf.grafico(
            figura_barras_agrupadas(
                [str(int(a)) for a in validas["Ano"]],
                {"Variação da média": list(validas["Variacao"] * 100)},
                "%", lambda v, _: f"{numero_br(v, 0)}%",
            ),
            titulo="Variação anual da média dos cenários",
        )

    # 3. Alertas
    pdf.secao("Alertas automáticos", "Sinais estatísticos do período. Não são previsões.")
    pdf.topicos([
        f"{titulo}: {_virgula(texto)}" for _, titulo, texto in _alertas(resumo, variacoes)[:6]
    ])

    # 4. Indicador secundário (se escolhido na tela)
    if secundario and secundario != "Nenhum":
        _, _, _, unidade_sec, _ = INDICADORES[secundario]
        sec = _carregar_indicador(secundario)
        sec = _resumo_anual(sec[sec["Ano"].between(periodo[0], periodo[1])])
        tabela = resumo[["Ano", "Media"]].merge(
            sec[["Ano", "Media"]], on="Ano", how="inner", suffixes=("", "_sec")
        )
        if not tabela.empty:
            pdf.secao(
                f"Comparação de médias anuais: {indicador} e {secundario}",
                "Cada indicador mantém sua unidade. Compare principalmente a direção das "
                "tendências.",
            )
            pdf.tabela(
                ["Ano", indicador, secundario],
                [[f"Ano {int(l.Ano)}", formatar(l.Media), _formatar(l.Media_sec, unidade_sec)]
                 for l in tabela.itertuples()],
                larguras=(20, 40, 40),
            )

    pdf.aviso(
        "P10: 10% dos cenários ficam abaixo desse valor; P90: 90% ficam abaixo. Variação "
        "anual: mudança percentual da média em relação ao ano anterior."
    )

    return pdf.gerar()
