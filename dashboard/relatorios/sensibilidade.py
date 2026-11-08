"""Relatório em PDF da Sensibilidade."""
import pandas as pd

from data.load_data import carregar_demonstrativo
from pages.regressao import RESULTADO, VARIACAO_IMPACTO, _moeda_mi, _num
from pages.sensibilidade import _calcular_sensibilidade, _simular_indicador
from relatorios.base import RelatorioPDF, figura_barras_horizontais

# Indicador que cada fator da simulação altera (mesma regra da tela)
INDICADOR_AFETADO = {
    "WACC": "EVA",
    "ROIC": "EVA",
    "Margem EBITDA": "EBITDA",
    "Receita": "EBITDA",
    "PMR": "necessidade de capital de giro",
    "PMP": "necessidade de capital de giro",
    "Investimentos": "fluxo de caixa livre",
}


def _sinal_moeda(valor):
    return ("+" if valor >= 0 else "−") + _moeda_mi(abs(valor))


def _base():
    df = carregar_demonstrativo().copy()
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    df["Cenario"] = pd.to_numeric(df["Cenario"], errors="coerce")
    return df


def gerar(ano, cenario, fator="WACC", variacao=0.10):
    """PDF com a regressão do ano e a simulação do fator escolhido no cenário."""
    df = _base()

    pdf = RelatorioPDF(
        "Sensibilidade",
        "Como variações nos fatores financeiros se relacionam com a geração de caixa e com "
        "os principais indicadores.",
        [("Ano", f"Ano {ano}"), ("Cenário de referência", f"Cenário {cenario}"),
         ("Simulação", f"{fator} {variacao * 100:+.0f}%")],
    )

    # 1. Regressão: o que move a geração de caixa
    resultado, erro = _calcular_sensibilidade(df, ano)
    pdf.secao(
        "Sensibilidade da geração de caixa",
        f"Quanto a {RESULTADO} muda, em média, se cada fator variar "
        f"{VARIACAO_IMPACTO:.0%} e os outros ficarem iguais, considerando todos os cenários "
        "do ano.",
    )
    if erro:
        pdf.paragrafo(erro)
    else:
        fatores, modelo = resultado["fatores"], resultado["modelo"]
        principal = fatores.iloc[0]
        direcao = "aumenta" if principal["Impacto"] >= 0 else "diminui"
        frases = [
            f"{principal['Variável']} é o fator de maior peso: uma variação de "
            f"{VARIACAO_IMPACTO:.0%} {direcao} a {RESULTADO} em cerca de "
            f"{_moeda_mi(abs(principal['Impacto']))}"
            + (f" ({_num(abs(principal['Impacto percentual']), 1)}% da média dos cenários)."
               if pd.notna(principal["Impacto percentual"]) else "."),
            f"Os fatores juntos explicam {_num(max(modelo['r2_ajustado'], 0) * 100, 0)}% das "
            f"diferenças de caixa entre os {_num(len(resultado['dados']), 0)} cenários do ano.",
        ]
        if resultado["removidos"]:
            frases.append(
                "Fatores retirados do modelo por colinearidade ou ausência de variação: "
                + ", ".join(resultado["removidos"]) + "."
            )
        pdf.topicos(frases)

        pdf.grafico(
            figura_barras_horizontais(
                list(fatores["Variável"]), list(fatores["Impacto"]), _sinal_moeda,
                cores=["#3E9C7A" if v >= 0 else "#E07B4A" for v in fatores["Impacto"]],
                altura_por_barra=0.45,
            ),
            titulo=f"Impacto de {VARIACAO_IMPACTO:.0%} em cada fator na {RESULTADO}",
        )
        pdf.tabela(
            ["Fator", "O que é", "Impacto", "% da média"],
            [
                [linha["Variável"], linha["Descrição"], _sinal_moeda(linha["Impacto"]),
                 f"{_num(linha['Impacto percentual'], 1)}%"
                 if pd.notna(linha["Impacto percentual"]) else "—"]
                for _, linha in fatores.iterrows()
            ],
            larguras=(30, 70, 26, 20),
        )

    # 2. Simulação do fator escolhido
    simulacao, erro = _simular_indicador(df, ano, cenario, fator, variacao)
    afetado = INDICADOR_AFETADO.get(fator, "indicador")
    pdf.secao(
        f"Simulação: {fator} {variacao * 100:+.0f}%",
        f"Efeito no {afetado} do Cenário {cenario}, alterando só esse fator.",
    )
    if erro:
        pdf.paragrafo(erro)
    else:
        original, simulado, impacto = (simulacao["original"] / 1e6, simulacao["simulado"] / 1e6,
                                       simulacao["impacto"] / 1e6)
        pdf.destaque(
            f"O {afetado} vai de {_moeda_mi(original)} para {_moeda_mi(simulado)}",
            [f"Uma variação de {variacao * 100:+.0f}% em {fator} muda o {afetado} em "
             f"{_sinal_moeda(impacto)}, mantendo os demais fatores iguais."],
        )
        pdf.cards([
            ("Valor original", _moeda_mi(original), "cenário de referência", None),
            ("Valor simulado", _moeda_mi(simulado), f"{fator} {variacao * 100:+.0f}%", None),
            ("Impacto estimado", _sinal_moeda(impacto), "simulado − original",
             "positivo" if impacto >= 0 else "negativo"),
        ], por_linha=3)

    pdf.aviso(
        "Os dados são de cenários simulados. A regressão mostra associações e não comprova "
        "causa e efeito. WACC e ROIC alteram o EVA; Margem EBITDA e Receita alteram o EBITDA; "
        "PMR e PMP alteram a necessidade de capital de giro (estimativa simplificada); "
        "Investimentos alteram o fluxo de caixa livre."
    )

    return pdf.gerar()
