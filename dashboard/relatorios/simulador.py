"""Relatório em PDF do simulador de cenários."""
from data.load_data import carregar_demonstrativo
from pages.regressao import _moeda_mi, _num
from pages.simulador import (
    MEDIA_CENARIOS,
    PREMISSAS,
    RESSALVA_SIMULACAO,
    _base,
    _margem,
    simular,
    texto_simulacao,
)
from relatorios.base import (
    RelatorioPDF,
    figura_barras_agrupadas,
    figura_barras_horizontais,
    numero_br,
)


def _pct(valor):
    return f"{_num(valor * 100, 1)}%"


def _delta(antes, depois, formato):
    diferenca = depois - antes
    if formato == "pct":
        pontos = diferenca * 100
        if abs(pontos) < 0.05:
            return "Sem mudança", None
        return (f"{'+' if pontos > 0 else '−'}{_num(abs(pontos), 1)} p.p.",
                "positivo" if pontos > 0 else "negativo")
    if abs(diferenca) < 0.005:
        return "Sem mudança", None
    return (f"{'+' if diferenca > 0 else '−'}{_moeda_mi(abs(diferenca))}",
            "positivo" if diferenca > 0 else "negativo")


def gerar(ano, cenario, premissas):
    """PDF da simulação. premissas = {"receita": 0.10, ...} (frações)."""
    df = carregar_demonstrativo()
    base = _base(df, ano, cenario)
    nome_cenario = cenario if cenario == MEDIA_CENARIOS else f"Cenário {cenario}"

    descricao_premissas = ", ".join(
        f"{PREMISSAS[k]} {'+' if v > 0 else '−' if v < 0 else ''}{_num(abs(v) * 100, 0)}%"
        for k, v in premissas.items()
    )
    pdf = RelatorioPDF(
        "Simular novo cenário",
        "Efeito das premissas escolhidas sobre os resultados, refazendo as contas da DRE "
        "e do fluxo de caixa.",
        [("Ano", f"Ano {ano}"), ("Base", nome_cenario), ("Premissas", descricao_premissas)],
    )

    if base is None:
        pdf.secao("Resultado")
        pdf.paragrafo("Não há dados para este cenário no ano escolhido.")
        return pdf.gerar()

    zero = {k: 0 for k in PREMISSAS}
    original = simular(base, zero)
    simulado = simular(base, premissas)

    # 1. Conclusão
    texto, _ = texto_simulacao(premissas, original, simulado, ano)
    if not any(premissas.values()):
        texto = (
            "Nenhuma premissa foi alterada: os valores simulados são iguais aos do cenário "
            "base. Ajuste as premissas na tela do simulador e gere o relatório de novo."
        )
    pdf.secao("Conclusão")
    pdf.destaque("O que muda com essas premissas", [texto, RESSALVA_SIMULACAO])

    # 2. Original × simulado
    pdf.secao("Original × simulado", f"Valores do Ano {ano}.")
    itens = [
        ("EBITDA", original["ebitda"], simulado["ebitda"], "moeda"),
        ("Margem EBITDA", _margem(original["ebitda"], original["receita"]),
         _margem(simulado["ebitda"], simulado["receita"]), "pct"),
        ("Resultado Líquido", original["resultado"], simulado["resultado"], "moeda"),
        ("Margem Líquida", _margem(original["resultado"], original["receita"]),
         _margem(simulado["resultado"], simulado["receita"]), "pct"),
        ("Geração de Caixa", original["caixa"], simulado["caixa"], "moeda"),
    ]
    formatar = lambda v, f: _pct(v) if f == "pct" else _moeda_mi(v)  # noqa: E731
    pdf.tabela(
        ["Indicador", "Original", "Simulado", "Diferença"],
        [[nome, formatar(a, f), formatar(d, f), _delta(a, d, f)[0]] for nome, a, d, f in itens],
        larguras=(40, 32, 32, 32),
    )

    # 3. Efeito ao longo dos anos
    anos = sorted(df["Ano"].dropna().astype(int).unique())
    originais, simulados = [], []
    for a in anos:
        b = _base(df, a, cenario)
        originais.append(simular(b, zero)["resultado"] / 1000 if b is not None else 0)
        simulados.append(simular(b, premissas)["resultado"] / 1000 if b is not None else 0)
    pdf.grafico(
        figura_barras_agrupadas(
            [str(a) for a in anos], {"Original": originais, "Simulado": simulados},
            "R$ bi", lambda v, _: numero_br(v), destaque=str(ano),
        ),
        titulo="Resultado Líquido por ano: original × simulado",
    )
    diferenca_total = sum(simulados) - sum(originais)
    pdf.leitura(
        "Aplicando as mesmas premissas a todos os anos, o Resultado Líquido acumulado dos "
        f"{len(anos)} anos {'aumenta' if diferenca_total >= 0 else 'diminui'} "
        f"{_moeda_mi(abs(diferenca_total) * 1000)}."
    )

    # 4. Cascata: da receita ao resultado
    etapas = [
        ("Receita", simulado["receita"]),
        ("Tributos", simulado["tributos"]),
        ("Custos", simulado["custos"]),
        ("Depreciação", simulado["depreciacao"]),
        ("Financeiro e outros", simulado["financeiro_outros"]),
        ("Imposto de renda", simulado["ir"]),
        ("Resultado Líquido", simulado["resultado"]),
    ]
    pdf.grafico(
        figura_barras_horizontais(
            [n for n, _ in etapas], [v for _, v in etapas], _moeda_mi,
            cores=["#1677E8" if n in ("Receita", "Resultado Líquido")
                   else "#6DB59A" if v >= 0 else "#E29A8F" for n, v in etapas],
        ),
        titulo=f"Da receita ao resultado no Ano {ano} (já com as premissas)",
    )
    if simulado["receita"]:
        sobra = simulado["resultado"] / simulado["receita"] * 100
        pdf.leitura(
            f"De cada R$ 100 de receita simulada, R$ {numero_br(sobra)} chegam ao resultado "
            "líquido depois de tributos, custos, depreciação, resultado financeiro e imposto."
        )

    pdf.aviso(
        "A simulação refaz as contas com regras simplificadas e não representa uma previsão. "
        "Valores em reais, abreviados em milhões (mi) e bilhões (bi)."
    )

    return pdf.gerar()
