"""Relatório em PDF da Comparação de cenários."""
import pandas as pd

from pages.comparacao import (
    COLUNAS_COMPARACAO,
    _formatar_indicador,
    _indicadores_ordenados,
    _preparar_dados,
    _rotulo_cenario,
    cenarios_padrao,
)
from relatorios.base import RelatorioPDF, figura_barras_agrupadas, numero_br

# Indicadores em que "maior é melhor", usados para dizer quem lidera
PRINCIPAIS = ["EBITDA", "Margem EBITDA", "Margem Líquida", "ROIC", "ROE", "FCO", "FCL"]
GRAFICO = ["EBITDA", "NOPAT", "FCO", "FCL"]
CENARIOS_POR_TABELA = 4


def _valor(dados_ano, cenario, indicador):
    linha = dados_ano.loc[dados_ano["Cenario"] == cenario]
    if linha.empty or indicador not in linha.columns:
        return float("nan")
    return linha[indicador].iloc[0]


def gerar(ano, cenarios):
    """PDF comparando os cenários escolhidos (nomes originais da base) no ano."""
    df = _preparar_dados()
    dados_ano = df.loc[df["Ano_Numero"] == ano].copy()

    cenarios = [c for c in (cenarios or []) if c in set(dados_ano["Cenario"])]
    if not cenarios:
        cenarios = cenarios_padrao(dados_ano)
    nomes = [_rotulo_cenario(c) for c in cenarios]

    pdf = RelatorioPDF(
        "Comparação de cenários",
        "Indicadores financeiros dos cenários escolhidos, lado a lado, no mesmo ano.",
        [("Ano", f"Ano {ano}"), ("Cenários", ", ".join(nomes))],
    )

    if dados_ano.empty or not cenarios:
        pdf.secao("Resultado")
        pdf.paragrafo(f"Não há indicadores disponíveis para o Ano {ano}.")
        return pdf.gerar()

    # 1. Quem lidera em cada indicador principal
    pdf.secao(
        "Resumo",
        "Para os indicadores em que um valor maior é melhor, quem fica na frente.",
    )
    frases, liderancas = [], {nome: 0 for nome in nomes}
    for indicador in PRINCIPAIS:
        valores = {
            nome: _valor(dados_ano, c, indicador) for c, nome in zip(cenarios, nomes)
        }
        validos = {n: v for n, v in valores.items() if pd.notna(v)}
        if len(validos) < 2:
            continue
        lider = max(validos, key=validos.get)
        ultimo = min(validos, key=validos.get)
        liderancas[lider] += 1
        frases.append(
            f"{indicador}: o {lider} lidera com {_formatar_indicador(indicador, validos[lider])}; "
            f"o {ultimo} tem {_formatar_indicador(indicador, validos[ultimo])}."
        )

    if len(cenarios) < 2:
        pdf.paragrafo(
            "Só um cenário foi escolhido. Selecione pelo menos dois na tela de Comparação "
            "para ver quem lidera em cada indicador."
        )
    elif frases:
        melhor = max(liderancas, key=liderancas.get)
        avaliados = len(frases)
        pdf.destaque(
            f"{melhor} lidera em {liderancas[melhor]} de {avaliados} indicadores principais",
            [
                "Contagem dos indicadores de resultado, margem, retorno e caixa em que cada "
                "cenário tem o maior valor: "
                + ", ".join(f"{n} ({q})" for n, q in liderancas.items()) + ".",
            ],
        )
        pdf.topicos(frases)

    # 2. Gráfico dos indicadores em reais
    existentes = [i for i in GRAFICO if i in dados_ano.columns]
    if existentes:
        series = {
            nome: [(_valor(dados_ano, c, i) or 0) / 1e6 for i in existentes]
            for c, nome in zip(cenarios, nomes)
        }
        series = {n: [0 if pd.isna(v) else v for v in vs] for n, vs in series.items()}
        pdf.grafico(
            figura_barras_agrupadas(existentes, series, "R$ mi", lambda v, _: numero_br(v, 0)),
            titulo="Resultado e caixa por cenário (R$ milhões)",
        )

    # 3. Todos os indicadores lado a lado (em blocos de até 4 cenários)
    indicadores = _indicadores_ordenados(
        [i for i in COLUNAS_COMPARACAO if i in dados_ano.columns]
    )
    pdf.secao("Todos os indicadores lado a lado")
    for inicio in range(0, len(cenarios), CENARIOS_POR_TABELA):
        bloco = list(zip(cenarios, nomes))[inicio:inicio + CENARIOS_POR_TABELA]
        pdf.tabela(
            ["Indicador"] + [nome for _, nome in bloco],
            [
                [indicador] + [
                    _formatar_indicador(indicador, _valor(dados_ano, c, indicador))
                    for c, _ in bloco
                ]
                for indicador in indicadores
            ],
            larguras=(44,) + (28,) * len(bloco),
        )

    pdf.aviso(
        "Fonte: aba _Indicadores da planilha Analise_Financeira.xlsx. “—” indica indicador "
        "sem valor no ano (os que usam o ano anterior não existem no Ano 1). Valores em reais "
        "aparecem em milhões (mi) ou bilhões (bi)."
    )

    return pdf.gerar()
