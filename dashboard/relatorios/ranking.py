"""Relatório em PDF do Ranking de cenários."""
from data.load_data import carregar_indicadores
from pages.indicadores import INDICADORES
from pages.ranking import _formatar_valor, calcular_ranking
from relatorios.base import RelatorioPDF, figura_barras_horizontais

QUANTIDADE = 10


def gerar(ano, indicador):
    """PDF do ranking dos cenários pelo indicador no ano."""
    df = carregar_indicadores()
    dados, formato = calcular_ranking(df, ano, indicador)
    formatar = lambda v: _formatar_valor(v, formato)  # noqa: E731

    pdf = RelatorioPDF(
        "Ranking de cenários",
        "Classificação dos cenários pelo indicador escolhido, do maior para o menor valor.",
        [("Ano", f"Ano {ano}"), ("Indicador", indicador)],
    )

    if dados.empty:
        pdf.secao("Resultado")
        pdf.paragrafo(f"Não há valores de {indicador} disponíveis para o Ano {ano}.")
        return pdf.gerar()

    valores = dados["Valor"]
    maior, menor = dados.iloc[0], dados.iloc[-1]
    media, mediana = valores.mean(), valores.median()

    # 1. Leitura
    pdf.secao("Resumo", INDICADORES[indicador].get("descricao"))
    quantidade_cenarios = f"{len(dados):,}".replace(",", ".")
    frases = [
        f"Entre os {quantidade_cenarios} cenários com valor no Ano {ano}, o {maior['Cenário']} "
        f"lidera com {formatar(maior['Valor'])} e o {menor['Cenário']} fica em último, com "
        f"{formatar(menor['Valor'])}.",
        f"A média dos cenários é {formatar(media)} e a mediana, {formatar(mediana)}: metade "
        "dos cenários fica acima e metade abaixo desse valor.",
    ]
    if media > mediana * 1.02 and mediana > 0:
        frases.append(
            "A média acima da mediana indica alguns cenários com valores bem altos puxando "
            "a média para cima."
        )
    elif media < mediana * 0.98 and mediana > 0:
        frases.append(
            "A média abaixo da mediana indica alguns cenários com valores bem baixos puxando "
            "a média para baixo."
        )
    acima = int((valores > media).sum())
    frases.append(f"{acima} cenários ({acima / len(dados):.0%}) ficam acima da média.")
    pdf.topicos(frases)
    pdf.aviso(
        "Maior nem sempre é melhor: em prazos (PMR, ciclo financeiro), necessidade de capital "
        "de giro e endividamento, valores menores costumam ser favoráveis."
    )

    pdf.cards([
        (f"Maior {indicador}", formatar(maior["Valor"]), maior["Cenário"], None),
        (f"Menor {indicador}", formatar(menor["Valor"]), menor["Cenário"], None),
        ("Média dos cenários", formatar(media), f"{quantidade_cenarios} cenários", None),
        ("Mediana", formatar(mediana), "valor do meio", None),
    ])

    # 2. Extremos
    quantidade = min(QUANTIDADE, len(dados))
    maiores = dados.head(quantidade)
    menores = dados.tail(quantidade).sort_values("Valor", ascending=True)

    pdf.grafico(
        figura_barras_horizontais(list(maiores["Cenário"]), list(maiores["Valor"]), formatar,
                                  cores=["#1677E8"] * quantidade),
        titulo=f"{quantidade} maiores cenários — {indicador}",
    )
    pdf.grafico(
        figura_barras_horizontais(list(menores["Cenário"]), list(menores["Valor"]), formatar,
                                  cores=["#E7A23B"] * quantidade),
        titulo=f"{quantidade} menores cenários — {indicador}",
    )

    pdf.aviso(
        "Fonte: aba _Indicadores da planilha Analise_Financeira.xlsx. O ranking considera a "
        "média dos registros de cada cenário no ano. Cenários sem valor para o indicador não "
        "entram na lista."
    )

    return pdf.gerar()
