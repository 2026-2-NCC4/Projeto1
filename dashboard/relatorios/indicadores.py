"""Relatório em PDF dos Indicadores Financeiros."""
import pandas as pd

from data.load_data import carregar_indicadores
from pages.indicadores import (
    INDICADORES,
    _formatar_indicador,
    _mapear_cenarios,
    cartoes_resumo,
    leituras_desempenho,
    leituras_estrutura,
    preparar_indicadores,
    recorte_indicadores,
)
from relatorios.base import RelatorioPDF


def gerar(ano, cenario):
    """PDF dos indicadores do ano (rótulo "Ano N") e do cenário (nome original ou "Todos")."""
    df = preparar_indicadores(carregar_indicadores())
    nome_cenario = "Todos os cenários" if cenario == "Todos" else _mapear_cenarios(df).get(cenario, cenario)
    df_ano, df_anterior = recorte_indicadores(df, ano, cenario)

    pdf = RelatorioPDF(
        "Indicadores Financeiros",
        "Rentabilidade, liquidez, endividamento, capital de giro, caixa e valor econômico "
        "do recorte escolhido, com leituras automáticas de cada indicador.",
        [("Ano", str(ano)), ("Cenário", nome_cenario)],
    )

    if df_ano.empty:
        pdf.secao("Resultado")
        pdf.paragrafo("Não existem dados para essa seleção.")
        return pdf.gerar()

    # 1. Resumo do ano
    pdf.secao(
        f"Resumo de {ano}",
        "Média dos cenários." if cenario == "Todos" else "Valores do cenário escolhido.",
    )
    pdf.cards([(titulo, valor, nota, None) for titulo, valor, nota in cartoes_resumo(df_ano)])

    # 2. Leituras automáticas (os mesmos textos da tela)
    desempenho = leituras_desempenho(df_ano, df_anterior, cenario)
    itens = desempenho["esquerda"] + desempenho["direita"] + desempenho["abaixo"]
    if itens:
        pdf.secao("Desempenho", "Leituras automáticas dos indicadores do ano.")
        pdf.topicos([f"{titulo}: {texto}" for titulo, texto in itens])

    esquerda, direita = leituras_estrutura(df_ano, cenario)
    if esquerda or direita:
        pdf.secao(
            "Estrutura, capital de giro e caixa",
            "Leituras de retorno, capital de giro e caixa. Com todos os cenários, usam a "
            "mediana para que cenários extremos não distorçam o resultado.",
        )
        pdf.topicos([f"{titulo}: {texto}" for titulo, texto in esquerda + direita])

    # 3. Todos os indicadores, por grupo
    pdf.secao(
        "Todos os indicadores",
        "Com todos os cenários: média, mediana e a faixa entre o menor e o maior valor. "
        "“—” indica indicador sem valor no ano." if cenario == "Todos"
        else "Valor do cenário em cada indicador. “—” indica indicador sem valor no ano.",
    )
    grupos = list(dict.fromkeys(config["grupo"] for config in INDICADORES.values()))
    for grupo in grupos:
        colunas = [c for c, cfg in INDICADORES.items() if cfg["grupo"] == grupo and c in df_ano.columns]
        if not colunas:
            continue
        pdf.subtitulo(grupo)
        if cenario == "Todos":
            linhas = []
            for coluna in colunas:
                serie = pd.to_numeric(df_ano[coluna], errors="coerce").dropna()
                if serie.empty:
                    linhas.append([coluna, "—", "—", "—"])
                    continue
                linhas.append([
                    coluna,
                    _formatar_indicador(coluna, serie.mean(), df_ano[coluna]),
                    _formatar_indicador(coluna, serie.median(), df_ano[coluna]),
                    f"{_formatar_indicador(coluna, serie.min(), df_ano[coluna])} a "
                    f"{_formatar_indicador(coluna, serie.max(), df_ano[coluna])}",
                ])
            pdf.tabela(["Indicador", "Média", "Mediana", "Faixa (menor a maior)"], linhas,
                       larguras=(46, 26, 26, 48))
        else:
            pdf.tabela(
                ["Indicador", "Valor", "O que mede"],
                [
                    [coluna,
                     _formatar_indicador(coluna, df_ano[coluna].iloc[0], df_ano[coluna]),
                     INDICADORES[coluna].get("descricao", "")]
                    for coluna in colunas
                ],
                larguras=(40, 26, 80),
            )

    pdf.aviso(
        "Os indicadores de caixa são estimados a partir do balanço e da DRE, não de um fluxo de "
        "caixa contábil completo. Indicadores que usam o ano anterior (ROE, FCO, FCL e "
        "coberturas) não existem no Ano 1. Fonte: aba _Indicadores da planilha "
        "Analise_Financeira.xlsx."
    )

    return pdf.gerar()
