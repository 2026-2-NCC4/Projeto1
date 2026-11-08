"""Relatório em PDF de Metas x Realizado."""
import pandas as pd

from data.load_data import carregar_demonstrativo
from pages.meta_realizado import (
    CORES_STATUS,
    _preparar_base,
    calcular_metas,
    formatar_percentual,
    formatar_valor,
    indicadores_padrao,
)
from relatorios.base import RelatorioPDF, figura_barras_horizontais


def gerar(ano, cenario, percentil, escolhidos=None):
    """PDF do cenário frente à meta analítica (percentil dos cenários do ano)."""
    df, colunas_base = _preparar_base(carregar_demonstrativo())
    df_ano = df[df["Ano"] == ano].copy()
    escolhidos = [e for e in (escolhidos or indicadores_padrao(colunas_base)) if e in colunas_base]

    pdf = RelatorioPDF(
        "Metas x Realizado",
        "Resultado de um cenário comparado com uma meta analítica calculada a partir de "
        "todos os cenários do mesmo ano.",
        [("Ano", f"Ano {ano}"), ("Cenário", f"Cenário {cenario}"),
         ("Meta", f"percentil {percentil} dos cenários")],
    )

    resultado = calcular_metas(df_ano, cenario, percentil, escolhidos, colunas_base)
    if resultado.empty:
        pdf.secao("Resultado")
        pdf.paragrafo("Não foi possível calcular os indicadores deste cenário.")
        return pdf.gerar()

    contagem = resultado["Status"].value_counts()
    total = len(resultado)
    atingidas = int(contagem.get("Atingida", 0))
    atencao = int(contagem.get("Atenção", 0))
    criticas = int(contagem.get("Crítica", 0))

    # 1. Conclusão
    if atingidas == total:
        titulo = f"O Cenário {cenario} atinge todas as {total} metas"
    elif atingidas == 0:
        titulo = f"O Cenário {cenario} não atinge nenhuma das {total} metas"
    else:
        titulo = f"O Cenário {cenario} atinge {atingidas} de {total} metas"

    linhas = []
    melhor = resultado.dropna(subset=["% Atingimento"]).sort_values("% Atingimento")
    if not melhor.empty:
        topo, base = melhor.iloc[-1], melhor.iloc[0]
        linhas.append(
            f"O melhor desempenho relativo é em {topo['Indicador']} "
            f"({formatar_percentual(topo['% Atingimento'])} da meta) e o mais distante da "
            f"meta é {base['Indicador']} ({formatar_percentual(base['% Atingimento'])})."
        )
    linhas.append(
        f"Com a meta no percentil {percentil}, só cerca de {100 - percentil}% dos cenários "
        "atingem 100% por construção: o status mostra a posição relativa do cenário, não um "
        "desempenho bom ou ruim em termos absolutos."
    )
    pdf.secao("Conclusão")
    pdf.destaque(titulo, linhas)

    pdf.cards([
        ("Indicadores analisados", str(total), "", None),
        ("Metas atingidas", str(atingidas), "a partir de 100%", "positivo" if atingidas else None),
        ("Em atenção", str(atencao), "de 90% a 99%", None),
        ("Críticas", str(criticas), "abaixo de 90%", "negativo" if criticas else None),
    ])

    # 2. Tabela e gráfico
    pdf.secao("Meta x Realizado por indicador")
    pdf.tabela(
        ["Indicador", "Realizado", "Meta analítica", "Atingimento", "Status"],
        [
            [linha["Indicador"],
             formatar_valor(linha["Realizado"], linha["Indicador"]),
             formatar_valor(linha["Meta analítica"], linha["Indicador"]),
             formatar_percentual(linha["% Atingimento"]),
             linha["Status"]]
            for _, linha in resultado.iterrows()
        ],
        larguras=(38, 28, 28, 24, 22),
    )

    grafico = resultado.dropna(subset=["% Atingimento"]).sort_values("% Atingimento", ascending=False)
    if not grafico.empty:
        pdf.grafico(
            figura_barras_horizontais(
                list(grafico["Indicador"]), list(grafico["% Atingimento"]),
                formatar_percentual,
                cores=[CORES_STATUS.get(s, "#8AA4BF") for s in grafico["Status"]],
                altura_por_barra=0.42,
            ),
            titulo="Atingimento da meta por indicador (100% = exatamente na meta)",
        )

    pdf.aviso(
        "Meta analítica: o percentil escolhido dos valores de todos os cenários no mesmo ano; "
        "não é uma meta orçamentária aprovada. Custos e despesas ficam negativos na base: "
        "quanto mais perto de zero, melhor. Margem EBITDA = EBITDA ÷ receita líquida."
    )

    return pdf.gerar()
