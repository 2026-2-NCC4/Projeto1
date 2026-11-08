"""Relatório em PDF dos Insights."""
from data.load_data import carregar_demonstrativo
from pages.insights import CAIXA, RECEITA, calcular_insights
from pages.regressao import _moeda_mi
from relatorios.base import RelatorioPDF, descrever_evolucao, figura_linhas, numero_br


def gerar(ano, cenario):
    """PDF dos Insights para o ano e o cenário (número) escolhidos."""
    df = carregar_demonstrativo()
    resultado = calcular_insights(df, ano, cenario)

    pdf = RelatorioPDF(
        "Insights",
        "Destaques do ano com recomendações e uma conclusão pronta para a apresentação, "
        "calculados a partir dos 1.200 cenários simulados.",
        [("Ano", f"Ano {ano}"), ("Cenário em destaque", f"Cenário {cenario}")],
    )

    # 1. Conclusão primeiro: é o que o leitor quer saber
    pdf.secao("Conclusão para a apresentação")
    pdf.destaque(resultado["conclusao_titulo"], resultado["conclusao"])

    # 2. Os quatro destaques que sustentam a conclusão
    pdf.secao(
        "Destaques do ano",
        "Cada destaque traz o número, o que ele significa e uma recomendação.",
    )
    for numero, card in enumerate(resultado["cards"], start=1):
        pdf.bloco_numerado(numero, card["titulo"], card["valor"], card["texto"], card["acao"])

    # 3. Gráficos de apoio
    pdf.secao("Contexto ao longo dos anos")

    receita = df.groupby("Ano")[RECEITA].mean().sort_index() / 1e9
    pdf.grafico(figura_linhas({"Receita média": receita}, "R$ bi", lambda y, _: numero_br(y)),
                titulo="Receita média dos cenários")
    frase = descrever_evolucao("A receita média", receita * 1000,
                               lambda v: _moeda_mi(v))
    if frase:
        pdf.leitura(frase)

    caixa_cenario = (
        df[df["Cenario"] == cenario].set_index("Ano")[CAIXA].sort_index() / 1e9
    )
    caixa_media = df.groupby("Ano")[CAIXA].mean().sort_index() / 1e9
    pdf.grafico(figura_linhas(
        {f"Cenário {cenario}": caixa_cenario, "Média dos cenários": caixa_media},
        "R$ bi", lambda y, _: numero_br(y),
    ), titulo=f"Geração de caixa: Cenário {cenario} × média dos cenários")
    comparacao = (caixa_cenario - caixa_media).dropna()
    if not comparacao.empty:
        acima = int((comparacao > 0).sum())
        pdf.leitura(
            f"O Cenário {cenario} gera mais caixa que a média em {acima} de "
            f"{len(comparacao)} anos."
        )

    # 4. Como ler
    pdf.secao("Como interpretar")
    pdf.topicos([
        "Caixa em destaque: compara a geração de caixa do cenário escolhido com a média "
        "dos cenários do ano.",
        "Receita: variação da receita média sobre o ano anterior.",
        "Melhor margem: cenário com a maior margem EBITDA do ano.",
        "Maior sensibilidade: variável que mais move o Resultado Líquido se variar 10%, "
        "estimada por regressão entre os cenários do ano.",
    ])
    pdf.aviso(
        "Os destaques são leituras descritivas dos cenários simulados, não previsões. "
        "Valores em reais, abreviados em milhões (mi) e bilhões (bi)."
    )

    return pdf.gerar()
