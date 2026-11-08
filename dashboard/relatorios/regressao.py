"""Relatório em PDF da Regressão."""
from data.load_data import carregar_demonstrativo
from pages.regressao import (
    FATORES,
    RESULTADO,
    VARIACAO_IMPACTO,
    _confianca,
    _moeda_mi,
    _moeda_sinal,
    _num,
    _p_valor,
    _qualidade_ajuste,
    calcular_regressao,
    texto_resposta,
)
from relatorios.base import (
    RelatorioPDF,
    figura_barras_horizontais,
    figura_dispersao,
    numero_br,
)


def gerar(ano, cenario):
    """PDF da Regressão para o ano escolhido, com o cenário em destaque."""
    df = carregar_demonstrativo()
    calculo = calcular_regressao(df, ano)

    pdf = RelatorioPDF(
        "Regressão",
        f"O que mais influencia a {RESULTADO}? A análise compara os 1.200 cenários "
        "simulados de um ano para responder.",
        [("Ano analisado", f"Ano {ano}"), ("Cenário em destaque", f"Cenário {cenario}")],
    )

    if "erro" in calculo:
        pdf.secao("Resultado")
        pdf.paragrafo(calculo["erro"])
        return pdf.gerar()

    modelo, fatores, recorte, y = (
        calculo["modelo"], calculo["fatores"], calculo["recorte"], calculo["y"]
    )

    # 1. A resposta, em destaque
    titulo, texto = texto_resposta(ano, fatores, modelo)
    pdf.secao("Resposta")
    pdf.destaque(titulo, [
        texto,
        "A análise mostra como os valores andam juntos nos cenários simulados; "
        "não prova causa e efeito.",
    ])

    # 2. Números do modelo
    explica = max(modelo["r2_ajustado"], 0)
    pdf.secao("Números do modelo")
    pdf.cards([
        ("Quanto o modelo explica", f"{_num(explica * 100, 0)}%",
         _qualidade_ajuste(modelo["r2_ajustado"]), None),
        ("Erro típico da previsão", f"± {_moeda_mi(modelo['rmse'])}",
         "entre o caixa previsto e o real", None),
        ("Cenários analisados", _num(len(recorte), 0), f"dados completos no Ano {ano}", None),
    ], por_linha=3)

    # 3. Impacto de cada fator
    pdf.secao(
        "Impacto de cada fator",
        f"Quanto a {RESULTADO} muda se o fator crescer {VARIACAO_IMPACTO:.0%} e os outros "
        "ficarem iguais. Custos e Investimentos são saídas de dinheiro: crescer significa "
        "gastar mais.",
    )
    pdf.grafico(figura_barras_horizontais(
        [f["nome"] for f in fatores],
        [f["impacto"] for f in fatores],
        _moeda_sinal,
        cores=["#3E9C7A" if f["impacto"] >= 0 else "#E07B4A" for f in fatores],
        altura_por_barra=0.45,
    ))
    pdf.topicos([
        f"{f['nome']} — {FATORES[f['nome']]}: {_moeda_sinal(f['impacto'])} na {RESULTADO}, "
        f"{_confianca(f['p'])[0].lower()}."
        for f in fatores
    ])

    # 4. O modelo acerta?
    previsto = modelo["previsto"]
    cenarios = recorte["Cenario"].to_numpy()
    destaque = None
    posicao = [i for i, c in enumerate(cenarios) if int(c) == int(cenario)]
    if posicao:
        destaque = (previsto[posicao[0]], y[posicao[0]])

    pdf.grafico(
        figura_dispersao(previsto, y, "Previsto (R$ mi)", "Real (R$ mi)", destaque,
                         lambda v, _: numero_br(v, 0)),
        titulo="O modelo acerta? Previsto × real",
        largura=125,
    )
    leitura = (
        "Cada ponto é um cenário; pontos perto da linha verde foram bem previstos. "
        f"O erro típico é de ± {_moeda_mi(modelo['rmse'])}."
    )
    if destaque is not None:
        leitura += (
            f" O Cenário {cenario} (em laranja) teve caixa real de {_moeda_mi(destaque[1])} "
            f"e previsto de {_moeda_mi(destaque[0])}."
        )
    pdf.leitura(leitura)

    # 5. Detalhes estatísticos
    pdf.secao(
        "Detalhes estatísticos",
        "Regressão linear múltipla (mínimos quadrados) entre os cenários do ano, valores "
        "em R$ mi. Coeficiente: variação do caixa, em R$ mi, a cada +R$ 1 mi no fator.",
    )
    pdf.tabela(
        ["Fator", "Coeficiente", "Erro padrão", "p-valor", "IC 95%"],
        [
            [f["nome"], _num(f["coef"]), _num(f["erro_padrao"]),
             _p_valor(f["p"]).replace("&lt;", "<"),
             f"{_num(f['ic_inf'])} – {_num(f['ic_sup'])}"]
            for f in fatores
        ],
        larguras=(34, 22, 22, 18, 30),
    )
    pdf.aviso(
        "p-valor abaixo de 0,01: confiança alta; entre 0,01 e 0,05: média; acima de 0,05: "
        "baixa. Associação estatística não comprova causa e efeito."
    )

    return pdf.gerar()
